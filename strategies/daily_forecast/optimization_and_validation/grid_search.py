from strategies.daily_forecast.optimization_and_validation.cross_validation import OptimizationAndValidation
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV


class GridSearch(OptimizationAndValidation):

    def __init__(self, model, model_output_file, tuned_parameters, kfold_n):
        model = GridSearchCV(model, tuned_parameters, cv=10)

        super(GridSearch, self).__init__(model, model_output_file)

        self.tuned_parameters = tuned_parameters
        self.kfold_n = kfold_n

    def get_summary_title(self):
        return 'grid_search (tuned_parameters={})'.format(self.tuned_parameters)

    def process(self, x, y):

        if self.model_output_file is not None:
            print('Warnig: model won\'t be saved in output file for GridSearch optimization and validation')

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.5, random_state=42)

        self.model.fit(x_train, y_train)
        self.calculate_stats_and_write_result(x_test, y_test)

    def calculate_stats_and_write_result(self, x_test, y_test):

        print('Optimised parameters found on training set:')
        print(self.model.best_estimator_, '\n')

        for params, mean_score, scores in self.model.grid_scores_:
            prediction = self.model.predict(x_test)
            print('%0.3f for %r' % (mean_score, params))

    def get_title(self):
        pass



