from oanda.stream import Stream


class StreamFactory:
    def __init__(self):
        pass

    def create(self, account_id, access_token, instruments):
        return Stream(account_id, access_token, instruments)
