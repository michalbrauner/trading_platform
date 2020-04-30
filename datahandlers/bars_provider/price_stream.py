from abc import ABCMeta, abstractmethod
from typing import List

from datahandlers.bars_provider.price_stream_price_item import PriceStreamPriceItem


class PriceStream(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_instruments(self) -> List[str]:
        raise NotImplementedError("Should implement get_instruments()")

    @abstractmethod
    def connect_to_stream(self) -> None:
        raise NotImplementedError("Should implement connect_to_stream()")

    @abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError("Should implement is_connected()")

    @abstractmethod
    def get_price(self) -> PriceStreamPriceItem:
        raise NotImplementedError("Should implement get_price()")
