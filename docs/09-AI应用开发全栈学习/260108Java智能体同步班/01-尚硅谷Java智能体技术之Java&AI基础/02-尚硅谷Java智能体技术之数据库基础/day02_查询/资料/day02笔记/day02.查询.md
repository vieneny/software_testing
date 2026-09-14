# day02-查询

```java
课前回顾:
  1.库操作:
    a.创建库: create database `库名`
    b.删库: drop database `库名`
  2.表操作:
    a.创建表:
       create table `表名`(
         列名 数据类型(长度)[约束],
         列名 数据类型(长度)[约束],
         列名 数据类型(长度)[约束]
       );
    b.删除表:
      drop table `表名`
    c.修改表结构:alter table开头的
  3.数据操作:
    a.添加数据: insert into 表名 (列名,列名) values (值1,值2)
               insert into 表名 values (值1,值2) -> 不加列名的时候值需要对所有列进行全覆盖
               insert into 表名 (列名,列名) values (值1,值2),(值1,值2),(值1,值2)...
    b.删除数据:
      delete from 表名 where 条件
    c.修改数据:
      update 表名 set 列名 = 新值 where 条件
    d.查询:
      select * from 表名 -> 查询所有数据,展示所有列
      select 列名 from 表名 -> 查询所有数据,展示指定列
  4.约束:
    a.主键约束: primary key
    b.自增长: auto_increment
    c.非空约束: NOT NULL
    d.唯一约束: UNIQUE

今日重点:
  1.会单表查询
  2.知道表和表之间的三种关系:一对一  一对多  多对多
  3.会多表查询
```

# 第一章.单表查询

```sql
#创建商品表：
create table product(
    pid int primary key,
    pname varchar(20),
    price double
);


INSERT INTO product(pid,pname,price) VALUES(1,'联想',5000);
INSERT INTO product(pid,pname,price) VALUES(2,'海尔',3000);
INSERT INTO product(pid,pname,price) VALUES(3,'雷神',5000);
INSERT INTO product(pid,pname,price) VALUES(4,'JACK JONES',800);
INSERT INTO product(pid,pname,price) VALUES(5,'真维斯',200);
INSERT INTO product(pid,pname,price) VALUES(6,'花花公子',440);
INSERT INTO product(pid,pname,price) VALUES(7,'劲霸',2000);
INSERT INTO product(pid,pname,price) VALUES(8,'香奈儿',800);
INSERT INTO product(pid,pname,price) VALUES(9,'相宜本草',200);
INSERT INTO product(pid,pname,price) VALUES(10,'面霸',5);
INSERT INTO product(pid,pname,price) VALUES(11,'好想你枣',56);
INSERT INTO product(pid,pname,price) VALUES(12,'香飘飘奶茶',1);
INSERT INTO product(pid,pname,price) VALUES(13,'果9',1);
```

## 1.简单查询

```sql
1.关键字: select  from
2.语法:
  a.select * from 表名  -> 查询所有数据,*代表的是展示所有列
  b.select 列名,列名 from 表名 -> 查询所有数据,展示指定的列

3.注意:
  查询出来的结果都是以表的形式展示,我们可以和这个查询出来的结果称之为"伪表",这个"伪表"是只读的,不能改里面的数据
```

```mysql
-- 查询product所有数据


-- 查询product 所有数据,展示pname和pid


/*
  去重复值

  关键字: distinct(列名)
*/



/*
  给列中的数据做计算
*/
-- 查询所有数据,给price列中所有的数据+100



/*
  给列和表取别名

  as 别名

  as可以省略
*/


-- 也可以给表取别名,但是不涉及到多表查询,给表取别名看不出效果来

```

```sql
-- 查询product所有数据
SELECT * FROM product;
-- 查询product 所有数据,展示pname和pid
SELECT pid,pname FROM product;
/*
  去重复值

  关键字: distinct(列名)
*/
SELECT DISTINCT(price) FROM product;

/*
  给列中的数据做计算
*/
-- 查询所有数据,给price列中所有的数据+100
SELECT pid,pname,price+100 FROM product;

/*
  给列和表取别名

  as 别名

  as可以省略
*/
SELECT pid,pname,price+100 `price` FROM product;


-- 也可以给表取别名,但是不涉及到多表查询,给表取别名看不出效果来
SELECT * FROM product `p`;
```

## 2.条件查询

