from __future__ import print_function

import datetime
import numpy as np
import os
import args_parser

from strategies.configuration_tools import ConfigurationTools

from events.signal_event import SignalEvent
from strategy import Strategy


class DebugTradingStrategy(Strategy):
    def __init__(self, bars, portfolio, events, signal_file, stop_loss_pips=None, take_profit_pips=None):
        """
        Initialises the Moving Average Cross Strategy.
        Parameters:
        bars - The DataHandler object that provides bar information
        portfolio
        events - The Event Queue object.
        stop_loss_pips
        take_profit_pips
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips
        self.signal_file = signal_file

        # Set to True if a symbol is in the market
        self.bought = self._calculate_initial_bought()

        self.signal_file_opened = open(self.signal_file, 'r')

        self.force_new_signal_type = None

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
        if event.type == 'MARKET':
            for s in self.symbol_list:
                if self.portfolio.current_positions[s] == 0:
                    self.bought[s] = 'OUT'

                bar_date = self.bars.get_latest_bar_datetime(s)
                bar_price = self.bars.get_latest_bar_value(s, 'close_bid')

                dt = datetime.datetime.utcnow()

                self.signal_file_opened.seek(0, 0)
                signal_from_file = self.signal_file_opened.readline()

                long_signal = signal_from_file == 'long'
                short_signal = signal_from_file == 'short'
                exit_signal = signal_from_file == 'exit'

                signal_generated = self.calculate_exit_signals(short_signal, long_signal, exit_signal, s, bar_date, dt)

                if signal_generated is False:
                    self.calculate_new_signals(short_signal, long_signal, s, bar_date, bar_price, dt)

    def calculate_new_signals(self, short_signal, long_signal, s, bar_date, bar_price, dt):

        current_position = self.portfolio.get_current_position(s)

        if long_signal and current_position is None:
            sig_dir = 'LONG'

            stop_loss = self.calculate_stop_loss_price(bar_price, self.stop_loss_pips, sig_dir)
            take_profit = self.calculate_take_profit_price(bar_price, self.take_profit_pips, sig_dir)

            signal = SignalEvent(1, s, bar_date, dt, sig_dir, 1.0, stop_loss, take_profit)
            self.events.put(signal)
            self.bought[s] = sig_dir

            return True

        elif short_signal and current_position is None:
            sig_dir = 'SHORT'

            stop_loss = self.calculate_stop_loss_price(bar_price, self.stop_loss_pips, sig_dir)
            take_profit = self.calculate_take_profit_price(bar_price, self.take_profit_pips, sig_dir)

            signal = SignalEvent(1, s, bar_date, dt, sig_dir, 1.0, stop_loss, take_profit)
            self.events.put(signal)
            self.bought[s] = sig_dir

            return True

        return False

    def calculate_exit_signals(self, short_signal, long_signal, exit_signal, s, bar_date, dt):

        current_position = self.portfolio.get_current_position(s)

        if current_position is not None and (
                (current_position.is_long() and short_signal) or
                (current_position.is_short() and long_signal) or exit_signal):

            sig_dir = 'EXIT'

            current_position = self.portfolio.get_current_position(s)

            signal = SignalEvent(1, s, bar_date, dt, sig_dir, 1.0, None, None, current_position.get_trade_id())
            self.events.put(signal)
            self.bought[s] = 'OUT'

            return True

        return False


class DebugTradingConfigurationTools(ConfigurationTools):
    def __init__(self, settings):
        self.settings = settings

    @staticmethod
    def get_long_opts():
        return ['signal_file=']

    def get_strategy_params(self):
        return dict(signal_file=self.settings['signal_file'])

    def use_argument_if_valid(self, option, argument_value):
        if option == '--signal_file':
            self.settings['signal_file'] = argument_value

        return self.settings

    def set_default_values(self):
        if 'signal_file' not in self.settings:
            self.settings['signal_file'] = None

        return self.settings

    def valid_arguments_and_convert_if_necessarily(self):
        if self.settings['signal_file'] is not None \
                and os.path.isfile(self.settings['signal_file']) is False:

            raise Exception('signal_file does not exist')

        return self.settings
