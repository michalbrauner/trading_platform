from core.portfolio import Portfolio

from core.backtest import Backtest
from core.configuration import Configuration
from datahandlers.data_handler_factory import DataHandlerFactory
from executionhandlers.simulated_execution import SimulatedExecutionHandler
from executionhandlers.execution_handler_factory import ExecutionHandlerFactory
from strategies.pinbar_notifications import PinBarNotificationsStrategy
from positionsizehandlers.fixed_position_size import FixedPositionSize
from loggers.text_logger import TextLogger
from datahandlers.historic_csv_data_handler import HistoricCSVDataHandler


def get_strategy():
    return PinBarNotificationsStrategy


def main():

    strategy = get_strategy()
    args_namespace = strategy.create_argument_parser(True).parse_args()

    events_log_file = '{}/events.log'.format(args_namespace.output_directory)

    strategy_params = strategy.get_strategy_params(args_namespace)
    strategy_params['send_notifications'] = False
    strategy_params['webhook'] = ''

    configuration = Configuration(data_handler_name=HistoricCSVDataHandler,
                                  execution_handler_name=SimulatedExecutionHandler)

    configuration.set_option(Configuration.OPTION_CSV_DIR, args_namespace.data_directory)

    simulation = Backtest(
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
        'equity.csv',
        'trades.csv',
    )

    simulation.run()
    simulation.print_performance()


if __name__ == "__main__":
    main()
