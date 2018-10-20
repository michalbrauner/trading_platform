from __future__ import print_function
import sys
from datahandlers.data_handler_factory import DataHandlerFactory
from core.portfolio import Portfolio
from core.configuration import Configuration
from strategies.strategy import Strategy
from positionsizehandlers.position_size import PositionSizeHandler
from loggers.logger import Logger
from executionhandlers.execution_handler_factory import ExecutionHandlerFactory
import time
import datetime
from core.worker import Worker

try:
    import Queue as queue
except ImportError:
    import queue


class Backtest(Worker):
    def __init__(
            self, output_directory: str, symbol_list: list, initial_capital: int, heartbeat: int, start_date: datetime,
            configuration: Configuration, data_handler_factory: DataHandlerFactory,
            execution_handler_factory: ExecutionHandlerFactory, portfolio_class: Portfolio.__name__,
            strategy_class: Strategy.__name__, position_size_handler: PositionSizeHandler.__name__, logger: Logger,
            enabled_logs: list, strategy_params_dict: dict, equity_filename: str, trades_filename: str
    ) -> None:
        self.output_directory = output_directory
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date
        self.configuration = configuration
        self.data_handler_factory = data_handler_factory
        self.execution_handler_factory = execution_handler_factory
        self.portfolio_class = portfolio_class
        self.strategy_class = strategy_class
        self.position_size_handler = position_size_handler
        self.logger = logger
        self.enabled_log_types = enabled_logs
        self.strategy_params_dict = strategy_params_dict
        self.equity_filename = equity_filename
        self.trades_filename = trades_filename

        self.events = queue.Queue()
        self.events_per_symbol = dict(((symbol, queue.Queue()) for (symbol) in self.symbol_list))

        self.signals = 0
        self.orders = 0
        self.fills = 0

        self.stats = None

        self._generate_trading_instances()

    def _generate_trading_instances(self):

        self.data_handler = self.data_handler_factory.create_from_settings(self.configuration, self.events_per_symbol,
                                                                           self.symbol_list, self.logger)

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
            if self.data_handler.backtest_should_continue(symbol):
                self.data_handler.update_bars(symbol)
            else:
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

    def write_progress(self, iteration: int):
        progress = int(round(self.data_handler.get_position_in_percentage(), 0))
        print('Running backtest ({}%)'.format(progress), end='\r')
        sys.stdout.flush()

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
