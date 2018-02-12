from strategies.daily_forecast.optimization_and_validation.cross_validation import OptimizationAndValidation
from sklearn import cross_validation


class KFold(OptimizationAndValidation):

    def __init__(self, model, model_output_file, n_fold):
        super(KFold, self).__init__(model, model_output_file)
        self.n_fold = n_fold

    def get_summary_title(self):
        return 'k_fold (n_folds={})'.format(self.n_fold)

    def process(self, x, y):
        kf = cross_validation.KFold(len(x), n_folds=self.n_fold, indices=False, shuffle=True, random_state=42)

        if self.model_output_file is not None:
            print('Warnig: model won\'t be saved in output file for KFold cross validation')

        for train_index, test_index in kf:
            x_train = x.ix[x.index[train_index]]
            x_test = x.ix[x.index[test_index]]
            y_train = y.ix[y.index[train_index]]
            y_test = y.ix[y.index[test_index]]

            self.model.fit(x_train, y_train)
            self.calculate_stats_and_write_result(x_test, y_test)

    def get_title(self):
        pass



