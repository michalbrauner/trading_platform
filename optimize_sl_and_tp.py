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
from datahandlers.data_handler_factory import DataHandlerFactory


def print_usage():
    print('Usage: python optimize_sl_and_tp.py -d <data_directory> -s <symbols> -c <initial_capital_usd> -b <start_datetime>'
          + ' -o <output_directory> --sl_min <int> --sl_max <int> --sl_step <int>'
          + ' --tp_min <int> --tp_max <int> --tp_step <int>'
  )
    print('  -> list of symbols separated by coma')
    print('  -> start_datetime is in \'yyyy-mm-ddThh:mm:ss\' format')


def get_settings(argv):

    if len(argv) == 0:
        print_usage()
        exit(1)

    long_opts = ['sl_min=', 'sl_max=', 'sl_step=', 'tp_min=', 'tp_max=', 'tp_step=']

    settings = args_parser.get_basic_settings(argv, long_opts)

    if settings['print_help']:
        print_usage()
        exit(0)

    opts, args = getopt.getopt(argv, args_parser.BASIC_ARGS, long_opts)

    for opt, arg in opts:
        if opt == '--sl_min':
            settings['sl_min'] = arg
        elif opt == '--sl_max':
            settings['sl_max'] = arg
        elif opt == '--sl_step':
            settings['sl_step'] = arg
        elif opt == '--tp_min':
            settings['tp_min'] = arg
        elif opt == '--tp_max':
            settings['tp_max'] = arg
        elif opt == '--tp_step':
            settings['tp_step'] = arg

    args_parser.validate_settings_is_number_and_set_to_int(settings, 'sl_min')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'sl_max')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'sl_step')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'tp_min')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'tp_max')
    args_parser.validate_settings_is_number_and_set_to_int(settings, 'tp_step')

    return settings


def main(argv):

    settings = get_settings(argv)

    heartbeat = 0

    csv_file = open('{}/optimization.csv'.format(settings['output_directory']), 'wb')
    csv_file_writer = csv.writer(csv_file, delimiter=',')
    csv_file_writer.writerow(['SL', 'TP', 'Total Return', 'Sharpe Ratio', 'Max Drawdown', 'Drawdown Duration'])

    sl_current = settings['sl_min']
    sl_max = settings['sl_max']
    sl_step = settings['sl_step']

    tp_max = settings['tp_max']
    tp_step = settings['tp_step']

    while sl_current <= sl_max:
        tp_current = settings['tp_min']

        while tp_current <= tp_max:
            events_log_file = '{}/events_{}_{}.log'.format(settings['output_directory'], sl_current,
                                                           tp_current)
            equity_filename = 'equity_{}_{}.csv'.format(sl_current, tp_current)

            print('Running backtest for: SL=%d, TP=%d' % (sl_current, tp_current))

            stats = run_backtest_instance(settings, events_log_file, heartbeat, sl_current,
                                          tp_current, equity_filename)

            os.remove(events_log_file)
            os.remove('{}/{}'.format(settings['output_directory'], equity_filename))

            csv_file_writer.writerow(
                [sl_current, tp_current, stats.get_total_return(), stats.get_sharpe_ratio(),
                 stats.get_max_drawdown(),
                 stats.get_drawdown_duration()])

            print('')

            tp_current = tp_current + tp_step

        sl_current = sl_current + sl_step

    csv_file.close()


def run_backtest_instance(settings, events_log_file, heartbeat, sl, tp, equity_filename):

    trained_model_file = '/home/ubuntu/backtester_output/forecast/2004_2010_model/logistic_regression/model/model.pkl'

    # trained_model_file = 'm:\\apps\\python\\forex\\backtesting\\backtester_output\\' \
    #                      + 'forecast\\logistic_regression\\model\\model.pkl'

    strategy_params = dict(
        stop_loss_pips=sl,
        take_profit_pips=tp,
        trained_model_file=trained_model_file
    )

    backtest = Backtest(
        settings['output_directory'],
        settings['symbols'],
        settings['initial_capital_usd'],
        heartbeat,
        settings['start_date'],
        {
            'data_handler_name': HistoricCSVDataHandler,
            'csv_dir': settings['data_directory'],
            'execution_handler_name': SimulatedExecutionHandler,
        },
        DataHandlerFactory(),
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
