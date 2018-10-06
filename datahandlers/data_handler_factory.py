from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from datahandlers.oanda_data_handler import OandaDataHandler
from oanda.stream_factory import StreamFactory
from datahandlers.oanda_data_handler import DataHandler
from core.configuration import Configuration
from oanda.instrument_api_client import InstrumentApiClient
from typing import Dict
from datahandlers.bars_provider.oanda_bars_provider_api import OandaBarsProviderApi
from timeframe.timeframe import TimeFrame

try:
    import Queue as queue
except ImportError:
    import queue


class DataHandlerFactory:
    def __init__(self):
        pass

    def create_from_settings(self, configuration: Configuration, events_per_symbol: Dict[str, queue.Queue],
                             symbol_list: list) -> DataHandler:

        if configuration.data_handler_name == HistoricCSVDataHandler:
            return DataHandlerFactory.create_historic_csv_data_handler(events_per_symbol, symbol_list,
                                                                       configuration.get_option(
                                                                           Configuration.OPTION_CSV_DIR))

        if configuration.data_handler_name == OandaDataHandler:
            bars_from_history = Configuration.OPTION_NUMBER_OF_BARS_PRELOAD_FROM_HISTORY

            return DataHandlerFactory.create_oanda_data_handler(events_per_symbol, symbol_list,
                                                                configuration.get_option(
                                                                    Configuration.OPTION_ACCOUNT_ID),
                                                                configuration.get_option(
                                                                    Configuration.OPTION_ACCESS_TOKEN),
                                                                configuration.get_option(
                                                                    Configuration.OPTION_TIMEFRAME),
                                                                int(configuration.get_option(bars_from_history)))

        raise Exception('Unknown DataHandler for {}'.format(configuration.data_handler_name))

    @staticmethod
    def create_historic_csv_data_handler(events_per_symbol: Dict[str, queue.Queue],
                                         symbol_list: list, csv_dir: str) -> DataHandler:

        return HistoricCSVDataHandler(events_per_symbol, csv_dir, symbol_list)

    @staticmethod
    def create_oanda_data_handler(events_per_symbol: Dict[str, queue.Queue], symbol_list: list,
                                  account_id: str, access_token: str, time_frame: str,
                                  number_of_bars_preload_from_history: int) -> DataHandler:
        stream_factory = StreamFactory()
        streams = []

        for symbol in symbol_list:
            streams.append(stream_factory.create(account_id, access_token, [symbol]))

        instrument_api_client = InstrumentApiClient(access_token)

        bars_provider = OandaBarsProviderApi(symbol_list, instrument_api_client, TimeFrame(time_frame))

        return OandaDataHandler(events_per_symbol, symbol_list, bars_provider, instrument_api_client, time_frame,
                                number_of_bars_preload_from_history)
