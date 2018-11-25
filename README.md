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

### Tutorial
You can follow the link https://s3-eu-west-1.amazonaws.com/tradingplatform.docs/index.html to see tutorial.

#### Disclaimer
Usage of this tool is on your own risk. I'm using it for my trading, but the platform is still under development. 



