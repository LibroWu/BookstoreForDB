import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid


class TestSearchOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_new_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_new_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        yield


    def test_ok(self):
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False, buy_all= False)
        assert ok
        code, order1 = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        code, order2 = self.buyer.new_order(self.store_id, buy_book_id_list)
        with open("./log/out.txt",'a') as f:
            f.write("*** #4443 {} \n".format(code)) 
        assert code == 200
        code, orders = self.buyer.search_order()
        
        assert code == 200 and sorted([order1,order2]) == sorted([order[0] for order in orders])
        
        
        
        
