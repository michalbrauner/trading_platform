from abc import ABCMeta, abstractmethod

from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib


class OptimizationAndValidation(object):
    __metaclass__ = ABCMeta

    CSV_SEPARATOR = ';'

    def __init__(self, model, model_output_file, models_summary_csv_writer):
        self.model = model
        self.model_output_file = model_output_file
        self.models_summary_csv_writer = models_summary_csv_writer

    def calculate_stats_and_write_result(self, x_test, y_test):
        prediction = self.model.predict(x_test)

        hit_rate = '%0.3f' % self.model.score(x_test, y_test)
        c_matrix = confusion_matrix(prediction, y_test)

        self.models_summary_csv_writer.writerow(
            [self.get_summary_title(), self.model.__class__.__name__, hit_rate, c_matrix[0][0], c_matrix[0][1],
             c_matrix[1][0], c_matrix[1][1]])

    def fit_and_save_model_if_file_defined(self, x, y):
        self.model.fit(x, y)

        if self.model_output_file is not None:
            joblib.dump(self.model, self.model_output_file)

    @staticmethod
    def write_summary_header(csv_writer):
        csv_writer.writerow(
            ['Validation name', 'Model', 'Hit rate', 'ConfusionMatrix[0,0]', 'ConfusionMatrix[0,1]',
             'ConfusionMatrix[1,0]', 'ConfusionMatrix[1,1]'])

    @abstractmethod
    def process(self, x, y):
        raise NotImplementedError("Should implement process()")

    @abstractmethod
    def get_summary_title(self):
        raise NotImplementedError("Should implement get_summary_title()")
