from positionsizehandlers.position_size import PositionSizeHandler


class FixedPositionSize(PositionSizeHandler):
    def __init__(self, current_positions, current_holdings):
        self.current_positions = current_positions
        self.current_holdings = current_holdings

    def get_position_size(self):
        return 0
