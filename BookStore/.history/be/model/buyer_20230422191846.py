import pymongo
import uuid
import json
import time
import logging
from be.model import error
from be.model.db_conn import *

class Buyer(DBConn):
    def __init__(self):
        DBConn.__init__(self)
        self.last_clear_time = 0 #int(time.time())

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id, )
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id, )
            self.__clear_unpaid_orders()
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            for book_id, count in id_and_count:
                collection = self.conn['store']
                query = {"store_id": store_id, "book_id": book_id}
                result = collection.find_one(query)
                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id, )
                stock_level = result["stock_level"]
                #book_info = result["book_info"]
                #book_info_json = json.loads(book_info)
                #price = book_info_json.get("price")
                price = result['price']
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
                "user_id": user_id,
                "state": UNPAID,
                "timestamp": int(time.time())
            })
            
            collection = self.conn['unpaid_order']
            collection.insert_one({
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id,
                "timestamp": int(time.time())
            })
            order_id = uid
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, "ok", order_id

    def __clear_unpaid_orders(self):
        now = int(time.time())
        if  now - self.last_clear_time > int(ORDER_TIMEOUT/2):
            self.last_clear_time = int(time.time())

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            orders = self.conn["new_order"]
            order = orders.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)
            if order['state']!=UNPAID:
                return error.error_invalid_order_state(order_id)
            self.__clear_unpaid_orders()
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

            #orders.delete_one({"order_id": order_id})
            #if orders.find_one({"order_id": order_id}):
            #    return error.error_invalid_order_id(order_id)
            orders.update_one({"order_id": order_id}, {"$set": {"state": PAID}})

            #order_details.delete_many({"order_id": order_id})
            #if order_details.find_one({"order_id": order_id}):
            #    return error.error_invalid_order_id(order_id)

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

    def __cancel_and_restore_stock(self, order_id, order = None):
        orders = self.conn['new_order']
        if order == None:
            order = order.find_one({'order_id':order_id})
        orders.update_one({"order_id": order_id}, {"$set": {"state": CANCELED}})
        order_details = self.conn["new_order_detail"]
        collection = self.conn['store']
        for detail in order_details.find({"order_id": order_id}):
            collection.update_many(
                {"store_id": order["store_id"], "book_id": detail["book_id"]},
                {"$inc": {"stock_level": detail["count"]}}
            )
            

    def confirm_receive(self, user_id, order_id) -> (int, str):
        try:
            with open("./log/out.txt",'a') as f:
                f.write("*** rc0 {} \n")
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            with open("./log/out.txt",'a') as f:
                f.write("*** rc1 {} \n")
            orders = self.conn["new_order"]
            order = orders.find_one({"order_id": order_id, 'user_id':user_id})
            with open("./log/out.txt",'a') as f:
                f.write("*** rc2 {} \n")
            if order == None:
                return error.error_invalid_order_id(order)
            if order["state"] != SENT:
                return error.error_invalid_order_state(order_id)
            with open("./log/out.txt",'a') as f:
                f.write("*** rc3 {} \n")
            orders.update_one({"order_id": order_id}, {"$set": {"state": RECEIVED}})
            with open("./log/out.txt",'a') as f:
                f.write("*** rc4 {} \n")
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, 'ok'

    def cancel_order(self, user_id, order_id) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            orders = self.conn["new_order"]
            mul_order = orders.find({"order_id": order_id, 'user_id':user_id})
            for order in mul_order:
                with open("./log/out.txt",'a') as f:
                    f.write("*** #711111 {} \n".format(order['state']))
                if order["state"] != UNPAID:
                    return error.error_invalid_order_state(order_id)
                self.__cancel_and_restore_stock(order_id, order)
            
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, 'ok'
    
    def search_order(self, user_id):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            with open("./log/out.txt",'a') as f:
                f.write("*** #4s441 {} \n".format("")) 
            orders = self.conn["new_order"]
            research_list = orders.find({'user_id':user_id})
            with open("./log/out.txt",'a') as f:
                f.write("*** #4s442 {} \n".format("")) 
            res = []
            for order in research_list:
                with open("./log/out.txt",'a') as f:
                    f.write("*** #4s442 {} \n".format(""))
                if order['state']==UNPAID and (int(time.time())-order['timestamp']>ORDER_TIMEOUT):
                    self.__cancel_and_restore_stock(order['order_id'],order)
                    order['state'] = CANCELED
                res.append([order['order_id'],order['state']])
            with open("./log/out.txt",'a') as f:
                f.write("*** #4s444 {} \n".format(len(res))) 
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, 'ok', res
    
    # search_params: [ #title, #tag, #content, #price_lower_bound, #price_upper_bound]
    def search_book(self, user_id, search_type, store_id, search_params):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            with open("./log/out.txt",'a') as f:
                f.write("condition init\n")

            if not self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            with open("./log/out.txt",'a') as f:
                f.write("condition init\n")
            books = self.conn["store"]
            condition = []
            
            with open("./log/out.txt",'a') as f:
                f.write("condition init\n")

            if search_params[0]!=None:
                condition.append({'title': {"$regex":f'.*{search_params[0]}.*'}})
                #condition.append({'title': search_params[0]})
            if search_params[1]!=None:
                condition.append({'tag': {"$in": search_params[1].split(',')}})
            if search_params[2]!=None:
                condition.append({'content':{"$regex":".*"+search_params[2]+".*"}})
            if search_params[3]!=None:
                #condition.append({'price': {"$in": [search_params[3],search_params[4]]}})
                condition.append({'price': {"$in": {'$gte': search_params[3], '$lte': search_params[4]}}})

            with open("./log/out.txt",'a') as f:
                f.write("param over\n")

            if search_type==0:
                condition = {'$or':condition}
                #condition = condition[0]
                with open("./log/out.txt",'a') as f:
                    f.write("*** #in search book final {}\n".format(condition))
                search_list = books.find(condition, {'title':1})
            else:
                condition.append({'store_id':store_id})
                condition = {'$or':condition}
                search_list = books.find(condition, {'title':1})
            search_list = [item['title'].encode().decode('unicode_escape').strip('"') for item in search_list]
            with open("./log/out.txt",'a') as f:
                f.write("*** #in search book final {},{}\n".format(search_list, condition))
            if len(search_list) == 0: 
                with open("./log/out.txt",'a') as f:
                    f.write("*** ????".format(search_list, condition))
                return error.error_non_exist_book_id("Querying One")
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        return 200, 'ok', search_list