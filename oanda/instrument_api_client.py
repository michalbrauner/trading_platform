import requests
import json


class InstrumentApiClient:

    def __init__(self, access_token):
        self.access_token = access_token
        self.domain = 'api-fxpractice.oanda.com'

    def get_candles(self, instrument: str, granularity: str, count: int, from_datetime: str = None):
        s = requests.Session()

        url_configuration = '&dailyAlignment=0&alignmentTimezone=UTC'
        url = 'https://{}/v3/instruments/{}/candles?price={}&granularity={}&count={}{}'.format(
            self.domain, instrument, 'BA', granularity, count, url_configuration)

        if from_datetime is not None:
            url = '{}&from={}&includeFirst=False'.format(url, from_datetime)

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
