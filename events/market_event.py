from events.event import Event


class MarketEvent(Event):
    def __init__(self, symbol: str):
        super().__init__('MARKET', symbol)

    def get_as_string(self) -> str:
        return ''
