from abc import ABCMeta, abstractmethod


class PositionSizeHandler(object):
    __metaclass__ = ABCMeta

    LOT_SIZE = 100000

    @abstractmethod
    def get_position_size(self):
        raise NotImplementedError("Should implement get_position_size()")
