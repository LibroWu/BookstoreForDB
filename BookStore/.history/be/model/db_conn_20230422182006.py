from be.model import store

UNPAID = 0
PAID = 1
CANCELED = 2
SENT = 3
RECEIVED = 4

ORDER_TIMEOUT = 5

class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()

    def user_id_exist(self, user_id):
        collection = self.conn['user']
        query = {"user_id": user_id}
        result = collection.find_one(query)
        return result is not None

    def book_id_exist(self, store_id, book_id):
        collection = self.conn['store']
        query = {"store_id": store_id, "book_id": book_id}
        result = collection.find_one(query)
        return result is not None

    def store_id_exist(self, store_id):
        collection = self.conn['user_store']
        with open("./log/out.txt",'a') as f:
            f.write("\nstore_id_exist: ?"+store_id) 
        query = {"store_id": store_id} 
        result = collection.find_one(query)
        return result is not None
