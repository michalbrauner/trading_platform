import sys, getopt
from sys import settrace

from core.portfolio import Portfolio

from core.backtest import Backtest
from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from executionhandlers.simulated_execution import SimulatedExecutionHandler
from strategies.mac import MovingAverageCrossStrategy
from positionsizehandlers.fixed_position_size import FixedPositionSize
from loggers.text_logger import TextLogger
import args_parser


def print_usage():
    print('Usage: python backtest.py -d <data_directory> -s <symbols> -c <initial_capital_usd> -b <start_datetime>'
          + ' -o <output_directory> --short_window=<int> --long_window=<int> --stop_loss=<int> --take_profit=<int>')
    print('  -> list of symbols separated by coma')
    print('  -> start_datetime is in \'yyyy-mm-ddThh:mm:ss\' format')


def get_settings(argv):

    if len(argv) == 0:
        print_usage()
        exit(1)

    long_opts = ['short_window=', 'long_window=', 'stop_loss=', 'take_profit=']

    settings = args_parser.get_basic_settings(argv, long_opts)

    if settings['print_help']:
        print_usage()
        exit(0)

    settings['stop_loss'] = None
    settings['take_profit'] = None

    opts, args = getopt.getopt(argv, args_parser.BASIC_ARGS, long_opts)

    for opt, arg in opts:
        if opt == '--short_window':
            settings['short_window'] = arg
        elif opt == '--long_window':
            settings['long_window'] = arg
        elif opt == '--stop_loss':
            settings['stop_loss'] = arg
        elif opt == '--take_profit':
            settings['take_profit'] = arg

    args_parser.validate_settings_is_number_and_set_to_int(settings, 'short_window')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'long_window')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'stop_loss', False)
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'take_profit', False)

    return settings


CSV_DIR = 'd:\\forex_backtesting\\backtest_data\\M15\\test_month\\'


def main(argv):

    settings = get_settings(argv)

    heartbeat = 0

    events_log_file = '{}/events.log'.format(settings['output_directory'])

    strategy_params = dict(
        short_window=settings['short_window'],
        long_window=settings['long_window'],
        stop_loss_pips=settings['stop_loss'],
        take_profit_pips=settings['take_profit']
    )

    backtest = Backtest(
        settings['data_directory'],
        settings['output_directory'],
        settings['symbols'],
        settings['initial_capital_usd'],
        heartbeat,
        settings['start_date'],
        HistoricCSVDataHandler,
        SimulatedExecutionHandler,
        Portfolio,
        MovingAverageCrossStrategy,
        FixedPositionSize(0.5),
        TextLogger(events_log_file),
        [Backtest.LOG_TYPE_EVENTS],
        strategy_params,
        'equity.csv'
    )

    backtest.simulate_trading()
    backtest.print_performance()


if __name__ == "__main__":
    main(sys.argv[1:])
