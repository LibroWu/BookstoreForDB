from be.model import error
from be.model.store import Store
from be.model.db_conn import *
import json

class Seller(DBConn):
    def __init__(self):
        DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            with open("./log/out.txt",'a') as f:
                f.write("*** #0 \n")
            book_json = json.loads(book_json_str)
            with open("./log/out.txt",'a') as f:
                f.write("*** #1 \n")
            store_collection = self.conn['store']
            store_doc = {
                'store_id': store_id,
                'book_id': book_id,
                'book_info': book_json_str,
                'stock_level': stock_level,
                'tag': book_json['tags'],
                'content': book_json['content'],
                'title': book_json['title'],
                'price': book_json['price']
            }
            with open("./log/out.txt",'a') as f:
                f.write("*** #2 \n")
            store_collection.insert_one(store_doc)
            with open("./log/out.txt",'a') as f:
                f.write("*** #3 \n")
        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            store_collection = self.conn['store']
            query = {"store_id": store_id, "book_id": book_id}
            store_collection.update_one(query, {"$inc": {"stock_level": add_stock_level}})
        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            user_store_collection = self.conn['user_store']
            user_store_doc = {'store_id': store_id, 'user_id': user_id}
            user_store_collection.insert_one(user_store_doc)
        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def confirm_send(self, user_id: str, order_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            orders = self.conn["new_order"]
            order = orders.find_one({"order_id": order_id, 'user_id':user_id})
            if order == None:
                return error.error_invalid_order_id(order)
            if order["state"] != PAID:
                return error.error_invalid_order_state(order_id)
            orders.update_one({"order_id": order_id}, {"$set": {"state": SENT}})
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, 'ok'