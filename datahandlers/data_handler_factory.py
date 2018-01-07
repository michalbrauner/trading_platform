from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from datahandlers.oanda_data_handler import OandaDataHandler
from oanda.stream_factory import StreamFactory
from datahandlers.oanda_data_handler import DataHandler
from core.configuration import Configuration

try:
    import Queue as queue
except ImportError:
    import queue


class DataHandlerFactory:
    def __init__(self):
        pass

    def create_from_settings(self, configuration, events, symbol_list):
        # type: (Configuration, queue.Queue, []) -> DataHandler

        if configuration.data_handler_name == HistoricCSVDataHandler:
            return self.create_historic_csv_data_handler(events, symbol_list,
                                                         configuration.get_option(Configuration.OPTION_CSV_DIR))

        if configuration.data_handler_name == OandaDataHandler:
            return self.create_oanda_data_handler(events, symbol_list,
                                                  configuration.get_option(Configuration.OPTION_ACCOUNT_ID),
                                                  configuration.get_option(Configuration.OPTION_ACCESS_TOKEN),
                                                  configuration.get_option(Configuration.OPTION_TIMEFRAME))

        raise Exception('Unknown DataHandler for {}'.format(configuration.data_handler_name))

    def create_historic_csv_data_handler(self, events, symbol_list, csv_dir):
        # type: (queue.Queue, [], str) -> DataHandler

        return HistoricCSVDataHandler(events, csv_dir, symbol_list)

    def create_oanda_data_handler(self, events, symbol_list, account_id, access_token, timeframe):
        # type: (queue.Queue, [], str, str, str) -> DataHandler

        stream_factory = StreamFactory()
        stream = stream_factory.create(account_id, access_token, symbol_list)

        return OandaDataHandler(events, symbol_list, stream, timeframe)
