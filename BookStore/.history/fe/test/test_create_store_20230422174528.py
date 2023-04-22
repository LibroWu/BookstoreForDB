import pytest

from fe.access.new_seller import register_new_seller
import uuid


class TestCreateStore:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        with open('log/out.txt','a') as f:
            f.write("*** start pre_run"+'\n')
        self.user_id = "test_create_store_user_{}".format(str(uuid.uuid1()))
        self.store_id = "test_create_store_store_{}".format(str(uuid.uuid1()))
        self.password = self.user_id
        yield

    def test_ok(self):
        self.seller = register_new_seller(self.user_id, self.password)
        
        code = self.seller.create_store(self.store_id)
        assert code == 200

    def test_error_exist_store_id(self):
        with open('log/out.txt','a') as f:
            f.write("*** start test_error\n")
        self.seller = register_new_seller(self.user_id, self.password)
        code = self.seller.create_store(self.store_id)
        
        with open('log/out.txt','a') as f:
            f.write("*** in test_error first"+ str(code)+'\n')
        assert code == 200

        code = self.seller.create_store(self.store_id)
        with open('log/out.txt','a') as f:
            f.write("*** in test_error second"+ str(code)+'\n')
        assert code != 200
