import getopt, sys

from core.portfolio import Portfolio

from core.backtest import Backtest
from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from executionhandlers.simulated_execution import SimulatedExecutionHandler
from strategies.mac import MovingAverageCrossStrategy
from positionsizehandlers.fixed_position_size import FixedPositionSize
from loggers.text_logger import TextLogger
import args_parser
import csv, os


def print_usage():
    print('Usage: python optimize_mac.py -d <data_directory> -s <symbols> -c <initial_capital_usd> -b <start_datetime>'
          + ' -o <output_directory> --short-window-min <int> --short-window-max <int> --short-window-step <int>'
          + ' --long-window-min <int> --long-window-max <int> --long-window-step <int>'
  )
    print('  -> list of symbols separated by coma')
    print('  -> start_datetime is in \'yyyy-mm-ddThh:mm:ss\' format')


def get_settings(argv):

    if len(argv) == 0:
        print_usage()
        exit(1)

    long_opts = ['short_window_min=', 'short_window_max=', 'short_window_step=',
                 'long_window_min=', 'long_window_max=', 'long_window_step=']

    settings = args_parser.get_basic_settings(argv, long_opts)

    if settings['print_help']:
        print_usage()
        exit(0)

    opts, args = getopt.getopt(argv, args_parser.BASIC_ARGS, long_opts)

    for opt, arg in opts:
        if opt == '--short_window_min':
            settings['short_window_min'] = arg
        elif opt == '--short_window_max':
            settings['short_window_max'] = arg
        elif opt == '--short_window_step':
            settings['short_window_step'] = arg
        elif opt == '--long_window_min':
            settings['long_window_min'] = arg
        elif opt == '--long_window_max':
            settings['long_window_max'] = arg
        elif opt == '--long_window_step':
            settings['long_window_step'] = arg

    args_parser.validate_settings_is_number_and_set_to_int(settings, 'short_window_min')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'short_window_max')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'short_window_step')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'long_window_min')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'long_window_max')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'long_window_step')

    return settings


def main(argv):

    settings = get_settings(argv)

    heartbeat = 0

    csv_file = open('{}/optimization.csv'.format(settings['output_directory']), 'wb')
    csv_file_writer = csv.writer(csv_file, delimiter=',')
    csv_file_writer.writerow(['Short window', 'Long window', 'Total Return', 'Sharpe Ratio', 'Max Drawdown', 'Drawdown Duration'])

    short_window_current = settings['short_window_min']
    short_window_max = settings['short_window_max']
    short_window_step = settings['short_window_step']

    long_window_max = settings['long_window_max']
    long_window_step = settings['long_window_step']

    while short_window_current <= short_window_max:
        long_window_current = settings['long_window_min']

        while long_window_current <= long_window_max:
            events_log_file = '{}/events_{}_{}.log'.format(settings['output_directory'], short_window_current,
                                                           long_window_current)
            equity_filename = 'equity_{}_{}.csv'.format(short_window_current, long_window_current)

            print('Running backtest for: short_window=%d, long_window=%d' % (short_window_current, long_window_current))

            stats = run_backtest_instance(settings, events_log_file, heartbeat, short_window_current,
                                          long_window_current, equity_filename)

            os.remove(events_log_file)
            os.remove('{}/{}'.format(settings['output_directory'], equity_filename))

            csv_file_writer.writerow(
                [short_window_current, long_window_current, stats.get_total_return(), stats.get_sharpe_ratio(),
                 stats.get_max_drawdown(),
                 stats.get_drawdown_duration()])

            print('')

            long_window_current = long_window_current + long_window_step

        short_window_current = short_window_current + short_window_step

    csv_file.close()


def run_backtest_instance(settings, events_log_file, heartbeat, short_window, long_window, equity_filename):
    strategy_params = dict(short_window=short_window, long_window=long_window)

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
        equity_filename
    )
    backtest.simulate_trading()

    return backtest.stats


if __name__ == "__main__":
    main(sys.argv[1:])
