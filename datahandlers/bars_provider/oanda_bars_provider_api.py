from oanda.stream import Stream as OandaPriceStream
from timeframe.timeframe import TimeFrame
from dateutil import parser
from datetime import datetime
import pandas as pd
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datahandlers.bars_provider.bars_provider import BarsProvider
from oanda.instrument_api_client import InstrumentApiClient

try:
    import Queue as queue
except ImportError:
    import queue


class OandaBarsProviderApi(BarsProvider):

    def __init__(self, symbols: list, instrument_api_client: InstrumentApiClient, time_frame: TimeFrame):
        self.symbols = symbols
        self.instrument_api_client = instrument_api_client
        self.time_frame = time_frame

        self.queues = dict((symbol, queue.Queue()) for (symbol) in symbols)
        self.last_bar_datetimes = dict((symbol, None) for (symbol) in symbols)

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
        last_bars = self.instrument_api_client.get_candles(symbol, self.time_frame.as_string(), 1)

        # ToDo: dodelat pouzivani last_bar_datetimes, kontrola jestli svice uz nebyla nactena a dodelat opakovani napr. kazdou minutu
        for price_data in last_bars['candles']:
            price_ask_data = price_data['ask']
            price_bid_data = price_data['bid']

            bar_data = self.create_bar_data(self.get_price_datetime(price_data['time']), price_ask_data['c'],
                                            price_ask_data['h'], price_ask_data['l'], price_ask_data['o'],
                                            price_bid_data['c'], price_bid_data['h'], price_bid_data['l'],
                                            price_bid_data['o'])

            self.queues[symbol].put_nowait(bar_data)
