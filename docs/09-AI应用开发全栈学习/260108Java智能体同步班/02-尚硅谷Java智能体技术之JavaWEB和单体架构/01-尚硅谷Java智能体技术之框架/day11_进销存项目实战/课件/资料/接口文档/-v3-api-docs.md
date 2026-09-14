# Lite IMS API


**简介**:Lite IMS API


**HOST**:http://localhost:8080


**联系人**:


**Version**:1.0


**接口路径**:/v3/api-docs


[TOC]






# 分类管理


## 获取分类列表

**接口地址**:`/api/categories`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`

**接口描述**:<p>查询所有商品分类</p>



**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 添加分类


**接口地址**:`/api/categories`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded,application/json`


**响应数据类型**:`*/*`

**接口描述**:<p>新增一个商品分类</p>



**请求示例**:


```javascript
{
  "name": "智能手机",
  "sort": 10,
  "description": "包含各类品牌智能手机及配件",
  "status": 1
}
```


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|category|商品分类信息管理|body|true|Category|Category|
|&emsp;&emsp;id|主键ID:系统自动生成的唯一分类标识||true|integer(int64)||
|&emsp;&emsp;name|分类名称:分类的显示名称（如：电子产品、服装鞋帽）||true|string||
|&emsp;&emsp;sort|排序值:分类在前端展示的顺序（数值越小越靠前）||false|integer(int32)||
|&emsp;&emsp;description|分类描述:分类的详细说明或备注信息||false|string||
|&emsp;&emsp;status|状态:分类上下架状态：0-下架，1-上架,可用值:0,1||false|integer(int32)||
|&emsp;&emsp;createTime|创建时间:分类记录首次创建时间||false|string(date-time)||
|&emsp;&emsp;updateTime|更新时间:分类信息最后修改时间||false|string(date-time)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 更新分类


**接口地址**:`/api/categories`


**请求方式**:`PUT`

**请求数据类型**:`application/x-www-form-urlencoded,application/json`


**响应数据类型**:`*/*`

**接口描述**:<p>修改分类信息</p>



**请求示例**:


```javascript
{
  "id": 1,
  "name": "智能手机",
  "sort": 10,
  "description": "包含各类品牌智能手机及配件",
  "status": 1
}
```


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|category|商品分类信息管理|body|true|Category|Category|
|&emsp;&emsp;id|主键ID:系统自动生成的唯一分类标识||true|integer(int64)||
|&emsp;&emsp;name|分类名称:分类的显示名称（如：电子产品、服装鞋帽）||true|string||
|&emsp;&emsp;sort|排序值:分类在前端展示的顺序（数值越小越靠前）||false|integer(int32)||
|&emsp;&emsp;description|分类描述:分类的详细说明或备注信息||false|string||
|&emsp;&emsp;status|状态:分类上下架状态：0-下架，1-上架,可用值:0,1||false|integer(int32)||
|&emsp;&emsp;createTime|创建时间:分类记录首次创建时间||false|string(date-time)||
|&emsp;&emsp;updateTime|更新时间:分类信息最后修改时间||false|string(date-time)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 删除分类

