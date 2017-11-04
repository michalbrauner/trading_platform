from positionsizehandlers.position_size import PositionSizeHandler


class PercentageRiskPositionSize(PositionSizeHandler):
    def __init__(self, percentage_risk):
        self.percentage_risk = percentage_risk

    def get_position_size(self, current_holdings, current_positions):
        return self.LOT_SIZE * 0.5
