import numpy
import talib
from numpy import genfromtxt

my_data = genfromtxt('data/2024-25_1minutes.csv', delimiter=',')

print(my_data)

close = my_data[:,4]

print(close)
# moving_average = talib.SMA(close, timeperiod=10)

# print(moving_average)

rsi = talib.RSI(close)

print(rsi)