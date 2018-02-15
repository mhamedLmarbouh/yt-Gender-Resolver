import json

import requests
from googleapiclient.discovery import build

with open('./configuration/api_config.json', 'r') as conf:
    api = json.load(conf)

gpbaseurl = 'https://www.googleapis.com/plus/v1/people/'





def gp_personnaldata(gpid):
    global gpbaseurl, api
    jsonres = requests.get(gpbaseurl + gpid, params=api["people"]).json()
    data = _prepare_data(jsonres)
    if data:
        return data


def _prepare_data(data):
    try:
        return data['gender']
    except KeyError:
        return ""
