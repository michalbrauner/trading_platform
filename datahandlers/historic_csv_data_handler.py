import os

import numpy as np
import pandas as pd
import pandas.io.parsers
from events.market_event import MarketEvent
from datahandlers.data_handler import DataHandler
from typing import Dict
from typing import List

try:
    import Queue as queue
except ImportError:
    import queue


class HistoricCSVDataHandler(DataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for
    each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface.
    """

    def __init__(self, events: queue.Queue, events_per_symbol: Dict[str, queue.Queue], csv_dir: str,
                 symbol_list: List[str]) -> None:
        """
        Initialises the historic data handler by requesting
        the location of the CSV files and a list of symbols.

        It will be assumed that all files are of the form
        'symbol.csv', where symbol is a string in the list.
        """
        self.events = events
        self.events_per_symbol = events_per_symbol
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.symbol_position_info = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

        self._open_convert_csv_files()

    def get_symbol_list(self) -> list:
        return self.symbol_list

    def backtest_should_continue(self):
        return self.continue_backtest

    def _open_convert_csv_files(self):
        """
        Opens the CSV files from the data directory, converting
        them into pandas DataFrames within a symbol dictionary.

        For this handler it will be assumed that the data is
        taken from DTN IQFeed. Thus its format will be respected.
        """
        comb_index = None
        for s in self.symbol_list:
            # Load the CSV file with no header information, indexed on date
            self.symbol_data[s] = pd.io.parsers.read_csv(
                os.path.join(self.csv_dir, '%s.csv' % s),
                header=2, index_col=0, parse_dates=True, delimiter=';',
                names=['datetime', 'open_bid', 'open_ask', 'high_bid', 'high_ask', 'low_bid', 'low_ask', 'close_bid',
                       'close_ask', 'volume']
            ).sort_index()

            self.symbol_position_info[s] = dict(
                number_of_items = self.symbol_data[s].shape[0],
                position = 0
            )

            # Combine the index to pad forward values
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []

        # Reindex the dataframes
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed as a tuple of
        (sybmbol, datetime, open, low, high, close, volume).
        """
        for b in self.symbol_data[symbol]:
            self.symbol_position_info[symbol]['position'] = self.symbol_position_info[symbol]['position'] + 1
            yield b

    def has_some_bars(self, symbol: str) -> bool:
        return symbol in self.latest_symbol_data and len(self.latest_symbol_data[symbol]) > 0

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
            return bars_list[-1][0]

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
            return getattr(bars_list[-1][1], val_type)

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
            return np.array([getattr(b[1], val_type) for b in bars_list])

    def update_bars(self, symbol: str):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for symbol
        """
        try:
            bar = next(self._get_new_bar(symbol))
        except StopIteration:
            self.continue_backtest = False
        else:
            if bar is not None:
                self.latest_symbol_data[symbol].append(bar)
                self.events.put(MarketEvent(symbol))
                self.events_per_symbol[symbol].put(MarketEvent(symbol))

    def get_position_in_percentage(self):
        positions_in_percentage = list()

        for s in self.symbol_list:
            positions_in_percentage.append(self.get_position_in_percentage_for_symbol(s))

        return np.round(np.mean(positions_in_percentage), 2)

    def get_position_in_percentage_for_symbol(self, symbol):
        position = float(self.symbol_position_info[symbol]['position'])
        number_of_items = float(self.symbol_position_info[symbol]['number_of_items'])

        return np.round(100 * (position / number_of_items), 2)

    def get_number_of_bars(self, symbol):
        """

        :type symbol: str
        """
        return self.symbol_position_info[symbol]['position']
