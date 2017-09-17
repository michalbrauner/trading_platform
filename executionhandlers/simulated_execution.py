import datetime

from executionhandlers.execution import ExecutionHandler
from events.order_event import OrderEvent
from events.fill_event import FillEvent
from events.close_pending_orders_event import ClosePendingOrdersEvent
import copy


class SimulatedExecutionHandler(ExecutionHandler):
    """
    The simulated execution handler simply converts all order
    objects into their equivalent fill objects automatically
    without latency, slippage or fill-ratio issues.
    This allows a straightforward "first go" test of any strategy,
    before implementation with a more sophisticated execution
    handler.
    """
    def __init__(self, bars, events):
        """
        Initialises the handler, setting the event queues
        up internally.
        Parameters:
        bars
        events - The Queue of Event objects.
        """
        self.bars = bars
        self.events = events
        self.limit_and_stop_orders = list()

    def execute_order(self, event):
        """
        Simply converts Order objects into Fill objects naively,
        i.e. without any latency, slippage or fill ratio problems.
        Parameters:
        event - Contains an Event object with order information.
        """
        if event.type == 'ORDER':
            if event.order_type == 'MKT':
                fill_event = FillEvent(
                    datetime.datetime.utcnow(), event.symbol, 'FOREX', event.quantity, event.direction, None
                )
                self.events.put(fill_event)

                reversed_direction = self.get_reversed_direction(event.direction)

                if event.stop_loss is not None:
                    stop_loss_order = OrderEvent(event.symbol, 'STP', event.quantity, reversed_direction, None, None,
                                       event.stop_loss)

                    self.limit_and_stop_orders.append(stop_loss_order)

                if event.take_profit is not None:
                    take_profit_order = OrderEvent(event.symbol, 'LMT', event.quantity, reversed_direction, None, None,
                                       event.take_profit)

                    self.limit_and_stop_orders.append(take_profit_order)

    def update_stop_and_limit_orders(self, market_event):
        for order in self.limit_and_stop_orders:

            price_bid = self.bars.get_latest_bar_value(order.symbol, 'close_bid')
            price_ask = self.bars.get_latest_bar_value(order.symbol, 'close_ask')

            note = ''
            should_be_filled = False

            if order.order_type == 'STP' and self.stop_order_should_be_filled(order, price_ask, price_bid):
                    should_be_filled = True
                    note = 'StopOrder hit at price Ask={}, Bid={}'.format(price_ask, price_bid)
            elif order.order_type == 'LMT' and self.limit_order_should_be_filled(order, price_ask, price_bid):
                    should_be_filled = True
                    note = 'LimitOrder hit at price Ask={}, Bid={}'.format(price_ask, price_bid)

            if should_be_filled:
                new_order = self.make_pending_order_market(order, note)
                self.events.put(new_order)

                close_pending_orders_event = ClosePendingOrdersEvent(order.symbol)
                self.events.put(close_pending_orders_event)

    def stop_order_should_be_filled(self, order, price_ask, price_bid):
        return (order.direction == 'BUY' and price_ask >= order.price) or \
        (order.direction == 'SELL' and price_bid <= order.price)

    def limit_order_should_be_filled(self, order, price_ask, price_bid):
        return (order.direction == 'BUY' and price_ask <= order.price) or \
               (order.direction == 'SELL' and price_bid >= order.price)

    def clear_limit_or_stop_orders(self, close_pending_orders_event):
        self.limit_and_stop_orders = filter(lambda order_item: order_item.symbol != close_pending_orders_event.symbol,
                                            self.limit_and_stop_orders)

    def make_pending_order_market(self, order, note):
        new_order = copy.copy(order)
        new_order.order_type = 'MKT'
        new_order.price = None
        new_order.note = note

        return new_order

    def get_reversed_direction(self, direction):
        if direction == 'BUY':
            return 'SELL'
        elif direction == 'SELL':
            return 'BUY'
        else:
            return ''
