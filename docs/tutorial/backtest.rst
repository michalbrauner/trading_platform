Test strategy on historical data
================================

When you have a new strategy, you should test it on historical data. To do this, you need to create new
python script (for example `backtest_my_strategy.py`). See `backtest_eurusd_daily_forecast.py` as an example.

The important part is to fetch all arguments from the command line. To do this, you need to define methods
:code:`create_argument_parser` and :code:`get_strategy_params` in your strategy.
These define list of arguments strategy uses.

Then you need to create an instance of :code:`Configuration` class with
:code:`execution_handler_name=SimulatedExecutionHandler` and set directory to historical data.

.. code:: python

    configuration = Configuration(data_handler_name=HistoricCSVDataHandler,
                                  execution_handler_name=SimulatedExecutionHandler)
    configuration.set_option(Configuration.OPTION_CSV_DIR, args_namespace.data_directory)

Finally, you can create an instance of the class :code:`Backtest` and run:

.. code:: python

    backtest.run()
    backtest.print_performance()


Then the script can be run as:

.. code::

    python3.6 backtest_eurusd_daily_forecast.py -d c:\historical_data\ -s eurusd -c 10000 -b 2017-01-01T00:00:00 -o c:\backtest_output --stop_loss 30 --take_profit 30 --trained_model_file c:\model.pkl --short_window 0 --long_window 0

There is an example of historical data CSV:

.. code::

    EUR_USD;D;2005-01-01T00:00:00;2016-12-31T23:59:59
    time;openBid;openAsk;highBid;highAsk;lowBid;lowAsk;closeBid;closeAsk;volume
    2005-01-01T22:00:00.000000Z;1.3555;1.3565;1.3565;1.3575;1.3536;1.3546;1.35475;1.35575;303
    2005-01-02T22:00:00.000000Z;1.35485;1.35585;1.35785;1.35845;1.3384;1.3387;1.3464;1.3466;38042

