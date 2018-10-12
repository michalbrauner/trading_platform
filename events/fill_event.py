from events.event import Event
from datetime import datetime
from typing import Optional


class FillEvent(Event):
    def __init__(self, time_index: datetime, symbol: str, exchange: str, quantity: float, direction: str,
                 fill_cost: Optional[float] = None, commission: Optional[float] = None, trade_id: Optional[int] = None):

        super().__init__('FILL', symbol)

        self.time_index = time_index
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

    def get_as_string(self) -> str:
        return 'Fill: TimeIndex: %s, Symbol: %s, Exchange: %s, Quantity: %f, Direction: %s,  FillCost: %f, TradeId: %d' % \
               (
                   self.time_index, self.symbol, self.exchange, self.quantity, self.direction, self.fill_cost,
                   self.trade_id
               )
