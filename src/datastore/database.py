import pymongo as mongo


class Database:

    def __init__(self, configuration):
        """

        :param configuration:
        :param logger:
        """
        try:
            self._client = mongo.MongoClient(configuration['hostname'], configuration['port'])
            self._db = self._client[configuration['bdname']]
        except mongo.errors.PyMongoError:
            raise Exception('Error initializing database')

    def create_store(self, collection_name):
        """
        this method create a collection in mongodb database
        :param collection_name: the collection name
        """
        try:
            mongo.collection.Collection(self._db, collection_name, create=True)
        except mongo.errors.PyMongoError:
            raise Exception('collection already exist')

    def insert(self, collection_name, item):
        """
        :param collection_name:
        :param item:
        :return :generated for keys of inserted elements if success else false
        """
        try:
            return self._db[collection_name].insert_one(item)
        except mongo.errors.PyMongoError:
            raise Exception('failed to insert data')

    def find_by_video_id(self, collection_name, video_id, projection={}):
        """
        :param collection_name:
        :param video_id:
        :param kvargs: {"key":val,...}possible key="comment","videoId","created_at","author", "lang", "likes","_id"
        possible val:1 to fetch,0 to ignore
        :return:
        """
        try:
            return self._db[collection_name].find({'videoId': video_id}, projection)
        except mongo.errors.PyMongoError:
            raise Exception('failed to find video by id')
