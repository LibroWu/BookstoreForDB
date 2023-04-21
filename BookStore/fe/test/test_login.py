import time

import pytest

from fe.access import auth
from fe import conf


class TestLogin:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.auth = auth.Auth(conf.URL)
        # register a user
        self.user_id = "test_login_{}".format(time.time())
        self.password = "password_" + self.user_id
        self.terminal = "terminal_" + self.user_id
        assert self.auth.register(self.user_id, self.password) == 200
        yield

    def test_ok(self):
        code, token = self.auth.login(self.user_id, self.password, self.terminal)
        with open('/mnt/e/大三下/DB/BookstoreForDB/BookStore/log/out.txt','a') as f:
            f.write("*** start test_ok" + str(code)+ '\n')
    
        assert code == 200

        code = self.auth.logout(self.user_id + "_x", token)
        
        with open('/mnt/e/大三下/DB/BookstoreForDB/BookStore/log/out.txt','a') as f:
            f.write("*** start test_ok" + str(code)+ '\n')
        assert code == 401

        code = self.auth.logout(self.user_id, token + "_x")
        with open('/mnt/e/大三下/DB/BookstoreForDB/BookStore/log/out.txt','a') as f:
            f.write("*** start test_ok" + str(code)+ '\n')
        assert code == 401

        code = self.auth.logout(self.user_id, token)
        with open('/mnt/e/大三下/DB/BookstoreForDB/BookStore/log/out.txt','a') as f:
            f.write("*** start test_ok" + str(code)+ '\n')
        assert code == 200

    def test_error_user_id(self):
        code, token = self.auth.login(self.user_id + "_x", self.password, self.terminal)
        assert code == 401

    def test_error_password(self):
        code, token = self.auth.login(self.user_id, self.password + "_x", self.terminal)
        assert code == 401
