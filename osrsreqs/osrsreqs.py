import requests
import json

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
    url = "https://prices.runescape.wiki/api/v1/osrs/latest?id=" + id
    response = requests.get(url, headers = headers)

    # process pulled data
    data_raw = response.json()
    data = data_raw['data'][str(id)]

    return data

