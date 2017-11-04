from abc import ABCMeta, abstractmethod


class Logger(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def open(self):
        raise NotImplementedError("Should implement open()")

    @abstractmethod
    def close(self):
        raise NotImplementedError("Should implement close()")

    @abstractmethod
    def write(self, log):
        raise NotImplementedError("Should implement write_event()")
