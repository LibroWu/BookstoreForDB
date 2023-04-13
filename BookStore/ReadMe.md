# Sketches Of Project

#### 环境：

需要在`Python>=3.7`环境下配置flask和pymongo，推荐用conda install将requirments里的所有包都下了

#### 前端：

已经写好，总的来说，使用flask，将请求以json形式发回后端，其中前端的链接设定在conf.py里。

#### 后端：

首先在相应端口挂起服务器，并连接至数据库，然后我们需要使用python的flask包完成接收前端数据，并返回相应输出的任务。

而将本地函数接口与flask格式关联的方法需要调用blueprint的一系列设置。blueprint简单来说就是一个路由表，将flask接口请求的url对应到相应函数。比如假设我们写好了一个login函数，而flask前段将会请求：`https://Server:port/login`，这时`/login` url就会被后端路由到login函数。blueprint作用是更好地将代码模块化。



# BackendInterface

`Blueprint()`为创建一个blueprint实例，我们需要指定其名字以及所在模块名，以及通常还会有该蓝图所对应的url前缀，假设我们创建了一个蓝图实例为：

`bp_auth = Blueprint("auth", __name__, url_prefix="/auth")`

那么第一个参数为该blueprint的名字，第二个参数为该blueprint所在模块名，第三个参数作用相当于提供一个相对路径，它与函数路由有关。

然后再该蓝图实例下，我们指定一个函数路由的方法如下：

```
from flask import request
@bp_auth.route("/login", methods=["POST"])
def login():
	user_id = request.json.get("user_id")
	return jsonify({"ok"}),code
```

若当前请求url为`https://Server:port/auth/login`时，那么该请求将会根据blueprint来到该函数下。其中参数`methods`表示该函数所处理的请求类型，`request`则可以得到请求内容。而return返回的内容会则会被重新发到前端。

然后我们需要实现三个部分以及一些辅助代码

# Auth

[Auth部分要求](https://github.com/LibroWu/BookstoreForDB/Bookstore/doc/auth)

相关接口在`be/model/user.py`下实现

# Buyer

[Buyer部分要求](https://github.com/LibroWu/BookstoreForDB/Bookstore/doc/buyer)

相关接口在`be/model/buyer.py`下实现

# Seller

[Seller部分要求](https://github.com/LibroWu/BookstoreForDB/Bookstore/doc/seller)

相关接口在`be/model/seller.py`下实现

# OtherPart

仅有这部分需要提供统一接口，上面三个部分都可以独立开发

- 创建pymongo数据库，提供与底层数据库的链接，可以仿照样例，在`db_conn.py`下实现。

- 创建错误相关处理接口，在`error.py`下实现。
- 运行后端，方法为跑`app.py`文件，目前前后端可以暂时都在`127.0.0.1`上运行，如果有宏伟的想法可以跑在服务器上(雾

# Benchmark

使用`pytest`运行`fe/test/`下任意文件，即在cmd中输入`pytest $aimtest.py`

# Note

待实现的接口名，参数，返回类型不要随意改变，其会涉及Blueprint中的调用。

需要实现的部分都在`Bookstore/be/model`文件夹下