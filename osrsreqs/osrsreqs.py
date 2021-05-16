import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# set user-agent function
def set_user_agent():
    headers = {
        'User-Agent': 'display live prices - OSLivePrice#7410'
    }
    return headers

# get latest prices
def get_latest(id):

    # pull data
    headers = set_user_agent()
    url = "https://prices.runescape.wiki/api/v1/osrs/latest?id=" + str(id)
    response = requests.get(url, headers = headers)
    print(response)

    # process pulled data
    data_raw = response.json()
    data = data_raw['data']

    return data

# get the file with all latest prices
def get_latest_all():

    # pull data
    headers = set_user_agent()
    url = "https://prices.runescape.wiki/api/v1/osrs/latest"
    response = requests.get(url, headers = headers)
    print(response)

    data_raw = response.json()
    data = data_raw['data']

    return data

# get 5-minute time series on a 4-hr scale
def get_five_min(id, live_ts):                # time is a unix timestamp

    # pull data
    headers = set_user_agent()
    url = "https://prices.runescape.wiki/api/v1/osrs/timeseries?timestep=5m&id=" + str(id)
    response = requests.get(url, headers = headers)
    print(response)

    data_raw = response.json()
    data = data_raw['data']

    df = pd.DataFrame(data)

    for i, ts in enumerate(df['timestamp']):
        if ts < (live_ts - 14400):
            df = df.drop([i])
        
    df_4h = df.reset_index(drop = True)

    for i, dt in enumerate(df_4h['timestamp']):
        df_4h['timestamp'][i] = pd.Timestamp(dt, unit ='s')
    
    return df_4h