```sql
1.语法:
  select * from 表名 where 条件 -> 按照条件查询展示所有列
  select 列名 from 表名 where 条件 -> 按照条件查询展示指定列
```

| **比较运算符** | > <  <=  >=   =  <>   | 大于、小于、大于(小于)等于、不等于                           |
| -------------- | --------------------- | ------------------------------------------------------------ |
|                | BETWEEN  ...AND...    | 显示在某一区间的值(含头含尾)                                 |
|                | 字段 IN(set)          | 显示在in列表中的值，例：price in(100,200)  查询id为1,3,7的商品: id  in(1,3,7) |
|                | 列名 LIKE ‘张pattern’ | 模糊查询，Like语句中，% 代表零个或多个任意字符，_ 代表一个字符， 例如：`first_name like '_a%';`   <br/>比如:查询姓张的人:name like '张%'<br> 查询商品名中带香的商品: pname like '%香%'<br>查询第二个字为想的商品: like '_想%'<br>查询商品名为四个字的商品:pname   like '____' |
|                | IS NULL               | 判断是否为空    不为空的就是 IS NOT NULL                     |
| **逻辑运行符** | and  (与)             | 多个条件同时成立  全为true,整体才为true                      |
|                | or(或)                | 多个条件任一成立   有真则真                                  |
|                | not(非)               | 不成立，例：`where not(salary>100); `                        |

```mysql
-- 查询商品名为'花花公子'的商品所有信息


-- 查询价格为800的商品


-- 查询商品价格大于60元的所有商品信息


-- 查询商品价格在200-1000之间的所有商品信息


-- 查询商品价格是200或者800的商品


-- 查询以'香'开头的商品


-- 查询含有'霸'的商品


-- 查询商品名为NULL的


-- 查询商品名不为NULL的

```

```sql
-- 查询商品名为'花花公子'的商品所有信息
SELECT * FROM product WHERE pname = '花花公子';

-- 查询价格为800的商品
SELECT * FROM product WHERE price = 800;

-- 查询商品价格大于60元的所有商品信息
SELECT * FROM product WHERE price > 60;

-- 查询商品价格在200-1000之间的所有商品信息
SELECT * FROM product WHERE price BETWEEN 200 AND 1000;

-- 查询商品价格是200或者800的商品
SELECT * FROM product WHERE price = 200 OR price = 800;
SELECT * FROM product WHERE price IN (200,800);

-- 查询以'香'开头的商品
SELECT * FROM product WHERE pname LIKE '香%';


-- 查询含有'霸'的商品
SELECT * FROM product WHERE pname LIKE '%霸%';

-- 查询商品名为NULL的
SELECT * FROM product WHERE pname IS NULL;

-- 查询商品名不为NULL的
SELECT * FROM product WHERE pname IS NOT NULL;
```

## 3.排序查询

```sql
1.关键字: order by
2.语法:
  select 列名 from 表名 order by 排序列名 排序规则
3.问题:是查询,还是先排序?
  先查询,最后排序
4.排序规则:
  ASC:升序 -> 默认
  DESC:降序
```

```mysql
书写sql语句关键字的顺序
select
from
where
group by
having
order by

执行顺序:
from
where
group by
having
select
order by

先定位到要查询哪个表,然后根据什么条件去查,表确定好了,条件也确定好了,开始利用select查询
查询得出一个结果,在针对这个结果进行一个排序
```

```mysql
-- 使用价格排序(降序)



-- 使用价格排序(升序)


-- 显示商品的价格(去重复),并排序(降序)

```

```sql
-- 使用价格排序(降序)
SELECT * FROM product ORDER BY price DESC;

-- 使用价格排序(升序)
SELECT * FROM product ORDER BY price ASC;
SELECT * FROM product ORDER BY price;

-- 显示商品的价格(去重复),并排序(降序)
SELECT DISTINCT(price) FROM product ORDER BY price DESC;
```

## 4.聚合查询

```sql
1.关键字:用到的是聚合函数
2.语法:
  select 聚合函数(列名) from 表名 where 条件
3.聚合函数:
  count(*) 统计一共有多少条数据
  sum(列名) 对指定列求和
  avg(列名) 对指定列求平均值
  max(列名) 对指定列求最大值
  min(列名) 对指定列求最小值
```

```mysql
-- 统计product的总记录数



-- 查询所有商品的价格总和



-- 查询pid为1,3,7 商品的价格平均值



-- 查询商品的最高价格以及最低价格

```

