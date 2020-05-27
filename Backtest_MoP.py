#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 08:30:50 2020

@author: sultanalmehairbi

Back test project, trying toimplement the MOP paper from EXCEL to python

"""
import os
os.chdir("/Users/sultanalmehairbi/Documents/Imperial/Modules/Term_3/ATS/Python_Code")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import PolynomialFeatures
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeClassifier
from sklearn.svm import LinearSVC
import scipy.stats as si
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from collections import Counter



def getData():

    
    sheetname       = ["Data","Managed futures TSMOM-12M","12 M signal lagged 1 month","11M signal lagged 1 month"]
    # levels          = ["ATM VOLS", "3M 25D RR"]
    filename        = "MOP_Edited.xlsx"
    
   # Dataframe of LOG returns on the 12 instruments and the risk-free-rate
    df_data         = pd.read_excel(filename,"Data",parse_dates=True, index_col='Dates')
    return (df_data)
    
""" ******************************************************************************************************* """

def EW_Port(df_data):
    
    """ Find average of each row in df_data"""
    """ first remove the US Cash then find average"""
    
    df_ewport    = pd.DataFrame()
    
    df_ewport ['portfolio'] = df_data.drop(['US Cash'], axis =1).mean(axis=1)
    return (df_ewport)


def df_trend (df_data):
   
   df_signal = df_data.drop(['US Cash'],axis = 1).rolling(min_periods=1, window=12).sum()
   df_signal = df_signal.tail(417-11).shift().tail(417-12)
   df_signal = df_signal < 0
   df_signal = df_signal.replace([True,False], [-1,1])
   return (df_signal)

def cont_not(df_data, df_signal):
    "finds the TSMOM with constant notional"
    df_ret    = df_signal*df_data.tail(417-12).drop(['US Cash'],axis = 1)
    return(df_ret)
    
def tsmom (df_ret):    
  # Portfolio Return
    df_ret_port = df_ret.mean(axis=1)
  # Annualized x returns
    df_ann_xret = 12 * df_ret.mean(axis=0)
  # Annualized volatility
    df_ann_vol = sqrt(12) * df_ret.std(axis=0)
  # Sharpe Ratio"
    df_sr = df_ann_xret/df_ann_vol
  # correl with ew portfolio"
    df_cor= df_ret.corrwith(df_ret_port, axis = 0)
  # Compute Porfolio Averages"
    df_port_avg= pd.DataFrame(columns = ['Portfolio Ret', 'Portfoilio vol', 'Portfolio SR'])
    a = [[df_ret_port.mean()*12, sqrt(12)*df_ret_port.std(), (df_ret_port.mean()*12)/(sqrt(12)*df_ret_port.std())]]
    df_port_avg = pd.DataFrame(a,columns = ['Portfolio Ret', 'Portfolio vol', 'Portfolio SR'])
    return (df_port_avg,df_cor, df_sr, df_ann_vol, df_ret_port)
    
def volatility(df_data):
    # Finds volatility of data
    df_vol= df_data.drop(['US Cash'],axis = 1).rolling(min_periods=1, window=12).std()*sqrt(12)
    df_vol= df_vol.shift().tail(417-12)
    return (df_vol)

def cont_risk(df_data, df_signal,df_vol):
    # finds the TSMOM with constant risk
    df_ret_2 = (df_signal*df_data.tail(417-12).drop(['US Cash'],axis = 1))*0.4/df_vol
    return(df_ret_2)

def tsmom_2 (df_ret_2, df_ret):  
   #Portfolio Return
    df_ret_port_2= df_ret_2.mean(axis=1)
   #Annualized x returns"""
    df_ann_xret_2 = 12 * df_ret_2.mean(axis=0)
   #Annualized volatility
    df_ann_vol_2 = sqrt(12) * df_ret.std(axis=0)
   # Sharpe Ratio
    df_sr_2 = df_ann_xret_2/df_ann_vol_2
   # correl with ew portfolio
    df_cor_2= df_ret_2.corrwith(df_ret_port_2, axis = 0)
   # Compute Porfolio Averages
    df_port_avg_2= pd.DataFrame(columns = ['Portfolio Ret', 'Portfoilio vol', 'Portfolio SR'])
    a_2= [[df_ret_port_2.mean()*12, sqrt(12)*df_ret_port_2.std(), (df_ret_port_2.mean()*12)/(sqrt(12)*df_ret_port_2.std())]]
    df_port_avg_2 = pd.DataFrame(a_2,columns = ['Portfolio Ret', 'Portfolio vol', 'Portfolio SR'])
    return( df_port_avg_2,df_cor_2, df_sr_2, df_ann_vol_2, df_ret_port_2)

def cum_ret(df_ret_port, df_data,df_port_avg,df_port_avg_2):
   # Find the  cumumlitive reutnr of EW portfolio and const. risk portfolio 
   # EQ scaled to Const. Vol 
    df_ewcum = pd.DataFrame().reindex_like(df_ret_port.to_frame())
    df_ewcum.iloc[0] = 1+df_data.iloc[12,0]+(df_ret_port.iloc[0]*(df_port_avg_2.iloc[0,1]/df_port_avg.iloc[0,1]))
    
    for i in range(1,df_ret_port.index.size):
        df_ewcum.iloc[i] = df_ewcum.iloc[i - 1] * (1+df_data.iloc[12+i,0]+(df_ret_port.iloc[i]*(df_port_avg_2.iloc[0,1]/df_port_avg.iloc[0,1])))
    return (df_ewcum)

def tsmom_cum(df_ret_port, df_data, df_ret_port_2):
    # Find the cumm return of the TSMOM Constant Risk
    
    df_tsmcum = pd.DataFrame().reindex_like(df_ret_port.to_frame())
    df_tsmcum.iloc[0] = 1+df_data.iloc[12,0]+df_ret_port_2.iloc[0]
    
    for i in range(1,df_ret_port.index.size):
        df_tsmcum.iloc[i] = df_tsmcum.iloc[i - 1] * (1+df_data.iloc[12+i,0]+df_ret_port_2.iloc[i])
    return (df_tsmcum)

################## START OF MAIN ###############


def main():
    getData()
    EW_Port(df_data)
    df_trend (df_data)
    cont_not(df_data, df_signal)
    tsmom (df_ret)
    volatility(df_data)
    cont_not(df_data, df_signal)
    tsmom (df_ret)
    volatility(df_data)
    cont_risk(df_data, df_signal,df_vol)
    tsmom_2 (df_ret_2, df_ret)
    cum_ret(df_ret_port, df_data,df_port_avg,df_port_avg_2)
    tsmom_cum(df_ret_port, df_data, df_ret_port_2)
    
main()









