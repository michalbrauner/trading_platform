import os

import numpy as np
import pandas as pd
import pandas.io.parsers
from events.market_event import MarketEvent
from oanda.stream import Stream as OandaPriceStream


from datahandlers.data_handler import DataHandler


class OandaDataHandler(DataHandler):

    def __init__(self, events,  symbol_list, account_id, access_token):
        """
        Parameters:
        events - The Event Queue.
        symbol_list - A list of symbol strings.
        """
        self.events = events
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.symbol_position_info = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

        self.stream = OandaPriceStream(account_id, access_token, self.symbol_list)
        self.stream.connect_to_stream()

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed as a tuple of
        (sybmbol, datetime, open, low, high, close, volume).
        """

        openedBar = pd.DataFrame()

        for price in self.stream.get_price():
            if price['instrument'] == symbol:
                newPriceData = pd.DataFrame(price, index=[price['datetime']])
                openedBar = openedBar.append(newPriceData)

        for b in self.symbol_data[symbol]:
            self.symbol_position_info[symbol]['position'] = self.symbol_position_info[symbol]['position'] + 1
            yield b

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
                    self.latest_symbol_data[s].append(bar)

        self.events.put(MarketEvent())


    def get_position_in_percentage(self):
        return 100
