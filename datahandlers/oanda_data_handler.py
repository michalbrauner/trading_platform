import numpy as np
import pandas as pd
from events.market_event import MarketEvent
from oanda.stream import Stream as OandaPriceStream
from timeframe.timeframe import TimeFrame
from dateutil import parser
from oanda.instrument_api_client import InstrumentApiClient

try:
    import Queue as queue
except ImportError:
    import queue

from datahandlers.data_handler import DataHandler


class OandaDataHandler(DataHandler):

    def __init__(self, events: queue.Queue, symbol_list: list, stream: OandaPriceStream,
                 instrument_api_client: InstrumentApiClient, time_frame: str,
                 number_of_bars_preload_from_history: int) -> None:

        self.events = events
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.symbol_position_info = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.time_frame = time_frame
        self.number_of_bars_preload_from_history = number_of_bars_preload_from_history

        self.instrument_api_client = instrument_api_client

        if number_of_bars_preload_from_history > 0:
            for symbol in self.symbol_list:
                self.preload_bars_from_history(symbol, self.number_of_bars_preload_from_history)

        self.stream = stream
        self.stream.connect_to_stream()

    def get_symbol_list(self) -> list:
        return self.symbol_list

    def backtest_should_continue(self):
        return self.continue_backtest

    def preload_bars_from_history(self, symbol, number_of_bars):
        candles_data = self.instrument_api_client.get_candles(symbol, self.time_frame, number_of_bars)

        for price_data in candles_data['candles']:
            price_ask_data = price_data['ask']
            price_bid_data = price_data['bid']

            bar_data = self.create_bar_data(self.get_price_datetime(price_data['time']), price_ask_data['c'],
                                            price_ask_data['h'], price_ask_data['l'], price_ask_data['o'],
                                            price_bid_data['c'], price_bid_data['h'], price_bid_data['l'],
                                            price_bid_data['o'])

            self.append_new_price_data(symbol, bar_data)

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed as a tuple of
        (sybmbol, datetime, open, low, high, close, volume).
        """

        openedBar = pd.DataFrame()
        opened_bar_finishes_at = None
        opened_bar_starts_at = None

        timeframe = TimeFrame(self.time_frame)

        for price in self.stream.get_price():
            if price['instrument'] == symbol:
                newPriceData = pd.DataFrame(price, index=[price['datetime']])

                price_datetime = self.get_price_datetime(price['datetime'])

                bar_borders = timeframe.get_time_frame_border(price_datetime)

                if opened_bar_finishes_at is None:
                    opened_bar_finishes_at = bar_borders[1]
                    opened_bar_starts_at = bar_borders[0]

                if opened_bar_finishes_at >= price_datetime or 'datetime' not in openedBar:
                    openedBar = openedBar.append(newPriceData)
                else:
                    price_bid_open = float(openedBar['bid'][0])
                    price_bid_close = float(openedBar['bid'][-1])
                    price_bid_high = float(openedBar['bid'].max())
                    price_bid_low = float(openedBar['bid'].min())

                    price_ask_open = float(openedBar['ask'][0])
                    price_ask_close = float(openedBar['ask'][-1])
                    price_ask_high = float(openedBar['ask'].max())
                    price_ask_low = float(openedBar['ask'].min())

                    data = self.create_bar_data(opened_bar_starts_at, price_ask_close, price_ask_high, price_ask_low,
                                                price_ask_open, price_bid_close, price_bid_high, price_bid_low,
                                                price_bid_open)

                    yield data

    @staticmethod
    def get_price_datetime(datetime_as_string):
        price_datetime = parser.parse(datetime_as_string)
        price_datetime = price_datetime.replace(tzinfo=None)
        price_datetime = price_datetime.replace(microsecond=0)

        return price_datetime

    @staticmethod
    def create_bar_data(opened_bar_starts_at, price_ask_close, price_ask_high, price_ask_low, price_ask_open,
                        price_bid_close, price_bid_high, price_bid_low, price_bid_open):
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

    def append_new_price_data(self, symbol, data):
        if symbol not in self.symbol_data:
            self.symbol_data[symbol] = [data]
            self.symbol_position_info[symbol] = dict(
                number_of_items=1,
                position=1
            )
        else:
            self.symbol_data[symbol].append(data)

            self.symbol_position_info[symbol]['number_of_items'] = \
                self.symbol_position_info[symbol]['number_of_items'] + 1

            self.symbol_position_info[symbol]['position'] = \
                self.symbol_position_info[symbol]['position'] + 1

        if symbol not in self.latest_symbol_data:
            self.latest_symbol_data[symbol] = []

        self.latest_symbol_data[symbol].append(data)

    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1]['datetime']

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1][val_type]

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return np.array([b[val_type] for b in bars_list])

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.append_new_price_data(s, bar)

        self.events.put(MarketEvent())

    def get_position_in_percentage(self):
        return 0

    def get_number_of_bars(self, symbol):
        """

        :type symbol: str
        """
        if symbol in self.symbol_data:
            return len(self.symbol_data[symbol])
        else:
            return 0
