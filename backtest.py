import datetime
import getopt
import sys

from core.portfolio import Portfolio

from core.backtest import Backtest
from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from executionhandlers.simulated_execution import SimulatedExecutionHandler
from strategies.mac import MovingAverageCrossStrategy


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def print_usage():
    print('Usage: python backtest.py -d <data_directory> -s <symbols> -c <initial_capital_usd> -b <start_datetime>'
          + ' -o <output_directory>')
    print('  -> list of symbols separated by coma')
    print('  -> start_datetime is in \'yyyy-mm-ddThh:mm:ss\' format')


def get_settings(argv):
    settings = dict(
        data_directory=None,
        symbols=None,
        initial_capital_usd=None,
        start_date=None,
        output_directory=None
    )

    opts, args = getopt.getopt(argv, "hd:s:c:b:o:")

    for opt, arg in opts:

        if opt == '-h':
            print_usage()
            exit(0)
        elif opt == '-d':
            settings['data_directory'] = arg
        elif opt == '-s':
            settings['symbols'] = arg
        elif opt == '-c':
            settings['initial_capital_usd'] = arg
        elif opt == '-b':
            settings['start_date'] = datetime.datetime.strptime(arg, DATETIME_FORMAT)
        elif opt == '-o':
            settings['output_directory'] = arg

    validate_settings(settings)

    return settings


def validate_settings(settings):
    if settings['data_directory'] is None:
        raise Exception('Missing values - data_directory is required')

    if settings['symbols'] is None:
        raise Exception('Missing values - symbols is required')

    if settings['initial_capital_usd'] is None:
        raise Exception('Missing values - initial_capital_usd is required')

    if settings['start_date'] is None:
        raise Exception('Missing values - start_date is required')

    if settings['output_directory'] is None:
        raise Exception('Missing value - output_directory is required')


CSV_DIR = 'd:\\forex_backtesting\\backtest_data\\M15\\test_month\\'


def main(argv):

    # settings = get_settings(argv)

    symbols = ['eurusd']
    initial_capital_usd = 10000
    heartbeat = 0
    start_date = datetime.datetime(2017, 6, 1, 0, 0, 0)

    backtest = Backtest(
        CSV_DIR,
        symbols,
        initial_capital_usd,
        heartbeat,
        start_date,
        HistoricCSVDataHandler,
        SimulatedExecutionHandler,
        Portfolio,
        MovingAverageCrossStrategy
    )

    backtest.simulate_trading()


if __name__ == "__main__":
    main(sys.argv[1:])
