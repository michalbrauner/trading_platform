from __future__ import print_function

import argparser_tools.basic
from strategies.strategy import Strategy
from datahandlers.data_handler import DataHandler
from core.portfolio import Portfolio
from events.event import Event
import argparse
from typing import Dict
import queue


class NoTradingStrategy(Strategy):
    def __init__(self, bars: DataHandler, portfolio: Portfolio, events_per_symbol: Dict[str, queue.Queue]):
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
        return

    @staticmethod
    def get_strategy_params(args_namespace) -> dict:
        return dict()

    @staticmethod
    def create_argument_parser(simulation_only: bool) -> argparse.ArgumentParser:
        parser = argparser_tools.basic.create_basic_argument_parser(simulation_only)

        if simulation_only:
            parser = argparser_tools.basic.with_backtest_arguments(parser)

        return parser
