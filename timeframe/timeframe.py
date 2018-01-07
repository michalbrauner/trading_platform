from datetime import datetime
import time
import pytz

class TimeFrame(object):

    TIMEFRAME_S5 = 'S5'
    TIMEFRAME_M1 = 'M1'
    TIMEFRAME_M15 = 'M15'

    NUMBER_OF_SECONDS_IN_TIMEFRAMES = {
        TIMEFRAME_S5: 5,
        TIMEFRAME_M1: 60,
        TIMEFRAME_M15: 60 * 15,
    }

    def __init__(self, timeframe):
        self.timeframe = timeframe

    def get_timeframe_border(self, time_to_analyze):
        # type: (datetime) -> tuple[datetime, datetime]
        datetime_in_seconds = int(time.mktime(time_to_analyze.timetuple()))

        number_of_seconds_in_timeframe = self.NUMBER_OF_SECONDS_IN_TIMEFRAMES[self.timeframe]

        border_lower_seconds = datetime_in_seconds - datetime_in_seconds % number_of_seconds_in_timeframe
        border_higher_seconds = border_lower_seconds + number_of_seconds_in_timeframe - 1

        return (
            datetime.fromtimestamp(border_lower_seconds),
            datetime.fromtimestamp(border_higher_seconds),
        )

