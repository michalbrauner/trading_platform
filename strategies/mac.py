from __future__ import print_function

import datetime

import numpy as np

from events.signal_event import SignalEvent
from strategy import Strategy


class MovingAverageCrossStrategy(Strategy):
    """
    Carries out a basic Moving Average Crossover strategy with a
    short/long simple weighted moving average. Default short/long
    windows are 100/400 periods respectively.
    """
    def __init__(
            self, bars, events, short_window=25, long_window=50
    ):
        """
        Initialises the Moving Average Cross Strategy.
        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        short_window - The short moving average lookback.
        long_window - The long moving average lookback.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.short_window = short_window
        self.long_window = long_window

        # Set to True if a symbol is in the market
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to 'OUT'.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'

        return bought

    def calculate_signals(self, event):
        """
        Generates a new set of signals based on the MAC
        SMA with the short window crossing the long window
        meaning a long entry and vice versa for a short entry.
        Parameters
        event - A MarketEvent object.
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars_values(
                    s, 'close_bid', N=self.long_window
                )
                bar_date = self.bars.get_latest_bar_datetime(s)

                if bars is not None and bars != []:
                    short_sma = np.mean(bars[-self.short_window:])
                    long_sma = np.mean(bars[-self.long_window:])

                    symbol = s
                    dt = datetime.datetime.utcnow()
                    sig_dir = ''

                    if short_sma > long_sma and self.bought[s] == 'OUT':
                        print('LONG: %s' % bar_date)
                        sig_dir = 'LONG'

                        signal = SignalEvent(1, symbol, bar_date, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'LONG'

                    elif short_sma < long_sma and self.bought[s] == "LONG":
                        print("SHORT: %s" % bar_date)
                        sig_dir = 'EXIT'

                        signal = SignalEvent(1, symbol, bar_date, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'OUT'
