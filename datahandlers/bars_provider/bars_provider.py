from abc import ABCMeta, abstractmethod
from typing import Optional
from datetime import datetime
from dateutil import parser

try:
    import Queue as queue
except ImportError:
    import queue


class BarsProvider(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_queue(self, symbol: str) -> queue.Queue:
        raise NotImplementedError("Should implement get_queue()")

    @abstractmethod
    def start_providing_bars(self) -> None:
        raise NotImplementedError("Should implement backtest_should_continue()")

    @staticmethod
    def create_bar_data(opened_bar_starts_at, price_ask_close, price_ask_high, price_ask_low, price_ask_open,
                        price_bid_close, price_bid_high, price_bid_low, price_bid_open) -> dict:
        return {
            'datetime': opened_bar_starts_at,
            'open_bid': float(price_bid_open),
            'open_ask': float(price_ask_open),
            'high_bid': float(price_bid_high),
            'high_ask': float(price_ask_high),
            'low_bid': float(price_bid_low),
            'low_ask': float(price_ask_low),
            'close_bid': float(price_bid_close),
            'close_ask': float(price_ask_close),
            'volume': 0
        }

    @staticmethod
    def get_price_datetime(datetime_as_string: str) -> datetime:
        price_datetime = parser.parse(datetime_as_string)
        price_datetime = price_datetime.replace(microsecond=0)

        return price_datetime
