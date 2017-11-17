from __future__ import print_function

import datetime
import args_parser
import os.path

from strategies.configuration_tools import ConfigurationTools

import pandas as pd
from sklearn.externals import joblib
from sklearn.qda import QDA
from sklearn.linear_model import LogisticRegression
from sklearn.lda import LDA
from sklearn.svm import LinearSVC, SVC
from sklearn.ensemble import RandomForestClassifier
from strategies.daily_forecast.cross_validation.train_test_split import TrainTestSplit

from events.signal_event import SignalEvent
from strategy import Strategy
from machine_learning.lagged_series import create_lagged_series


class EurUsdDailyForecastStrategy(Strategy):
    def __init__(self, bars, portfolio, events, trained_model_file=None, train_data=None, model_output_file=None,
                 model_start_date=None, stop_loss_pips=None, take_profit_pips=None):
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.datetime_now = datetime.datetime.utcnow()
        self.portfolio = portfolio

        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips

        self.bought = self._calculate_initial_bought()
        self.bar_indexes = self._calculate_initial_bar_indexes()

        self.trained_model = trained_model_file
        self.train_data = train_data
        self.model_output_file = model_output_file

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
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to 'OUT'.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'

        return bought

    def _calculate_initial_bar_indexes(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to 'OUT'.
        """
        bar_indexes = {}
        for s in self.symbol_list:
            bar_indexes[s] = 0

        return bar_indexes

    def create_symbol_forecast_model(self, file, model_start_date):
        eurusd_ret = create_lagged_series(file, model_start_date, lags=5)

        x = eurusd_ret[['Lag1', 'Lag2']]
        y = eurusd_ret['Direction']

        model = self.get_model()
        cross_validation = TrainTestSplit(model, self.model_output_file, 0.8, 42)
        cross_validation.process(x, y)

        return model

    def get_model(self):
        # model = RandomForestClassifier(n_estimators=1000, criterion='gini', max_depth=None, min_samples_split=2,
        #                                min_samples_leaf=1, max_features='auto', bootstrap=True, oob_score=False,
        #                                n_jobs=1, random_state=None, verbose=0)

        # model = SVC(C=1000000.0, cache_size=200, class_weight=None, coef0=0.0, degree=3,
        #             gamma=0.0001, kernel='rbf', max_iter=-1, probability=False, random_state=None,
        #             shrinking=True, tol=0.001, verbose=False)

        #model = LogisticRegression()
        #model = QDA()
        # model = LDA()
        model = LinearSVC()

        return model

    def calculate_signals(self, event):
        symbol = self.symbol_list[0]
        datetime_now = self.datetime_now

        if event.type == 'MARKET' and symbol == 'eurusd':

            if self.portfolio.current_positions[symbol] == 0:
                self.bought[symbol] = 'OUT'

            self.bar_indexes[symbol] += 1

            if self.bar_indexes[symbol] > 5:

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

                prediction = self.model.predict(prediction_series)

                if prediction > 0 and self.bought[symbol] == 'OUT':
                    direction = 'LONG'

                    self.bought[symbol] = direction

                    stop_loss = self.calculate_stop_loss_price(bar_price, self.stop_loss_pips, direction)
                    take_profit = self.calculate_take_profit_price(bar_price, self.take_profit_pips, direction)

                    signal = SignalEvent(1, symbol, bar_date, datetime_now, direction, 1.0, stop_loss, take_profit)
                    self.events.put(signal)

                if prediction < 0 and self.bought[symbol] == 'OUT':
                    direction = 'SHORT'

                    self.bought[symbol] = direction

                    stop_loss = self.calculate_stop_loss_price(bar_price, self.stop_loss_pips, direction)
                    take_profit = self.calculate_take_profit_price(bar_price, self.take_profit_pips, direction)

                    signal = SignalEvent(1, symbol, bar_date, datetime_now, direction, 1.0, stop_loss, take_profit)
                    self.events.put(signal)

                if prediction > 0 and self.bought[symbol] == 'SHORT':
                    self.bought[symbol] = 'OUT'
                    signal = SignalEvent(1, symbol, bar_date, datetime_now, 'EXIT', 1.0)
                    self.events.put(signal)

                if prediction < 0 and self.bought[symbol] == 'LONG':
                    self.bought[symbol] = 'OUT'
                    signal = SignalEvent(1, symbol, bar_date, datetime_now, 'EXIT', 1.0)
                    self.events.put(signal)


class EurUsdDailyForecastStrategyConfigurationTools(ConfigurationTools):
    def __init__(self, settings):
        self.settings = settings
        self.set_default_values()

    @staticmethod
    def get_long_opts():
        return ['trained_model_file=', 'train_data=', 'model_output_file=',
                'model_start_date=']

    def get_strategy_params(self):
        return dict(
            trained_model_file=self.settings['trained_model_file'],
            train_data=self.settings['train_data'],
            model_output_file=self.settings['model_output_file'],
            model_start_date=self.settings['model_start_date']
        )

    def use_argument_if_valid(self, option, argument_value):
        if option == '--trained_model_file':
            self.settings['trained_model_file'] = argument_value
        elif option == '--train_data':
            self.settings['train_data'] = argument_value
        elif option == '--model_output_file':
            self.settings['model_output_file'] = argument_value
        elif option == '--model_start_date':
            self.settings['model_start_date'] = argument_value

        return self.settings

    def set_default_values(self):
        if 'trained_model_file' not in self.settings:
            self.settings['trained_model_file'] = None

        if 'train_data' not in self.settings:
            self.settings['train_data'] = None

        if 'model_output_file' not in self.settings:
            self.settings['model_output_file'] = None

        if 'model_start_date' not in self.settings:
            self.settings['model_start_date'] = None

        return self.settings

    def valid_arguments_and_convert_if_necessarily(self):
        if self.settings['trained_model_file'] is not None \
        and os.path.isfile(self.settings['trained_model_file']) is False:

            raise Exception('trained_model_file does not exist')

        if self.settings['train_data'] is not None and os.path.isfile(self.settings['train_data']) is False:
            raise Exception('train_data does not exist')

        args_parser.validate_settings_is_datetime_and_set_to_datetime_object(self.settings, 'model_start_date', False)

        return self.settings
