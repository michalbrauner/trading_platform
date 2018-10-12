from events.event import Event


class ClosePendingOrdersEvent(Event):
    def __init__(self, symbol: str) -> None:

        super().__init__('CLOSE_PENDING_ORDERS', symbol)

    def get_as_string(self) -> str:
        return 'ClosePendingOrders: %s' % self.symbol
