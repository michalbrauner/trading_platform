Tutorial
========

This tutorial should provide you the introduction to TradingPlatform so you can easily start to use it. Basically, tool allows you
to create your own strategies and test them on historical data. After strategies are tested, they can be easily run on your account
using connector Oanda broker.

Create new strategy
-------------------

All strategies are stored in directory :code:`strategies`. A strategy is encapsulated by one class that extends :code:`strategies.strategy.Strategy`.

You have to define method :code:`calculate_signals(self, event: Event)`. You should check this event for type :code:`MARKET`
which represents that something new came from the market.

.. code:: python

    if event.type == 'MARKET':
        symbol = event.symbol

To get last prices you can use one of these methods:

.. code:: python

    last_price = self.bars.get_latest_bar_value(symbol, 'close_bid')
    last_three_prices = self.bars.get_latest_bars_values(symbol, 'close_bid', 3)

When your strategy calculates that new position should be opened, you need to create new event :code:`SignalEvent` and insert it into queue:

.. code:: python

    signal = SignalEvent(1, symbol, self.bars.get_latest_bar_datetime(s), datetime.datetime.utcnow(), 'SHORT', 1.0, stop_loss, take_profit)
    self.events_per_symbol[symbol].put(signal)



