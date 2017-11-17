from abc import ABCMeta, abstractmethod

from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib


class OptimizationAndValidation(object):
    __metaclass__ = ABCMeta

    def __init__(self, model, model_output_file):
        self.model = model
        self.model_output_file = model_output_file

    def calculate_stats_and_show_result(self, x_test, y_test):
        prediction = self.model.predict(x_test)

        self.print_title()

        print('Hit rate:\n%0.3f' % self.model.score(x_test, y_test))
        print('Confusion matrix: %s\n' % confusion_matrix(prediction, y_test))
        print('\n')

    def print_title(self):
        title_separator = '-------------------------------------'
        print('{}\n{}\n{}\n'.format(title_separator, self.get_summary_title(), title_separator))

    def fit_and_save_model_if_file_defined(self, x, y):
        self.model.fit(x, y)

        if self.model_output_file is not None:
            joblib.dump(self.model, self.model_output_file)

    @abstractmethod
    def process(self, x, y):
        raise NotImplementedError("Should implement process()")

    @abstractmethod
    def get_summary_title(self):
        raise NotImplementedError("Should implement get_summary_title()")
