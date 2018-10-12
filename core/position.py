class Position(object):
    def __init__(self, symbol: str, trade_id: int, quantity: float) -> None:
        self.symbol = symbol
        self.trade_id = trade_id
        self.quantity = quantity

    def get_quantity(self) -> float:
        return self.quantity

    def set_quantity(self, quantity: float) -> None:
        self.quantity = quantity

    def get_trade_id(self) -> int:
        return self.trade_id

    def is_long(self) -> bool:
        return self.quantity > 0

    def is_short(self) -> bool:
        return self.quantity < 0
