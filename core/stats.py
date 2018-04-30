class Stats(object):
    def __init__(self, total_return, sharpe_ratio, max_drawdown, drawdown_duration, trades):
        self.total_return = total_return
        self.sharpe_ratio = sharpe_ratio
        self.max_drawdown = max_drawdown
        self.drawdown_duration = drawdown_duration
        self.trades = trades

    def get_total_return(self):
        return self.total_return

    def get_sharpe_ratio(self):
        return self.sharpe_ratio

    def get_max_drawdown(self):
        return self.max_drawdown

    def get_drawdown_duration(self):
        return self.drawdown_duration

    def get_number_of_trades(self):
        return len(self.trades)

    def print_stats(self):
        print('Total Return: %0.2f%%' % self.get_total_return())
        print('Sharpe Ratio: %0.2f' % self.get_sharpe_ratio())
        print('Max Drawdown: %0.2f%%' % self.get_max_drawdown())
        print('Drawdown Duration: %d' % self.get_drawdown_duration())
        print('Number of trades: %d' % self.get_number_of_trades())
