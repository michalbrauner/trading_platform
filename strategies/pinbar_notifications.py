from __future__ import print_function

import argparser_tools.basic
from strategies.strategy import Strategy
from datahandlers.data_handler import DataHandler
from core.portfolio import Portfolio
from events.event import Event
import argparse
import urllib.request
import json
from typing import Dict
from datetime import datetime

try:
    import Queue as queue
except ImportError:
    import queue


class PinBarNotificationsStrategy(Strategy):
    def __init__(self, bars: DataHandler, portfolio: Portfolio, events_per_symbol: Dict[str, queue.Queue],
                 send_notifications: bool):
        self.bars = bars
        self.portfolio = portfolio
        self.events_per_symbol = events_per_symbol
        self.send_notifications = send_notifications

        # Set to True if a symbol is in the market
        self.bought = self._calculate_initial_bought()

        self.webhook_to_call = 'https://hooks.zapier.com/hooks/catch/3483057/w8sbxq/'

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
            price_close = self.bars.get_latest_bar_value(symbol, 'close_bid')
            price_open = self.bars.get_latest_bar_value(symbol, 'open_bid')
            price_high = self.bars.get_latest_bar_value(symbol, 'high_bid')
            price_low = self.bars.get_latest_bar_value(symbol, 'low_bid')

            self.notify_about_pinbar(symbol, price_close, price_open, price_high, price_low, bar_date)

            size_of_bar = abs(price_high - price_low)

            if size_of_bar > 0:
                size_of_body = abs(price_open - price_close)
                body_to_bar_ratio = size_of_body / size_of_bar
                upper_tail_to_bar_ratio = (price_high - max(price_open, price_close)) / size_of_bar
                lower_tail_to_bar_ratio = (min(price_open, price_close) - price_low) / size_of_bar

                bigger_tail = max(lower_tail_to_bar_ratio, upper_tail_to_bar_ratio)
                smaller_tail = min(lower_tail_to_bar_ratio, upper_tail_to_bar_ratio)

                if body_to_bar_ratio <= .2:
                    if bigger_tail >= .7 and smaller_tail <= .2:
                        if self.send_notifications:
                            self.notify_about_pinbar(symbol, price_close, price_open, price_high, price_low, bar_date)

    def notify_about_pinbar(self, symbol: str, price_close: float, price_open: float, price_high: float,
                            price_low: float, bar_date: datetime) -> None:
        opener = urllib.request.build_opener()
        opener.addheaders = [('Content-Type', 'application/json')]

        data = json.dumps([
            {
                'symbol': symbol,
                'price_close': price_close,
                'price_open': price_open,
                'price_high': price_high,
                'price_low': price_low,
                'bar_date': bar_date.strftime("%Y-%m-%d %H:%M:%S")
            }
        ])
        data = data.encode('ascii')

        with opener.open(self.webhook_to_call, data) as response:
            response = response.read().decode('utf-8')

    @staticmethod
    def get_strategy_params(args_namespace) -> dict:
        return dict(
            send_notifications=False
        )

    @staticmethod
    def create_argument_parser(simulation_only: bool) -> argparse.ArgumentParser:
        parser = argparser_tools.basic.create_basic_argument_parser(simulation_only)

        if simulation_only:
            parser = argparser_tools.basic.with_backtest_arguments(parser)

        return parser
