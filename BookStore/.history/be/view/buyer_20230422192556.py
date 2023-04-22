from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.buyer import Buyer

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")


@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    books: [] = request.json.get("books")
    id_and_count = []
    for book in books:
        book_id = book.get("id")
        count = book.get("count")
        id_and_count.append((book_id, count))

    b = Buyer()
    code, message, order_id = b.new_order(user_id, store_id, id_and_count)
    return jsonify({"message": message, "order_id": order_id}), code


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    password: str = request.json.get("password")
    b = Buyer()
    code, message = b.payment(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/add_funds", methods=["POST"])
def add_funds():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    b = Buyer()
    code, message = b.add_funds(user_id, password, add_value)
    return jsonify({"message": message}), code

@bp_buyer.route("/cancel_order", methods=["POST"])
def cancel_order():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    b = Buyer()
    with open("./log/out.txt",'a') as f:
        f.write("*** #view cancel_order #1 {} \n".format("")) 
    code, message = b.cancel_order(user_id, order_id)
    with open("./log/out.txt",'a') as f:
        f.write("*** #view cancel_order #2 {} \n".format(code)) 
    return jsonify({"message": message}), code

@bp_buyer.route("/search_order", methods=["POST"])
def search_order():
    user_id = request.json.get("user_id")
    b = Buyer()
    code, message, order_list = b.search_order(user_id)
    return jsonify({"message": message, 'order_info': order_list}), code

@bp_buyer.route("/search_book", methods=["POST"])
def search_book():
    user_id = request.json.get("user_id")
    search_type = request.json.get("search_type")
    store_id = request.json.get("store_id")
    search_params = request.json.get("search_params")
    b = Buyer()
    code, message, res = b.search_book(user_id, search_type, store_id, search_params)
    with open("./log/out.txt",'a') as f:
        f.write("*** #in view search book {},{}\n".format(code,res))
    return jsonify({"message": message, "book_name":res}), code

@bp_buyer.route("/confirm_receive", methods=["POST"])
def confirm_receive():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    b = Buyer()
    code, message = b.confirm_receive(user_id, order_id)
    return jsonify({"message": message}), code