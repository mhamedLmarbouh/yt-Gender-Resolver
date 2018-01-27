import json

import requests
from googleapiclient.discovery import build

with open('./configuration/api_config.json', 'r') as conf:
    api = json.load(conf)

service = build(api["youtube"]["name"], api["youtube"]["version"], developerKey=api["youtube"]["key"],
                cache_discovery=False)
peoplebaseurl = "https://content-people.googleapis.com/v1/"
gpbaseurl = 'https://www.googleapis.com/plus/v1/people/'


def channels_withgp(youtubeids):
    channelswithgp = []
    res = service.channels().list(
        part='status',
        id=','.join(map(lambda id: id["authorChannelId"], youtubeids)),
        maxResults=50
    ).execute()
    for item in res["items"]:
        if item["status"]["isLinked"]:
            channelswithgp.append(item["id"])
    return channelswithgp


#
# def gp_personnaldata(gpid, personalFields: list = ['genders']) -> list:
#     global peoplebaseurl, api
#     url = peoplebaseurl + "people/" + gpid
#     url += "?personFields=" + ",".join(personalFields)
#     url += "&key=" + api["people"]["key"]
#     res = requests.get(url).json()
#     if "genders" in res.keys():
#         return res["genders"][0]["value"]
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
