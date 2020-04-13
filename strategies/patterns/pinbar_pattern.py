from strategies.patterns.pattern import Pattern
from strategies.patterns.pattern_resolving_result import PatternResolvingResult
from strategies.patterns.trade_type import TradeType


class PinBarPattern(Pattern):
    # ToDo zmenit poradi argumentu - OHLC
    def __init__(self, open_price: float, close_price: float, high_price: float, low_price: float):
        self.open_price = open_price
        self.close_price = close_price
        self.high_price = high_price
        self.low_price = low_price

    def resolve(self) -> PatternResolvingResult:
        size_of_bar = abs(self.high_price - self.low_price)

        if size_of_bar == 0:
            return PatternResolvingResult(False, TradeType.UNKNOWN)

        body_to_bar_ratio = self.calculate_body_to_bar_ratio(size_of_bar)

        body_top = max(self.open_price, self.close_price)
        body_bottom = min(self.open_price, self.close_price)

        upper_tail_to_bar_ratio = (self.high_price - body_top) / size_of_bar
        lower_tail_to_bar_ratio = (body_bottom - self.low_price) / size_of_bar

        bigger_tail = max(lower_tail_to_bar_ratio, upper_tail_to_bar_ratio)
        smaller_tail = min(lower_tail_to_bar_ratio, upper_tail_to_bar_ratio)

        if body_to_bar_ratio <= .2:
            if bigger_tail >= .7 and smaller_tail <= .2:
                if upper_tail_to_bar_ratio > lower_tail_to_bar_ratio:
                    trade_type = TradeType.SHORT
                else:
                    trade_type = TradeType.LONG

                return PatternResolvingResult(True, trade_type)

        return PatternResolvingResult(False, TradeType.UNKNOWN)

    def calculate_body_to_bar_ratio(self, size_of_bar) -> float:
        size_of_body = abs(self.open_price - self.close_price)

        return size_of_body / size_of_bar
