import logging
from datetime import datetime as dt

from src.datastore.database import Database


class DatabaseService:
    def __init__(self, database_connection: Database, collection_name, logger=None):
        self._logger = logger or logging.getLogger(__name__)
        self._database = database_connection
        self._collection_name = collection_name
        self._last_videoId: str = None
        self._last_find_result: list = None
        self._last_find_count = 0
        self._last_projection: dict = None

    def load_data(self, comments:list) -> bool:
        """
        load a list to database, raise exception
        :param comments:
        :return: tr
        """
        self._logger.info('starting to load data')
        try:
            # if comments not empty
            if comments:
                comm, cnt = self.find_by_videoId(comments[0]["videoId"], cash=True)
                if cnt == 0 or (dt.now() - comments[0]["created_at"]).days > 1:
                    # try to create collection and index
                    self.verify_collection_existence()
                    # insert data
                    self._database.insert(self._collection_name, comments)
                    self._logger.info('finished loading data')
                    return True
                else:
                    # data already exists
                    raise Exception("comments for this video were loaded less then a day ago")
            else:
                # comments list is empty
                return False
        except Exception as e:
            # Error occurred while inserting comments
            raise e

    def verify_collection_existence(self) -> None:
        try:
            self._database.create_store(self._collection_name)
        except Exception as e:
            self._logger.warning(str(e))
            pass
        try:
            self._database.create_text_index(self._collection_name, "comment")
        except Exception as e:
            self._logger.warning(str(e))
            pass

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

        # if videoid is the same as last one return last result
        if cash and videoId == self._last_videoId and self._last_projection == projection:
            res = self._last_find_result, self._last_find_count

        elif videoId is not None and videoId != "":
            # fetch from db
            cursor = self._database.find_by_video_id(self._collection_name, videoId, projection=projection)
            # convert cursor to list
            result_list = list(cursor)
            # length of results
            count = result_list.count()

            # optimize research by saving the last search result if cash is true
            self._cash_result(cash, count, projection, result_list, videoId)

            res = result_list, count

        else:
            res = [], 0

        return res

    def find_expression(self, expression: str, videoId: str, words_number: int, caseSensitive: bool = False) -> tuple:
        try:
            result: any
            if words_number == 1:
                result = self._database.find_by_query(
                    self._collection_name,
                    {
                        '$text': {'$search': expression, '$caseSensitive': caseSensitive},
                        'videoId': videoId
                    }
                )
            elif words_number > 1:
                result = self._database.find_by_query(
                    self._collection_name,
                    {
                        '$text': {'$search': '\"' + expression + '\"'},
                        'videoId': videoId
                    }
                )
            return list(result), result.count()

        except Exception as e:
            self._logger.warning(str(e))
            return [], 0

    def _cash_result(self, cash: bool, count: int, projection: dict, result_list: list, videoId: str):
        if cash:
            self._last_find_result = result_list
            self._last_videoId = videoId
            self._last_find_count = count
            self._last_projection = projection

    def _uncash_resuls(self):
        self._last_videoId: str = None
        self._last_find_result: list = None
        self._last_find_count = 0
        self._last_kvargs: dict = None
