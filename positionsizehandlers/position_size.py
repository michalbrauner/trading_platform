from abc import ABCMeta, abstractmethod


class PositionSizeHandler(object):
    __metaclass__ = ABCMeta

    LOT_SIZE = 100000

    @abstractmethod
    def get_position_size(self, current_holdings, current_positions):
        raise NotImplementedError("Should implement get_position_size()")
