import requests
import json


class OrderApiClient:

    def __init__(self, account_id, access_token):
        self.access_token = access_token
        self.account_id = account_id
        self.domain = 'api-fxpractice.oanda.com'

    def create_new_order(self, direction, units, instrument, stop_loss=None, take_profit=None):
        """
        :type direction: str
        :type units: int
        :type instrument: str
        :type stop_loss: float
        :type take_profit: float
        """
        if (direction == 'SELL' and units > 0) or (direction == 'BUY' and units < 0):
            units = units * -1

        data_order = {
            'units': units,
            'instrument': instrument,
            'timeInForce': 'FOK',
            'type': 'MARKET',
            'positionFill': 'DEFAULT'
        }

        if stop_loss is not None:
            data_order['stopLossOnFill'] = {'price': ('%.5f' % stop_loss)}

        response = self.send_request(self.get_orders_endpoint(), {'order': data_order})

        if take_profit is not None and 'orderFillTransaction' in response:
            if 'tradeOpened' in response['orderFillTransaction']:
                trade_id = response['orderFillTransaction']['tradeOpened']['tradeID']
                take_profit_response = self.create_take_profit_order(trade_id, take_profit)

        return response

    def create_take_profit_order(self, trade_id, price):
        """
        :type trade_id: str
        :type price: float
        """
        data = {
            'order': {
                'type': 'TAKE_PROFIT',
                'tradeID': trade_id,
                'price': '%.5f' % price,
                'timeInForce': 'GTC',
                'triggerCondition': 'DEFAULT'
            }
        }

        return self.send_request(self.get_orders_endpoint(), data)

    def create_new_exit_order(self, units, instrument, trade_id, trade_to_exit_direction):
        """
        :type direction: str
        :type units: int
        :type instrument: str
        :type trade_id: int
        :type trade_to_exit_direction: string
        """
        if (trade_to_exit_direction == 'SELL' and units < 0) or (trade_to_exit_direction == 'BUY' and units > 0):
            units = units * -1

        data = {
            'order': {
                'units': units,
                'instrument': instrument,
                'type': 'MARKET',
                'tradeClose ': {
                    'tradeID': trade_id,
                    'units': 'ALL'
                },
            }
        }

        return self.send_request(self.get_orders_endpoint(), data)

    def send_request(self, url, data):
        """
        :type url: str
        :type data: dict
        """

        s = requests.Session()
        headers = {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Content-Type': 'application/json'
        }

        try:
            req = requests.Request('POST', url, headers=headers, data=json.dumps(data))
            pre = req.prepare()
            response = s.send(pre, stream=True, verify=True)

            return json.loads(response.content)

        except Exception as e:
            s.close()
            raise Exception('Caught exception when connecting to API\n' + str(e))

    def get_orders_endpoint(self):
        return 'https://{}/v3/accounts/{}/orders'.format(self.domain, self.account_id)
