# -*- coding: utf-8 -*-
"""
Created on Sun May 17 11:33:03 2020

@author: tomw1
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import data_summary

"""
    Get data from file
"""
data = pd.read_excel("Commodity Data.xlsx", sheet_name = "Return indices").set_index("date")
asset_sector = pd.read_excel("Commodity Data.xlsx", sheet_name = "Assets")
try:
    returns = pd.read_csv("Commodity_Returns.csv").set_index("date")
except FileNotFoundError:
    returns = data/data.shift(1)
    returns.to_csv("Commodity_Returns.csv")

"""
    Get list of commodities in each sector
"""
agri_livestock = [asset_sector["Commodity"][i] for i in range(asset_sector.shape[0]) if asset_sector["Sector"][i]=="Agri & livestock"]
energy = [asset_sector["Commodity"][i] for i in range(asset_sector.shape[0]) if asset_sector["Sector"][i]=="Energy"]
metals = [asset_sector["Commodity"][i] for i in range(asset_sector.shape[0]) if asset_sector["Sector"][i]=="Metals"]
commodities = agri_livestock + energy + metals

"""
    Summarize commodity data
"""
data_summary.summarize_data(data, commodities)

"""
    Create commodity market factor
"""
market_factor = pd.DataFrame(index=data.index)
market_factor["Return"] = returns.mean(axis=1)
market_factor["C. Return"] = market_factor["Return"].cumprod()

fig, ax1 = plt.subplots()
ax1.plot(market_factor["C. Return"])
ax1.set_xlabel("Year")
ax1.set_ylabel("Cumulative Return")
plt.show()



