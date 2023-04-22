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
        with open("./log/out.txt",'a') as f:
            f.write("*** #pre run \n" + str(code) + '\n')
        assert code == 200
        book_db = book.BookDB()
        # self.books = book_db.get_book_info(0, 2)
        # with open("./log/out.txt",'a') as f:
        #     f.write("*** into initialization... ")
        # code = self.seller.add_book(self.store_id, 0, b)
        for b in self.books:
            # with open("./log/out.txt",'a') as f:
            #     f.write("*** # add book {}, {}\n".format(b.title, b.price))
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200
        yield
        # do after test

    def test_ok(self):
        with open("./log/out.txt",'a') as f:
            f.write("b.books: \n")
            for b in self.books:
                f.write(str(b))
            f.write("b.books: \n")



        ### Whole Site Search
        for b in self.books:
            code, books = self.buyer.search_book(1,self.store_id,[None,None,None,None,10000])
            with open("./log/out.txt",'a') as f:
                f.write("*** #test ok #1 {},{}\n".format(code,b.title))
                if b.title in books:
                    f.write("site trap in!\n")
                else:
                    f.write("trap failed!\n")
                f.write("start assertion\n")

            assert code == 200 and b.title in books
        with open("./log/out.txt",'a') as f:
            f.write("*** after whole site search... ")
        ### Store Search

        for b in self.books:
            code, books = self.buyer.search_book(1,self.store_id,[b.title,None,None,None,1000000])
            assert code == 200 and b.title in books

    def test_error_non_exist_store_id(self):
        # assert False
        with open("./log/out.txt",'a') as f:
            f.write("***\n\nSTART test erro exist store id\n")
        for b in self.books:
            # non exist store id
            with open("./log/out.txt",'a') as f:
                f.write("book title:"+b.title+"\n")
            code = self.buyer.search_book(self,1,self.seller_id+"_x",[b.title,None,None,None,1000000])
            with open("./log/out.txt",'a') as f:
                f.write("*** #test store id {}\n".format(code))
            assert code == 513
        with open("./log/out.txt",'a') as f:
            f.write("***\n\nEND test erro exist store id\n")

    def test_error_non_exist_book_id(self):
        assert False
        code = self.buyer.search_book(self,0,None,["..........."])
        with open("./log/out.txt",'a') as f:
            f.write("*** #test book id {}\n".format(code))
        assert code == 515


