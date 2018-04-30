from __future__ import print_function
import pprint
import sys
from datahandlers.data_handler_factory import DataHandlerFactory
from core.portfolio import Portfolio
from core.configuration import Configuration
from strategies.strategy import Strategy
from positionsizehandlers.position_size import PositionSizeHandler
from loggers.logger import Logger
from executionhandlers.execution_handler import ExecutionHandler
from executionhandlers.execution_handler_factory import ExecutionHandlerFactory

try:
    import Queue as queue
except ImportError:
    import queue

try:
    import Queue as queue
except ImportError:
    import queue

import time
import datetime
from oanda.symbol_name_converter import SymbolNameConverter


class Backtest(object):
    """
    Enscapsulates the settings and components for carrying out
    an event-driven backtest.
    """

    LOG_TYPE_EVENTS = 'events'

    def __init__(
            self, output_directory, symbol_list, initial_capital,
            heartbeat, start_date, configuration, data_handler_factory,
            execution_handler_factory, portfolio, strategy, position_size_handler, logger, enabled_logs,
            strategy_params_dict, equity_filename, trades_filename
    ):
        # type: (str, [], int, int, datetime, Configuration, DataHandlerFactory, ExecutionHandlerFactory, Portfolio.__name__, Strategy.__name__, PositionSizeHandler.__name__, Logger, [], {}, str, str) -> None

        self.output_directory = output_directory
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date
        self.configuration = configuration
        self.data_handler_factory = data_handler_factory
        self.execution_handler_factory = execution_handler_factory
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy
        self.position_size_handler = position_size_handler
        self.logger = logger
        self.enabled_log_types = enabled_logs
        self.strategy_params_dict = strategy_params_dict
        self.equity_filename = equity_filename
        self.trades_filename = trades_filename

        self.events = queue.Queue()
        self.signals = 0
        self.orders = 0
        self.fills = 0

        self.stats = None

        self._generate_trading_instances()

    def _generate_trading_instances(self):

        self.data_handler = self.data_handler_factory.create_from_settings(self.configuration, self.events,
                                                                           self.symbol_list)

        self.portfolio = self.portfolio_cls(self.data_handler, self.events, self.start_date, self.initial_capital,
                                            self.output_directory, self.equity_filename, self.trades_filename,
                                            self.position_size_handler)

        self.strategy = self.strategy_cls(self.data_handler, self.portfolio, self.events, **self.strategy_params_dict)

        self.execution_handler = self.execution_handler_factory.create_from_settings(self.configuration,
                                                                                     self.data_handler,
                                                                                     self.events, self.logger)

    def _run_backtest(self):
        if self.logger is not None:
            self.logger.open()

        self.write_progress()

        i = 0
        while True:
            i += 1
            self.write_progress()

            # Update the market bars
            if self.data_handler.backtest_should_continue():
                self.data_handler.update_bars()
            else:
                break

            # Handle the events
            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'CLOSE_PENDING_ORDERS':
                            self.execution_handler.clear_limit_or_stop_orders(event)
                        elif event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            self.execution_handler.update_stop_and_limit_orders(event)
                            self.portfolio.update_timeindex(event)
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

        print('')
        sys.stdout.flush()

        if self.logger is not None:
            self.logger.close()

    def log_message(self, iteration, message):
        if self.logger is not None and message != '':
            self.logger.write('#%d - %s' % (iteration, message))

    def log_event(self, iteration, event):
        if self.logger is not None and self.LOG_TYPE_EVENTS in self.enabled_log_types:
            if event is not None:
                log = event.get_as_string()
            else:
                log = 'Event: None'

            self.log_message(iteration, log)

    def write_progress(self):
        progress = int(round(self.data_handler.get_position_in_percentage(), 0))
        print('Running backtest ({}%)'.format(progress), end='\r')
        sys.stdout.flush()

    def _save_equity_and_generate_stats(self):
        print('Starting to generate equity')
        sys.stdout.flush()

        self.portfolio.create_equity_curve_dataframe()
        self.stats = self.portfolio.output_summary_stats()

    def print_performance(self):
        self.stats.print_stats()

        print("Signals: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % self.fills)

    def simulate_trading(self):
        """
        Simulates the backtest.
        """
        self._run_backtest()
        self._save_equity_and_generate_stats()
