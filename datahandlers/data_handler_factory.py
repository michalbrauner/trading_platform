from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from datahandlers.oanda_data_handler import OandaDataHandler
from oanda.stream_factory import StreamFactory
from datahandlers.oanda_data_handler import DataHandler
from core.configuration import Configuration
from oanda.instrument_api_client import InstrumentApiClient

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
                                                  configuration.get_option(Configuration.OPTION_TIMEFRAME),
                                                  configuration.get_option(
                                                      Configuration.OPTION_NUMBER_OF_BARS_PRELOAD_FROM_HISTORY))

        raise Exception('Unknown DataHandler for {}'.format(configuration.data_handler_name))

    def create_historic_csv_data_handler(self, events, symbol_list, csv_dir):
        # type: (queue.Queue, [], str) -> DataHandler

        return HistoricCSVDataHandler(events, csv_dir, symbol_list)

    def create_oanda_data_handler(self, events, symbol_list, account_id, access_token, timeframe,
                                  number_of_bars_preload_from_history):
        # type: (queue.Queue, [], str, str, str, int) -> DataHandler

        stream_factory = StreamFactory()
        stream = stream_factory.create(account_id, access_token, symbol_list)

        instrument_api_client = InstrumentApiClient(access_token)

        return OandaDataHandler(events, symbol_list, stream, instrument_api_client, timeframe,
                                number_of_bars_preload_from_history)
