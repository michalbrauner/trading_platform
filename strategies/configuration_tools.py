from abc import ABCMeta, abstractmethod


class ConfigurationTools(object):
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def get_long_opts():
        raise NotImplementedError("Should implement get_long_opts()")

    @abstractmethod
    def get_strategy_params(self):
        raise NotImplementedError("Should implement get_strategy_params()")

    @abstractmethod
    def use_argument_if_valid(self, option, argument_value):
        raise NotImplementedError("Should implement use_argument_if_valid()")

    @abstractmethod
    def set_default_values(self):
        raise NotImplementedError("Should implement set_default_values()")

    @abstractmethod
    def valid_arguments_and_convert_if_necessarily(self):
        raise NotImplementedError("Should implement valid_arguments_and_convert_if_necessarily()")
