Run strategy
============

When you have a new strategy and you have tested it, you can trade with Oanda broker. To do this, you need to create new
python script (for example `trading_my_strategy.py`). See `trading_eurusd_daily_forecast.py` as an example.

The script is similar to the script created for testing on historical data, but some arguments are added and
different handlers for data and execution are used:

.. code:: python

    configuration = Configuration(data_handler_name=OandaDataHandler, execution_handler_name=OandaExecutionHandler)

    configuration.set_option(Configuration.OPTION_ACCOUNT_ID, os.environ.get('OANDA_API_ACCOUNT_ID'))
    configuration.set_option(Configuration.OPTION_ACCESS_TOKEN, os.environ.get('OANDA_API_ACCESS_TOKEN'))
    configuration.set_option(Configuration.OPTION_TIMEFRAME, args_namespace.time_frame)
    configuration.set_option(Configuration.OPTION_NUMBER_OF_BARS_PRELOAD_FROM_HISTORY, 10)

As you can see, there are credentials for Oanda (account id and access token). You also need to specify timeframe and
the number of bars you would like to load from history before trading (for example to calculate initial signals).

And instead :code:`Backtest` class you need to use :code:`Trading`.

.. code:: python

    trading = Trading(args_namespace.output_directory, list(args_namespace.symbols), 0,
                      configuration, DataHandlerFactory(), ExecutionHandlerFactory(), Portfolio, strategy,
                      FixedPositionSize(0.01), TextLogger(events_log_file), [Trading.LOG_TYPE_EVENTS], strategy_params,
                      'equity.csv', 'trades.csv')

    trading.run()
    trading.print_performance()