```sql
-- 统计product的总记录数
SELECT COUNT(*) FROM product;
SELECT COUNT(pid) FROM product;

-- 查询所有商品的价格总和
SELECT SUM(price) FROM product;


-- 查询pid为1,3,7 商品的价格平均值
SELECT AVG(price) FROM product WHERE pid IN(1,3,7);


-- 查询商品的最高价格以及最低价格
SELECT MIN(price),MAX(price) FROM product;
```

## 5.分组查询

```mysql
1.关键字:group by
2.语法: select 聚合函数(列名) from 表名 group by 分组列名 having 条件
3.怎么确定分组字段?
  看哪个字段需要合并展示就按照哪个字段分组
  相同的字段数据合并为一组
  不同的字段数据单独为一组

5.where和having区别
  where在分组查询之前执行
  having在分组查询之后执行
```

```mysql
书写sql语句关键字的顺序:偏向的是关键字
select
from
where
group by
having
order by

执行顺序:偏向的是逻辑
from
where
group by
having
select
order by

先定位到要查询哪个表,然后根据什么条件去查,表确定好了,条件也确定好了,开始利用select查询
查询得出一个结果,在针对这个结果进行一个排序
```

```sql
-- 查询相同商品的价格总和


-- 查询相同商品的价格总和并排序


-- 查询相同商品的价格总和,再展示出价格总和大于等于2000的商品

```

```sql
-- 查询相同商品的价格总和
SELECT pname,SUM(price) FROM product GROUP BY pname;

-- 查询相同商品的价格总和并排序
-- SELECT pname,SUM(price) FROM product GROUP BY pname order by SUM(price);
SELECT pname,SUM(price) `newprice` FROM product GROUP BY pname ORDER BY `newprice`;

-- 查询相同商品的价格总和,再展示出价格总和大于等于2000的商品

#按照关键字书写顺序来说:where要写到分组前面
SELECT pname,SUM(price) `newprice` FROM product GROUP BY pname WHERE newprice>=2000;


#按照关键字执行顺序来看,先确定查询条件,再执行查询,再先确定where条件的时候,newprice还没产生呢
SELECT pname,SUM(price) `newprice` FROM product WHERE newprice>=2000 GROUP BY pname;

#先执行where条件,在执行where的时候还没求和查询,所以果9没出来
SELECT pname,SUM(price) `newprice` FROM product WHERE price>=2000 GROUP BY pname;

#having条件书写在分组后,还执行在分组后
SELECT pname,SUM(price) `newprice` FROM product GROUP BY pname HAVING newprice>=2000;
```

> 课程配图（未随笔记提交）

## 6.分页查询

```mysql
1.语法:
  select * from 表名 limit m,n

2.字母代表啥:
  m:每页的起始位置
  n:每页显示条数
3.小技巧:
  我们将整个表的每一条数据进行编号,从0开始

4.每页的起始位置快速算法:
  (当前页-1)*每页显示条数

  当前页 -> 第几页

5.其他分页参数:
  a.每页的起始位置:
    (当前页-1)*每页显示条数
  b.int curPage = 2; -- 当前页数
  c.int pageSize = 5; -- 每页显示数量
  d.int startRow = (curPage - 1) * pageSize; -- 当前页, 记录开始的位置(行数)计算

  e.int totalSize = select count(*) from products; -- 记录总数量
  f.int totalPage = Math.ceil(totalSize * 1.0 / pageSize); -- 总页数
                总页数 = (总记录数/每页显示条数)向上取整
```

```mysql
-- 第一页
SELECT * FROM product LIMIT 0,5;

-- 第二页
SELECT * FROM product LIMIT 5,5;

-- 第三页
SELECT * FROM product LIMIT 10,5;

-- 第四页
SELECT * FROM product LIMIT 15,5;
```

> 课程配图（未随笔记提交）

# 第二章.数据库的备份与还原

## 1.用命令去操作数据库的备份与还原

### 1.1.命令操作备份

```mysql
mysqldump  -u用户名 -p密码 数据库名>生成的脚本文件路径

生成的脚本文件路径:指定备份的路径,写路径时最后要指明备份的sql文件名,命令后不要加;
```

### 1.2.命令操作还原

```mysql
mysql  -uroot  -p密码 数据库名 < 文件路径

注意:我们利用命令备份出来的sql文件中没有单独创建数据库的语句,所以如果利用命令去还原的话,需要我们自己手动先创建对应的库
    命令后不要加;
```

