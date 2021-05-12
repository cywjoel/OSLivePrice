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
