from events.event import Event


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, symbol, order_type, quantity, direction, stop_loss=None, take_profit=None):
        """
        Initialises the order type, setting whether it is
        a Market order ('MKT') or Limit order ('LMT'), has
        a quantity (integral) and its direction ('BUY' or
        'SELL').

        Parameters:
        symbol - The instrument to trade.
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        stop_loss - The price where the order is closed at market automatically with loss.
        take_profit - The price where the order is closed at market automatically with profit.
        """

        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def get_as_string(self):
        """
        Return this order as a string
        """
        return 'Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s, StopLoss=%f, TakeProfit=%f' % \
               (self.symbol, self.order_type, self.quantity, self.direction,
                self.get_zero_if_none_or_value(self.stop_loss), self.get_zero_if_none_or_value(self.take_profit))

    def get_zero_if_none_or_value(self, value):
        if value is None:
            return 0
        else:
            return value