## 2.利用点击去操作数据库的备份与还原

### 2.1.利用点击去备份

> 课程配图（未随笔记提交）

### 2.2.利用点击去还原

> 课程配图（未随笔记提交）：1680058782201

# 第三章.数据库三范式

```java
好的数据库设计对数据的存储性能和后期的程序开发，都会产生重要的影响。建立科学的，规范的数据库就需要满足一些规则来优化数据的设计和存储，这些规则就称为范式。
```

## 1第一范式: **确保每列保持原子性**

第一范（1NF）式是最基本的范式。如果数据库表中的所有字段值都是不可分解的原子值，就说明该数据库表满足了第一范式。

第一范式的合理遵循需要根据系统的实际需求来定。比如某些数据库系统中需要用到“地址”这个属性，本来直接将“地址”属性设计成一个数据库表的字段就行。但是如果系统经常会访问“地址”属性中的“城市”部分，那么就非要将“地址”这个属性重新拆分为省份、城市、详细地址等多个部分进行存储，这样在对地址中某一部分操作的时候将非常方便。这样设计才算满足了数据库的第一范式，如下表所示。

> 课程配图（未随笔记提交）：课堂配图

如果不遵守第一范式，查询出数据还需要进一步处理（查询不方便）。遵守第一范式，需要什么字段的数据就查询什么数据（方便查询）

```java
列名:详细地址手机号

    北京市昌平区北七家镇宏福苑小区19号楼1501087xxxx -> 不行,因为数据可以拆分,不符合第一范式原子性
```

## 2 第二范式: **确保表中的每行都能唯一区分**

第二范式（2NF)第二范式（2NF）是在第一范式（1NF）的基础上建立起来的，即满足第二范式（2NF）必须先满足第一范式（1NF）。第二范式（2NF）要求数据库表中的每个实例或行必须可以被惟一的区分。为实现区分通常需要为表加上一个列，以存储各个实例的惟一标识。

## 3 第三范式: **3NF:非主键字段不能相互依赖**

假设有一个员工表，其中包含员工ID（主键）、员工姓名、部门名称和部门负责人。在这里，“部门负责人”依赖于“部门名称”，而“部门名称”又依赖于“员工ID”，因此“部门负责人”传递依赖于“员工ID”。这不符合3NF。需要将部门相关信息拆分到另一个表中，例如一个独立的部门表。

通过逐步满足这三个范式，可以设计出更加规范化、减少冗余和依赖关系的数据库结构，从而提高数据的完整性和查询效率。

```java
总结:
  1.一列的数据不能再拆分
  2.每张表要有主键
  3.一张表不要记录多张表的信息
```

# 第四章.多表之间的关系

在关系数据库管理系统中，很多表之间是有关系的，表之间的关系分为一对一关系、一对多关系和多对多关系。

## 4.1.一对一

该关系中第一个表中的一个行只可以与第二个表中的一个行相关，且第二个表中的一个行也只可以与第一个表中的一个行相关。

例如，"人员信息表","身份证表",一个人只能有一个身份证号,反过来一个身份证号只能对应一个人

> 课程配图（未随笔记提交）

## 4.2.一对多

第一个表中的一个行可以与第二个表中的一个或多个行相关，但第二个表中的一个行只可以与第一个表中的一个行相关。

例如，“商品分类表”和“商品信息表”。一个商品分类对应多个商品,反过来一个商品只属于一个分类,形成了一对多

> 课程配图（未随笔记提交）

## 4.3.多对多

该关系中第一个表中的一个行可以与第二个表中的一个或多个行相关。第二个表中的一个行也可以与第一个表中的一个或多个行相关。通常两个表的多对多关系会借助第三张表，转换为两个一对多的关系。

例如，选课系统的“学生信息表”和“课程信息表”是多对多关系。一个学生可以选择多门课，一门课程可以被多个学生选择，即“学生信息表”中一条记录可以与“课程信息表”多条记录对应，反过来“课程信息表”的一条记录也可以与“学生信息表”中多条记录对应。它们之间借助第三张“选课信息表”实现关联关系，而“学生信息表”与“选课信息表”是一对多关系，“课程信息表”与“选课信息表”也是一对多关系。“选课信息表”中“学号”字段与“学生信息表”中“学号”字段意义相同。“课程信息表”中“课程编号”字段与“课程信息表”中“课程编号”字段意义相同。

