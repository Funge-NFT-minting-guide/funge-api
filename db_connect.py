from pymongo import MongoClient

from env.db_config import *


class FungeDAO:
    def __init__(self):
        self.DB_NAME = 'funge'
        self.mongo = MongoClient(host='localhost', port=db_config['port'], username=db_config['username'], password=db_config['password'], authSource=self.DB_NAME)[self.DB_NAME]

        
    def find(self, collection, query):
        return self.mongo[collection].find(query)

    def insert_one(self, collection, document):
        return self.mongo[collection].insert_one(document)

    def insert_many(self, collection, documents):
        return self.mongo[collection].insert_many(documents)
