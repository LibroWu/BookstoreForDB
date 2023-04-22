import pytest


from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid
import time

class TestNewOrder:
    buy_book_info_list: [Book]
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_new_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_new_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        
        
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_id_list = buy_book_id_list
        self.buy_book_info_list = self.gen_book.buy_book_info_list
        assert ok
        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num
        yield


    def test_ok(self):
        with open("./log/out.txt",'a') as f:
            f.write("*** #test ok {} \n".format(""))
        code = self.buyer.cancel_order(self.order_id)
        assert code == 200
        code, orders = self.buyer.search_order()
        assert code == 200 and self.order_id not in orders
        with open("./log/out.txt",'a') as f:
            f.write("*** #test ok  return{} \n".format(""))

    def test_out_dated(self):
        #with open("./log/out.txt",'a') as f:
        #    f.write("*** #test_out-dated {} \n".format(""))
        #code, orderId = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        #with open("./log/out.txt",'a') as f:
        #    f.write("*** #111111 {} \n".format(code))
        #assert code == 200
        time.sleep(8)
        code, orders = self.buyer.search_order()
        with open("./log/out.txt",'a') as f:
            f.write("*** #211111 {},{} \n".format(code, orders))
        assert code == 200 and self.order_id not in orders
    
    def test_status_error(self):
        #code, orderId = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        #with open("./log/out.txt",'a') as f:
        #    f.write("*** #311111 {} \n".format(code))
        #assert code == 200
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.order_id)
        assert code == 520

