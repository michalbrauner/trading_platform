import re
import argparse
import os
import datetime


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

REG_DATETIME_DATE_PART = r'[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}'
REG_DATETIME_TIME_PART = r'[0-9]{2}[:]{1}[0-9]{2}[:]{1}[0-9]{2}'
REG_DATETIME = r'^{}T{}$'.format(REG_DATETIME_DATE_PART, REG_DATETIME_TIME_PART)


def datetime_argument(value):

    if re.match(REG_DATETIME, value) is None:
        message = '{} needs to be in \'yyyy-mm-ddThh:mm:ss\' format'.format(value)
        raise argparse.ArgumentTypeError(message)

    return datetime.datetime.strptime(value, DATETIME_FORMAT)


def existing_directory(value):
    if os.path.isdir(value) is False:
        message = '{} is not existing directory'.format(value)
        raise argparse.ArgumentTypeError(message)

    return value


def existing_file(value):
    if os.path.isfile(value) is False:
        message = '{} is not existing file'.format(value)
        raise argparse.ArgumentTypeError(message)

    return value


def create_basic_argument_parser():
    # () -> argparse.ArgumentParser

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--symbols', nargs='+', required=True)
    parser.add_argument('-o', '--output_directory', type=existing_directory, required=True)

    return parser


def with_backtest_arguments(parser):
    # (argparse.ArgumentParser) -> argparse.ArgumentParser

    parser.add_argument('-d', '--data_directory', type=existing_directory, required=True)
    parser.add_argument('-c', '--initial_capital_usd', type=int, required=True)
    parser.add_argument('-b', '--start_date', type=datetime_argument, required=True)

    return parser


def with_sl_and_tp(parser):
    # (argparse.ArgumentParser) -> argparse.ArgumentParser

    parser.add_argument('--stop_loss', type=int)
    parser.add_argument('--take_profit', type=int)

    return parser


def with_sma_short_and_long(parser):
    # (argparse.ArgumentParser) -> argparse.ArgumentParser

    parser.add_argument('--short_window', type=int)
    parser.add_argument('--long_window', type=int)

    return parser
