import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from datahandlers.oanda_data_handler import OandaDataHandler
from timeframe.timeframe import TimeFrame
from oanda.instrument_api_client import InstrumentApiClient
import asyncio

try:
    import Queue as queue
except ImportError:
    import queue


class Price(object):
    def __init__(self, ask, bid):
        self.ask = ask
        self.bid = bid


class TestOandaDataHandler(unittest.TestCase):

    @patch('datahandlers.bars_provider.bars_provider.BarsProvider')
    @patch('queue.Queue')
    def test_update_bars(self, bars_provider, queue):
        symbol_eur_usd = 'EUR_USD'

        queue.get.side_effect = TestOandaDataHandler._get_prices_to_return()

        events_per_symbol = {symbol_eur_usd: queue}

        bars_provider.get_queue = MagicMock(return_value=queue)
        bars_provider.start_providing_bars = MagicMock()

        instrument_api_client = InstrumentApiClient('accesstoken')

        data_handler = OandaDataHandler(events_per_symbol, [symbol_eur_usd], bars_provider, instrument_api_client,
                                        TimeFrame.TIME_FRAME_S5, 0)
        data_handler.providing_bars_loop = asyncio.get_event_loop()

        all_expected_data = TestOandaDataHandler._get_prices_to_return()

        for iteration in [0, 1, 2, 3]:
            data_handler.update_bars(symbol_eur_usd)
            self.assertEqual(
                all_expected_data[iteration],
                data_handler.get_latest_bar(symbol_eur_usd)
            )

        self.assertEqual(all_expected_data, data_handler.get_latest_bars(symbol_eur_usd, 4))

    @staticmethod
    def _get_expected_data():
        return TestOandaDataHandler._get_prices_to_return()

    @staticmethod
    def _get_prices_to_return() -> list:
        return [
            TestOandaDataHandler._create_price_data_item(
                u'2017-01-01T15:00:01.0001Z',
                Price(1.512, 1.511),
                Price(1.612, 1.611),
                Price(1.312, 1.311),
                Price(1.412, 1.411),
            ),
            TestOandaDataHandler._create_price_data_item(
                u'2017-01-01T15:00:01.0002Z',
                Price(1.522, 1.521),
                Price(1.622, 1.621),
                Price(1.322, 1.321),
                Price(1.422, 1.421),
            ),
            TestOandaDataHandler._create_price_data_item(
                u'2017-01-01T15:00:04.0001Z',
                Price(1.532, 1.531),
                Price(1.632, 1.631),
                Price(1.332, 1.331),
                Price(1.432, 1.431),
            ),
            TestOandaDataHandler._create_price_data_item(
                u'2017-01-01T15:00:05.0001Z',
                Price(1.542, 1.541),
                Price(1.642, 1.641),
                Price(1.342, 1.341),
                Price(1.442, 1.441),
            ),
        ]

    @staticmethod
    def _create_price_data_item(time: str, open: Price, high: Price, low: Price, close: Price) -> dict:
        return {
            'datetime': time,
            'open_bid': open.bid,
            'open_ask': open.ask,
            'high_bid': high.bid,
            'high_ask': high.ask,
            'low_bid': low.bid,
            'low_ask': low.ask,
            'close_bid': close.bid,
            'close_ask': close.ask,
            'volume': 0
        }
