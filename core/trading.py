from __future__ import print_function
import datetime
from datahandlers.data_handler_factory import DataHandlerFactory
from core.configuration import Configuration
from positionsizehandlers.position_size import PositionSizeHandler
from loggers.logger import Logger
from executionhandlers.execution_handler_factory import ExecutionHandlerFactory
from oanda.symbol_name_converter import SymbolNameConverter
from typing import Type
from core.portfolio import Portfolio
from strategies.strategy import Strategy
import os
from core.worker import Worker

try:
    import Queue as queue
except ImportError:
    import queue

import time


class Trading(Worker):
    def __init__(self, output_directory: str, symbol_list: list, heartbeat: int, configuration: Configuration,
                 data_handler_factory: DataHandlerFactory, execution_handler_factory: ExecutionHandlerFactory,
                 portfolio_class: Type[Portfolio], strategy_class: Type[Strategy], position_size_handler: PositionSizeHandler,
                 logger: Logger, enabled_log_types: list, strategy_params_dict: dict, equity_filename: str,
                 trades_filename: str):

        self.output_directory = output_directory
        self.symbol_list = SymbolNameConverter().convert_symbol_names_to_oanda_symbol_names(symbol_list)
        self.heartbeat = heartbeat
        self.configuration = configuration
        self.data_handler_factory = data_handler_factory
        self.execution_handler_factory = execution_handler_factory
        self.portfolio_class = portfolio_class
        self.strategy_class = strategy_class
        self.position_size_handler = position_size_handler
        self.logger = logger
        self.enabled_log_types = enabled_log_types
        self.strategy_params_dict = strategy_params_dict
        self.equity_filename = equity_filename
        self.trades_filename = trades_filename

        self.start_date = datetime.datetime.now()
        self.initial_capital = 0

        self.events_per_symbol = dict(((symbol, queue.Queue()) for (symbol) in self.symbol_list))

        self.signals = 0
        self.orders = 0
        self.fills = 0

        self.stats = None

        summary_file = os.path.join(self.output_directory, 'output_summary.txt')
        self.output_summary_file = open(summary_file, 'w')

        self._generate_trading_instances()

    def _generate_trading_instances(self):

        self.data_handler = self.data_handler_factory.create_from_settings(self.configuration, self.events_per_symbol,
                                                                           self.symbol_list)

        self.portfolio = self.portfolio_class(self.data_handler, self.events_per_symbol, self.start_date,
                                              self.initial_capital, self.output_directory, self.equity_filename,
                                              self.trades_filename, self.position_size_handler)

        self.strategy = self.strategy_class(self.data_handler, self.portfolio, self.events_per_symbol,
                                            **self.strategy_params_dict)

        self.execution_handler = self.execution_handler_factory.create_from_settings(self.configuration,
                                                                                     self.data_handler,
                                                                                     self.events_per_symbol,
                                                                                     self.logger)

    def _run_symbol(self, symbol: str):
        self.write_progress(0)

        i = 0
        while True:
            i += 1
            self.write_progress(i)

            # Update the market bars
            if self.data_handler.backtest_should_continue():
                self.data_handler.update_bars(symbol)
            else:
                error_message = self.data_handler.get_error_message()

                if self.get_logger() is not None and error_message is not None:
                    self.get_logger().write(error_message)

                break

            # Handle the events
            while True:
                try:
                    event = self.events_per_symbol[symbol].get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'CLOSE_PENDING_ORDERS':
                            self.execution_handler.clear_limit_or_stop_orders(event)
                        elif event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            self.execution_handler.update_stop_and_limit_orders(event)
                            self.portfolio.update_timeindex()
                        elif event.type == 'SIGNAL':
                            self.signals += 1
                            self.portfolio.update_signal(event)
                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.execution_handler.execute_order(event)
                        elif event.type == 'FILL':
                            self.fills += 1
                            self.portfolio.update_fill(event)

                    self.log_event(i, event)

            time.sleep(self.heartbeat)

        self.log_message(i, 'Stopping processing pair {}'.format(symbol))

    def write_progress(self, iteration: int):
        number_of_bars_for_symbols = []

        for symbol in self.symbol_list:
            number_of_bars = self.data_handler.get_number_of_bars(symbol)
            last_bar = self.data_handler.get_latest_bar(symbol) if number_of_bars > 0 else None

            number_of_bars_for_symbols.append(
                '  --> {}: {} bars, last datetime open: {}\n'.format(symbol, number_of_bars, last_bar[
                    'datetime'] if last_bar is not None else ''))

        number_of_dots = iteration % 10
        dots = ['.'] * number_of_dots

        self.output_summary_file.seek(0)
        self.output_summary_file.truncate()

        self.output_summary_file.seek(0)
        self.output_summary_file.write('Trading{}\n'.format(str.join('', dots)), )
        self.output_summary_file.write('{}'.format(str.join('', number_of_bars_for_symbols)))

        self.output_summary_file.flush()

    def get_signals(self) -> int:
        return self.signals

    def get_fills(self) -> int:
        return self.fills

    def get_orders(self) -> int:
        return self.orders

    def get_portfolio(self) -> Portfolio:
        return self.portfolio

    def get_logger(self) -> Logger:
        return self.logger

    def get_enabled_log_types(self) -> list:
        return self.enabled_log_types

    def get_symbol_list(self) -> list:
        return self.symbol_list

