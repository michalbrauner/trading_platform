from strategies.patterns.trade_type import TradeType


class PatternResolvingResult(object):
    def __init__(self, is_valid: bool, trade_type: TradeType):
        self._is_valid = is_valid
        self._trade_type = trade_type

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @property
    def trade_type(self) -> TradeType:
        return self._trade_type