> 课程配图（未随笔记提交）

> 总结:
>
> 1.一对一:  正着看,倒着看都是一对一
>
> 2.一对多:  正着看一对多,倒着看一对一
>
> 3.多对多:  正着看,倒着看都是一对多

# 第五章.创建外键约束

```java
1.为什么在多表之间创建外键约束:
  为了让多表之间的数据有限制,联系起来
2.比如:
  商品分类表和商品信息表

  这两张表就需要联系起来,同时里面的数据要限制一下 -> 分类表中没有的分类,你商品表中就不能有额外的商品

  如果没有外键约束,这两张表中的数据就随便填了
```

```mysql
格式:alter table 从表 add [constraint 外键名称(自定义)] foreign key 从表(外键列名) references 主表(主键列名)
```

## 1.一对多的表创建外键约束

```java
1.商品分类表和商品信息表啥关系?
  a.一个分类包含了多个商品 -> 一对多
  b.一个商品属于一个分类 -> 一对一
  c.结论:一对多

2.分清主表和从表:看哪张表中的数据限制哪张表
   分类表中的数据限制商品表的数据,不能出现没有的分类对应的商品
   主表:分类表
   从表:商品表

3.默认情况下两张表谁也不会限制谁,如何让主表数据限制从表数据呢?
  建立外键约束

  在从表中添加一列数据,这一列的数据保存的是主表的主键
```

> 课程配图（未随笔记提交）

```mysql
    #商品分类表->主表
    CREATE TABLE category (
      cid VARCHAR(32) PRIMARY KEY ,
      cname VARCHAR(50)
    );

    #商品表->从表
    CREATE TABLE products(
      pid VARCHAR(32) PRIMARY KEY ,
      pname VARCHAR(50),
      price DOUBLE,
      category_id VARCHAR(32)-- 外键  存储的是主表的主键内容
    );



```

```mysql
    #商品分类表->主表
    CREATE TABLE category (
      cid VARCHAR(32) PRIMARY KEY ,
      cname VARCHAR(50)
    );

    #商品表->从表
    CREATE TABLE products(
      pid VARCHAR(32) PRIMARY KEY ,
      pname VARCHAR(50),
      price DOUBLE,
      category_id VARCHAR(32)-- 外键  存储的是主表的主键内容
    );

-- alter table 从表 add [constraint 外键名称(自定义)] foreign key 从表(外键列名) references 主表(主键列名)
ALTER TABLE products ADD CONSTRAINT cp FOREIGN KEY products(category_id) REFERENCES category(cid);
```

> 课程配图（未随笔记提交）

## 2.多对多的表创建外键约束

```java
1.商品表和订单表啥关系?
   a.一个商品可以对应多个订单
   b.一个订单包含了多少商品
   c.结论:多对多

2.谁是主表,谁是从表?
  都是主表

3.多对多的表之间想要建立外键约束,我们都会创建一个中间表,中间表中存的都是外键数据

   中间表:从表
```

> 课程配图（未随笔记提交）

```mysql
# 订单表 -> 主表
 CREATE TABLE `orders`(
  `oid` VARCHAR(32) PRIMARY KEY ,
  `totalprice` DOUBLE 	#总计
  );

#订单项表->中间表->从表
CREATE TABLE orderitem(
  pid VARCHAR(50),-- 商品id->外键
  oid VARCHAR(50)-- 订单id ->外键
);

```

```sql
# 订单表 -> 主表
 CREATE TABLE `orders`(
  `oid` VARCHAR(32) PRIMARY KEY ,
  `totalprice` DOUBLE 	#总计
  );

#订单项表->中间表->从表
CREATE TABLE orderitem(
  pid VARCHAR(50),-- 商品id->外键
  oid VARCHAR(50)-- 订单id ->外键
);

-- alter table 从表 add [constraint 外键名称(自定义)] foreign key 从表(外键列名) references 主表(主键列名)

-- 先创建products和orderitem之间的外键约束
ALTER TABLE orderitem ADD CONSTRAINT po FOREIGN KEY orderitem(pid) REFERENCES products(pid);

-- 再创建orders和orderitem之间的外键约束
ALTER TABLE orderitem ADD CONSTRAINT oo FOREIGN KEY orderitem(oid) REFERENCES orders(oid);
```

> 课程配图（未随笔记提交）

