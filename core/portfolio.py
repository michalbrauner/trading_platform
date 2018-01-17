from __future__ import print_function

try:
    import Queue as queue
except ImportError:
    import queue

import os
import pandas as pd
from events.order_event import OrderEvent
from events.fill_event import FillEvent
from events.close_pending_orders_event import ClosePendingOrdersEvent
from perfomance import create_sharpe_ratio, create_drawdowns
from stats import Stats
from core.position import Position


class Portfolio(object):

    """
    The Portfolio class handles the positions and market
    value of all instruments at a resolution of a "bar",
    i.e. secondly, minutely, 5-min, 30-min, 60 min or EOD.

    The positions DataFrame stores a time-index of the
    quantity of positions held.

    The holdings DataFrame stores the cash and total market
    holdings value of each symbol for a particular
    time-index, as well as the percentage change in
    portfolio total across bars.
    """

    def __init__(self, bars, events, start_date, initial_capital, output_directory, equity_filename,
                 position_size_handler):
        """
        Initialises the portfolio with bars and an event queue.
        Also includes a starting datetime index and initial capital
        (USD unless otherwise stated).
        Parameters:
        bars - The DataHandler object with current market data.
        events - The Event Queue object.
        start_date - The start date (bar) of the portfolio.
        initial_capital - The starting capital in USD.
        position_size_handler - Calculate position size for new order
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital
        self.output_directory = output_directory
        self.equity_filename = equity_filename
        self.position_size_handler = position_size_handler

        self.all_positions = self.construct_all_positions()
        self.current_positions = dict( (k,v) for k, v in \
                                       [(s, None) for s in self.symbol_list] )
        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()

    def get_current_position(self, symbol):
        # type: (str) -> Position
        return self.current_positions[symbol]

    def construct_all_positions(self):
        """
        Constructs the positions list using the start_date
        to determine when the time index will begin.
        """
        d = dict( (k,v) for k, v in [(s, None) for s in self.symbol_list] )
        d['datetime'] = self.start_date

        return [d]

    def construct_all_holdings(self):
        """
        Constructs the holdings list using the start_date
        to determine when the time index will begin.
        """
        d = dict( (k,v) for k, v in [(s, 0.0) for s in self.symbol_list] )
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital

        return [d]

    def construct_current_holdings(self):
        """
        This constructs the dictionary which will hold the instantaneous
        value of the portfolio across all symbols.
        """
        d = dict( (k,v) for k, v in [(s, 0.0) for s in self.symbol_list] )
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital

        return d

    def update_timeindex(self, event):
        """
        Adds a new record to the positions matrix for the current
        market data bar. This reflects the PREVIOUS bar, i.e. all
        current market data at this stage is known (OHLCV).
        Makes use of a MarketEvent from the events queue.
        """
        latest_datetime = self.bars.get_latest_bar_datetime(
            self.symbol_list[0]
        )
        # Update positions
        # ================
        dp = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        dp['datetime'] = latest_datetime

        for s in self.symbol_list:
            dp[s] = self.get_current_position(s)

        # Append the current positions
        self.all_positions.append(dp)

        # Update holdings
        # ===============
        dh = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for s in self.symbol_list:
            # Approximation to the real value
            position = self.get_current_position(s)
            if position is not None:
                market_value = position.get_quantity() * self.bars.get_latest_bar_value(s, "close_bid")
            else:
                market_value = 0

            dh[s] = market_value
            dh['total'] += market_value

        # Append the current holdings
        self.all_holdings.append(dh)

    def get_fill_direction_koeficient(self, fill):
        # type: (FillEvent) -> int

        fill_direction_koeficient = 0

        if fill.direction == 'BUY':
            fill_direction_koeficient = 1

        elif fill.direction == 'SELL':
            fill_direction_koeficient = -1

        return fill_direction_koeficient

    def update_positions_from_fill(self, fill):

        fill_dir = self.get_fill_direction_koeficient(fill)

        quantity = fill_dir * fill.quantity

        # Update positions list with new quantities
        position = self.get_current_position(fill.symbol)
        if position is None:
            position = Position(fill.symbol, fill.trade_id, quantity)
        else:
            position.set_quantity(position.get_quantity() + quantity)

        if position.get_quantity() == 0:
            self.current_positions[fill.symbol] = None
        else:
            self.current_positions[fill.symbol] = position

    def update_holdings_from_fill(self, fill):
        """
        Takes a Fill object and updates the holdings matrix to
        reflect the holdings value.

        Parameters:
        fill - The Fill object to update the holdings with.
        """

        # Check whether the fill is a buy or sell
        fill_dir = self.get_fill_direction_koeficient(fill)

        # Update holdings list with new quantities
        fill_cost = self.bars.get_latest_bar_value(fill.symbol, 'close_bid')
        cost = fill_dir * fill_cost * fill.quantity

        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings
        from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The tuple containing Signal information.
        """
        order = None
        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength
        mkt_quantity = self.position_size_handler.get_position_size(self.current_holdings, self.current_positions)

        position = self.get_current_position(symbol)
        if position is not None:
            cur_quantity = self.get_current_position(symbol).get_quantity()
        else:
            cur_quantity = 0

        order_type = 'MKT'

        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY', signal.stop_loss, signal.take_profit)

        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL', signal.stop_loss, signal.take_profit)

        if direction == 'EXIT' and cur_quantity != 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'EXIT', None, None, None, None,
                               signal.trade_id_to_exit)

        return order

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders
        based on the portfolio logic.
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)

            if order_event is not None:
                self.events.put(order_event)

            if event.signal_type == 'EXIT':
                close_pending_orders_event = ClosePendingOrdersEvent(event.symbol)
                self.events.put(close_pending_orders_event)

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio.
        """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']
        sharpe_ratio = create_sharpe_ratio(returns, periods=252*60*6.5)
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown

        stats = Stats((total_return - 1.0) * 100.0, sharpe_ratio, max_dd * 100.0, dd_duration)

        self.equity_curve.to_csv(os.path.join(self.output_directory, self.equity_filename))

        return stats
