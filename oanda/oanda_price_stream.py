from datetime import datetime
from dateutil import parser
import requests
import json
import threading
from typing import List, Iterable
from datahandlers.bars_provider.price_stream import PriceStream
from datahandlers.bars_provider.price_stream_price_item import PriceStreamPriceItem


class OandaPriceStream(PriceStream):

    def __init__(self, account_id, access_token, instruments):
        self.access_token = access_token
        self.account_id = account_id
        self.instruments = instruments
        self.domain = 'stream-fxpractice.oanda.com'

        self.response = None
        self.response_iter_lines = None
        self.connected = False
        self.lock = threading.Lock()

    def get_instruments(self) -> List[str]:
        return self.instruments

    def connect_to_stream(self):
        if self.lock.acquire(True, 10):
            if self.is_connected():
                return

            s = requests.Session()
            url = 'https://{}/v3/accounts/{}/pricing/stream'.format(self.domain, self.account_id)
            headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
            params = {'instruments': ','.join(self.instruments)}

            try:
                req = requests.Request('GET', url, headers=headers, params=params)
                pre = req.prepare()
                self.response = s.send(pre, stream=True, verify=True, timeout=(10, 60))

                if self.response.status_code == 200:
                    self.connected = True

            except Exception as exception:
                s.close()
                raise Exception('Caught exception when connecting to stream\n' + str(exception))
            finally:
                self.lock.release()
        else:
            raise Exception('Could not get lock')

    def is_connected(self):
        return self.connected

    def get_price(self) -> Iterable[PriceStreamPriceItem]:

        if self.response is None:
            raise Exception('Stream is not connected')

        if self.response.status_code != 200:
            print(self.response.text)
            return

        if self.response_iter_lines is None:
            self.response_iter_lines = self.response.iter_lines(1)

        for line in self.response_iter_lines:
            if line:
                try:
                    line = line.decode('utf-8')
                    msg = json.loads(line)

                except Exception as e:
                    raise Exception('Caught exception when converting message into json\n' + str(e))

                if 'instrument' in msg:
                    ask_price = float(msg['asks'][0]['price'])
                    bid_price = float(msg['bids'][0]['price'])

                    price_datetime = OandaPriceStream.get_price_datetime(msg['time'])

                    stream_price = PriceStreamPriceItem(msg['instrument'], price_datetime, ask_price, bid_price)

                    yield stream_price

    @staticmethod
    def get_price_datetime(datetime_as_string: str) -> datetime:
        price_datetime = parser.parse(datetime_as_string)
        price_datetime = price_datetime.replace(microsecond=0)

        return price_datetime
