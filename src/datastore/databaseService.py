from src.datastore.database import Database


class DatabaseService:
    def __init__(self, database_connection: Database, collection_name):
        self._database = database_connection
        self._collection_name = collection_name

    def find_by_videoId(self, videoId, cash=True, projection={}) -> tuple:
        '''
        :param videoId:
        :param sort:
        :param cash:
        :param
        :return resultlist,count:
        '''
        # elements to project: 1 project, 0 ignore
        projection = {"comment": 1, "original_comment": 1, "author": 1, "created_at": 1, "lang": 1, "likes": 1,
                      "_id": 0} if projection == {} else projection

        if videoId is not None and videoId != "":
            # fetch from db
            cursor = self._database.find_by_video_id(self._collection_name, videoId, projection=projection)
            # convert cursor to list
            res = list(cursor)
        else:
            res = []

        return res
