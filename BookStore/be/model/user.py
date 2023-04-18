import jwt
import time
import logging
import sqlite3 as sqlite
from be.model import error
from be.model import db_conn

class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:

    def register(self, user_id: str, password: str):

    def check_token(self, user_id: str, token: str) -> (int, str):

    def check_password(self, user_id: str, password: str) -> (int, str):

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):

    def logout(self, user_id: str, token: str) -> bool:

    def unregister(self, user_id: str, password: str) -> (int, str):
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
    

