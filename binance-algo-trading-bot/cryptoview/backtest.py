import backtrader as bt
import datetime

# Define the RSI strategy
class RSIStrategy(bt.Strategy):
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=14)  # Use Backtrader's built-in RSI
        self.buy_price = None  # Track the buy price
        self.position.size = 0
        self.initial_cash = self.broker.getcash()
        self.order_number = 0
        self.buy_order = 0
        self.sell_order = 0
        self.stop_loss_hit_order = 0

    def start(self):
        # Calculate the initial position size based on initial cash and the current price
        initial_cash = self.broker.getcash()
        initial_price = self.data.close[0]
        self.buy_price = initial_price
        print(f"\n------Initial Cash: {initial_cash}, Initialized Position Size: {self.position.size}, Initial Price: {initial_price}-----")
        if initial_price > 0:  # Ensure valid price
            self.position.size = initial_cash / initial_price  # Calculate max size
            print(f"self position size: {self.position.size}")
        else:
            self.position_size = 0  # Default to 0 if price is invalid
            
    def next(self):
        # Buy condition
        if not self.position:
            if self.rsi[0] <= 40:  # Oversold
                self.buy_order += 1
                size = self.broker.getcash() / self.data.close[0]  # Calculate maximum affordable size
                self.buy(size=size)
                self.buy_price = self.data.close[0]
                print(f"\n-----------------------------------------")
                print(f"Order {self.buy_order}: BUY at {self.buy_price:.2f} (Size: {size:.2f})")

        # Sell condition (if there's an open position)
        elif self.position:
            stop_loss_margin = self.buy_price - self.data.close[0]
            stop_loss_limit = self.initial_cash * 0.01

            if stop_loss_margin >= stop_loss_limit:  # 1% Stop-loss condition
                self.stop_loss_hit_order += 1
                print(f"Order {self.stop_loss_hit_order}: STOP LOSS hit - Bought at {self.buy_price:.2f}, Sold at {self.data.close[0]:.2f}")
                self.close()

            elif self.rsi[0] >= 60 and self.data.close[0] > self.buy_price:  # Overbought condition
                self.sell_order += 1
                print(f"Order {self.sell_order}: TARGET ACHIEVED - Bought at {self.buy_price:.2f}, Sold at {self.data.close[0]:.2f}")
                self.close()


    def notify_order(self, order):
        # This method is called when an order is executed
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f"Order number: {self.sell_order} Started - Bought at {order.executed.price} (Size: {order.executed.size})")
            elif order.issell():
                print(f"Order number: {self.sell_order} Completed - Sold at {order.executed.price} (Size: {order.executed.size})")
            
                # After the order has been executed, update and print the net profit
                current_value = self.broker.getvalue()
                initial_cash = self.broker.startingcash
                net_profit = current_value - initial_cash
                print(f"Net Profit after order execution: {net_profit:.2f} (Current Value: {current_value:.2f})\n-----------------------------------------\n")


    def stop(self):
        # At the end of the backtest, print the final net profit
        final_value = self.broker.getvalue()
        net_profit = final_value - self.broker.startingcash
        print(f"\n\n-----------------------------------------\n Starting Cash: {self.broker.startingcash}\n Ending Cash: {self.broker.getcash()}\n Portfolio Value: {final_value}\n Net Profit: {net_profit:.2f}\n-----------------------------------------\n\n")
        print(f"Total Orders: {self.buy_order}, Successful Orders: {self.sell_order}, Stop Loss Hit Orders: {self.stop_loss_hit_order}")

# Initialize Cerebro
cerebro = bt.Cerebro()

# Set broker cash
cerebro.broker.setcash(10000)  # Initial cash
# cerebro.broker.setcommission(commission=0.001)  # Optional: Add a commission (e.g., 0.1%)

# Define the data feed
fromdate = datetime.datetime(2024, 1, 1)
todate = datetime.datetime(2025, 1, 1)

data = bt.feeds.GenericCSVData(
    dataname='data/2024-25_15minutes.csv',
    dtformat=2,  # Interpret datetime as Unix timestamp
    compression=15,  # 15-minute data
    timeframe=bt.TimeFrame.Minutes,
    fromdate=fromdate,
    todate=todate,
    openinterest=-1  # No open interest column
)

# print(f"Data: {data}, type: {type(data)}")
# Add the data to Cerebro
cerebro.adddata(data)

# Add the strategy
cerebro.addstrategy(RSIStrategy)

# Add Value observer to display portfolio value (used for ROI display)
# cerebro.addobserver(bt.observers.Value)

# Add analyzers
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')  # Add Returns analyzer

# Run the backtest
results = cerebro.run()

# Get the analyzer results
returns_analyzer = results[0].analyzers.returns

# Print Returns Information
print(f"Total Return: {returns_analyzer.get_analysis()['rtot']:.2%}")
print(f"Annual Return: {returns_analyzer.get_analysis()['ravg']:.2%}")
print(f"Max Drawdown: {returns_analyzer.get_analysis()['rnorm100']:.2%}")

# Plot the results with the portfolio value (ROI proxy)
cerebro.plot(style='candlestick')