from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from datahandlers.oanda_data_handler import OandaDataHandler
from oanda.stream_factory import StreamFactory
from datahandlers.oanda_data_handler import DataHandler
from core.configuration import Configuration
from oanda.instrument_api_client import InstrumentApiClient
from typing import Dict
from datahandlers.bars_provider.oanda_bars_provider_api import OandaBarsProviderApi
from timeframe.timeframe import TimeFrame
from loggers.logger import Logger

try:
    import Queue as queue
except ImportError:
    import queue


class DataHandlerFactory:
    @staticmethod
    def create_from_settings(configuration: Configuration, events_per_symbol: Dict[str, queue.Queue],
                             symbol_list: list, logger: Logger) -> DataHandler:

        if configuration.data_handler_name == HistoricCSVDataHandler:
            csv_dir = Configuration.OPTION_CSV_DIR
            return DataHandlerFactory.create_historic_csv_data_handler(events_per_symbol, symbol_list,
                                                                       configuration.get_option(csv_dir))

        if configuration.data_handler_name == OandaDataHandler:
            bars_from_history = Configuration.OPTION_NUMBER_OF_BARS_PRELOAD_FROM_HISTORY
            access_token = Configuration.OPTION_ACCESS_TOKEN
            timeframe = Configuration.OPTION_TIMEFRAME

            return DataHandlerFactory.create_oanda_data_handler(events_per_symbol, symbol_list,
                                                                configuration.get_option(access_token),
                                                                configuration.get_option(timeframe),
                                                                int(configuration.get_option(bars_from_history)),
                                                                logger)

        raise Exception('Unknown DataHandler for {}'.format(configuration.data_handler_name))

    @staticmethod
    def create_historic_csv_data_handler(events_per_symbol: Dict[str, queue.Queue],
                                         symbol_list: list, csv_dir: str) -> DataHandler:
        return HistoricCSVDataHandler(events_per_symbol, csv_dir, symbol_list)

    @staticmethod
    def create_oanda_data_handler(events_per_symbol: Dict[str, queue.Queue], symbol_list: list, access_token: str,
                                  time_frame: str, number_of_bars_preload_from_history: int,
                                  logger: Logger) -> DataHandler:
        instrument_api_client = InstrumentApiClient(access_token)

        bars_provider = OandaBarsProviderApi(symbol_list, instrument_api_client, TimeFrame(time_frame), logger)

        return OandaDataHandler(events_per_symbol, symbol_list, bars_provider, instrument_api_client, time_frame,
                                number_of_bars_preload_from_history)
