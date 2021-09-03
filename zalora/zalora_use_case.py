#!/usr/bin/env python
# coding: utf-8

# ### Import required libraries

# In[ ]:


import requests
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt


# ### Download file 

# In[ ]:


print("downloading the data file from api.")
url_link = "https://storage.googleapis.com/zalora-interview-data/bitstampUSD_1-min_data_2012-01-01_to_2020-09-14.csv"

req = requests.get(url_link)
url_content = req.content

csv_file = open('bitstampUSD_1-min_data_2012-01-01_to_2020-09-14.csv', 'wb')

csv_file.write(url_content)
csv_file.close()
print("data file download complete")


# ### Read file in pandas dataframe

# In[ ]:


data_df = pd.read_csv("bitstampUSD_1-min_data_2012-01-01_to_2020-09-14.csv")

print(data_df.shape)


# In[ ]:


# convert integer timestamp into date time format

data_df['timestamp'] = pd.to_datetime(data_df.Timestamp, unit='s')


# In[ ]:


# filter the data before '2012-01-01'

df = data_df[data_df['timestamp'] >= datetime.strptime('2012-01-01','%Y-%m-%d')]


# In[ ]:


# records that are of before '2012-01-01'

data_df.shape[0] - df.shape[0]


# In[ ]:


df['dates'] = df['timestamp'].dt.date


# In[ ]:


df = df[['dates','Weighted_Price']]

moving_avg = df.groupby(['dates']).mean()


# ### Simple moving average (SMA)

# A moving average, also called as rolling average or running average is a used to analyze the time-series data by calculating a series of averages of the different subsets of full dataset.
# 
# The simple moving average = (sum of the an asset price over the past n periods) / (number of periods)

# In[ ]:


moving_avg['50_SMA'] = moving_avg['Weighted_Price'].rolling(window=50, min_periods=1).mean()
moving_avg['100_SMA'] = moving_avg['Weighted_Price'].rolling(window=100, min_periods=1).mean()


# In our existing pandas dataframe, created a new column ‘Signal’ such that if 50-day SMA is greater than 100-day SMA then set Signal value as 1 else when 100-day SMA is greater than 50-day SMA then set it’s value as 0.

# In[ ]:


moving_avg['signal'] = 0.0
moving_avg['signal'] = np.where(moving_avg['50_SMA'] > moving_avg['100_SMA'], 1.0, 0.0)


# From these ‘Signal’ values, the position orders can be generated to represent trading signals. Crossover happens when the faster moving average and the slower moving average cross

# In[ ]:


moving_avg['position'] = moving_avg['signal'].diff()


# #### plot the graph to see buying and selling signal
'''plt.figure(figsize = (20,10))

moving_avg['Weighted_Price'].plot(color = 'k', label= 'Weighted Price') 
moving_avg['50_SMA'].plot(color = 'b',label = '50-day SMA') 
moving_avg['100_SMA'].plot(color = 'g', label = '100-day SMA')
# plot ‘buy’ signals
plt.plot(moving_avg[moving_avg['position'] == 1].index, 
         moving_avg['50_SMA'][moving_avg['position'] == 1], 
         '^', markersize = 15, color = 'g', label = 'buy')
# plot ‘sell’ signals
plt.plot(moving_avg[moving_avg['position'] == -1].index, 
         moving_avg['50_SMA'][moving_avg['position'] == -1], 
         'v', markersize = 15, color = 'r', label = 'sell')
plt.ylabel('Weighted Price', fontsize = 15 )
plt.xlabel('Date', fontsize = 15 )
plt.title('BITCOIN - SMA Crossover', fontsize = 20)
plt.legend()
plt.grid()
plt.show()'''
# ### Final output is saved as CSV

# In[ ]:


buy_signal = moving_avg[(moving_avg['position'] == 1.0)].reset_index()[['dates','Weighted_Price']]
buy_signal.columns = ['buying_date', 'buying_price']


# In[ ]:


sell_signal = moving_avg[(moving_avg['position'] == -1.0)].reset_index()[['dates','Weighted_Price']]
sell_signal.columns = ['selling_date', 'selling_price']


# ### Return on Investment

# Return on investment is calculated using below formula
# 
# ROI = ( Net Profit / Cost of the investment ) * 100

# In[ ]:


final_df = pd.concat([buy_signal, sell_signal], axis=1)

final_df['ROI in %'] = final_df.apply(lambda x: ((x['selling_price'] - x['buying_price']) / x['buying_price']) * 100, axis=1)

final_df = final_df.round(2)


# In[ ]:


final_df.to_csv("results.csv", header=True, sep=',', index=False)

print("final result.csv is saved in current running directory.")

