# -*- coding: utf-8 -*-
"""
Created on Sun May 17 20:51:58 2020

@author: mihnea
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

from pyti.exponential_moving_average import exponential_moving_average as ema


#### FUNCTIONS ######

def simple_moving_average_signal (prices,fast=50,slow=200):
    
    """ Calculate slow and fast Simple Moving Averages (SMA) and identify
    crossovers (i.e. when the fast moving average crosses the slow one from
    below (bullish -> Golden Cross) and from above (bearish -> Death Cross)
    for a single commodity type"""
    
    sma_fast = prices.rolling(window = fast).mean() 
    sma_slow = prices.rolling(window = slow).mean()
    
    signal = pd.concat([sma_fast,sma_slow],axis=1) #concatenate slow SMA and fast SMA data
    signal.columns = ['SMA Fast', 'SMA Slow']
    
    signal['Signal'] = np.where(signal['SMA Slow'] < signal['SMA Fast'],1,0) # Compare Slow SMA to fast SMA and generate 1,0 signal
    signal = signal.dropna() #Discard NaN values
    signal['SMA Crossovers'] = signal['Signal'].diff() # use diff() to identify when the signal changes sign (i.e. when the two SMAs cross)
    signal.loc[signal['SMA Crossovers'] == -1, 'SMA Crossovers'] = 'Death Cross' # -1 : Fast SMA crosses slow SMA from above - bearish signal
    signal.loc[signal['SMA Crossovers'] == 1, 'SMA Crossovers'] = 'Golden Cross' # +1 : Fast SMA crosses slow SMA from below - bullish signal
    
    signal = signal[signal['SMA Crossovers'] != 0]  # Keep only observations of crossovers
    signal = signal.dropna()
    return signal

def exponential_moving_average_signal (prices,fast=50,slow=200):
    
    """Calculate slow and fast Exponential Moving Averages (EMA) and identify 
    crossovers - i.e. when the fast EMA crosses the slow EMA from below (bullish) 
    and from above (bearish) for a single commodity type
    NOTE: Computation time for this function is quite long """
    
    from pyti.exponential_moving_average import exponential_moving_average as ema # Technical analysis python library (https://pypi.org/project/pyti/)
    
    ema_fast = pd.DataFrame(ema(prices,fast),index = prices.index)
    ema_slow = pd.DataFrame(ema(prices,slow),index = prices.index)
    
    signal = pd.concat([ema_fast,ema_slow],axis=1) #concatenate slow EMA and fast EMA data
    signal.columns = ['EMA Fast', 'EMA Slow']
    
    signal['Signal'] = np.where(signal['EMA Slow'] < signal['EMA Fast'],1,0) # Compare Slow EMA to fast EMA and generate 1,0 signal
    signal = signal.dropna()
    signal['EMA Crossovers'] = signal['Signal'].diff()
    signal.loc[signal['EMA Crossovers'] == -1, 'EMA Crossovers'] = 'Death Cross' # -1 : Fast EMA crosses slow EMA from above - bearish signal
    signal.loc[signal['EMA Crossovers'] == 1, 'EMA Crossovers'] = 'Golden Cross' # +1 : Fast EMA crosses slow EMA from below - bullish signal
    
    signal = signal[signal['EMA Crossovers'] != 0] # Keep only observations of crossovers
    signal = signal.dropna()
    return signal


os.chdir(r'/Users/mihne/Desktop/MSc/Summer Term/ATS/Backtesting') # Change Directory

# Get commodities data

cmdty = pd.read_excel("Commodity Data.xlsx", sheet_name = "Return indices").set_index("date")
sectors = pd.read_excel("Commodity Data.xlsx", sheet_name = "Assets")

# Calculate daily returns
try:
    returns = pd.read_csv("Commodity_Returns.csv").set_index("date")
except FileNotFoundError:
    returns = cmdty/cmdty.shift(1)
    returns.to_csv("Commodity_Returns.csv")

# Get list of commodities in each sector
agri_livestock = [sectors["Commodity"][i] for i in range(sectors.shape[0]) if sectors["Sector"][i]=="Agri & livestock"]
energy = [sectors["Commodity"][i] for i in range(sectors.shape[0]) if sectors["Sector"][i]=="Energy"]
metals = [sectors["Commodity"][i] for i in range(sectors.shape[0]) if sectors["Sector"][i] == "Metals"]
commodities_list = agri_livestock + energy + metals

lastIndex = cmdty.shape[0] - 1  #Get index number of last observation

"""
# SMA and EMA signals for each commodity (print for now, need to store them at some point in order to trade based on the signals)
for i in commodities_list:
    sma = pd.DataFrame(simple_moving_average_signal(cmdty[i])['SMA Crossovers'])
    ema = pd.DataFrame(exponential_moving_average_signal(cmdty[i])['EMA Crossovers'])
    print(i)
    print(pd.concat([sma,ema], axis = 1))
"""

### Summary stats
summary_stats = pd.DataFrame(columns=cmdty.columns, index=['First Obs Date','No Obs','Tot Ret','Avg Ret', 'SD', 'Sharpe', 'Skew', 'Kurtosis'])
## No Obs
summary_stats.loc['No Obs'] = returns.count()
## Total Return (there's an easier way to do it since every series start at 100)
for i in commodities_list:
    summary_stats.loc['Tot Ret'][i] = \
        (cmdty.iloc[lastIndex][i] - cmdty.iloc[cmdty[i].index.get_loc(cmdty[i].first_valid_index())][i]) / \
        cmdty.iloc[cmdty[i].index.get_loc(cmdty[i].first_valid_index())][i]*100
## Date of first observation
for i in commodities_list:
    summary_stats.loc['First Obs Date'][i] = \
        cmdty.loc[cmdty[i].first_valid_index()].name.date()
## Average Return
summary_stats.loc['Avg Ret'] = (returns-1).mean()*252*100
## Standard Deviation
summary_stats.loc['SD'] = returns.std() * np.sqrt(252) * 100
## Sharpe (returns are already in excess of the risk free rate)
summary_stats.loc['Sharpe'] = summary_stats.loc['Avg Ret'] / summary_stats.loc['SD']
## Skewness
summary_stats.loc['Skew'] = returns.skew()
## Kurtosis
summary_stats.loc['Kurtosis'] = returns.kurt()


# Commodity Market Factor
CMF = pd.DataFrame(columns = ['CMF'], index = returns.index.copy())

for i in range(0,lastIndex):
    CMF.iloc[i]['CMF'] = (returns.iloc[i]-1).mean()  # Commodity Market Factor = equal weighted return of all commodities traded during a single day

# Attach CMF to returns dataframe and normalize percentages
returns = returns - 1
returns['CMF'] = CMF['CMF']
returns = returns * 100
