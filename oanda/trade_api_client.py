import requests
import json


class TradeApiClient:

    def __init__(self, account_id, access_token):
        self.access_token = access_token
        self.account_id = account_id
        self.domain = 'api-fxpractice.oanda.com'

    def close_trade(self, trade_id):
        """
        :type trade_id: int
        """

        data = {'units': 'ALL'}

        return self.send_request(self.get_close_trade_endpoint(trade_id), 'PUT', data)

    def send_request(self, url, method, data):
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
            req = requests.Request(method, url, headers=headers, data=json.dumps(data))
            pre = req.prepare()
            response = s.send(pre, stream=True, verify=True)

            return json.loads(response.content)

        except Exception as e:
            s.close()
            raise Exception('Caught exception when connecting to API\n' + str(e))

    def get_close_trade_endpoint(self, trade_id):
        return 'https://{}/v3/accounts/{}/trades/{}/close'.format(self.domain, self.account_id, trade_id)
