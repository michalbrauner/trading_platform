from datahandlers.data_handler import DataHandler
from executionhandlers.execution_handler import ExecutionHandler


class Configuration(object):

    OPTION_CSV_DIR = 'csv_dir'
    OPTION_ACCOUNT_ID = 'account_id'
    OPTION_ACCESS_TOKEN = 'access_token'
    OPTION_TIMEFRAME = 'timeframe'
    OPTION_NUMBER_OF_BARS_PRELOAD_FROM_HISTORY = 'number_of_bars_preload_from_history'

    def __init__(self, data_handler_name: object, execution_handler_name: object):
        self.data_handler_name = data_handler_name
        self.execution_handler_name = execution_handler_name

        self.options = {}

    def set_option(self, option: str, value: str):
        self.options[option] = value

    def get_option(self, option: str) -> str:
        return self.options[option]
