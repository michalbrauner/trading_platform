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
            order = OrderApiClient(self.account_id, self.access_token)

            if event.order_type == 'MKT':

                if event.direction == 'EXIT':
                    response = order.create_new_exit_order(event.quantity, event.symbol, event.trade_id_to_exit)
                else:
                    response = order.create_new_order(event.direction, event.quantity, event.symbol, event.stop_loss,
                                                      event.take_profit)

                if event.direction == 'EXIT':
                    trade_id = event.trade_id_to_exit

                    if response['side'] == 'sell':
                        fill_direction_koeficient = -1
                    else:
                        fill_direction_koeficient = 1
                else:
                    trade_id = None
                    fill_direction_koeficient = None

                fill_event = FillEvent(
                    datetime.datetime.utcnow(), event.symbol, 'FOREX', event.quantity, event.direction, None, None,
                    trade_id, fill_direction_koeficient
                )

                self.events.put(fill_event)

    def update_stop_and_limit_orders(self, market_event):
        pass

    def clear_limit_or_stop_orders(self, close_pending_orders_event):
        pass
