import unittest
from mock import patch
from datahandlers.oanda_data_handler import OandaDataHandler
from  timeframe.timeframe import TimeFrame
from datetime import datetime

try:
    import Queue as queue
except ImportError:
    import queue


class TestOandaDataHandler(unittest.TestCase):
    symbol_eur_usd = 'EUR_USD'

    @patch('oanda.stream.Stream')
    def test_update_bars(self, MockStream):
        stream = MockStream()
        events = queue.Queue()

        stream.get_price.side_effect = self._get_prices_to_return()

        data_handler = OandaDataHandler(events, [self.symbol_eur_usd], stream, TimeFrame.TIME_FRAME_S5)
        data_handler.update_bars()

        self.assertEqual(
            {
                'close_ask': 1.64,
                'close_bid': 1.54,
                'datetime': datetime(year=2017, month=1, day=1, hour=15, minute=0, second=0),
                'high_ask': 1.74,
                'high_bid': 1.75,
                'low_ask': 1.42,
                'low_bid': 1.43,
                'open_ask': 1.61,
                'open_bid': 1.51,
                'volume': 0,
            },
            data_handler.latest_symbol_data[self.symbol_eur_usd][0]
        )

    def _get_prices_to_return(self):
        return [
            [
                self._get_price_data_item(u'2017-01-01T15:00:01.0001Z', 1.61, 1.51),
                self._get_price_data_item(u'2017-01-01T15:00:01.0002Z', 1.42, 1.43),
                self._get_price_data_item(u'2017-01-01T15:00:03.0001Z', 1.74, 1.75),
                self._get_price_data_item(u'2017-01-01T15:00:04.0001Z', 1.64, 1.54),
                self._get_price_data_item(u'2017-01-01T15:00:05.0001Z', 1.65, 1.55),
            ]
        ]

    def _get_price_data_item(self, time, ask_price, bid_price):
        return {'instrument': self.symbol_eur_usd, 'datetime': time, 'ask': ask_price, 'bid': bid_price}
