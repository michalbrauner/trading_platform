import datetime
import getopt
import sys, os, re

from core.portfolio import Portfolio

from core.backtest import Backtest
from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from executionhandlers.simulated_execution import SimulatedExecutionHandler
from strategies.mac import MovingAverageCrossStrategy


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
REG_SYMBOLS_SEPARATED_BY_COMA = r'^([a-zA-Z]{6})([,]{1}[a-zA-Z]{6})*$'
REG_NUMBER = r'^[0-9]+$'

REG_DATETIME_DATE_PART = r'[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}'
REG_DATETIME_TIME_PART = r'[0-9]{2}[:]{1}[0-9]{2}[:]{1}[0-9]{2}'
REG_DATETIME = r'^{}T{}$'.format(REG_DATETIME_DATE_PART, REG_DATETIME_TIME_PART)

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
            settings['start_date'] = arg
        elif opt == '-o':
            settings['output_directory'] = arg

    validate_settings(settings)

    return settings


def validate_settings(settings):
    if settings['data_directory'] is None:
        raise Exception('Missing values - data_directory is required')
    elif os.path.isdir(settings['data_directory']) is False:
        raise Exception('data_directory doesn\'t exist')

    if settings['symbols'] is None:
        raise Exception('Missing values - symbols is required')
    elif re.match(REG_SYMBOLS_SEPARATED_BY_COMA, settings['symbols']) is None:
        raise Exception('symbols needs to be list of symbols separated by coma')
    else:
        settings['symbols'] = settings['symbols'].split(',')

    if settings['initial_capital_usd'] is None:
        raise Exception('Missing values - initial_capital_usd is required')
    elif re.match(REG_NUMBER, settings['initial_capital_usd']) is None:
        raise Exception('initial_capital_usd needs to be a number')
    else:
        settings['initial_capital_usd'] = int(settings['initial_capital_usd'])

    if settings['start_date'] is None:
        raise Exception('Missing values - start_date is required')
    elif re.match(REG_DATETIME, settings['start_date']) is None:
        raise Exception('start_date needs to be in \'yyyy-mm-ddThh:mm:ss\' format')
    else:
        settings['start_date'] = datetime.datetime.strptime(settings['start_date'], DATETIME_FORMAT)

    if settings['output_directory'] is None:
        raise Exception('Missing value - output_directory is required')
    elif os.path.isdir(settings['output_directory']) is False:
        raise Exception('output_directory doesn\'t exist')


CSV_DIR = 'd:\\forex_backtesting\\backtest_data\\M15\\test_month\\'


def main(argv):

    settings = get_settings(argv)

    heartbeat = 0

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
        MovingAverageCrossStrategy
    )

    backtest.simulate_trading()


if __name__ == "__main__":
    main(sys.argv[1:])
