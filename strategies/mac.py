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
            self, bars, portfolio, events, short_window=25, long_window=50, stop_loss_pips=100, take_profit_pips=200
    ):
        """
        Initialises the Moving Average Cross Strategy.
        Parameters:
        bars - The DataHandler object that provides bar information
        portfolio
        events - The Event Queue object.
        short_window - The short moving average lookback.
        long_window - The long moving average lookback.
        stop_loss_pips
        take_profit_pips
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.short_window = short_window
        self.long_window = long_window
        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips

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
                if self.portfolio.current_positions[s] == 0:
                    self.bought[s] = 'OUT'

                bars = self.bars.get_latest_bars_values(
                    s, 'close_bid', N=self.long_window
                )
                bar_date = self.bars.get_latest_bar_datetime(s)
                bar_price = self.bars.get_latest_bar_value(s, 'close_bid')

                if bars is not None and bars != []:
                    short_sma = np.mean(bars[-self.short_window:])
                    long_sma = np.mean(bars[-self.long_window:])

                    symbol = s
                    dt = datetime.datetime.utcnow()
                    sig_dir = ''

                    if short_sma > long_sma and self.bought[s] == 'OUT':
                        print('LONG: %s' % bar_date)
                        sig_dir = 'LONG'

                        stop_loss = bar_price - (self.stop_loss_pips * self.get_pip_value())
                        take_profit = bar_price + (self.take_profit_pips * self.get_pip_value())

                        signal = SignalEvent(1, symbol, bar_date, dt, sig_dir, 1.0, stop_loss, take_profit)
                        self.events.put(signal)

                        self.bought[s] = 'LONG'

                    elif short_sma < long_sma and self.bought[s] == "LONG":
                        print("SHORT: %s" % bar_date)
                        sig_dir = 'EXIT'

                        signal = SignalEvent(1, symbol, bar_date, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'OUT'

    def get_pip_value(self):
        return 0.00001
