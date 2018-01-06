import datetime

from executionhandlers.execution_handler import ExecutionHandler
from events.fill_event import FillEvent
from oanda.order_api_client import OrderApiClient

try:
    import Queue as queue
except ImportError:
    import queue


class OandaExecutionHandler(ExecutionHandler):
    def __init__(self, bars, events, account_id, access_token):
        """
        :type bars: []
        :type events: queue
        :type account_id: str
        :type access_token: str
        """
        self.bars = bars
        self.events = events
        self.access_token = access_token
        self.account_id = account_id

        self.limit_and_stop_orders = list()

    def execute_order(self, event):
        """
        :type event: queue
        """
        if event.type == 'ORDER':
            if event.order_type == 'MKT':
                fill_event = FillEvent(
                    datetime.datetime.utcnow(), event.symbol, 'FOREX', event.quantity, event.direction, None
                )
                self.events.put(fill_event)

                order = OrderApiClient(self.account_id, self.access_token)
                response = order.create_new_order(event.quantity, event.symbol, event.stop_loss, event.take_profit)

    def update_stop_and_limit_orders(self, market_event):
        pass

    def clear_limit_or_stop_orders(self, close_pending_orders_event):
        pass
