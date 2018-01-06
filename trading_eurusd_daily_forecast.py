import sys, getopt
from sys import settrace

from core.portfolio import Portfolio

from core.trading import Trading
from datahandlers.data_handler_factory import DataHandlerFactory
from executionhandlers.oanda_execution import OandaExecutionHandler
from executionhandlers.execution_handler_factory import ExecutionHandlerFactory
import strategies.eurusd_daily_forecast as eurusd_daily_forecast
from positionsizehandlers.fixed_position_size import FixedPositionSize
from loggers.text_logger import TextLogger
import args_parser
import os
from datahandlers.oanda_data_handler import OandaDataHandler


def get_strategy_configuration_tools_long_options():
    return eurusd_daily_forecast.EurUsdDailyForecastStrategyConfigurationTools.get_long_opts()


def get_strategy_configuration_tools(settings):
    return eurusd_daily_forecast.EurUsdDailyForecastStrategyConfigurationTools(settings)


def get_strategy():
    return eurusd_daily_forecast.EurUsdDailyForecastStrategy


def print_usage():
    print('Usage: python trading.py -s <symbols> -o <output_directory> --stop_loss=<int> --take_profit=<int>')
    print('  -> list of symbols separated by coma')


def get_settings(argv):
    if len(argv) == 0:
        print_usage()
        exit(1)

    long_opts = get_strategy_configuration_tools_long_options()

    settings = args_parser.get_basic_settings(argv, long_opts)

    configuration_tools = get_strategy_configuration_tools(settings)

    if settings['print_help']:
        print_usage()
        exit(0)

    settings['stop_loss'] = None
    settings['take_profit'] = None

    opts, args = getopt.getopt(argv, args_parser.BASIC_ARGS, long_opts)

    for opt, arg in opts:
        if opt == '--stop_loss':
            settings['stop_loss'] = arg
        elif opt == '--take_profit':
            settings['take_profit'] = arg
        else:
            settings = configuration_tools.use_argument_if_valid(opt, arg)

    args_parser.validate_settings_is_number_and_set_to_int(settings, 'stop_loss', False)
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'take_profit', False)
    configuration_tools.valid_arguments_and_convert_if_necessarily()

    return settings


def main(argv):
    settings = get_settings(argv)

    heartbeat = 0

    events_log_file = '{}/events.log'.format(settings['output_directory'])

    strategy_params = dict(stop_loss_pips=settings['stop_loss'], take_profit_pips=settings['take_profit'])
    strategy_params.update(get_strategy_configuration_tools(settings).get_strategy_params())

    account_id = os.environ.get('OANDA_API_ACCOUNT_ID')
    access_token = os.environ.get('OANDA_API_ACCESS_TOKEN')

    trading = Trading(settings['output_directory'], settings['symbols'], settings['initial_capital_usd'], heartbeat,
                      settings['start_date'], {
                          'data_handler_name': OandaDataHandler,
                          'execution_handler_name': OandaExecutionHandler,
                          'account_id': account_id,
                          'access_token': access_token
                      }, DataHandlerFactory(), ExecutionHandlerFactory(), Portfolio, get_strategy(),
                      FixedPositionSize(0.5),
                      TextLogger(events_log_file), [Trading.LOG_TYPE_EVENTS], strategy_params, 'equity.csv')

    trading.run()
    trading.print_performance()


if __name__ == "__main__":
    main(sys.argv[1:])