> 在开发的时候,我们不用先建立外键约束,我们该怎么查就怎么查 ,原因是:
>
> 我们写完需求之后,我们需要自己测一遍,我们都会随便找点数据去测代码,如果提前就建立了外键约束了,我们就不能随便找数据去测试了
>
> 所以我们都是开发好之后,再建立外键约束

# 第六章.多表查询

```mysql
    # 分类表
    CREATE TABLE category (
      cid VARCHAR(32) PRIMARY KEY ,
      cname VARCHAR(50)
    );

    #商品表
    CREATE TABLE products(
      pid VARCHAR(32) PRIMARY KEY ,
      pname VARCHAR(50),
      price DOUBLE,
      flag VARCHAR(2), #是否上架标记为：1表示上架、0表示下架
      category_id VARCHAR(32), -- 外键
      CONSTRAINT products_fk FOREIGN KEY (category_id) REFERENCES category (cid)
    );
    #分类
INSERT INTO category(cid,cname) VALUES('c001','家电');
INSERT INTO category(cid,cname) VALUES('c002','服饰');
INSERT INTO category(cid,cname) VALUES('c003','化妆品');
#商品
INSERT INTO products(pid, pname,price,flag,category_id) VALUES('p001','联想',5000,'1','c001');
INSERT INTO products(pid, pname,price,flag,category_id) VALUES('p002','海尔',3000,'1','c001');
INSERT INTO products(pid, pname,price,flag,category_id) VALUES('p003','雷神',5000,'1','c001');

INSERT INTO products (pid, pname,price,flag,category_id) VALUES('p004','JACK JONES',800,'1','c002');
INSERT INTO products (pid, pname,price,flag,category_id) VALUES('p005','真维斯',200,'1','c002');
INSERT INTO products (pid, pname,price,flag,category_id) VALUES('p006','花花公子',440,'1','c002');
INSERT INTO products (pid, pname,price,flag,category_id) VALUES('p007','劲霸',2000,'1','c002');

INSERT INTO products (pid, pname,price,flag,category_id) VALUES('p008','香奈儿',800,'1','c003');
INSERT INTO products (pid, pname,price,flag,category_id) VALUES('p009','相宜本草',200,'1','c003');
```

## 1.交叉查询

```mysql
1.语法:
  select 列名 from 表A,表B
2.注意:
  交叉查询要防止笛卡尔乘积
```

```mysql
-- 查询所有商品的商品信息
SELECT * FROM category,products;

-- 属于内连接查询
SELECT * FROM category,products WHERE category.`cid` = products.`category_id`;
```

> 课程配图（未随笔记提交）



> 课程配图（未随笔记提交）

## 2.内连接查询

```mysql
1.关键字:inner join on   -> inner 可以省略
2.两种内连接方式
  a.显示内连接:select 列名 from 表A join 表B on 条件
  b.隐式内连接:select 列名 from 表A,表B where 条件
```

```mysql
-- 查询具体的商品信息->隐式内连接


-- 查询具体的商品信息->显示内连接


-- 用显示内连接的方式查询"化妆品"的商品信息

```

```sql
-- 查询具体的商品信息->隐式内连接
SELECT * FROM category,products WHERE category.`cid` = products.`category_id`;

SELECT * FROM category c,products p WHERE c.`cid` = p.`category_id`;
-- 查询具体的商品信息->显示内连接
SELECT * FROM category c JOIN products p ON c.`cid` = p.`category_id`;

-- 用显示内连接的方式查询"化妆品"的商品信息
SELECT * FROM category c JOIN products p ON c.`cid` = p.`category_id` AND cname='化妆品';

SELECT * FROM category c JOIN products p ON c.`cid` = p.`category_id` WHERE cname='化妆品';
```

## 3.外连接

```mysql
1.关键字:outer join on -> outer 可以省略
2.分两种:
  a.左外连接: select 列名 from 表A left join 表B on 条件
  b.右外连接: select 列名 from 表A right join 表B on 条件
3.分清楚谁是左边,谁是右表
  在join左边的就是左表;右边就是右表
4.左外连接,右外连接,内连接区别
```

```mysql
-- 查询所有的商品信息 左外连接


-- 查询所有的商品信息 右外连接


-- 查询所有的商品信息内连接

```

