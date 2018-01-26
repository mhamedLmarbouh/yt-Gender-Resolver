import json

from src.datastore import database, databaseService


class DatabaseFactory:
    def __init__(self):
        self._database_connection = None

    def build(self):
        try:
            with open('../configuration/database_config.json', 'r') as config:
                database_conf = json.load(config)
            self._database_connection = database.Database(database_conf)
            return self
        except Exception as e:
            return None

    def get_database_service(self, collection_name="comments"):
        try:
            if self._database_connection is None:
                self.build()
            database_service = databaseService.DatabaseService(self._database_connection, collection_name)
            return database_service
        except Exception as e:
            return None
