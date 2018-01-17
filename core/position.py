class Position(object):
    def __init__(self, symbol, trade_id, quantity):
        """

        :type symbol: str
        :type trade_id: int
        :type quantity: float
        """

        self.symbol = symbol
        self.trade_id = trade_id
        self.quantity = quantity

    def get_quantity(self):
        # type: () -> float
        return self.quantity

    def set_quantity(self, quantity):
        # type: (float) -> None
        self.quantity = quantity

    def get_trade_id(self):
        # type: () -> int
        return self.trade_id

    def is_long(self):
        # type: () -> bool
        return self.quantity > 0

    def is_short(self):
        # type: () -> bool
        return self.quantity < 0
