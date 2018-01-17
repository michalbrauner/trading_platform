from events.event import Event
from datetime import datetime


class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    DIRECTION_KOEFICIENT_LONG = 1
    DIRECTION_KOEFICIENT_SHORT = 1

    def __init__(self, timeindex, symbol, exchange, quantity,
                 direction, fill_cost, commission=None, trade_id=None, fill_direction_koeficient=None):
        """

        :type timeindex: datetime
        :type symbol: str
        :type exchange: str
        :type quantity: float
        :type direction: str
        :type fill_cost: float|None
        :type commission: float|None
        :type trade_id: int|None
        :type fill_direction_koeficient: int|None
        """
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_direction_koeficient = fill_direction_koeficient

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

        if fill_direction_koeficient is None:
            if self.direction == 'BUY':
                self.fill_direction_koeficient = 1
            else:
                self.fill_direction_koeficient = -1
        else:
            self.fill_direction_koeficient = fill_direction_koeficient

    def get_as_string(self):
        return 'Fill: TimeIndex: %s, Symbol: %s, Exchange: %s, Quantity: %f, Direction: %s,  FillCost: %f, TradeId: %d, FillDirectionKoeficient: %d' % \
               (
                   self.timeindex, self.symbol, self.exchange, self.quantity, self.direction, self.fill_cost,
                   self.trade_id, self.fill_direction_koeficient
               )
