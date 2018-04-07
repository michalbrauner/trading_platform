import requests
import json


class InstrumentApiClient:

    def __init__(self, access_token):
        self.access_token = access_token
        self.domain = 'api-fxpractice.oanda.com'

    def get_candles(self, instrument, granularity, count):
        """
        :type instrument: str
        :type granularity: str
        :type count: int
        """
        s = requests.Session()
        url = 'https://{}/v3/instruments/{}/candles?price={}&granularity={}&count={}'.format(self.domain, instrument,
                                                                                             'BA', granularity, count)
        headers = {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Content-Type': 'application/json'
        }

        try:
            req = requests.Request('GET', url, headers=headers)
            pre = req.prepare()
            response = s.send(pre, stream=False, verify=True)

            return json.loads(response.content)

        except Exception as e:
            s.close()
            raise Exception('Caught exception when connecting to API\n' + str(e))
