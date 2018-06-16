from __future__ import print_function

import datetime
import os.path
import csv

import pandas as pd
from sklearn.externals import joblib
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn.ensemble import RandomForestClassifier
from strategies.daily_forecast.optimization_and_validation.train_test_split import TrainTestSplit

from events.signal_event import SignalEvent
from strategies.strategy import Strategy
from machine_learning.lagged_series import create_lagged_series
from core.portfolio import Portfolio
from datahandlers.data_handler import DataHandler
import argparser_tools.basic

import numpy as np

try:
    import Queue as queue
except ImportError:
    import queue


class EurUsdDailyForecastStrategy(Strategy):
    def __init__(self, bars, portfolio, events, trained_model_file=None, train_data=None, model_output_file=None,
                 model_start_date=None, stop_loss_pips=None, take_profit_pips=None, sma_short_period=None,
                 sma_long_period=None):
        """

        :type bars: DataHandler
        :type portfolio: Portfolio
        :type events: queue.Queue
        :type trained_model_file: str
        :type train_data: str
        :type model_output_file: str
        :type model_start_date: datetime.datetime
        :type stop_loss_pips: int
        :type take_profit_pips: int
        :type sma_short_period: int
        :type sma_long_period: int
        """
        self.bars = bars
        self.symbol_list = self.bars.get_symbol_list()
        self.events = events
        self.datetime_now = datetime.datetime.utcnow()
        self.portfolio = portfolio

        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips

        self.sma_short_period = sma_short_period
        self.sma_long_period = sma_long_period

        self.bought = self._calculate_initial_bought()

        self.trained_model = trained_model_file
        self.train_data = train_data
        self.model_output_directory = model_output_file

        if trained_model_file is None and train_data is None:
            raise Exception('Either trained_model_file or train_data need to be defined')

        if self.train_data is not None:

            if model_start_date is None:
                raise Exception('You need to define model_start_date to train model')

            self.model_start_date = model_start_date

            self.model = self.create_symbol_forecast_model(self.train_data, self.model_start_date)

        elif self.trained_model is not None:
            self.model = joblib.load(self.trained_model)

    def _calculate_initial_bought(self):
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'

        return bought

    def create_symbol_forecast_model(self, file, model_start_date):
        eurusd_ret = create_lagged_series(file, model_start_date, lags=5)

        x = eurusd_ret[['Lag1', 'Lag2']]
        y = eurusd_ret['Direction']

        models = self.get_models_to_analyze()
        model_to_return = None

        models_output_summary_file = self.model_output_directory + os.path.sep + 'summary.csv'
        models_output_summary_file_opened = open(models_output_summary_file, 'wb')
        models_output_summary_file_csv_writer = csv.writer(models_output_summary_file_opened, delimiter=',')

        for model in models:

            model_output_directory = self.model_output_directory + os.path.sep + model.__class__.__name__

            if not os.path.exists(model_output_directory):
                os.mkdir(model_output_directory)

            model_output_filename = model_output_directory + os.path.sep + 'model.pkl'

            cross_validation = TrainTestSplit(model, model_output_filename, models_output_summary_file_csv_writer, 0.8,
                                              42)

            # cross_validation = KFold(model, self.model_output_file, 10)

            # tuned_parameters = [{
            #     'kernel': ['rbf'],
            #     'gamma': [1e-3, 1e-4],
            #     'C': [1, 10, 100, 1000]
            #  }]
            #
            # cross_validation = GridSearch(model, self.model_output_file, tuned_parameters, 10)
            cross_validation.process(x, y)

            if model_to_return is None:
                model_to_return = model

            models_output_summary_file_opened.flush()

        models_output_summary_file_opened.close()

        return model_to_return

    @staticmethod
    def get_models_to_analyze():
        models = list()

        models.append(RandomForestClassifier(n_estimators=1000, criterion='gini', max_depth=None, min_samples_split=2,
                                             min_samples_leaf=1, max_features='auto', bootstrap=True, oob_score=False,
                                             n_jobs=1, random_state=None, verbose=0))

        models.append(SVC(C=1000000.0, cache_size=200, class_weight=None, coef0=0.0, degree=3,
                    gamma=0.0001, kernel='rbf', max_iter=-1, probability=False, random_state=None,
                    shrinking=True, tol=0.001, verbose=False))

        models.append(SVC())

        models.append(LogisticRegression())
        models.append(QuadraticDiscriminantAnalysis())
        models.append(LinearDiscriminantAnalysis())
        models.append(LinearSVC())

        return models

    def get_model(self):
        # model = RandomForestClassifier(n_estimators=1000, criterion='gini', max_depth=None, min_samples_split=2,
        #                                min_samples_leaf=1, max_features='auto', bootstrap=True, oob_score=False,
        #                                n_jobs=1, random_state=None, verbose=0)

        # model = SVC(C=1000000.0, cache_size=200, class_weight=None, coef0=0.0, degree=3,
        #             gamma=0.0001, kernel='rbf', max_iter=-1, probability=False, random_state=None,
        #             shrinking=True, tol=0.001, verbose=False)

        # model = SVC()

        model = LogisticRegression()
        # model = QuadraticDiscriminantAnalysis()
        # model = LinearDiscriminantAnalysis()
        # model = LinearSVC()

        return model

    def calculate_signals(self, event):
        symbol = self.symbol_list[0]
        datetime_now = self.datetime_now

        if event.type == 'MARKET' and (symbol == 'EUR_USD' or symbol == 'eurusd'):

            if self.portfolio.current_positions[symbol] == 0:
                self.bought[symbol] = 'OUT'

            number_of_bars = self.bars.get_number_of_bars(symbol)

            max_sma_period = max(self.sma_long_period, self.sma_short_period)

            if number_of_bars > 5 and number_of_bars > max_sma_period:

                bar_date = self.bars.get_latest_bar_datetime(symbol)
                bar_price = self.bars.get_latest_bar_value(symbol, 'close_bid')

                lags = self.bars.get_latest_bars_values(symbol, 'close_bid', N=3)
                lags_returns = pd.Series(lags).pct_change() * 100

                prediction_series = pd.Series(
                    {
                        'Lag1': lags_returns[1],
                        'Lag2': lags_returns[2]
                    }
                )

                prediction = self.model.predict([prediction_series])

                sma_enabled = self.sma_short_period > 0 and self.sma_long_period > 0

                if sma_enabled:

                    bars = self.bars.get_latest_bars_values(symbol, 'close_bid', N=max_sma_period)

                    sma_short = self.calculate_sma(self.sma_short_period, bars)
                    sma_long = self.calculate_sma(self.sma_long_period, bars)
                else:
                    sma_short = 0
                    sma_long = 0

                signal_generated = self.calculate_exit_signals(symbol, bar_date, prediction, datetime_now)

                self.calculate_new_signals(symbol, bar_date, bar_price, prediction, sma_short, sma_long,
                                           datetime_now)

    def calculate_new_signals(self, symbol, bar_date, bar_price, prediction, sma_short, sma_long, datetime_now):

        current_position = self.portfolio.get_current_position(symbol)

        sma_enabled = self.sma_short_period > 0 and self.sma_long_period > 0

        if current_position is None:
            if prediction > 0 and ((sma_enabled and sma_short > sma_long) or not sma_enabled):
                direction = 'LONG'

                self.bought[symbol] = direction

                stop_loss = self.calculate_stop_loss_price(bar_price, self.stop_loss_pips, direction)
                take_profit = self.calculate_take_profit_price(bar_price, self.take_profit_pips, direction)

                signal = SignalEvent(1, symbol, bar_date, datetime_now, direction, 1.0, stop_loss, take_profit)
                self.events.put(signal)

                return True

            if prediction < 0 and ((sma_enabled and sma_short < sma_long) or not sma_enabled):
                direction = 'SHORT'

                self.bought[symbol] = direction

                stop_loss = self.calculate_stop_loss_price(bar_price, self.stop_loss_pips, direction)
                take_profit = self.calculate_take_profit_price(bar_price, self.take_profit_pips, direction)

                signal = SignalEvent(1, symbol, bar_date, datetime_now, direction, 1.0, stop_loss, take_profit)
                self.events.put(signal)

                return True

        return False

    def calculate_exit_signals(self, symbol, bar_date, prediction, datetime_now):

        current_position = self.portfolio.get_current_position(symbol)

        if current_position is not None and \
                ((prediction > 0 and current_position.is_short()) or (prediction < 0 and current_position.is_long())):
            signal = SignalEvent(1, symbol, bar_date, datetime_now, 'EXIT', 1.0, None, None,
                                 current_position.get_trade_id())
            self.events.put(signal)

            self.bought[symbol] = 'OUT'

            return True

        return False

    @staticmethod
    def calculate_sma(period, bars):
        return np.mean(bars[-period:])

    @staticmethod
    def get_strategy_params(args_namespace):
        return dict(
            trained_model_file=args_namespace.trained_model_file,
            train_data=args_namespace.train_data,
            model_output_file=args_namespace.model_output_file,
            model_start_date=args_namespace.model_start_date,
            sma_short_period=args_namespace.short_window,
            sma_long_period=args_namespace.long_window
        )

    @staticmethod
    def create_argument_parser(backtest_only):
        # (bool) -> argparse.ArgumentParser

        parser = argparser_tools.basic.create_basic_argument_parser(backtest_only)

        if backtest_only:
            parser = argparser_tools.basic.with_backtest_arguments(parser)

        parser = argparser_tools.basic.with_sl_and_tp(parser)
        parser = argparser_tools.basic.with_sma_short_and_long(parser)

        parser.add_argument('--trained_model_file', type=argparser_tools.basic.existing_file)
        parser.add_argument('--train_data', type=argparser_tools.basic.existing_file)
        parser.add_argument('--model_output_file')
        parser.add_argument('--model_start_date', type=argparser_tools.basic.datetime_argument)

        return parser
