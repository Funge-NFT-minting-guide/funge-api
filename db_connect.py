from pymongo import MongoClient

from env.db_config import *


class DAO:
    def __init__(self, db_name):
        self.DB_NAME = db_name
        self.mongo = MongoClient(host=db_config['host'], port=db_config['port'], username=db_config['username'], password=db_config['password'], authSource=self.DB_NAME)[self.DB_NAME]

        
    def find(self, collection, query):
        return self.mongo[collection].find(query)

    def find_one(self, collection, query):
        return self.mongo[collection].find_one(query)

    def find_one_and_update(self, collection, query, update, sort=None, upsert=False):
        return self.mongo[collection].find_one_and_update(query, update, sort=sort, upsert=upsert)

    def insert_one(self, collection, document):
        return self.mongo[collection].insert_one(document)

    def insert_many(self, collection, documents):
        return self.mongo[collection].insert_many(documents)
