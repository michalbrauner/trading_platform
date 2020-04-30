from datetime import datetime


class PriceStreamPriceItem(object):
    def __init__(self, symbol: str, price_datetime: datetime, price_ask: float, price_bid: float):
        self._symbol = symbol
        self._price_datetime = price_datetime
        self._price_ask = price_ask
        self._price_bid = price_bid

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def price_datetime(self) -> datetime:
        return self._price_datetime

    @property
    def price_ask(self) -> float:
        return self._price_ask

    @property
    def price_bid(self) -> float:
        return self._price_bid
