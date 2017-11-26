import getopt, sys

from core.portfolio import Portfolio

from core.backtest import Backtest
from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from executionhandlers.simulated_execution import SimulatedExecutionHandler
from strategies.mac import MovingAverageCrossStrategy
from strategies.eurusd_daily_forecast import EurUsdDailyForecastStrategy
from positionsizehandlers.fixed_position_size import FixedPositionSize
from loggers.text_logger import TextLogger
import args_parser
import csv, os
import itertools
import string


def print_usage():
    print('Usage: python optimize_eurusd_daily_forecast.py -d <data_directory> -s <symbols> -c <initial_capital_usd> '
          + ' -b <start_datetime> -o <output_directory> --sl_min <int> --sl_max <int> --sl_step <int>'
          + ' --tp_min <int> --tp_max <int> --tp_step <int>'
          + ' --short-window-min <int> --short-window-max <int> --short-window-step <int> '
          + ' --long-window-min <int> --long-window-max <int> --long-window-step <int> '
          + ' --trained_model_file <string> '
  )
    print('  -> list of symbols separated by coma')
    print('  -> start_datetime is in \'yyyy-mm-ddThh:mm:ss\' format')


def get_settings(argv):

    if len(argv) == 0:
        print_usage()
        exit(1)

    long_opts = [
        'sl_min=', 'sl_max=', 'sl_step=', 'tp_min=', 'tp_max=', 'tp_step=',
        'short_window_min=', 'short_window_max=', 'short_window_step=',
        'long_window_min=', 'long_window_max=', 'long_window_step=',
        'trained_model_file='
    ]

    settings = args_parser.get_basic_settings(argv, long_opts)

    if settings['print_help']:
        print_usage()
        exit(0)

    opts, args = getopt.getopt(argv, args_parser.BASIC_ARGS, long_opts)

    for opt, arg in opts:
        settings_name = string.replace(opt, '--', '')
        settings[settings_name] = arg

    validate_as_number = ['sl_min', 'sl_max', 'sl_step', 'tp_min', 'tp_max', 'tp_step',
                          'short_window_min', 'short_window_max', 'short_window_step', 'long_window_min',
                          'long_window_max', 'long_window_step']

    for argument in validate_as_number:
        args_parser.validate_settings_is_number_and_set_to_int(settings, argument)

    if os.path.isfile(settings['trained_model_file']) is False:
        raise Exception('trained_model_file does not exist')

    return settings


def main(argv):

    settings = get_settings(argv)

    heartbeat = 0

    csv_file = open('{}/optimization.csv'.format(settings['output_directory']), 'wb')
    csv_file_writer = csv.writer(csv_file, delimiter=',')
    csv_file_writer.writerow(['SL', 'TP', 'SMA_short', 'SMA_long', 'Total Return',
                              'Sharpe Ratio', 'Max Drawdown', 'Drawdown Duration'])

    values_to_try = [
        range(settings['sl_min'], settings['sl_max'] + 1, settings['sl_step']),
        range(settings['tp_min'], settings['tp_max'] + 1, settings['tp_step']),
        range(settings['short_window_min'], settings['short_window_max'] + 1, settings['short_window_step']),
        range(settings['long_window_min'], settings['long_window_max'] + 1, settings['long_window_step']),
    ]

    for parameters in itertools.product(*values_to_try):
        run_and_log_optimization_instance(csv_file_writer, heartbeat, settings, parameters[0], parameters[1],
                                          parameters[2], parameters[3])

    csv_file.close()


def run_and_log_optimization_instance(csv_file_writer, heartbeat, settings, sl, tp, short_window, long_window):

    events_log_file = '{}/events_{}_{}.log'.format(settings['output_directory'], sl, tp)

    equity_filename = 'equity_{}_{}.csv'.format(sl, tp)

    print('Running backtest for: SL=%d, TP=%d, SMA_short=%d, SMA_long=%d' % (sl, tp, short_window, long_window))

    stats = run_backtest_instance(settings, events_log_file, heartbeat, sl, tp, short_window, long_window,
                                  equity_filename, settings['trained_model_file'])

    files_to_remove = [
        events_log_file,
        '{}/{}'.format(settings['output_directory'], equity_filename)
    ]

    for file_name in files_to_remove:
        if os.path.isfile(file_name):
            os.remove(file_name)

    csv_file_writer.writerow(
        [
            sl,
            tp,
            short_window,
            long_window,
            stats.get_total_return(),
            stats.get_sharpe_ratio(),
            stats.get_max_drawdown(),
            stats.get_drawdown_duration()
        ]
    )

    print('')


def run_backtest_instance(settings, events_log_file, heartbeat, sl, tp, short_window, long_window, equity_filename,
                          trained_model_file):

    strategy_params = dict(
        stop_loss_pips=sl,
        take_profit_pips=tp,
        trained_model_file=trained_model_file,
        sma_short_period=short_window,
        sma_long_period=long_window
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
        EurUsdDailyForecastStrategy,
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
