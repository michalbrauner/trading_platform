import sys, getopt

from core.portfolio import Portfolio

from core.trading import Trading
from core.configuration import Configuration
from datahandlers.data_handler_factory import DataHandlerFactory
from executionhandlers.oanda_execution import OandaExecutionHandler
from executionhandlers.execution_handler_factory import ExecutionHandlerFactory
import strategies.mac as mac
from positionsizehandlers.fixed_position_size import FixedPositionSize
from loggers.text_logger import TextLogger
import args_parser_trading as args_parser
import os
from datahandlers.oanda_data_handler import OandaDataHandler
from timeframe.timeframe import TimeFrame


def get_strategy_configuration_tools_long_options():
    return mac.MovingAverageCrossStrategyConfigurationTools.get_long_opts()


def get_strategy_configuration_tools(settings):
    return mac.MovingAverageCrossStrategyConfigurationTools(settings)


def get_strategy():
    return mac.MovingAverageCrossStrategy


def print_usage():
    print('Usage: python trading_eurusd_mac.py -s <symbols> -o <output_directory> '
          + ' --stop_loss=<int> --take_profit=<int>'
          + ' --short_window=<int> --long_window=<int>')


def get_settings(argv):
    if len(argv) == 0:
        print_usage()
        exit(1)

    long_opts = ['stop_loss=', 'take_profit='] + get_strategy_configuration_tools_long_options()

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

    configuration = Configuration(data_handler_name=OandaDataHandler,
                                  execution_handler_name=OandaExecutionHandler)

    configuration.set_option(Configuration.OPTION_ACCOUNT_ID, os.environ.get('OANDA_API_ACCOUNT_ID'))
    configuration.set_option(Configuration.OPTION_ACCESS_TOKEN, os.environ.get('OANDA_API_ACCESS_TOKEN'))
    configuration.set_option(Configuration.OPTION_TIMEFRAME, TimeFrame.TIMEFRAME_M1)

    trading = Trading(settings['output_directory'], settings['symbols'], heartbeat,
                      configuration, DataHandlerFactory(), ExecutionHandlerFactory(), Portfolio, get_strategy(),
                      FixedPositionSize(0.5),
                      TextLogger(events_log_file), [Trading.LOG_TYPE_EVENTS], strategy_params, 'equity.csv')

    trading.run()
    trading.print_performance()


if __name__ == "__main__":
    main(sys.argv[1:])
