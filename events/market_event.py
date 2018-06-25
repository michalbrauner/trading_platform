from events.event import Event


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self):
        super().__init__('MARKET')

    def get_as_string(self):
        return ''
