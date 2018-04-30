from core.portfolio import Portfolio

from core.backtest import Backtest
from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from executionhandlers.simulated_execution import SimulatedExecutionHandler
from executionhandlers.execution_handler_factory import ExecutionHandlerFactory
from strategies.eurusd_daily_forecast import EurUsdDailyForecastStrategy
from positionsizehandlers.fixed_position_size import FixedPositionSize
from loggers.text_logger import TextLogger
import csv, os
import itertools
import numpy as np
from datahandlers.data_handler_factory import DataHandlerFactory
from core.configuration import Configuration
import argparser_tools.basic
import argparser_tools.optimization


def get_argument_parser():
    # () -> argparse.ArgumentParser

    parser = argparser_tools.basic.create_basic_argument_parser(True)
    parser = argparser_tools.basic.with_backtest_arguments(parser)
    parser = argparser_tools.optimization.with_sma_short_and_long(parser)
    parser = argparser_tools.optimization.with_sl_and_tp(parser)

    parser.add_argument('--trained_model_file', type=argparser_tools.basic.existing_file)

    return parser


def main():

    args_namespace = get_argument_parser().parse_args()

    heartbeat = 0

    csv_file = open('{}/optimization.csv'.format(args_namespace.output_directory), 'wb')
    csv_file_writer = csv.writer(csv_file, delimiter=',')
    csv_file_writer.writerow(['SL', 'TP', 'SMA_short', 'SMA_long', 'Total Return',
                              'Sharpe Ratio', 'Max Drawdown', 'Drawdown Duration'])

    values_to_try = [
        range(args_namespace.sl_min, args_namespace.sl_max + 1, args_namespace.sl_step),
        range(args_namespace.tp_min, args_namespace.tp_max + 1, args_namespace.tp_step),
        range(args_namespace.short_window_min, args_namespace.short_window_max + 1, args_namespace.short_window_step),
        range(args_namespace.long_window_min, args_namespace.long_window_max + 1, args_namespace.long_window_step),
    ]

    total_test_to_run = np.product([len(data) for data in values_to_try])
    print('Total number of tests to run: %d' % total_test_to_run)

    for parameters in itertools.product(*values_to_try):
        run_and_log_optimization_instance(csv_file, csv_file_writer, heartbeat, args_namespace, parameters[0], parameters[1],
                                          parameters[2], parameters[3])

    csv_file.close()


def run_and_log_optimization_instance(csv_file, csv_file_writer, heartbeat, args_namespace, sl, tp, short_window,
                                      long_window):
    events_log_file = '{}/events_{}_{}_{}_{}.log'.format(args_namespace.output_directory, sl, tp, short_window,
                                                         long_window)

    equity_filename = 'equity_{}_{}_{}_{}.csv'.format(sl, tp, short_window, long_window)

    print('Running backtest for: SL=%d, TP=%d, SMA_short=%d, SMA_long=%d' % (sl, tp, short_window, long_window))

    stats = run_backtest_instance(args_namespace, events_log_file, heartbeat, sl, tp, short_window, long_window,
                                  equity_filename, args_namespace.trained_model_file)

    files_to_remove = [
        events_log_file,
        '{}/{}'.format(args_namespace.output_directory, equity_filename)
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
    csv_file.flush()

    print('')


def run_backtest_instance(args_namespace, events_log_file, heartbeat, sl, tp, short_window, long_window, equity_filename,
                          trained_model_file):

    trades_filename = 'trades.csv'

    strategy_params = dict(
        stop_loss_pips=sl,
        take_profit_pips=tp,
        trained_model_file=trained_model_file,
        sma_short_period=short_window,
        sma_long_period=long_window
    )

    configuration = Configuration(data_handler_name=HistoricCSVDataHandler,
                                  execution_handler_name=SimulatedExecutionHandler)
    configuration.set_option(Configuration.OPTION_CSV_DIR, args_namespace.data_directory)

    backtest = Backtest(
        args_namespace.output_directory,
        args_namespace.symbols,
        args_namespace.initial_capital_usd,
        heartbeat,
        args_namespace.start_date,
        configuration,
        DataHandlerFactory(),
        ExecutionHandlerFactory(),
        Portfolio,
        EurUsdDailyForecastStrategy,
        FixedPositionSize(0.5),
        TextLogger(events_log_file),
        [Backtest.LOG_TYPE_EVENTS],
        strategy_params,
        equity_filename,
        trades_filename
    )
    backtest.simulate_trading()

    return backtest.stats


if __name__ == "__main__":
    main()
