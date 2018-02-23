import os

import numpy as np
import pandas as pd
from events.market_event import MarketEvent
from oanda.stream import Stream as OandaPriceStream
from timeframe.timeframe import TimeFrame
from dateutil import parser

try:
    import Queue as queue
except ImportError:
    import queue

from datahandlers.data_handler import DataHandler


class OandaDataHandler(DataHandler):

    def __init__(self, events,  symbol_list, stream, timeframe):
        # type: (queue.Queue, [], OandaPriceStream) -> None

        self.events = events
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.symbol_position_info = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.timeframe = timeframe

        self.stream = stream
        self.stream.connect_to_stream()

    def get_symbol_list(self):
        # type: () -> []
        return self.symbol_list

    def backtest_should_continue(self):
        return self.continue_backtest

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed as a tuple of
        (sybmbol, datetime, open, low, high, close, volume).
        """

        openedBar = pd.DataFrame()
        opened_bar_finishes_at = None
        opened_bar_starts_at = None

        timeframe = TimeFrame(self.timeframe)

        for price in self.stream.get_price():
            if price['instrument'] == symbol:
                newPriceData = pd.DataFrame(price, index=[price['datetime']])

                price_datetime = parser.parse(price['datetime'])
                price_datetime = price_datetime.replace(tzinfo=None)
                price_datetime = price_datetime.replace(microsecond=0)

                bar_borders = timeframe.get_timeframe_border(price_datetime)

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

                    data = {
                        'datetime': opened_bar_starts_at,
                        'open_bid': price_bid_open,
                        'open_ask': price_ask_open,
                        'high_bid': price_bid_high,
                        'high_ask': price_ask_high,
                        'low_bid': price_bid_low,
                        'low_ask': price_ask_low,
                        'close_bid': price_bid_close,
                        'close_ask': price_ask_close,
                        'volume': 0
                    }

                    if symbol not in self.symbol_data:
                        self.symbol_data[symbol] = [data]
                        self.symbol_position_info[symbol] = dict(
                            number_of_items=1,
                            position=1
                        )

                        yield data
                    else:
                        self.symbol_data[symbol].append(data)

                        self.symbol_position_info[symbol]['number_of_items'] = \
                            self.symbol_position_info[symbol]['number_of_items'] + 1

                        self.symbol_position_info[symbol]['position'] = \
                            self.symbol_position_info[symbol]['position'] + 1

                        yield data

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
                    if s not in self.latest_symbol_data:
                        self.latest_symbol_data[s] = []

                    self.latest_symbol_data[s].append(bar)

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
