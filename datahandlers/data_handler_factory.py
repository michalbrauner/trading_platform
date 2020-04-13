from datahandlers.bars_provider.zmq_bars_provider_from_tick_data import ZmqBarsProviderFromTickData
from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from datahandlers.oanda_data_handler import OandaDataHandler
from datahandlers.zmq_data_handler import ZmqDataHandler
from datahandlers.oanda_data_handler import DataHandler
from core.configuration import Configuration
from oanda.instrument_api_client import InstrumentApiClient
from typing import Dict
from datahandlers.bars_provider.oanda_bars_provider_api import OandaBarsProviderApi
from timeframe.timeframe import TimeFrame
from loggers.logger import Logger
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
            time_frame = Configuration.OPTION_TIMEFRAME

            return DataHandlerFactory.create_oanda_data_handler(events_per_symbol, symbol_list,
                                                                configuration.get_option(access_token),
                                                                configuration.get_option(time_frame),
                                                                int(configuration.get_option(bars_from_history)),
                                                                logger)

        if configuration.data_handler_name == ZmqDataHandler:
            time_frame = Configuration.OPTION_TIMEFRAME

            return DataHandlerFactory.create_zmq_data_handler(events_per_symbol, symbol_list,
                                                              configuration.get_option(time_frame), logger)

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
        instrument_api_client.start_process_requests()

        bars_provider = OandaBarsProviderApi(symbol_list, instrument_api_client, TimeFrame(time_frame), logger)

        return OandaDataHandler(events_per_symbol, symbol_list, bars_provider, instrument_api_client, time_frame,
                                number_of_bars_preload_from_history)

    @staticmethod
    def create_zmq_data_handler(events_per_symbol: Dict[str, queue.Queue], symbol_list: list, time_frame: str,
                                logger: Logger) -> DataHandler:
        bars_provider = ZmqBarsProviderFromTickData(symbol_list, TimeFrame(time_frame), logger)

        return ZmqDataHandler(events_per_symbol, symbol_list, bars_provider, time_frame)
