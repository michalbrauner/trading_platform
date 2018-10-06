import numpy as np
from concurrent.futures import ThreadPoolExecutor
from events.market_event import MarketEvent
from oanda.stream import Stream as OandaPriceStream
from timeframe.timeframe import TimeFrame
from dateutil import parser
from oanda.instrument_api_client import InstrumentApiClient
from datahandlers.bars_provider.oanda_bars_provider_stream import OandaBarsProviderStream
from datahandlers.bars_provider.oanda_bars_provider_api import OandaBarsProviderApi
import asyncio
from typing import Dict
from typing import List
from typing import Optional

try:
    import Queue as queue
except ImportError:
    import queue

from datahandlers.data_handler import DataHandler
from datahandlers.bars_provider.bars_provider import BarsProvider


class OandaDataHandler(DataHandler):

    def __init__(self, events_per_symbol: Dict[str, queue.Queue], symbol_list: list, bars_provider: BarsProvider,
                 instrument_api_client: InstrumentApiClient, time_frame: str,
                 number_of_bars_preload_from_history: int) -> None:

        self.events_per_symbol = events_per_symbol

        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.symbol_position_info = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.error_message = None
        self.time_frame = time_frame
        self.number_of_bars_preload_from_history = number_of_bars_preload_from_history
        self.bars_provider = bars_provider

        self.instrument_api_client = instrument_api_client

        self.providing_bars_loop = None

        if number_of_bars_preload_from_history > 0:
            for symbol in self.symbol_list:
                self.preload_bars_from_history(symbol, self.number_of_bars_preload_from_history)

    def start_providing_bars(self) -> None:
        self.providing_bars_loop = asyncio.new_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)

        self.providing_bars_loop.run_in_executor(executor, self.bars_provider.start_providing_bars)

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

        if self.providing_bars_loop is None:
            self.start_providing_bars()

        symbol_data_queue = self.bars_provider.get_queue(symbol)

        while True:
            symbol_data = symbol_data_queue.get(True)

            if 'action' in symbol_data:
                if symbol_data['action'] == 'exit':
                    raise StopIteration(symbol_data['message'])
            else:
                yield symbol_data


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

    def has_some_bars(self, symbol: str) -> bool:
        return symbol in self.latest_symbol_data and len(self.latest_symbol_data[symbol]) > 0

    def get_latest_bar(self, symbol: str):
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

    def update_bars(self, symbol: str):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for symbol
        """
        try:
            bar = next(self._get_new_bar(symbol))
        except StopIteration as e:
            self.continue_backtest = False
            self.error_message = e.value
        else:
            if bar is not None:
                self.append_new_price_data(symbol, bar)
                self.events_per_symbol[symbol].put(MarketEvent(symbol))

    def get_error_message(self) -> Optional[str]:
        return self.error_message

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
