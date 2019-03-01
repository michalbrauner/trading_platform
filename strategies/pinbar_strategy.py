from __future__ import print_function

import datetime
import argparser_tools.basic
from events.signal_event import SignalEvent
from strategies.patterns.trade_type import TradeType
from strategies.strategy import Strategy
from datahandlers.data_handler import DataHandler
from core.portfolio import Portfolio
from events.event import Event
import argparse
from typing import Dict
from strategies.patterns.pinbar_pattern import PinBarPattern

import queue


class PinBarStrategy(Strategy):
    def __init__(self, bars: DataHandler, portfolio: Portfolio, events_per_symbol: Dict[str, queue.Queue],
                 stop_loss_pips=None, take_profit_pips=None):
        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips
        self.bars = bars
        self.portfolio = portfolio
        self.events_per_symbol = events_per_symbol

        # Set to True if a symbol is in the market
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self) -> dict:
        bought = {}
        for s in self.bars.get_symbol_list():
            bought[s] = 'OUT'

        return bought

    def calculate_signals(self, event: Event):
        if event.type == 'MARKET':
            symbol = event.symbol

            if not self.bars.has_some_bars(symbol):
                return

            bar_date = self.bars.get_latest_bar_datetime(symbol)
            bar_price = self.bars.get_latest_bar_value(symbol, 'close_bid')
            dt = datetime.datetime.utcnow()

            price_close = self.bars.get_latest_bar_value(symbol, 'close_bid')
            price_open = self.bars.get_latest_bar_value(symbol, 'open_bid')
            price_high = self.bars.get_latest_bar_value(symbol, 'high_bid')
            price_low = self.bars.get_latest_bar_value(symbol, 'low_bid')

            pinbar_pattern = PinBarPattern(price_open, price_close, price_high, price_low)
            pinbar_pattern_result = pinbar_pattern.resolve()

            if pinbar_pattern_result.is_valid:
                current_position = self.portfolio.get_current_position(symbol)

                if pinbar_pattern_result.trade_type == TradeType.LONG and current_position is None:
                    sig_dir = 'LONG'

                    stop_loss = self.calculate_stop_loss_price(bar_price, self.stop_loss_pips, sig_dir)
                    take_profit = self.calculate_take_profit_price(bar_price, self.take_profit_pips, sig_dir)

                    signal = SignalEvent(1, symbol, bar_date, dt, sig_dir, 1.0, stop_loss, take_profit)
                    self.events_per_symbol[symbol].put(signal)
                    self.bought[symbol] = sig_dir

                    return True

                elif pinbar_pattern_result.trade_type == TradeType.SHORT and current_position is None:
                    sig_dir = 'SHORT'

                    stop_loss = self.calculate_stop_loss_price(bar_price, self.stop_loss_pips, sig_dir)
                    take_profit = self.calculate_take_profit_price(bar_price, self.take_profit_pips, sig_dir)

                    signal = SignalEvent(1, symbol, bar_date, dt, sig_dir, 1.0, stop_loss, take_profit)
                    self.events_per_symbol[symbol].put(signal)
                    self.bought[symbol] = sig_dir

                    return True

                return False

    @staticmethod
    def get_strategy_params(args_namespace) -> dict:
        return dict()

    @staticmethod
    def create_argument_parser(simulation_only: bool) -> argparse.ArgumentParser:
        parser = argparser_tools.basic.create_basic_argument_parser(simulation_only)

        if simulation_only:
            parser = argparser_tools.basic.with_backtest_arguments(parser)

        return parser
