from typing import Optional


class InstrumentApiRequest(object):
    def __init__(self, instrument: str, granularity: str, count: int, from_datetime: str = None):
        self.instrument = instrument
        self.granularity = granularity
        self.count = count
        self.from_datetime = from_datetime

    def get_instrument(self) -> str:
        return self.instrument

    def get_granularity(self) -> str:
        return self.granularity

    def get_count(self) -> int:
        return self.count

    def get_from_datetime(self) -> Optional[str]:
        return self.from_datetime
