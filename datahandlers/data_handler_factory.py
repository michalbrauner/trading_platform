from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from datahandlers.oanda_data_handler import OandaDataHandler
from oanda.stream_factory import StreamFactory
from datahandlers.oanda_data_handler import DataHandler
from core.configuration import Configuration
from oanda.instrument_api_client import InstrumentApiClient
from typing import Dict

try:
    import Queue as queue
except ImportError:
    import queue


class DataHandlerFactory:
    def __init__(self):
        pass

    def create_from_settings(self, configuration: Configuration, events: queue.Queue,
                             events_per_symbol: Dict[str, queue.Queue], symbol_list: list) -> DataHandler:

        if configuration.data_handler_name == HistoricCSVDataHandler:
            return self.create_historic_csv_data_handler(events, events_per_symbol, symbol_list,
                                                         configuration.get_option(Configuration.OPTION_CSV_DIR))

        if configuration.data_handler_name == OandaDataHandler:
            return self.create_oanda_data_handler(events, events_per_symbol, symbol_list,
                                                  configuration.get_option(Configuration.OPTION_ACCOUNT_ID),
                                                  configuration.get_option(Configuration.OPTION_ACCESS_TOKEN),
                                                  configuration.get_option(Configuration.OPTION_TIMEFRAME),
                                                  int(configuration.get_option(
                                                      Configuration.OPTION_NUMBER_OF_BARS_PRELOAD_FROM_HISTORY)))

        raise Exception('Unknown DataHandler for {}'.format(configuration.data_handler_name))

    def create_historic_csv_data_handler(self, events: queue.Queue, events_per_symbol: Dict[str, queue.Queue],
                                         symbol_list: list, csv_dir: str) -> DataHandler:

        return HistoricCSVDataHandler(events, events_per_symbol, csv_dir, symbol_list)

    def create_oanda_data_handler(self, events: queue.Queue, events_per_symbol: Dict[str, queue.Queue], symbol_list: list,
                                  account_id: str, access_token: str, timeframe: str,
                                  number_of_bars_preload_from_history: int) -> DataHandler:
        stream_factory = StreamFactory()
        stream = stream_factory.create(account_id, access_token, symbol_list)

        instrument_api_client = InstrumentApiClient(access_token)

        return OandaDataHandler(events, events_per_symbol, symbol_list, stream, instrument_api_client, timeframe,
                                number_of_bars_preload_from_history)
