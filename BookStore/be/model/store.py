import logging
from pymongo import MongoClient


class Store:
    def __init__(self, db_uri):
        self.client = MongoClient(db_uri)
        self.db = self.client["bookstore"]
        self.init_collections()

    def init_collections(self):
        self.user_collection = self.db["user"]
        self.user_collection.create_index("user_id", unique=True)

        self.user_store_collection = self.db["user_store"]
        self.user_store_collection.create_index([("user_id", 1), ("store_id", 1)], unique=True)

        self.store_collection = self.db["store"]
        self.store_collection.create_index([("store_id", 1), ("book_id", 1)], unique=True)

        self.new_order_collection = self.db["new_order"]
        self.new_order_collection.create_index("order_id", unique=True)

        self.new_order_detail_collection = self.db["new_order_detail"]
        self.new_order_detail_collection.create_index([("order_id", 1), ("book_id", 1)], unique=True)

    def get_user(self, user_id):
        return self.user_collection.find_one({"user_id": user_id})

    def create_user(self, user_id, password, balance, token=None, terminal=None):
        user = {"user_id": user_id, "password": password, "balance": balance}
        if token:
            user["token"] = token
        if terminal:
            user["terminal"] = terminal
        self.user_collection.insert_one(user)

    def update_user(self, user_id, update_dict):
        self.user_collection.update_one({"user_id": user_id}, {"$set": update_dict})

    def get_user_stores(self, user_id):
        return [us["store_id"] for us in self.user_store_collection.find({"user_id": user_id})]

    def add_user_store(self, user_id, store_id):
        self.user_store_collection.insert_one({"user_id": user_id, "store_id": store_id})

    def remove_user_store(self, user_id, store_id):
        self.user_store_collection.delete_one({"user_id": user_id, "store_id": store_id})

    def get_store_books(self, store_id):
        return [book for book in self.store_collection.find({"store_id": store_id})]

    def get_book_stock_level(self, store_id, book_id):
        book = self.store_collection.find_one({"store_id": store_id, "book_id": book_id})
        if book:
            return book["stock_level"]
        else:
            return None

    def update_book_stock_level(self, store_id, book_id, stock_level):
        self.store_collection.update_one({"store_id": store_id, "book_id": book_id}, {"$set": {"stock_level": stock_level}})

    def create_new_order(self, order_id, user_id, store_id):
        self.new_order_collection.insert_one({"order_id": order_id, "user_id": user_id, "store_id": store_id})

    def add_order_detail(self, order_id, book_id, count, price):
        self.new_order_detail_collection.insert_one({"order_id": order_id, "book_id": book_id, "count": count, "price": price})

    def get_order_details(self, order_id):
        return [od for od in self.new_order_detail_collection.find({"order_id": order_id})]


database_instance: Store = None

def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()