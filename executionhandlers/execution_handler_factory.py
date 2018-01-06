from executionhandlers.simulated_execution import SimulatedExecutionHandler
from executionhandlers.oanda_execution import OandaExecutionHandler
from executionhandlers.execution_handler import ExecutionHandler
from core.configuration import Configuration
from datahandlers.data_handler import DataHandler

try:
    import Queue as queue
except ImportError:
    import queue


class ExecutionHandlerFactory:
    def __init__(self):
        pass

    def create_from_settings(self, configuration, data_handler, events):
        # type: (Configuration, DataHandler, queue.Queue) -> ExecutionHandler

        if configuration.execution_handler_name == SimulatedExecutionHandler:
            return self.create_historic_csv_data_handler(data_handler, events)

        if configuration.execution_handler_name == OandaExecutionHandler:
            return self.create_oanda_data_handler(data_handler, events,
                                                  configuration.get_option(Configuration.OPTION_ACCOUNT_ID),
                                                  configuration.get_option(Configuration.OPTION_ACCESS_TOKEN))

        raise Exception('Unknown ExecutionHandler for {}'.format(configuration.execution_handler_name))

    def create_historic_csv_data_handler(self, data_handler, events):
        # type: (DataHandler, queue.Queue) -> ExecutionHandler

        return SimulatedExecutionHandler(data_handler, events)

    def create_oanda_data_handler(self, data_handler, events, account_id, access_token):
        # type: (DataHandler, queue.Queue, str, str) -> ExecutionHandler

        return OandaExecutionHandler(data_handler, events, account_id, access_token)