```sql
-- 查询所有的商品信息 左外连接
SELECT * FROM category c LEFT JOIN products p ON c.`cid` = p.`category_id`;

-- 查询所有的商品信息 右外连接
SELECT * FROM category c RIGHT JOIN products p ON c.`cid` = p.`category_id`;

-- 查询所有的商品信息内连接
SELECT * FROM category c JOIN products p ON c.`cid` = p.`category_id`;
```

> 课程配图（未随笔记提交）

## 4.union联合查询实现全外连接查询（了解）

```java
首先要明确，联合查询不是多表连接查询的一种方式。联合查询是将多条查询语句的查询结果合并成一个结果并去掉重复数据。
全外连接查询的意思就是将左表和右表的数据都查询出来，然后按照连接条件连接

只要将两个结果一连接,左表和右表没有交叉的部分也就都查出来了
```

```java
1.union的语法:
  查询语句1 union 查询语句2 union 查询语句3 ...
```

```mysql
-- 全外连接
SELECT * FROM category c LEFT JOIN products p ON c.`cid` = p.`category_id`
UNION
SELECT * FROM category c RIGHT JOIN products p ON c.`cid` = p.`category_id`;
```

## 5.子查询

```mysql
1.一条sql语句作为另外一条sql语句的条件使用
```

```mysql
-- 查询products表中'化妆品'的商品信息


-- 查询products表中化妆品和家电的商品信息

```

```sql
-- 查询products表中'化妆品'的商品信息
SELECT * FROM products WHERE category_id = 'c003';

/*
  单纯看products表,其实我们不确定c003一定是化妆品
  后来一想,c003是从category表中来的
  我们可以先利用化妆品当做条件将化妆品对应的id从category表中查询出来
  然后当条件使用
*/

SELECT cid FROM category WHERE cname = '化妆品';

SELECT * FROM products WHERE category_id = (SELECT cid FROM category WHERE cname = '化妆品');

-- 查询products表中化妆品和家电的商品信息
SELECT * FROM products WHERE category_id IN ('c001','c003');

-- 先从category中将c001和c003查询出来
SELECT cid FROM category WHERE cname IN('化妆品','家电');

SELECT * FROM products WHERE category_id IN (SELECT cid FROM category WHERE cname IN('化妆品','家电'));
```

## 6.子查询作为伪表使用

```mysql
一条查询语句之后查询出来的结果作为伪表和其他的表继续做联查
```

```mysql
-- 查询化妆品的所有商品信息

-- 查询所有化妆品和家电的商品信息
```

```sql
-- 查询化妆品的所有商品信息
SELECT * FROM category c,products p WHERE c.`cid` = p.`category_id` AND cname = '化妆品';

#先查询化妆品
SELECT * FROM category WHERE cname = '化妆品';

-- 组合

SELECT * FROM (SELECT * FROM category WHERE cname = '化妆品') c,products p WHERE c.`cid` = p.`category_id`;

-- 查询所有化妆品和家电的商品信息
-- 先将家电和化妆品查出来作为伪表
SELECT * FROM category WHERE cname IN ('化妆品','家电');

SELECT * FROM (SELECT * FROM category WHERE cname IN ('化妆品','家电')) c,products p WHERE c.`cid` = p.`category_id`

```

> 课程配图（未随笔记提交）

# 第七章.sql练习

## 1.创建数据库

```mysql
CREATE DATABASE mytest01;
USE mytest01;
```

## 2.创建表以及添加数据

```mysql
# 创建部门表dept  部门表中包含 部门id 部门名称
CREATE TABLE dept(
  id INT PRIMARY KEY AUTO_INCREMENT,
  NAME VARCHAR(20)
)

INSERT INTO dept (NAME) VALUES ('开发部'),('市场部'),('财务部');
```

