import datetime

from executionhandlers.execution_handler import ExecutionHandler
from events.fill_event import FillEvent
from events.order_event import OrderEvent
from oanda.order_api_client import OrderApiClient
from loggers.logger import Logger

try:
    import Queue as queue
except ImportError:
    import queue


class OandaExecutionHandler(ExecutionHandler):
    def __init__(self, bars, events, account_id, access_token, logger):
        """
        :type bars: []
        :type events: queue
        :type account_id: str
        :type access_token: str
        :type logger: Logger
        """
        self.bars = bars
        self.events = events
        self.access_token = access_token
        self.account_id = account_id
        self.logger = logger

        self.limit_and_stop_orders = list()

    def execute_order(self, event):
        """
        :type event: OrderEvent
        """
        if event.type == 'ORDER':
            order = OrderApiClient(self.account_id, self.access_token)

            if event.order_type == 'MKT':

                if event.direction == 'EXIT':
                    response = order.create_new_exit_order(event.quantity, event.symbol, event.trade_id_to_exit,
                                                           event.trade_to_exit_direction)
                else:
                    response = order.create_new_order(event.direction, event.quantity, event.symbol, event.stop_loss,
                                                      event.take_profit)

                if 'errorCode' in response:
                    self.logger.write(
                        'Error during executing the order: errorCode=%s, errorMessage="%s"' % (response['errorCode'],
                                                                                               response[
                                                                                                   'errorMessage']))
                else:
                    trade_id = int(response['orderFillTransaction']['orderID'])

                    fill_event = FillEvent(
                        datetime.datetime.utcnow(), event.symbol, 'FOREX', event.quantity, event.direction, None, None,
                        trade_id
                    )

                    if event.stop_loss is not None:
                        stop_loss = event.stop_loss
                    else:
                        stop_loss = 0.0

                    if event.take_profit is not None:
                        take_profit = event.take_profit
                    else:
                        take_profit = 0.0

                    self.logger.write(
                        'Executed the order with stopLoss=%10.5f, takeProfit=%10.5f' % (
                            stop_loss, take_profit))

                    self.events.put(fill_event)

    def update_stop_and_limit_orders(self, market_event):
        pass

    def clear_limit_or_stop_orders(self, close_pending_orders_event):
        pass
