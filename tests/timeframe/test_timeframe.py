import unittest
from unittest_data_provider import data_provider
from datetime import datetime

from timeframe.timeframe import TimeFrame


class TestTimeFrame(unittest.TestCase):
    test_get_timeframe_border_data = lambda: (
        (
            (
                datetime(year=2017, month=1, day=1, hour=10, minute=10, second=30),
                datetime(year=2017, month=1, day=1, hour=10, minute=10, second=34),
            ),
            datetime(year=2017, month=1, day=1, hour=10, minute=10, second=33),
            TimeFrame.TIMEFRAME_S5,
        ),
        (
            (
                datetime(year=2017, month=1, day=1, hour=10, minute=10, second=30),
                datetime(year=2017, month=1, day=1, hour=10, minute=10, second=34),
            ),
            datetime(year=2017, month=1, day=1, hour=10, minute=10, second=30),
            TimeFrame.TIMEFRAME_S5,
        ),
        (
            (
                datetime(year=2017, month=1, day=1, hour=10, minute=10, second=30),
                datetime(year=2017, month=1, day=1, hour=10, minute=10, second=34),
            ),
            datetime(year=2017, month=1, day=1, hour=10, minute=10, second=34),
            TimeFrame.TIMEFRAME_S5,
        ),
        (
            (
                datetime(year=2017, month=1, day=1, hour=10, minute=0, second=0),
                datetime(year=2017, month=1, day=1, hour=10, minute=14, second=59),
            ),
            datetime(year=2017, month=1, day=1, hour=10, minute=10, second=34),
            TimeFrame.TIMEFRAME_M15,
        ),
        (
            (
                datetime(year=2017, month=1, day=1, hour=10, minute=0, second=0),
                datetime(year=2017, month=1, day=1, hour=10, minute=14, second=59),
            ),
            datetime(year=2017, month=1, day=1, hour=10, minute=00, second=34),
            TimeFrame.TIMEFRAME_M15,
        ),
    )

    @data_provider(test_get_timeframe_border_data)
    def test_get_timeframe_border(self, expected_border, test_datetime, timeframe):
        timeframe_object = TimeFrame(timeframe)

        bar_border = timeframe_object.get_timeframe_border(test_datetime)

        self.assertEqual(expected_border, bar_border)


if __name__ == '__main':
    unittest.main()
