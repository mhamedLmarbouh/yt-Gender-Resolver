from collections import Counter
import requests
from src.datastore.databaseService import DatabaseService
from src.services import scrapper

database_service: DatabaseService


def detect_gender(videoId: str,logger):
    res = database_service.find_by_videoId(videoId, projection={"_id": 0, "authorChannelId": 1})
    data = scrapper.get_googleplus_data(res)
    gendercount = dict(Counter(data))
    gendercount['videoId'] = videoId
    res=database_service.load_data(gendercount, collection='genderData')
    try:
        if res:
            logger.info('finished getting gender data for video '+videoId)
            postdata={'videoId':videoId,'status':'success'}
            requests.post('http://127.0.0.1:8000/youtubestats/api/v1/comments',data=postdata)
        else:
            logger.info('failed to load gender data for video ' + videoId)
            postdata = {'videoId': videoId, 'status': 'failed'}
            requests.post('http://127.0.0.1:8000/youtubestats/api/v1/gender', data=postdata)
    except Exception:
        pass