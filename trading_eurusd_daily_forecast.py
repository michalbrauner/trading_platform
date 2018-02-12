from core.portfolio import Portfolio

from core.trading import Trading
from core.configuration import Configuration
from datahandlers.data_handler_factory import DataHandlerFactory
from executionhandlers.oanda_execution import OandaExecutionHandler
from executionhandlers.execution_handler_factory import ExecutionHandlerFactory
import strategies.eurusd_daily_forecast as eurusd_daily_forecast
from positionsizehandlers.fixed_position_size import FixedPositionSize
from loggers.text_logger import TextLogger
import os
from datahandlers.oanda_data_handler import OandaDataHandler


def get_strategy():
    return eurusd_daily_forecast.EurUsdDailyForecastStrategy


def main():

    strategy = get_strategy()
    args_namespace = strategy.create_argument_parser().parse_args()
    strategy_params_special = strategy.get_strategy_params(args_namespace)

    events_log_file = '{}/events.log'.format(args_namespace.output_directory)

    strategy_params = dict(stop_loss_pips=args_namespace.stop_loss, take_profit_pips=args_namespace.take_profit)
    strategy_params.update(strategy_params_special)

    configuration = Configuration(data_handler_name=OandaDataHandler,
                                  execution_handler_name=OandaExecutionHandler)
    configuration.set_option(Configuration.OPTION_ACCOUNT_ID, os.environ.get('OANDA_API_ACCOUNT_ID'))
    configuration.set_option(Configuration.OPTION_ACCESS_TOKEN, os.environ.get('OANDA_API_ACCESS_TOKEN'))

    trading = Trading(args_namespace.output_directory, args_namespace.symbols, 0,
                      configuration, DataHandlerFactory(), ExecutionHandlerFactory(), Portfolio, strategy,
                      FixedPositionSize(0.01), TextLogger(events_log_file), [Trading.LOG_TYPE_EVENTS], strategy_params,
                      'equity.csv')

    trading.run()
    trading.print_performance()


if __name__ == "__main__":
    main()
