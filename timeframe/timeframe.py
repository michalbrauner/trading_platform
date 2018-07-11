from datetime import datetime
import time


class TimeFrame(object):
    TIME_FRAME_S5 = 'S5'
    TIME_FRAME_M1 = 'M1'
    TIME_FRAME_M15 = 'M15'
    TIME_FRAME_H1 = 'H1'
    TIME_FRAME_H4 = 'H4'

    NUMBER_OF_SECONDS_IN_TIME_FRAMES = {
        TIME_FRAME_S5: 5,
        TIME_FRAME_M1: 60,
        TIME_FRAME_M15: 60 * 15,
        TIME_FRAME_H1: 60 * 60,
        TIME_FRAME_H4: 60 * 60 * 4,
    }

    def __init__(self, time_frame):
        self.time_frame = time_frame

    def get_time_frame_border(self, time_to_analyze):
        # type: (datetime) -> tuple[datetime, datetime]
        datetime_in_seconds = int(time.mktime(time_to_analyze.timetuple()))

        number_of_seconds_in_time_frame = self.NUMBER_OF_SECONDS_IN_TIME_FRAMES[self.time_frame]

        border_lower_seconds = datetime_in_seconds - datetime_in_seconds % number_of_seconds_in_time_frame
        border_higher_seconds = border_lower_seconds + number_of_seconds_in_time_frame - 1

        return (
            datetime.fromtimestamp(border_lower_seconds),
            datetime.fromtimestamp(border_higher_seconds),
        )

    @staticmethod
    def get_allowed_time_frames():
        return [
            TimeFrame.TIME_FRAME_S5,
            TimeFrame.TIME_FRAME_M1,
            TimeFrame.TIME_FRAME_M15,
            TimeFrame.TIME_FRAME_H1,
            TimeFrame.TIME_FRAME_H4,
        ]
