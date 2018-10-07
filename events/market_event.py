from events.event import Event


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self, symbol: str):
        super().__init__('MARKET', symbol)

    def get_as_string(self):
        return ''
