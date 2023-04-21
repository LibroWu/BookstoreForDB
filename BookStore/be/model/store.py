import logging
from pymongo import MongoClient
import os
from urllib.parse import quote

class Store:
    def __init__(self, db_uri):
        # self.client = MongoClient('mongodb://be.db')
        self.client = MongoClient('mongodb://localhost:27017/')

        self.db = self.client["bookstore"]
        self.init_collections()

    def init_collections(self):
        self.user_collection = self.db["user"]
        self.user_collection.create_index("user_id", unique=True)

        self.user_store_collection = self.db["user_store"]
        self.user_store_collection.create_index([("user_id", 1), ("store_id", 1)], unique=True)

        self.store_collection = self.db["store"]
        self.store_collection.create_index([("store_id", 1), ("book_id", 1)], unique=True)
        #self.store_collection.create_index('price', unique=False)
        #self.store_collection.create_index('title', unique=False)
        #self.store_collection.create_index('content', unique=False)

        self.new_order_collection = self.db["new_order"]
        self.new_order_collection.create_index([("order_id",1),("store_id",1),("user_id",1)], unique=True)

        self.new_order_detail_collection = self.db["new_order_detail"]
        self.new_order_detail_collection.create_index([("order_id", 1), ("book_id", 1)], unique=True)

        self.new_order_detail_collection = self.db["unpaid_order"]
        self.new_order_collection.create_index([("order_id",1), ("timestamp",1)], unique=True)


    def get_db_conn(self):
        return self.db

database_instance: Store = None

def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()