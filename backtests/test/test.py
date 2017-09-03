import datetime

from portfolio import Portfolio

from core.backtest import Backtest
from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from executionhandlers.simulated_execution import SimulatedExecutionHandler
from strategies.mac import MovingAverageCrossStrategy

CSV_DIR = 'd:\\forex_backtesting\\backtest_data\\M15\\test_month\\'


def main():
    symbols = ['eurusd']
    initial_capital_usd = 10000
    heartbeat = 0
    start_date = datetime.datetime(2017, 6, 1, 0, 0, 0)

    backtest = Backtest(
        CSV_DIR,
        symbols,
        initial_capital_usd,
        heartbeat,
        start_date,
        HistoricCSVDataHandler,
        SimulatedExecutionHandler,
        Portfolio,
        MovingAverageCrossStrategy
    )

    backtest.simulate_trading()


if __name__ == "__main__":
    main()
