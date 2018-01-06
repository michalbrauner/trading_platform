from datahandlers.data_handler import DataHandler
from executionhandlers.execution_handler import ExecutionHandler


class Configuration(object):

    OPTION_CSV_DIR = 'csv_dir'
    OPTION_ACCOUNT_ID = 'account_id'
    OPTION_ACCESS_TOKEN = 'access_token'

    def __init__(self, data_handler_name, execution_handler_name):
        """

        :type data_handler_name: object
        :type execution_handler_name: object
        """
        self.data_handler_name = data_handler_name
        self.execution_handler_name = execution_handler_name

        self.options = {}

    def set_option(self, option, value):
        """

        :type option: str
        :type value: str
        """

        self.options[option] = value

    def get_option(self, option):
        """

        :type option: str
        :return mixed
        """

        return self.options[option]
