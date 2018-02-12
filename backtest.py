from core.portfolio import Portfolio

from core.backtest import Backtest
from core.configuration import Configuration
from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler
from executionhandlers.simulated_execution import SimulatedExecutionHandler
from executionhandlers.execution_handler_factory import ExecutionHandlerFactory
import strategies.eurusd_daily_forecast as eurusd_daily_forecast
from positionsizehandlers.fixed_position_size import FixedPositionSize
from loggers.text_logger import TextLogger
from datahandlers.data_handler_factory import DataHandlerFactory


def get_strategy():
    return eurusd_daily_forecast.EurUsdDailyForecastStrategy


def main():

    strategy = get_strategy()
    args_namespace = strategy.create_argument_parser().parse_args()
    strategy_params_special = strategy.get_strategy_params(args_namespace)

    events_log_file = '{}/events.log'.format(args_namespace.output_directory)

    strategy_params = dict(stop_loss_pips=args_namespace.stop_loss, take_profit_pips=args_namespace.take_profit)
    strategy_params.update(strategy_params_special)

    configuration = Configuration(data_handler_name=HistoricCSVDataHandler,
                                  execution_handler_name=SimulatedExecutionHandler)
    configuration.set_option(Configuration.OPTION_CSV_DIR, args_namespace.data_directory)

    backtest = Backtest(
        args_namespace.output_directory,
        args_namespace.symbols,
        args_namespace.initial_capital_usd,
        0,
        args_namespace.start_date,
        configuration,
        DataHandlerFactory(),
        ExecutionHandlerFactory(),
        Portfolio,
        strategy,
        FixedPositionSize(0.5),
        TextLogger(events_log_file),
        [Backtest.LOG_TYPE_EVENTS],
        strategy_params,
        'equity.csv'
    )

    backtest.simulate_trading()
    backtest.print_performance()


if __name__ == "__main__":
    main()
