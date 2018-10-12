from oanda.stream import Stream as OandaPriceStream
from timeframe.timeframe import TimeFrame
import pandas as pd
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datahandlers.bars_provider.bars_provider import BarsProvider

try:
    import Queue as queue
except ImportError:
    import queue


class OandaBarsProviderStream(BarsProvider):

    def __init__(self, streams: List[OandaPriceStream], symbols: list, time_frame: TimeFrame):
        self.streams = streams
        self.symbols = symbols
        self.time_frame = time_frame

        self.queues = dict((symbol, queue.Queue()) for (symbol) in symbols)

        self.opened_bars = dict((symbol, pd.DataFrame()) for (symbol) in symbols)
        self.opened_bars_finishes_at = dict((symbol, None) for (symbol) in symbols)
        self.opened_bars_starts_at = dict((symbol, None) for (symbol) in symbols)

    def get_queue(self, symbol: str) -> queue.Queue:
        return self.queues[symbol]

    def start_providing_bars(self) -> None:
        for stream in self.streams:
            if not stream.is_connected():
                stream.connect_to_stream()

        some_stream_is_not_connected = False

        for stream in self.streams:
            if stream.response.status_code != 200:
                for symbol in stream.get_instruments():
                    self.queues[symbol].put_nowait({
                        'action': 'exit',
                        'message': 'Stream not connected'
                    })
                some_stream_is_not_connected = True

        if some_stream_is_not_connected:
            return

        futures = []

        executor = ThreadPoolExecutor(max_workers=len(self.streams))
        streams_loop = asyncio.new_event_loop()
        for stream in self.streams:
            futures.append(streams_loop.run_in_executor(executor, self.handle_prices_stream, stream))

        done, futures = asyncio.wait(futures, loop=streams_loop, return_when=asyncio.ALL_COMPLETED)

    def handle_prices_stream(self, stream: OandaPriceStream):
        for price in stream.get_price():
            symbol = price['instrument']

            price_datetime = self.get_price_datetime(price['datetime'])
            bar_borders = self.time_frame.get_time_frame_border(price_datetime)

            if self.opened_bars_finishes_at[symbol] is None:
                self.opened_bars_finishes_at[symbol] = bar_borders[1]
                self.opened_bars_starts_at[symbol] = bar_borders[0]

            if self.opened_bars_finishes_at[symbol] >= price_datetime or 'datetime' not in self.opened_bars[symbol]:
                new_price_data = pd.DataFrame(price, index=[price['datetime']])
                self.opened_bars[symbol] = self.opened_bars[symbol].append(new_price_data)
            else:
                price_bid_open = float(self.opened_bars[symbol]['bid'][0])
                price_bid_close = float(self.opened_bars[symbol]['bid'][-1])
                price_bid_high = float(self.opened_bars[symbol]['bid'].max())
                price_bid_low = float(self.opened_bars[symbol]['bid'].min())

                price_ask_open = float(self.opened_bars[symbol]['ask'][0])
                price_ask_close = float(self.opened_bars[symbol]['ask'][-1])
                price_ask_high = float(self.opened_bars[symbol]['ask'].max())
                price_ask_low = float(self.opened_bars[symbol]['ask'].min())

                data = self.create_bar_data(self.opened_bars_starts_at[symbol], price_ask_close, price_ask_high,
                                            price_ask_low,
                                            price_ask_open, price_bid_close, price_bid_high, price_bid_low,
                                            price_bid_open)

                self.opened_bars_finishes_at[symbol] = None
                self.opened_bars_starts_at[symbol] = None

                self.queues[symbol].put_nowait(data)
