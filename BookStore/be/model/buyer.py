import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):

    def add_funds(self, user_id, password, add_value) -> (int, str):
        
