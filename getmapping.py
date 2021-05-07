import requests
import json
import os

url = 'https://prices.runescape.wiki/api/v1/osrs/mapping'

headers = {                                         # set user-agent
    'User-Agent': 'OSLivePrice - Rene#4136'
}

response = requests.get(url, headers=headers)       # pull the data
data = response.json()                              # jsonify data

with open('id_mapping.json', 'w') as id_mapping:    # dump to json
    if not os.path.exists('id_mapping.json'):
        json.load(id_mapping)                       # load the file...

    id_mapping.seek(0)                              # move cursor to front to overwrite
    json.dump(data, id_mapping, indent = 4)                     # dump to json file
    id_mapping.truncate()                           # delete excess (if any)
