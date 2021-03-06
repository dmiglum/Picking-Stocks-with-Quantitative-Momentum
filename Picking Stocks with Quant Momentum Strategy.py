# -*- coding: utf-8 -*-
"""
Created on Sun Feb 27 15:57:09 2022

@author: Dmitriy Glumov
"""

import pandas as pd
import requests
import numpy as np
from scipy.stats import percentileofscore as score
from statistics import mean
from math import floor
import yfinance as yf

# # Set the start and end date
start_date = '2022-01-01'
end_date = '2022-02-27'
# # Set the ticker
# ticker = 'AMZN'
# # Get the data
# data = yf.download(ticker, start_date, end_date)
# # Print 5 rows
# data.tail()

# data = yf.download(ticker, start_date, end_date)


# CREATING S&P 500 SYMBOL LIST

sp500 = pd.read_csv('sp500.csv')
sp500_list = np.array(sp500['Symbol'])
print(sp500_list[:20])


#Taking first 15 values as a test
test_data = sp500_list[:15]

df = pd.DataFrame() #initiating an empty DF

for i in test_data:
    data = yf.download(i, start_date, end_date)['Close']
    #df = pd.concat(data, axis = 1, join = 'inner')
    df = df.append(data)

df = df.T #transposing DF
df.columns = test_data #adding columns


# EXTRACTING INTRADAY PRICES OF S&P 500 STOCKS

# def get_intraday_prices(symbol):
#     ticker = symbol
#     date = df[1]['date']
        
#     time = []
#     open = []
#     high = []
#     low = []
#     close = []
#     volume = []
#     number_of_trades = []
    
#     for i in range(len(df)):
#         time.append(df[i]['label'])
#         open.append(df[i]['open'])
#         high.append(df[i]['high'])
#         low.append(df[i]['low'])
#         close.append(df[i]['close'])
#         volume.append(df[i]['volume'])
#         number_of_trades.append(df[i]['numberOfTrades'])
        
#     time_df = pd.DataFrame(time).rename(columns = {0:'Time'})
#     open_df = pd.DataFrame(open).rename(columns = {0:'Open'})
#     high_df = pd.DataFrame(high).rename(columns = {0:'High'})
#     low_df = pd.DataFrame(low).rename(columns = {0:'Low'})
#     close_df = pd.DataFrame(close).rename(columns = {0:'Close'})
#     volume_df = pd.DataFrame(volume).rename(columns = {0:'Volume'})
#     number_of_trades_df = pd.DataFrame(number_of_trades).rename(columns = {0:'Number of Trades'})
     
#     frames = [time_df, open_df, high_df, low_df, close_df, volume_df, number_of_trades_df]
#     df = pd.concat(frames, axis = 1, join = 'inner')
#     df = df.set_index('Time')
#     return df
  
#   df = pd.DataFrame(columns = sp500_list)
  
# for i in df.columns:
#     try:
#         df[i] = get_intraday_prices(i)['Close']
#         print(f'{i} is successfully extracted')
#     except:
#         pass
 



# IMPORTING THE EXTRACTED INTRADAY DATA

sp500 = pd.read_csv('sp500.csv', index_col = 0)
print(sp500.head())

# CALCULATING DAY CHANGE OF STOCKS

dc = []
for i in sp500.columns:
    dc.append(sp500[i].pct_change().sum())
    
    
sp500_momentum = pd.DataFrame(columns = ['symbol', 'day_change'])
sp500_momentum['symbol'] = sp500.columns
sp500_momentum['day_change'] = dc

# CALCULATING MOMENTUM

sp500_momentum['momentum'] = 'N/A'
for i in range(len(sp500_momentum)):
    sp500_momentum.loc[i, 'momentum'] = score(sp500_momentum.day_change, sp500_momentum.loc[i, 'day_change'])/100
    
sp500_momentum['momentum'] = sp500_momentum['momentum'].astype(float)    
print(sp500_momentum.head())

top_picks = sp500_momentum.nlargest(10, 'momentum')['symbol'].reset_index().drop('index', axis = 1)
print(top_picks)

# BACKTEST

portfolio_val = 1000000
per_stock_val = portfolio_val/len(top_picks)

day_close = []
for i in top_picks['symbol']:
    data = sp500[i]
    day_close.append(data[-1])
    
backtest_df = pd.DataFrame(columns = ['selected_symbols', 'day_close', 'number_of_stocks', 'return', 'return_percentage'])
backtest_df['selected_symbols'] = top_picks['symbol']
backtest_df['day_close'] = day_close
for i in range(len(backtest_df)):
    backtest_df.loc[i, 'number_of_stocks'] = floor(per_stock_val/day_close[i])
    
returns = []
for i in top_picks['symbol']:
    ret = np.diff(sp500[i])
    ret = ret[~np.isnan(ret)]
    returns.append(round(sum(ret), 2))
    
backtest_returns = []
return_percentage = []
for i in range(len(backtest_df)):
    br = returns[i]*backtest_df.loc[i, 'number_of_stocks']
    rp = br/per_stock_val*100
    backtest_returns.append(round(br, 2))
    return_percentage.append(round(rp, 2))
backtest_df['return'] = backtest_returns
backtest_df['return_percentage'] = return_percentage

backtest_df