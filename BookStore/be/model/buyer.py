import pymongo
import uuid
import json
import logging
from be.model import error
from be.model.db_conn import DBConn


class Buyer(DBConn):
    def __init__(self):
        DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id, )
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id, )
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            for book_id, count in id_and_count:
                collection = self.conn['store']
                query = {"store_id": store_id, "book_id": book_id}
                result = collection.find_one(query)
                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id, )
                stock_level = result["stock_level"]
                book_info = result["book_info"]
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                res_update = collection.update_many(
                    {"store_id": store_id, "book_id": book_id, "stock_level": {"$gte": count}},
                    {"$inc": {"stock_level": -count}}
                )
                
                if res_update.modified_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id, )
                
                collection = self.conn['new_order_detail']
                collection.insert_one({
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                })
            collection = self.conn['new_order']
            collection.insert_one({
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id
            })
            order_id = uid
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            orders = self.conn["new_order"]
            order = orders.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            buyer_id = order["user_id"]
            store_id = order["store_id"]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            users = self.conn["user"]
            user = users.find_one({"user_id": buyer_id})
            if user is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = user["balance"]
            if password != user["password"]:
                return error.error_authorization_fail()

            stores = self.conn["user_store"]
            store = stores.find_one({"store_id": store_id})
            if store is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = store["user_id"]
            
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            order_details = self.conn["new_order_detail"]
            total_price = 0
            for detail in order_details.find({"order_id": order_id}):
                count = detail["count"]
                price = detail["price"]
                total_price += price * count
            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            users.update_one({"user_id": buyer_id, "balance": {"$gte": total_price}}, {"$inc": {"balance": -total_price}})
            if not users.find_one({"user_id": buyer_id, "balance": {"$gte": 0}}):
                return error.error_not_sufficient_funds(order_id)

            users.update_one({"user_id": seller_id}, {"$inc": {"balance": total_price}})

            orders.delete_one({"order_id": order_id})
            if orders.find_one({"order_id": order_id}):
                return error.error_invalid_order_id(order_id)

            order_details.delete_many({"order_id": order_id})
            if order_details.find_one({"order_id": order_id}):
                return error.error_invalid_order_id(order_id)

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
    
    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            user = self.conn['user'].find_one({"user_id": user_id})
            if user is None:
                return error.error_non_exist_user_id(user_id)

            if user["password"] != password:
                return error.error_authorization_fail()

            result = self.conn['user'].update_one({"user_id": user_id}, {"$inc": {"balance": add_value}})

            if result.modified_count == 0:
                return error.error_non_exist_user_id(user_id)

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