**接口地址**:`/api/categories/{id}`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`

**接口描述**:<p>逻辑删除指定分类</p>



**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||path|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


# 登录模块


## 用户登录

**接口地址**:`/api/login`


**请求方式**:`POST`

**请求数据类型**:`application/x-www-form-urlencoded,application/json`


**响应数据类型**:`*/*`

**接口描述**:<p>通过用户名和密码登录</p>



**请求示例**:


```javascript
{
  "username": "admin",
  "password": "123456",
}
```


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|sysUser|系统用户信息|body|true|SysUser|SysUser|
|&emsp;&emsp;username|用户名:登录使用的用户名（唯一）||true|string||
|&emsp;&emsp;password|密码:加密后的用户密码||false|string||

**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 用户登出

**接口地址**:`/api/logout`

**请求方式**:`GET`

**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`

**接口描述**:<p>清除Session</p>



**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


# 客户管理


## 获取客户列表


**接口地址**:`/api/customers`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:<p>查询所有客户</p>



**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 添加客户

**接口地址**:`/api/customers`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded,application/json`


**响应数据类型**:`*/*`


**接口描述**:<p>新增一个客户</p>



**请求示例**:


```javascript
{
  "id": 1001,
  "name": "某某科技有限公司",
  "contact": "张三",
  "phone": "13800138000",
  "email": "contact@example.com",
  "address": "上海市浦东新区XX路123号"
}
```


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|customer|客户信息实体|body|true|Customer|Customer|
|&emsp;&emsp;id|主键ID:系统自动生成的唯一标识||true|integer(int64)||
|&emsp;&emsp;name|客户名称:客户公司全称||true|string||
|&emsp;&emsp;contact|联系人:主要对接人姓名||true|string||
|&emsp;&emsp;phone|手机号:联系人手机号码||false|string||
|&emsp;&emsp;email|邮箱:官方电子邮箱||false|string||
|&emsp;&emsp;address|地址:公司详细办公地址||false|string||
|&emsp;&emsp;createTime|创建时间:记录创建时间||false|string(date-time)||
|&emsp;&emsp;updateTime|更新时间:最后修改时间||false|string(date-time)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 更新客户


**接口地址**:`/api/customers`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded,application/json`


**响应数据类型**:`*/*`


**接口描述**:<p>修改客户信息</p>



**请求示例**:


```javascript
{
  "id": 1001,
  "name": "某某科技有限公司",
  "contact": "张三",
  "phone": "13800138000",
  "email": "contact@example.com",
  "address": "上海市浦东新区XX路123号"
}
```


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|customer|客户信息实体|body|true|Customer|Customer|
|&emsp;&emsp;id|主键ID:系统自动生成的唯一标识||true|integer(int64)||
|&emsp;&emsp;name|客户名称:客户公司全称||true|string||
|&emsp;&emsp;contact|联系人:主要对接人姓名||true|string||
|&emsp;&emsp;phone|手机号:联系人手机号码||false|string||
|&emsp;&emsp;email|邮箱:官方电子邮箱||false|string||
|&emsp;&emsp;address|地址:公司详细办公地址||false|string||
|&emsp;&emsp;createTime|创建时间:记录创建时间||false|string(date-time)||
|&emsp;&emsp;updateTime|更新时间:最后修改时间||false|string(date-time)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 删除客户


**接口地址**:`/api/customers/{id}`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:<p>逻辑删除指定客户</p>



**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||path|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


# 商品管理


## 获取商品列表

**接口地址**:`/api/products`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`

**接口描述**:<p>支持分页、名称搜索和分类筛选</p>



**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|page|页码|query|false|integer(int32)||
|size|每页大小|query|false|integer(int32)||
|name|商品名称|query|false|string||
|categoryId|分类ID|query|false|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 添加商品


**接口地址**:`/api/products`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded,application/json`


**响应数据类型**:`*/*`


**接口描述**:<p>新增一个商品</p>



**请求示例**:


```javascript
{
  "id": 1,
  "categoryId": 5,
  "name": "华为Mate60 Pro",
  "price": 5999,
  "stock": 100,
  "status": 1
}
```


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|product|商品信息实体类|body|true|Product|Product|
|&emsp;&emsp;id|主键ID:自动生成的商品唯一标识||true|integer(int64)||
|&emsp;&emsp;categoryId|分类ID:商品所属分类ID||true|integer(int64)||
|&emsp;&emsp;name|商品名称:商品展示名称||true|string||
|&emsp;&emsp;price|价格:商品销售价格（单位：元）||true|number||
|&emsp;&emsp;stock|库存数量:当前可用库存||false|integer(int32)||
|&emsp;&emsp;status|状态:商品上下架状态：1-上架，0-下架,可用值:0,1||false|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 更新商品


