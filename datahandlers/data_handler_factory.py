from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from datahandlers.oanda_data_handler import OandaDataHandler
from oanda.stream_factory import StreamFactory
from datahandlers.oanda_data_handler import DataHandler

try:
    import Queue as queue
except ImportError:
    import queue


class DataHandlerFactory:
    def __init__(self):
        pass

    def create_from_settings(self, settings, events, symbol_list):
        # type: ({}, queue.Queue, []) -> DataHandler

        if settings['data_handler_name'] == HistoricCSVDataHandler:
            return self.create_historic_csv_data_handler(events, symbol_list, settings['csv_dir'])

        if settings['data_handler_name'] == OandaDataHandler:
            return self.create_oanda_data_handler(events, symbol_list, settings['account_id'], settings['access_token'])

        raise Exception('Unknown DataHandler for {}'.format(settings['data_handler_name']))

    def create_historic_csv_data_handler(self, events, symbol_list, csv_dir):
        # type: (queue.Queue, [], str) -> DataHandler

        return HistoricCSVDataHandler(events, csv_dir, symbol_list)

    def create_oanda_data_handler(self, events, symbol_list, account_id, access_token):
        # type: (queue.Queue, [], str, str) -> DataHandler

        stream_factory = StreamFactory()
        stream = stream_factory.create(account_id, access_token, symbol_list)

        return OandaDataHandler(events, symbol_list, stream)
