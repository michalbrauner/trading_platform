from executionhandlers.simulated_execution import SimulatedExecutionHandler
from executionhandlers.oanda_execution import OandaExecutionHandler
from executionhandlers.execution_handler import ExecutionHandler
from core.configuration import Configuration
from datahandlers.data_handler import DataHandler
from loggers.logger import Logger

try:
    import Queue as queue
except ImportError:
    import queue


class ExecutionHandlerFactory:
    def __init__(self):
        pass

    @staticmethod
    def create_from_settings(configuration, data_handler, events, logger):
        # type: (Configuration, DataHandler, queue.Queue, logger) -> ExecutionHandler

        if configuration.execution_handler_name == SimulatedExecutionHandler:
            return ExecutionHandlerFactory.create_historic_csv_execution_handler(data_handler, events)

        if configuration.execution_handler_name == OandaExecutionHandler:
            return ExecutionHandlerFactory.create_oanda_execution_handler(data_handler, events,
                                                                          configuration.get_option(
                                                                              Configuration.OPTION_ACCOUNT_ID),
                                                                          configuration.get_option(
                                                                              Configuration.OPTION_ACCESS_TOKEN),
                                                                          logger)

        raise Exception('Unknown ExecutionHandler for {}'.format(configuration.execution_handler_name))

    @staticmethod
    def create_historic_csv_execution_handler(data_handler, events):
        # type: (DataHandler, queue.Queue) -> ExecutionHandler

        return SimulatedExecutionHandler(data_handler, events)

    @staticmethod
    def create_oanda_execution_handler(data_handler, events, account_id, access_token, logger):
        # type: (DataHandler, queue.Queue, str, str, Logger) -> ExecutionHandler

        return OandaExecutionHandler(data_handler, events, account_id, access_token, logger)