**接口地址**:`/api/products`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded,application/json`


**响应数据类型**:`*/*`


**接口描述**:<p>修改商品信息</p>



**请求示例**:


```javascript
{
  "id": 1,
  "categoryId": 5,
  "name": "华为Mate60 Pro",
  "price": 5999,
  "stock": 100,
  "status": 1
}
```


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|product|商品信息实体类|body|true|Product|Product|
|&emsp;&emsp;id|主键ID:自动生成的商品唯一标识||true|integer(int64)||
|&emsp;&emsp;categoryId|分类ID:商品所属分类ID||true|integer(int64)||
|&emsp;&emsp;name|商品名称:商品展示名称||true|string||
|&emsp;&emsp;price|价格:商品销售价格（单位：元）||true|number||
|&emsp;&emsp;stock|库存数量:当前可用库存||false|integer(int32)||
|&emsp;&emsp;status|状态:商品上下架状态：1-上架，0-下架,可用值:0,1||false|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 删除商品


**接口地址**:`/api/products/{id}`


**请求方式**:`DELETE`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:<p>逻辑删除指定商品</p>



**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||path|true|integer(int64)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


# 订单管理


## 更新订单状态

**接口地址**:`/api/orders/{id}/{status}`


**请求方式**:`PUT`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`

**接口描述**:


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|id||path|true|integer(int64)||
|status||query|true|integer(int32)||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 获取订单列表


**接口地址**:`/api/orders`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:<p>支持分页和订单号搜索</p>



**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|page|页码|query|false|integer(int32)||
|size|每页大小|query|false|integer(int32)||
|orderNo|订单号|query|false|string||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


## 创建订单


**接口地址**:`/api/orders`


**请求方式**:`POST`


**请求数据类型**:`application/x-www-form-urlencoded,application/json`


**响应数据类型**:`*/*`


**接口描述**:<p>创建新订单及其明细</p>



**请求示例**:


```javascript
{
  "customerId": 5001,
  "userId": 100,
  "items": [
    {
      "productId": 3001,
      "quantity": 2
    }
  ]
}
```


**请求参数**:


| 参数名称 | 参数说明 | 请求类型    | 是否必须 | 数据类型 | schema |
| -------- | -------- | ----- | -------- | -------- | ------ |
|orderDTO|订单数据传输对象|body|true|OrderDTO|OrderDTO|
|&emsp;&emsp;customerId|客户ID:下单客户的主键ID||true|integer(int64)||
|&emsp;&emsp;userId|系统用户ID:操作员工的系统用户ID||true|integer(int64)||
|&emsp;&emsp;items|订单明细项数据传输对象||true|array|OrderItemDTO|
|&emsp;&emsp;&emsp;&emsp;productId|购买商品的主键ID||true|integer||
|&emsp;&emsp;&emsp;&emsp;quantity|购买商品的数量||true|integer||


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||object||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {}
}
```


# 仪表盘


## 获取统计数据

**接口地址**:`/api/dashboard/stats`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`

**接口描述**:<p>获取首页统计指标</p>



**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK|Result<DashboardVO>|


**响应参数**:


| 参数名称 | 参数说明 | 类型 | schema |
| -------- | -------- | ----- |----- |
|code||integer(int32)|integer(int32)|
|message||string||
|data||DashboardVO|DashboardVO|
|&emsp;&emsp;productCount|商品总量:当前系统中所有商品的总数量|integer(int64)||
|&emsp;&emsp;todayOrderCount|今日订单量:当天新产生的订单总数|integer(int64)||
|&emsp;&emsp;totalSales|总销售额:当日累计成交金额（单位：元）|number||


**响应示例**:
```javascript
{
    "code": 0,
    "message": "",
    "data": {
        "productCount": 1500,
        "todayOrderCount": 42,
        "totalSales": 89999
    }
}
```


# 数据导出


## 导出订单报表


**接口地址**:`/api/excel/orders/export`


**请求方式**:`GET`


**请求数据类型**:`application/x-www-form-urlencoded`


**响应数据类型**:`*/*`


**接口描述**:


**请求参数**:


暂无


**响应状态**:


| 状态码 | 说明 | schema |
| -------- | -------- | ----- |
|200|OK||


**响应参数**:


暂无


**响应示例**:
```javascript

```