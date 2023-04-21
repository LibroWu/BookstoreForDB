## !取消订单

将订单从库中删除，5s未支付自动取消，支付后不能取消

#### URL：

POST http://[address]/buyer/cancel_order

Headers:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

Body:

```json
{
  "user_id": "$seller id$",
  "order_id": "$order id$"
}
```

| key      | 类型   | 描述   | 是否可为空 |
| -------- | ------ | ------ | ---------- |
| user_id  | string | 用户ID | N          |
| order_id | string | 订单ID | N          |

#### Response

Status Code:

| 码   | 描述         |
| ---- | ------------ |
| 200  | 取消成功     |
| 511  | 用户ID不存在 |
| 518  | 订单ID不存在 |
| 520  | 订单状态错误 |





## !查询订单

#### URL：

POST http://[address]/buyer/search_order

Headers:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

Body:

```json
{
  "user_id": "$seller id$",
}
```

| key     | 类型   | 描述   | 是否可为空 |
| ------- | ------ | ------ | ---------- |
| user_id | string | 用户ID | N          |

#### Response

Status Code:

| 码   | 描述          |
| ---- | ------------- |
| 200  | 查询成功      |
| 511  | 用户ID 不存在 |

##### Body:

```json
{
  "order_info": "order_info"
}
```

##### 属性说明：

| 变量名     | 类型 | 描述                          | 是否可为空 |
| ---------- | ---- | ----------------------------- | ---------- |
| order_info | list | 订单信息，只有返回200时才有效 |            |





## !搜索书本

#### URL：

POST http://[address]/buyer/search_book

Headers:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

Body:

```json
{
  "user_id": "$seller id$",
  "search_type":"$search type",
  "store_id": "$store id$",
  "search_params":"$names,...$"
}
```

| key           | 类型   | 描述                       | 是否可为空 |
| ------------- | ------ | -------------------------- | ---------- |
| user_id       | string | 用户ID                     | N          |
| search_type   | int    | 搜索状态，0为全局，1为指定 | N          |
| store_id      | string | 商店ID，0为None            | N          |
| search_params | list   | 参数个数，保证个数小于10   | N          |

#### Response

Status Code:

| 码   | 描述          |
| ---- | ------------- |
| 200  | 查询成功      |
| 513  | 商店ID 不存在 |
| 515  | 图书不存在    |
| 511  | 用户ID不存在  |

##### Body:

```json
{
  "book_name": "book_name"
}
```

##### 属性说明：

| 变量名    | 类型 | 描述                      | 是否可为空 |
| --------- | ---- | ------------------------- | ---------- |
| book_name | list | 书名，只有返回200时才有效 |            |

## !确认收货

将订单从库中删除

#### URL：

POST http://[address]/buyer/confirm_receive

Headers:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

Body:

```json
{
  "user_id": "$seller id$",
  "order_id": "$order id$"
}
```

| key      | 类型   | 描述   | 是否可为空 |
| -------- | ------ | ------ | ---------- |
| user_id  | string | 用户ID | N          |
| order_id | string | 订单ID | N          |

#### Response

Status Code:

| 码   | 描述          |
| ---- | ------------- |
| 200  | 收货成功      |
| 518  | Order不存在   |
| 520  | Order状态错误 |
| 511  | 用户ID不存在  |



## 买家下单

#### URL：
POST http://[address]/buyer/new_order

#### Request

##### Header:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

##### Body:
```json
{
  "user_id": "buyer_id",
  "store_id": "store_id",
  "books": [
    {
      "id": "1000067",
      "count": 1
    },
    {
      "id": "1000134",
      "count": 4
    }
  ]
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
store_id | string | 商铺ID | N
books | class | 书籍购买列表 | N

books数组：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
id | string | 书籍的ID | N
count | string | 购买数量 | N


#### Response

Status Code:

码 | 描述
--- | ---
200 | 下单成功
5XX | 买家用户ID不存在
5XX | 商铺ID不存在
5XX | 购买的图书不存在
5XX | 商品库存不足

##### Body:
```json
{
  "order_id": "uuid"
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
order_id | string | 订单号，只有返回200时才有效 | N


## 买家付款

#### URL：
POST http://[address]/buyer/payment

#### Request

##### Body:
```json
{
  "user_id": "buyer_id",
  "order_id": "order_id",
  "password": "password"
}
```

##### 属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
order_id | string | 订单ID | N
password | string | 买家用户密码 | N 


#### Response

Status Code:

码 | 描述
--- | ---
200 | 付款成功
5XX | 账户余额不足
5XX | 无效参数
401 | 授权失败 


## 买家充值

#### URL：
POST http://[address]/buyer/add_funds

#### Request



##### Body:
```json
{
  "user_id": "user_id",
  "password": "password",
  "add_value": 10
}
```

##### 属性说明：

key | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
password | string | 用户密码 | N
add_value | int | 充值金额，以分为单位 | N


Status Code:

码 | 描述
--- | ---
200 | 充值成功
401 | 授权失败
5XX | 无效参数