```mysql
# 创建员工表
CREATE TABLE emp (
  id INT PRIMARY KEY AUTO_INCREMENT,
  NAME VARCHAR(10),
  gender CHAR(1),   -- 性别
  salary DOUBLE,   -- 工资
  join_date DATE,  -- 入职日期
  dept_id INT,
  FOREIGN KEY (dept_id) REFERENCES dept(id) -- 外键，关联部门表(部门表的主键)
)

INSERT INTO emp(NAME,gender,salary,join_date,dept_id) VALUES('小松松','男',7200,'2013-02-24',1);
INSERT INTO emp(NAME,gender,salary,join_date,dept_id) VALUES('鱼小鱼','女',3600,'2015-12-02',2);
INSERT INTO emp(NAME,gender,salary,join_date,dept_id) VALUES('小霈霈','男',8000,'2013-12-02',3);
INSERT INTO emp(NAME,gender,salary,join_date,dept_id) VALUES('亮仔','男',5000,'2017-11-11',2);
INSERT INTO emp(NAME,gender,salary,join_date,dept_id) VALUES('坤仔','男',8000,'2012-02-02',1);
INSERT INTO emp(NAME,gender,salary,join_date,dept_id) VALUES('福姐','女',6500,'2011-09-12',3);
INSERT INTO emp(NAME,gender,salary,join_date,dept_id) VALUES('熊姐','女',10500,'2018-12-02',3);
INSERT INTO emp(NAME,gender,salary,join_date,dept_id) VALUES('猛哥','男',9500,'2016-07-08',2);
INSERT INTO emp(NAME,gender,salary,join_date,dept_id) VALUES('栋栋','男',8500,'2018-06-28',2);
```

## 3.练习

```mysql
-- 1.查询员工和部门的名字
SELECT emp.`name`, dept.`name` FROM emp,dept WHERE emp.`dept_id` = dept.`id`;
```

```mysql
-- 2.查询鱼小鱼的信息，显示员工id，姓名，性别，工资和所在的部门名称(使用显式内连接)
SELECT * FROM emp e INNER JOIN dept d ON e.`dept_id` = d.`id` WHERE e.`name`='鱼小鱼';
```

```mysql
-- 3.将上面查到的内容 表头使用别名的形式展示 比如显示id为员工id  name为姓名 等
SELECT e.id 编号,e.name 姓名,e.gender 性别,e.salary 工资,d.name 部门名字 FROM emp e INNER JOIN dept d ON e.dept_id = d.id WHERE e.name='鱼小鱼';
```

```mysql
-- 4.在部门表中增加一个销售部
INSERT INTO dept (NAME) VALUES ('销售部');
SELECT * FROM dept;
```

```mysql
-- 5.查询所有的部门信息关联查询出该部门中的所有员工信息
SELECT * FROM dept d LEFT JOIN emp e ON d.`id` = e.`dept_id`;
```

```mysql
-- 6.查询所有的部门信息关联查询出该部门中的所有员工的名字  部门 以及 工资
SELECT e.name 姓名,d.name 部门, e.salary 工资 FROM dept d LEFT JOIN emp e ON d.id = e.dept_id;
```

```mysql
-- 7.统计出 每个部门的员工人数   查询显示 部门名称 人数
SELECT d.name 部门,COUNT(e.name) 人数 FROM dept d LEFT JOIN emp e ON d.id = e.dept_id GROUP BY d.name;
```

```mysql
-- 8.统计出 每个部门员工 平均薪资 按照 薪资排序 查询显示 部门名称 平均薪资
SELECT d.name 部门,AVG(e.salary) `平均薪资` FROM dept d LEFT JOIN emp e ON d.id = e.dept_id GROUP BY d.name ORDER BY salary;
```

```mysql
-- 9.统计出，每个部门的平均薪资 按照薪资排序 并且筛选出平均薪资>7000的部门
SELECT d.name 部门,AVG(e.salary) 人数 FROM dept d LEFT JOIN emp e ON d.id = e.dept_id
GROUP BY d.name HAVING AVG(e.salary)>7000 ORDER BY salary;
```

```mysql
-- 10.查询最高工资是多少
SELECT MAX(salary) FROM emp;
```

```mysql
-- 11.根据最高工资到员工表查询到对应的员工信息
SELECT * FROM emp WHERE salary=(SELECT MAX(salary) FROM emp)
```

```mysql
-- 12.查询工资小于平均工资的员工有哪些
SELECT * FROM emp WHERE salary < (SELECT AVG(salary) FROM emp);
```

```mysql
-- 13.查询工资大于5000的员工，来自于哪些部门的名字
 SELECT dept.name FROM dept WHERE dept.id IN (SELECT dept_id FROM emp WHERE salary > 5000
```

```mysql
-- 14.查询开发部与财务部所有的员工信息
SELECT * FROM emp WHERE dept_id IN (SELECT id FROM dept WHERE NAME IN('开发部','财务部'));
```

```mysql
-- 15.查询出2011年以后入职的员工信息，包括部门名称
SELECT * FROM dept d, (SELECT * FROM emp WHERE join_date > '2011-1-1') e WHERE e.dept_id = d.id;
```
