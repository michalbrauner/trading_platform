from events.event import Event
from datetime import datetime
from typing import Optional


class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self, timeindex: datetime, symbol: str, exchange: str, quantity: float, direction: str,
                 fill_cost: Optional[float] = None, commission: Optional[float] = None, trade_id: Optional[int] = None):

        super().__init__('FILL')

        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction

        if commission is None:
            self.commission = 0
        else:
            self.commission = commission

        if fill_cost is None:
            self.fill_cost = 0
        else:
            self.fill_cost = fill_cost

        if trade_id is None:
            self.trade_id = 0
        else:
            self.trade_id = trade_id

    def get_as_string(self):
        return 'Fill: TimeIndex: %s, Symbol: %s, Exchange: %s, Quantity: %f, Direction: %s,  FillCost: %f, TradeId: %d' % \
               (
                   self.timeindex, self.symbol, self.exchange, self.quantity, self.direction, self.fill_cost,
                   self.trade_id
               )
