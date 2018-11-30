import requests
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from oanda.instrument_api_request import InstrumentApiRequest
import time

try:
    import Queue as queue
except ImportError:
    import queue


class InstrumentApiClient:

    WAIT_BETWEEN_REQUESTS_SECONDS = 10

    def __init__(self, access_token):
        self.access_token = access_token
        self.domain = 'api-fxpractice.oanda.com'
        self.requests_queue = queue.Queue()
        self.candles_for_symbol_queue = dict()
        self.processing_requests_started = False

    def start_process_requests(self):
        self.processing_requests_started = True

        futures = []

        executor = ThreadPoolExecutor(max_workers=1)
        streams_loop = asyncio.new_event_loop()
        futures.append(streams_loop.run_in_executor(executor, self.process_requests))

        asyncio.wait(futures, loop=streams_loop, return_when=asyncio.FIRST_COMPLETED)

    def process_requests(self):
        while True:
            request = self.get_request_from_queue()
            instrument = request.get_instrument()

            request_response = self.get_candles_from_api(instrument, request.get_granularity(),
                                                         request.get_count(), request.get_from_datetime())

            self.candles_for_symbol_queue[instrument].put(request_response)

            time.sleep(self.WAIT_BETWEEN_REQUESTS_SECONDS)

    def get_request_from_queue(self) -> InstrumentApiRequest:
        return self.requests_queue.get()

    def get_candles(self, instrument: str, granularity: str, count: int, from_datetime: str = None):
        if self.processing_requests_started is False:
            raise Exception('InstrumentApiClient - processing requests not started')

        if instrument not in self.candles_for_symbol_queue:
            self.candles_for_symbol_queue[instrument] = queue.Queue()

        api_request = InstrumentApiRequest(instrument, granularity, count, from_datetime)
        self.requests_queue.put(api_request)

        return self.candles_for_symbol_queue[instrument].get()

    def get_candles_from_api(self, instrument: str, granularity: str, count: int, from_datetime: str = None):
        s = requests.Session()

        url_configuration = '&dailyAlignment=3&alignmentTimezone=Europe/Prague'
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
            raise Exception('Caught exception when connecting to API\n' + str(e)) from e
