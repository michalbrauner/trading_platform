from strategies.daily_forecast.optimization_and_validation.cross_validation import OptimizationAndValidation
from sklearn.cross_validation import train_test_split


class TrainTestSplit(OptimizationAndValidation):

    def __init__(self, model, model_output_file, test_size, random_state):
        super(TrainTestSplit, self).__init__(model, model_output_file)
        self.test_size = test_size
        self.random_state = random_state

    def get_summary_title(self):
        return 'train_test_split (test_size={}, random_state={})'.format(self.test_size, self.random_state)

    def process(self, x, y):
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=self.test_size,
                                                            random_state=self.random_state)

        self.fit_and_save_model_if_file_defined(x_train, y_train)
        self.calculate_stats_and_show_result(x_test, y_test)



