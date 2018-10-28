# TradingPlatform

The TradingPlatform is a tool for algorithmic trading using your own strategies. It can be used in two different ways: testing strategies on historical data and trading strategies using connector to broker.  
Currently are two data handlers supported - `HistoricCsvDataHandler` for using historical data and `OandaDataHandler` for getting data from Oanda broker.

There are also some example strategies you can inspire from. See directory `strategies` where all strategies are saved.

In root directory is a few scripts that use the strategies from directory mentioned above.

- `backtest_eurusd_daily_forecast.py` - test on historical data for `EurUsdDailyForecastStrategy` strategy
- `trading_eurusd_daily_forecast.py` - trading a strategy `EurUsdDailyForecastStrategy` 
- `optimize_eurusd_daily_forecast.py` - optimization of strategy `EurUsdDailyForecastStrategy` (finding best parameters)
- `notifications_pinbar_oanda.py` - strategy `PinBarNotificationsStrategy` detects PinBars and call defined url (for example to send an email)
- `notifications_pinbar_simulation.py` - testing `PinBarNotificationsStrategy` on historical data 
- `trading_debug_trading.py` - strategy `DebugTradingStrategy` reads the file and take signals from it. I use it to test sending orders to the market (for example during testing broker connector). 
- `trading_eurusd_mac.py` - trading a strategy `MovingAverageCrossStrategy`

#### Installation
The platform is tested on Python 3.6. 
You can install all requirements by the command: `pip install -r requirements.txt`

#### Example of usage

##### Notify when PinBar appears on eurusd, eurjpy or gbpusd   
```
nohup python3.6 notifications_pinbar_oanda.py -s eurusd eurjpy gbpusd  -o trading_output/ --time_frame H4 > logs/main_log.log  2> logs/main_log_error.log &
```

##### Test `EurUsdDailyForecastStrategy` strategy on historical data using trained machine learning model
```
python3.6 backtest_eurusd_daily_forecast.py -d data/M15/2011-2015/ -s eurusd -c 10000 -b 2011-01-01T00:00:00 \
	-o /backtest_output --trained_model_file model.pkl --stop_loss 50 --take_profit 10 --short_window 9 --long_window 100
```

#### Disclaimer
Usage of this tool is on your own risk. I'm using it for my trading, but the platform is still under development. 



