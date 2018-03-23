import requests
import json


class Stream:

    def __init__(self, account_id, access_token, instruments):
        self.access_token = access_token
        self.account_id = account_id
        self.instruments = instruments
        self.domain = 'stream-fxpractice.oanda.com'

        self.response = None
        self.response_iter_lines = None

    def connect_to_stream(self):
        s = requests.Session()
        url = 'https://{}/v3/accounts/{}/pricing/stream'.format(self.domain, self.account_id)
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        params = {'instruments': ','.join(self.instruments)}

        try:
            req = requests.Request('GET', url, headers=headers, params=params)
            pre = req.prepare()
            self.response = s.send(pre, stream=True, verify=True, timeout=(10, 60))

        except Exception as e:
            s.close()
            raise Exception('Caught exception when connecting to stream\n' + str(e))

    def get_price(self):

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
                    ask_price = msg['asks'][0]['price']
                    bid_price = msg['bids'][0]['price']

                    yield {'instrument': msg['instrument'], 'datetime': msg['time'], 'ask': ask_price, 'bid': bid_price}
