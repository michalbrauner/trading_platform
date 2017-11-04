from events.event import Event


class ClosePendingOrdersEvent(Event):
    """
    Handles the event in order to close pending orders
    """

    def __init__(self, symbol):
        """
        Initialises the SystemEvent.
        """
        self.type = 'CLOSE_PENDING_ORDERS'
        self.symbol = symbol

    def get_as_string(self):
        return 'ClosePendingOrders: %s' % self.symbol
