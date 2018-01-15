class Position(object):
    def __init__(self, symbol, trade_id, quantity):
        """

        :type symbol: str
        :type trade_id: int
        :type quantity: int
        """

        self.symbol = symbol
        self.trade_id = trade_id
        self.quantity = quantity

    def get_quantity(self):
        # type: () -> int
        return self.quantity

    def set_quantity(self, quantity):
        # type: (int) -> None
        self.quantity = quantity
