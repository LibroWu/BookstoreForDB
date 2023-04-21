import pytest
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid


class TestSearchBook:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.seller_id = "test_add_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_add_books_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_payment_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        code = self.seller.create_store(self.store_id)
        assert code == 200
        book_db = book.BookDB()
        self.books = book_db.get_book_info(0, 2)

        yield
        # do after test

    def test_ok(self):
        ### Whole Site Search
        for b in self.books:
            code, books = self.buyer.search_book(self,0,None,[b.title])
            assert code == 200 and b in books
        ### Store Search
        for b in self.books:
            code, books = self.buyer.search_book(self,1,self.store_id,[b.title])
            assert code == 200 and b in books

    def test_error_non_exist_store_id(self):
        for b in self.books:
            # non exist store id
            code = self.buyer.search_book(self,1,self.seller_id+"_x",[b.title])
            assert code == 513

    def test_error_non_exist_book_id(self):
        code = self.buyer.search_book(self,0,None,["..........."])
        assert code == 515


