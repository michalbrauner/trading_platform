from oanda.stream import Stream as OandaPriceStream
from timeframe.timeframe import TimeFrame
from dateutil import parser
from datetime import datetime
import pandas as pd

try:
    import Queue as queue
except ImportError:
    import queue


class OandaDataHandlerBarsProvider(object):

    def __init__(self, stream: OandaPriceStream, symbols: list, time_frame: TimeFrame):
        self.stream = stream
        self.symbols = symbols
        self.time_frame = time_frame

        self.queues = dict((symbol, queue.Queue()) for (symbol) in symbols)

        self.opened_bars = dict((symbol, pd.DataFrame()) for (symbol) in symbols)
        self.opened_bars_finishes_at = dict((symbol, None) for (symbol) in symbols)
        self.opened_bars_starts_at = dict((symbol, None) for (symbol) in symbols)

    def get_queue(self, symbol: str) -> queue.Queue:
        return self.queues[symbol]

    def start_providing_bars(self):
        if not self.stream.is_connected():
            self.stream.connect_to_stream()

        if self.stream.response.status_code != 200:
            for symbol in self.queues:
                self.queues[symbol].put_nowait({
                    'action': 'exit',
                    'message': 'Stream not connected'
                })

            return

        for price in self.stream.get_price():
            symbol = price['instrument']

            price_datetime = self.get_price_datetime(price['datetime'])

            bar_borders = self.time_frame.get_time_frame_border(price_datetime)

            if self.opened_bars_finishes_at[symbol] is None:
                self.opened_bars_finishes_at[symbol] = bar_borders[1]
                self.opened_bars_starts_at[symbol] = bar_borders[0]

            if self.opened_bars_finishes_at[symbol] >= price_datetime or 'datetime' not in self.opened_bars[symbol]:
                new_price_data = pd.DataFrame(price, index=[price['datetime']])
                self.opened_bars[symbol] = self.opened_bars[symbol].append(new_price_data)
            else:
                price_bid_open = float(self.opened_bars[symbol]['bid'][0])
                price_bid_close = float(self.opened_bars[symbol]['bid'][-1])
                price_bid_high = float(self.opened_bars[symbol]['bid'].max())
                price_bid_low = float(self.opened_bars[symbol]['bid'].min())

                price_ask_open = float(self.opened_bars[symbol]['ask'][0])
                price_ask_close = float(self.opened_bars[symbol]['ask'][-1])
                price_ask_high = float(self.opened_bars[symbol]['ask'].max())
                price_ask_low = float(self.opened_bars[symbol]['ask'].min())

                data = self.create_bar_data(self.opened_bars_starts_at[symbol], price_ask_close, price_ask_high, price_ask_low,
                                            price_ask_open, price_bid_close, price_bid_high, price_bid_low,
                                            price_bid_open)

                self.opened_bars_finishes_at[symbol] = None
                self.opened_bars_starts_at[symbol] = None

                self.queues[symbol].put_nowait(data)

    @staticmethod
    def create_bar_data(opened_bar_starts_at, price_ask_close, price_ask_high, price_ask_low, price_ask_open,
                        price_bid_close, price_bid_high, price_bid_low, price_bid_open) -> dict:
        return {
            'datetime': opened_bar_starts_at,
            'open_bid': float(price_bid_open),
            'open_ask': float(price_ask_open),
            'high_bid': float(price_bid_high),
            'high_ask': float(price_ask_high),
            'low_bid': float(price_bid_low),
            'low_ask': float(price_ask_low),
            'close_bid': float(price_bid_close),
            'close_ask': float(price_ask_close),
            'volume': 0
        }

    @staticmethod
    def get_price_datetime(datetime_as_string: str) -> datetime:
        price_datetime = parser.parse(datetime_as_string)
        price_datetime = price_datetime.replace(tzinfo=None)
        price_datetime = price_datetime.replace(microsecond=0)

        return price_datetime
