from __future__ import print_function

import datetime
import numpy as np
import argparser_tools.basic
from events.signal_event import SignalEvent
from strategies.strategy import Strategy
from typing import Dict
from datahandlers.data_handler import DataHandler
from core.portfolio import Portfolio

try:
    import Queue as queue
except ImportError:
    import queue


class MovingAverageCrossStrategy(Strategy):
    """
    Carries out a basic Moving Average Crossover strategy with a
    short/long simple weighted moving average. Default short/long
    windows are 100/400 periods respectively.
    """

    def __init__(
            self, bars: DataHandler, portfolio: Portfolio, events: queue, events_per_symbol: Dict[str, queue.Queue],
            short_window: int = 3, long_window: int = 45,
            stop_loss_pips=None, take_profit_pips=None
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
        self.symbol_list = self.bars.get_symbol_list()
        self.events = events
        self.events_per_symbol = events_per_symbol
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

                if self.bars.get_number_of_bars(s) >= max(self.long_window, self.short_window):
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

                        if short_sma > long_sma and self.bought[s] == 'OUT':
                            sig_dir = 'LONG'

                            stop_loss = self.calculate_stop_loss_price(bar_price, self.stop_loss_pips, sig_dir)
                            take_profit = self.calculate_take_profit_price(bar_price, self.take_profit_pips, sig_dir)

                            signal = SignalEvent(1, symbol, bar_date, dt, sig_dir, 1.0, stop_loss, take_profit)
                            self.events.put(signal)

                            self.bought[s] = sig_dir

                        elif short_sma < long_sma and self.bought[s] == 'OUT':
                            sig_dir = 'SHORT'

                            stop_loss = self.calculate_stop_loss_price(bar_price, self.stop_loss_pips, sig_dir)
                            take_profit = self.calculate_take_profit_price(bar_price, self.take_profit_pips, sig_dir)

                            signal = SignalEvent(1, symbol, bar_date, dt, sig_dir, 1.0, stop_loss, take_profit)
                            self.events.put(signal)

                            self.bought[s] = sig_dir

                        elif short_sma < long_sma and self.bought[s] == "LONG":
                            sig_dir = 'EXIT'

                            signal = SignalEvent(1, symbol, bar_date, dt, sig_dir, 1.0)
                            self.events.put(signal)
                            self.bought[s] = 'OUT'

                        elif short_sma > long_sma and self.bought[s] == "SHORT":
                            sig_dir = 'EXIT'

                            signal = SignalEvent(1, symbol, bar_date, dt, sig_dir, 1.0)
                            self.events.put(signal)
                            self.bought[s] = 'OUT'

    @staticmethod
    def get_strategy_params(args_namespace):
        return dict(
            short_window=args_namespace.short_window,
            long_window=args_namespace.long_window
        )

    @staticmethod
    def create_argument_parser(backtest_only):
        # (bool) -> argparse.ArgumentParser

        parser = argparser_tools.basic.create_basic_argument_parser(backtest_only)

        if (backtest_only):
            parser = argparser_tools.basic.with_backtest_arguments(parser)

        parser = argparser_tools.basic.with_sl_and_tp(parser)
        parser = argparser_tools.basic.with_sma_short_and_long(parser)

        return parser
