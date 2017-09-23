import sys

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
          + ' -o <output_directory>')
    print('  -> list of symbols separated by coma')
    print('  -> start_datetime is in \'yyyy-mm-ddThh:mm:ss\' format')


def get_settings(argv):

    if len(argv) == 0:
        print_usage()
        exit(1)

    settings = args_parser.get_basic_settings(argv, [])

    if settings['print_help']:
        print_usage()
        exit(0)

    return settings


CSV_DIR = 'd:\\forex_backtesting\\backtest_data\\M15\\test_month\\'


def main(argv):

    settings = get_settings(argv)

    heartbeat = 0

    events_log_file = '{}/events.log'.format(settings['output_directory'])

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
        dict(),
        'equity.csv'
    )

    backtest.simulate_trading()
    backtest.print_performance()


if __name__ == "__main__":
    main(sys.argv[1:])
