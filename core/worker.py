from abc import ABCMeta, abstractmethod
import asyncio
import sys
from core.portfolio import Portfolio
from loggers.logger import Logger
from concurrent.futures import ThreadPoolExecutor


class Worker(object):

    __metaclass__ = ABCMeta

    LOG_TYPE_EVENTS = 'events'

    @abstractmethod
    def get_signals(self) -> int:
        raise NotImplementedError("Should implement get_signals()")

    @abstractmethod
    def get_fills(self) -> int:
        raise NotImplementedError("Should implement get_fills()")

    @abstractmethod
    def get_orders(self) -> int:
        raise NotImplementedError("Should implement get_orders()")

    @abstractmethod
    def get_portfolio(self) -> Portfolio:
        raise NotImplementedError("Should implement get_portfolio()")

    @abstractmethod
    def get_logger(self) -> Logger:
        raise NotImplementedError("Should implement get_logger()")

    @abstractmethod
    def get_enabled_log_types(self) -> list:
        raise NotImplementedError("Should implement get_enabled_log_types()")

    @abstractmethod
    def write_progress(self, iteration: int):
        raise NotImplementedError("Should implement write_progress()")

    @abstractmethod
    def get_symbol_list(self) -> list:
        raise NotImplementedError("Should implement get_symbol_list()")

    @abstractmethod
    def _run_symbol(self, symbol: str):
        raise NotImplementedError("Should implement _run_symbol()")

    async def _run(self):
        if self.get_logger() is not None:
            self.get_logger().open()

        loop = asyncio.get_event_loop()

        futures = []

        symbol_list = self.get_symbol_list()

        executor = ThreadPoolExecutor(max_workers=len(symbol_list))

        for symbol in symbol_list:
            futures.append(loop.run_in_executor(executor, self._run_symbol, symbol))

        done, futures = await asyncio.wait(futures, loop=loop, return_when=asyncio.ALL_COMPLETED)
        for f in done:
            await f

        print('')
        sys.stdout.flush()

        if self.get_logger() is not None:
            self.get_logger().close()

    def log_message(self, iteration, message):
        if self.get_logger() is not None and message != '':
            self.get_logger().write('#%d - %s' % (iteration, message))

    def log_event(self, iteration, event):
        if self.get_logger() is not None and self.LOG_TYPE_EVENTS in self.get_enabled_log_types():
            if event is not None:
                log = event.get_as_string()
            else:
                log = 'Event: None'

            self.log_message(iteration, log)

    def _save_equity_and_generate_stats(self):
        print('Starting to generate equity')
        sys.stdout.flush()

        self.get_portfolio().create_equity_curve_dataframe()
        self.stats = self.get_portfolio().output_summary_stats()

    def print_performance(self):
        self.stats.print_stats()

        print("Signals: %s" % self.get_signals())
        print("Orders: %s" % self.get_orders())
        print("Fills: %s" % self.get_fills())

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self._run())

        self._save_equity_and_generate_stats()
