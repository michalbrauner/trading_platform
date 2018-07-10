from core.portfolio import Portfolio

from core.trading import Trading
from core.configuration import Configuration
from datahandlers.data_handler_factory import DataHandlerFactory
from executionhandlers.oanda_execution import OandaExecutionHandler
from executionhandlers.execution_handler_factory import ExecutionHandlerFactory
from strategies.pinbar_notifications import PinBarNotificationsStrategy
from positionsizehandlers.fixed_position_size import FixedPositionSize
from loggers.text_logger import TextLogger
import os
from datahandlers.oanda_data_handler import OandaDataHandler


def get_strategy():
    return PinBarNotificationsStrategy


def main():

    strategy = get_strategy()
    args_namespace = strategy.create_argument_parser(False).parse_args()

    events_log_file = '{}/events.log'.format(args_namespace.output_directory)

    strategy_params = strategy.get_strategy_params(args_namespace)
    strategy_params['send_notifications'] = True

    configuration = Configuration(data_handler_name=OandaDataHandler, execution_handler_name=OandaExecutionHandler)
    configuration.set_option(Configuration.OPTION_NUMBER_OF_BARS_PRELOAD_FROM_HISTORY, 0)

    configuration.set_option(Configuration.OPTION_ACCOUNT_ID, os.environ.get('OANDA_API_ACCOUNT_ID'))
    configuration.set_option(Configuration.OPTION_ACCESS_TOKEN, os.environ.get('OANDA_API_ACCESS_TOKEN'))
    configuration.set_option(Configuration.OPTION_TIMEFRAME, args_namespace.time_frame)

    trading = Trading(args_namespace.output_directory, list(args_namespace.symbols), 0,
                      configuration, DataHandlerFactory(), ExecutionHandlerFactory(), Portfolio, strategy,
                      FixedPositionSize(0.01), TextLogger(events_log_file), [Trading.LOG_TYPE_EVENTS], strategy_params,
                      'equity.csv', 'trades.csv')

    trading.run()
    trading.print_performance()


if __name__ == "__main__":
    main()
