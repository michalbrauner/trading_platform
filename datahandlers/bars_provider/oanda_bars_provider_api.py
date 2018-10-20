from timeframe.timeframe import TimeFrame
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datahandlers.bars_provider.bars_provider import BarsProvider
from oanda.instrument_api_client import InstrumentApiClient
import time
from loggers.logger import Logger

try:
    import Queue as queue
except ImportError:
    import queue


class OandaBarsProviderApi(BarsProvider):

    def __init__(self, symbols: list, instrument_api_client: InstrumentApiClient, time_frame: TimeFrame,
                 logger: Logger):
        self.symbols = symbols
        self.instrument_api_client = instrument_api_client
        self.time_frame = time_frame
        self.logger = logger

        self.queues = dict((symbol, queue.Queue()) for (symbol) in symbols)
        self.last_bar_datetimes = dict((symbol, None) for (symbol) in symbols)
        self.reload_last_candle_delay_seconds = 60
        self.max_attempts_to_recover_after_oanda_exception = 5
        self.attempts_to_recover_after_oanda_exception = 0

    def get_queue(self, symbol: str) -> queue.Queue:
        return self.queues[symbol]

    def start_providing_bars(self):

        futures = []

        executor = ThreadPoolExecutor(max_workers=len(self.symbols))
        streams_loop = asyncio.new_event_loop()
        for symbol in self.symbols:
            futures.append(streams_loop.run_in_executor(executor, self.handle_bars_for_symbol, symbol))

        done, futures = asyncio.wait(futures, loop=streams_loop, return_when=asyncio.ALL_COMPLETED)

    def handle_bars_for_symbol(self, symbol: str):
        while True:
            last_datetime = None
            if symbol in self.last_bar_datetimes:
                last_datetime = self.last_bar_datetimes[symbol]

            newest_closed_bar = None

            try:
                last_bars = self.instrument_api_client.get_candles(symbol, self.time_frame.as_string(), 2,
                                                                   last_datetime)

                if 'errorMessage' in last_bars:
                    self.stop_providing_bars_for_symbol(symbol, last_bars['errorMessage'])

                for candle in last_bars['candles']:
                    if candle['complete']:
                        newest_closed_bar = candle

            except Exception as e:
                self.attempts_to_recover_after_oanda_exception += 1

                if self.attempts_to_recover_after_oanda_exception > self.max_attempts_to_recover_after_oanda_exception:
                    self.stop_providing_bars_for_symbol(symbol, str(e))
                else:
                    self.logger.write('Error from Oanda API call, recover attempt: {}, error: {}'.format(
                        self.attempts_to_recover_after_oanda_exception, str(e)))

            if newest_closed_bar is None:
                time.sleep(self.reload_last_candle_delay_seconds)
                continue

            if symbol not in self.last_bar_datetimes or self.last_bar_datetimes[symbol] != newest_closed_bar['time']:
                price_ask_data = newest_closed_bar['ask']
                price_bid_data = newest_closed_bar['bid']

                bar_data = self.create_bar_data(self.get_price_datetime(newest_closed_bar['time']), price_ask_data['c'],
                                                price_ask_data['h'], price_ask_data['l'], price_ask_data['o'],
                                                price_bid_data['c'], price_bid_data['h'], price_bid_data['l'],
                                                price_bid_data['o'])

                self.last_bar_datetimes[symbol] = newest_closed_bar['time']

                self.queues[symbol].put_nowait(bar_data)

            time.sleep(self.reload_last_candle_delay_seconds)

    def stop_providing_bars_for_symbol(self, symbol: str, message: str):
        self.queues[symbol].put_nowait({
            'action': 'exit',
            'message': 'Error from Oanda API call, error: {}'.format(message)
        })

        raise StopIteration(message)
