from abc import ABCMeta, abstractmethod
from typing import Optional


class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of bars (OLHCVI) for each symbol requested.

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_symbol_list(self) -> list:
        raise NotImplementedError("Should implement get_symbol_list()")

    @abstractmethod
    def backtest_should_continue(self, symbol: str) -> bool:
        raise NotImplementedError("Should implement backtest_should_continue()")

    @abstractmethod
    def has_some_bars(self, symbol: str) -> bool:
        raise NotImplementedError("Should implement has_some_bars()")

    @abstractmethod
    def get_latest_bar(self, symbol):
        """
        Returns the last bar updated.
        """
        raise NotImplementedError("Should implement get_latest_bar()")

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or fewer if less bars are available.
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_datetime()")

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        from the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_value()")

    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        raise NotImplementedError("Should implement get_latest_bars_values()")

    @abstractmethod
    def update_bars(self, symbol: str):
        """
        Pushes the latest bars to the bars_queue for each symbol
        in a tuple OHLCVI format: (datetime, open, high, low,
        close, volume, open interest).
        """
        raise NotImplementedError("Should implement update_bars()")

    @abstractmethod
    def get_position_in_percentage(self):
        raise NotImplementedError("Should implement get_position_in_percentage()")

    @abstractmethod
    def get_error_message(self) -> Optional[str]:
        raise NotImplementedError("Should implement get_error_message()")

    @abstractmethod
    def get_number_of_bars(self, symbol):
        raise NotImplementedError("Should implement get_number_of_bars()")
