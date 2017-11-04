from positionsizehandlers.position_size import PositionSizeHandler


class FixedPositionSize(PositionSizeHandler):
    def __init__(self, position_size_in_lot):
        self.position_size_in_lot = position_size_in_lot

    def get_position_size(self, current_holdings, current_positions):
        return self.position_size_in_lot * self.LOT_SIZE
