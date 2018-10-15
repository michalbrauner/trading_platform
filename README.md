# TradingPlatform

The TradingPlatform is a tool for developing, testing and trading strategies.  
You can write your own strategies (see examples in `strategies` directory.), test them using historical data in CSV file 
and then trade them (currently only Oanda is supported).

More detailed documentation will be written in future, so far there are some examples in the root directory:
- `backtest_eurusd_daily_forecast.py` - historical backtest of `EurUsdDailyForecastStrategy` strategy 
- `notifications_pinbar_oanda.py` - strategy `PinBarNotificationsStrategy` detects PinBars and call webhook (for example to send an email)
- `notifications_pinbar_simulation.py` - simulation of strategy `PinBarNotificationsStrategy` 
- `optimize_eurusd_daily_forecast.py` - optimization of strategy `EurUsdDailyForecastStrategy` (finding best parameters)
- `trading_debug_trading.py` - strategy `DebugTradingStrategy` reads the file and take signals from it. I use it to test sending orders to the market.
- `trading_eurusd_daily_forecast.py` - trading a strategy `EurUsdDailyForecastStrategy` 
- `trading_eurusd_mac.py` - trading a strategy `MovingAverageCrossStrategy`

#### Installation
The platform is tested on Python 3.6. 
You can install all requirements by the command: `pip install -r requirements.txt`

#### Example of usage

##### Notify when PinBar appears on eurusd, eurjpy or gbpusd   
```
nohup python3.6 notifications_pinbar_oanda.py -s eurusd eurjpy gbpusd  -o trading_output/ --time_frame H4   > logs/main_log.log  2> logs/main_log_error.log &
```

##### Test `EurUsdDailyForecastStrategy` strategy on historical data using trained machine learning model
```
python3.6 backtest_eurusd_daily_forecast.py -d data/M15/2011-2015/ -s eurusd -c 10000 -b 2011-01-01T00:00:00 \
	-o /backtest_output --trained_model_file model.pkl --stop_loss 50 --take_profit 10 --short_window 9 --long_window 100
```

#### Disclaimer
Usage of this tool is on your own risk. I'm using it for my trading, but the platform is still under development. 



