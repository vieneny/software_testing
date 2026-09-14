# day01_数据库基础

```java
课前回顾:
  1.HashMap:
    无序 无索引 key唯一,value可重复 线程不安全 可以存null  哈希表
    put get remove containsKey values  keySet entrySet
  2.LinkedHashMap:
    有序 无索引 key唯一,value可重复 线程不安全  哈希表+双向链表
  3.TreeSet:
    对元素进行排序 无索引 元素唯一  线程不安全 红黑树
    TreeSet()对元素进行自然排序 (ascii码表)
    TreeSet(比较器) 按照指定的顺序排序
  4.TreeMap:
    对key进行排序 无索引 key唯一,value可重复 线程不安全 红黑树
    TreeMap()对key进行自然排序 (ascii码表)
    TreeMap(比较器) 按照指定的顺序排序
  5.Hashtable
    无序 无索引 key唯一,value可重复 不可以存null 线程安全 哈希表
  6.Vector:
    有序 有索引 元素可重复 线程安全 数组
  7.Properties:
   无序 无索引 key唯一,value可重复 线程安全 key和value都是String 哈希表
   setProperty   getProperty  stringPropertyNames load
今日重点:
  1.会创建数据库以及创建表
  2.会对表中的数据进行增删改查
  3.认识基本的约束以及此约束的特点
```

# 第一章.数据库介绍

## 1.数据库介绍

```java
1.概述:存储数据的仓库
2.为啥要用数据库存数据:
  之前学的数组和集合都是临时存储(代码运行的时候数据还在,运行完毕,数据不在了),后来我们学了IO流,可以将数据永久保存到硬盘上,但是数据在txt中不好操作,所以我们需要学习数据库,将数据存到表中,然后用数据库独有的语句根据条件快速定位到这个单元格中,对单元格中的数据进行增删改查操作
```

> 常见的关系型数据库:
>
> mysql    oracle

## 2.数据库管理系统

```java
1.注意:我们程序员不是直接去操作数据库中的数据,数据库都有一个库管,这个库管帮我们去操作数据库->数据库管理系统
2.作用:保证数据库中的数据的一个统一性,安全性
```

<img src="image/image-20260203093250183.png" alt="image-20260203093250183" style="zoom:80%;" />

## 3.数据库表

```java
1.概述:就是存放数据的地方 -> table
2.表由哪几部分构成:
  a.表名
  b.列名(字段名),每一列要指定数据类型
  c.行
```

## 4.数据库表和Java类的对应关系

```java
1.表名 -> 类名
2.列名 -> 属性名
3.每一列的类型 -> 属性的类型
4.每一行 -> javabean对象
5.单元格数据 -> javabean对象的属性值

  第一行: User user1 = new User(1,"tom","111")
  第二行: User user2 = new User(2,"jack","222")
```

<img src="image/image-20260203093928246.png" alt="image-20260203093928246" style="zoom:80%;" />

### 4.1.javabean在开发中如何跟表联系起来的->添加数据

```
将页面中的数据封装成javabean对象,将这一个javabean对象传递到dao层,然后将javabean封装好的数据获取出来,放到sql语句中进行添加
```

<img src="img/1744508169718.png" alt="1744508169718" style="zoom:80%;" />

### 4.2.javabean在开发中如何跟表联系起来的->查询数据

```java
将数据库中查询出来的数据封装成多个javabean对象,然后将多个javabean对象放到一个集合中,最终返回给页面进行展示
```

<img src="img/1744508271847.png" alt="1744508271847" style="zoom:80%;" />

# 第二章.mysql8安装

## 1.MySQL数据库安装

![](img/2.png)

![](img/3.png)

![](img/4.png)

![](img/5.png)



![](img/6.png)

![](img/7.png)



![](img/8.png)

![](img/9.png)

> ​                     一定要选择传统密码

![](img/10.png)

![](img/11.png)

![](img/12.png)

![](img/13.png)



## 2.数据库服务启动和停止

```java
MySQL软件的服务器端必须先启动，客户端才可以连接和使用使用数据库。
```

### 2.1.方式1:图形化方式

```java
* 计算机（点击鼠标右键）==》管理（点击）==》服务和应用程序（点击）==》服务（点击）==》MySQL57（点击鼠标右键）==》启动或停止（点击）
* 控制面板（点击）==》系统和安全（点击）==》管理工具（点击）==》服务（点击）==》MySQL57（点击鼠标右键）==》启动或停止（点击）
* 任务栏（点击鼠标右键）==》启动任务管理器（点击）==》服务（点击）==》MySQL57（点击鼠标右键）==》启动或停止（点击）
```

### 2.2.方式2:命令方式

```java
启动 MySQL 服务命令：
net start MySQL80

停止 MySQL 服务命令：
net stop MySQL80
```

## 3.配置数据库环境变量

### 3.1.方式1:使用MYSQL_HOME

| 环境变量名 | 操作 |              环境变量值              |
| :--------: | :--: | :----------------------------------: |
| MYSQL_HOME | 新建 | D:\ProgramFiles\mysql\MySQLServer5.7 |
|    path    | 编辑 |           %MYSQL_HOME%\bin           |

### 3.2.方式2:直接配置mysql的bin路径

| 环境变量名 | 操作 |                环境变量值                |
| :--------: | :--: | :--------------------------------------: |
|    path    | 编辑 | D:\ProgramFiles\mysql\MySQLServer5.7\bin |

## 4.数据库服务端安装之后登陆

```java
1.win+R-->调出黑窗口
2.登录命令:
  a.mysql -u用户名 -p密码->回车   -> 缺点,在登录的时候密码显示出来了
  b.mysql -u 用户名 -p   ->回车
    输入密码(密码将显示成小星星)
```

```mysql
问题:输入mysql命令出现"不是内部或外部命令"
原因:环境变量没配置
解决:将mysql安装路径下的bin目录复制到环境变量下的path中
    如果path下有,还出现了"不是内部或者外部命令",干掉重新配置一下
```

```java
问题:ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)
原因:输入的mysql用户名或者密码有问题
```

```java
问题:ERROR 2003 (HY000): Can't connect to MySQL server on 'localhost' (10061)
原因:mysql服务没有启动
```

## 5.黑窗口乱码问题(可以忽略)

```java
1.在黑窗口中默认编码为GBK,而我们mysql为UTF-8,所以在黑窗口中操作中文就会乱码
2.解决:
  a.在黑窗口中输入:set names gbk   ->临时将mysql编码修改成gbk
  b.在mysql安装路径下修改my.ini文件，将涉及到编码的地方都修改了,重启服务所有地方生效。
```

```java
在路径：D:\ProgramFiles\mysql\MySQLServer8\Data 找到my.ini文件

修改内容1：
    找到[mysql]命令，大概在63行左右，在其下一行添加
        default-character-set=utf8
修改内容2:
    找到[mysqld]命令，大概在76行左右，在其下一行添加
        character-set-server=utf8
        collation-server=utf8_general_ci

修改完毕后，重启MySQL57服务
```

```java
show variables like 'character_%';
show variables like 'collation_%';
```

![image-20210913231100322](img/image-20210913231100322.png)



## 6.mysql客户端(可视化工具)安装

```java
例如：Navicat Preminum，SQLyog 等工具
```

### 6.1.SQLyog

![image-20210913231743884](img/image-20210913231743884.png)

<img src="img/image-20220402094150194.png" alt="image-20220402094150194" style="zoom:80%;" />

```java
通过黑窗口先登录数据库
处理无法连接：ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '你的密码';
```

<img src="img/1684723765667.png" alt="1684723765667" style="zoom:80%;" />

### 6.2.Navicat

![image-20210913231808531](img/image-20210913231808531.png)

# 第三章.sql语言

## 1.sql语言介绍

```java
1.什么叫做sql语言:是所有关系型数据库语法的一个标准,规范
2.作用:规范了关系型数据库的语法以及一些关键字的使用: create drop insert select update等
3.注意:不同的关系型数据库在都遵守sql语言规范的基础上,会有一些差异,这些差异叫做sql方言
```

## 2.sql语言分类

```java
- 数据定义语言：简称DDL(Data Definition Language)，用来定义数据库对象：数据库，表，列等。关键字：create，alter，drop等

- 数据操作语言：简称DML(Data Manipulation Language)，用来对数据库中表的记录进行操作。关键字：insert，delete，update等

- 数据控制语言：简称DCL(Data Control Language)，用来定义数据库的访问权限和安全级别，及创建用户。

- 数据查询语言：简称DQL(Data Query Language)，用来查询数据库中表的记录。关键字：select，from，where等
```

## 3.sql语句的通用语法

```sql
1.- SQL语句可以单行或多行书写，以分号结尾
2.- 可使用空格和缩进来增强语句的可读性:基本上一个单词就一个空格
3.- MySQL数据库的SQL语句不区分大小写，关键字建议使用大写

  - 例如：SELECT * FROM user。
4.- 同样可以使用/**/的方式完成注释
    /*
     我是一个注释
    */
    #我也是一个注释
   -- 我也是一个注释
```

## 4.sql中的数据类型

| **类型名称**          | 说明                                                         |
| --------------------- | ------------------------------------------------------------ |
| int                   | 整数类型                                                     |
| double                | 小数类型                                                     |
| decimal（m,d）        | 指定整数位与小数位长度的小数类型                             |
| date                  | 日期类型，格式为yyyy-MM-dd，包含年月日，不包含时分秒  2020-01-01 |
| datetime              | 日期类型，格式为 YYYY-MM-DD HH:mm:ss，包含年月日时分秒   到9999年 |
| timestamp             | 日期类型，时间戳  从1970年到2038年                           |
| varchar（字符串长度） | 文本类型， M为0~65535之间的整数                              |

```java
我们先学  mysql
```

# 第四章.mysql中语句

## 1.DDL之数据库操作：database

### 1.1 创建数据库

```mysql
语法: create database `库名`
```

```mysql
-- 创建库
CREATE DATABASE `bj20260108`;
```

> 库名,表名,列名建议用``包裹
>
> <img src="image/image-20260203103610540.png" alt="image-20260203103610540" style="zoom:80%;" />



### 1.2 查看数据库(了解)

```mysql
语法: show databases
```

```sql
-- 查看库
SHOW DATABASES;
```

### 1.3 删除数据库

```mysql
语法:drop database `库名`
```

```mysql
-- 删除库
DROP DATABASE `bj20260108`;
```

<img src="image/image-20260203104234589.png" alt="image-20260203104234589" style="zoom:80%;" />

### 1.4 使用数据库(切换数据库)

```mysql
语法:use `库名`
```

```mysql
-- 切换库
USE `bj20260108`;
```

## 2.DDL之表操作->table

### 2.1 创建表

```mysql
create table `表名`(
  列名 数据类型(长度)[约束],
  列名 数据类型(长度)[约束],
  列名 数据类型(长度)[约束]
)
```

```mysql
#创建表
CREATE TABLE `products`(
   pid INT,
   pname VARCHAR(10),
   pdesc VARCHAR(20)
)
```

<img src="image/image-20260203111847127.png" alt="image-20260203111847127" style="zoom:80%;" />

### 2.3 查看表(了解)

```mysql
#查看所有表
show tables;

#查看表结构
desc 表名;
```

```mysql
#查看所以表
SHOW TABLES;

#查看表结构
DESC products;
```

### 2.4 删除表

```mysql
1.语法:
  drop table `表名`
```

```mysql
#删除表 drop table `表名`
DROP TABLE products;
```

### 2.5修改表结构(了解)

```java
alter table 表名 add 列名 类型(长度) [约束];
作用：添加列.
```

```mysql
ALTER TABLE products ADD price DOUBLE;
```

```mysql
alter table 表名 modify 列名 类型(长度) [约束];
  作用：修改列的类型,长度及约束.
```

```mysql
ALTER TABLE products MODIFY price INT;
```

```mysql
  alter table 表名 change 旧列名 新列名 类型(长度) [约束];
  作用：修改列名.
```

```mysql
ALTER TABLE products CHANGE price jiage DOUBLE;
```

```mysql
  alter table 表名 drop 列名;
  作用：修改表_删除列.
```

```mysql
ALTER TABLE products DROP jiage;
```

```mysql
 rename table 表名 to 新表名;
 作用：修改表名
```

```mysql
RENAME TABLE products TO goods;

RENAME TABLE goods TO products;
```

## 3.DML之数据操作语言

### 3.1 插入数据

```mysql
1.关键字: insert into values
2.语法:
  a.insert into 表名 (列名1,列名2) values (值1,值2)
  b.insert into 表名 values (值1,值2)-> 如果不指定列名,那么我们的值就需要覆盖所有列
  c.insert into 表名 (列名1,列名2) values (值1,值2),(值1,值2),(值1,值2)...   -> 一次添加多条数据
```

```mysql
/*
   如果数据为varchar类型,那么不建议用双引号,建议用单引号
   因为将来我们需要将sql语句放到java中写
   String sql = "INSERT INTO products (pid,pname,pdesc) VALUES (1,"苹果","通红但不甜的")"
   双引号会自动匹配,有可能将一些字符匹配到引号外面去,就报错了

   如果用单引号如下:
     String sql = "INSERT INTO products (pid,pname,pdesc) VALUES (1,'苹果','通红但不甜的')"
*/

#a.insert into 表名 (列名1,列名2) values (值1,值2)
-- insert into products (pid,pname,pdesc) values (1,"苹果","通红但不甜的");

-- 建议用单引号
INSERT INTO products (pid,pname,pdesc) VALUES (2,'梨','吃一口得糖尿病');

#b.insert into 表名 values (值1,值2)-> 如果不指定列名,那么我们的值就需要覆盖所有列
INSERT INTO products VALUES (3,'香蕉','蕉绿的');

#c.insert into 表名 (列名1,列名2) values (值1,值2),(值1,值2),(值1,值2)...   -> 一次添加多条数据
INSERT INTO products (pid,pname,pdesc) VALUES (4,'西瓜','都是籽'),(5,'榴莲','微房'),(6,'草莓','嗷嗷酸');
```

> 1.表名,库名,列名用``
>
> 2.varchar类型的数据用''

### 3.2 删除数据

```mysql
1.关键字: delete from where
2.语法:
  a.delete from 表名 -> 将所有数据都删除
  b.delete from 表名 where 条件
```

| java | mysql       |
| ---- | ----------- |
| ==   | =           |
| >    | >           |
| <    | <           |
| >=   | >=          |
| <=   | <=          |
| !=   | !=  或者 <> |

```sql
-- 删除cid为1的记录
-- 删除cid>=5的记录
-- 删除cid不等于3的记录
```

```sql
DELETE FROM products;

-- 删除pid为1的记录
DELETE FROM products WHERE pid = 1;
-- 删除pid>=5的记录
DELETE FROM products WHERE pid >= 5;
-- 删除pid不等于3的记录
DELETE FROM products WHERE pid != 3;
DELETE FROM products WHERE pid <> 3;
DELETE FROM products WHERE NOT (pid = 3);
```

### 3.3 修改数据

```mysql
1.关键字: update set where
2.语法: update 表名 set 列名 = 新值 where 条件
```

```mysql
-- 将表中的内裤改成裤衩

-- 将pid为5的desc改成涛哥买的

-- 将pid不等于1的pname都改成睡衣
```

```sql
-- 将表中的内裤改成裤衩
UPDATE products SET pname = '裤衩' WHERE pname = '内裤';
-- 将pid为5的pdesc改成涛哥买的
UPDATE products SET pdesc = '涛哥买的' WHERE pid = 5;
-- 将pid不等于1的pname都改成睡衣
UPDATE products SET pname = '睡衣' WHERE pid!=1;
```

# 第五章.约束

```java
约束是对指定列的数据进行约束
```

## 1.主键约束

```mysql
1.关键字: primary key
2.特点:
  a.一张表中应该有一个主键
  b.主键列的数据代表一整行数据,相当于人的身份证
  c.主键列中的数据不能重复
  d.主键列中的数据不能为NULL
```

### 1.1.添加方式1:在创建表时,在字段后面直接指定(重点)

```mysql
create table 表名(
  列名 数据类型(长度) primary key,
  列名 数据类型(长度),
  列名 数据类型(长度)
);
```

```sql
#方式1:在创建表的时候确定约束
CREATE TABLE category(
  cid INT PRIMARY KEY,
  cname VARCHAR(20)
);

INSERT INTO category(cid,cname) VALUES (1,'蔬菜');
-- INSERT INTO category(cid,cname) VALUES (1,'水果');
-- INSERT INTO category(cid,cname) VALUES (null,'服装');
```

### 1.2.添加方式2:在constraint约束区域,去指定主键约束

```mysql
1.什么叫做constraint域
  创建表的时候,最后一列和右半个小括号之间的区域
2.语法:
  [constraint 名字] primary key (字段名)
3.注意:[constraint 名字]:可写可不写
```

```mysql
CREATE TABLE category(
  cid INT,
  cname VARCHAR(20),
  PRIMARY KEY(cid)
);
```

<img src="image/image-20260203145428372.png" alt="image-20260203145428372" style="zoom:80%;" />

### 1.3.添加方式3:通过修改表结构的方式

```mysql
1.格式:ALTER TABLE 表名 ADD [CONSTRAINT 名称] PRIMARY KEY (字段列表)
2.注意:[CONSTRAINT 名称]可以省略不写
```

```mysql
CREATE TABLE category(
  cid INT,
  cname VARCHAR(20)
);

ALTER TABLE category ADD PRIMARY KEY (cid);
```

### 1.4.联合主键

```mysql
1.概述:多个列并成为一个主键
2.特点:
  主键的多个列中的数据不能完全一样,不能为NULL
```

```mysql
-- 联合主键

CREATE TABLE person(
  xing VARCHAR(10),
  ming VARCHAR(10),
  city VARCHAR(10),
  PRIMARY KEY(xing,ming)
);

INSERT INTO person (xing,ming,city) VALUES ('柳','岩','湖南');
INSERT INTO person (xing,ming,city) VALUES ('柳','青','湖南');
INSERT INTO person (xing,ming,city) VALUES ('柳','岩','河北');
```

### 1.5.删除主键约束

```mysql
ALTER TABLE 表名 DROP PRIMARY KEY->删除主键约束
```

```mysql
ALTER TABLE person DROP PRIMARY KEY;
```

## 2.自增长约束

### 2.1.基本操作

```mysql
1.关键字:auto_increment
2.特点:
  a.都是配合主键约束使用
  b.主键自增长的列中的数据不用我们自己维护,mysql会自动维护
  c.如果删除最后一条数据,我们重新添加,不会重新生成最后那一条数据的编号,会继续往下编
```

``` mysql
CREATE TABLE `user`(
  uid INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(10),
  `password` VARCHAR(10)
)

INSERT INTO `user` (username,`password`) VALUES ('tom','111');
INSERT INTO `user` (username,`password`) VALUES ('jack','222');

-- 如果不指定列名,我们所写的值就必须覆盖所有列
INSERT INTO `user` VALUES (NULL,'rose','333');

-- 删除
DELETE FROM `user` WHERE uid = 3;

INSERT INTO `user` VALUES (NULL,'jerry','444');


-- truncate table 表名 -> 摧毁表结构,删除所有数据,再添加会重新编号
TRUNCATE TABLE `user`;
```

> ```mysql
> /*
> 自增长是一个约束,操作起来和其他约束不太一样
>
> 如果自增长约束和主键约束合起来使用想删除
>
> 先删除自增长约束
> 再删除主键约束
>
> */
>
> drop table category;
> create table category(
> cid int primary key auto_increment,
> cname varchar(100)
> );
>
> alter table category modify cid int;
>
> alter table category drop primary key;
> ```

### 2.2.truncate和delete区别

```mysql
1.delete:如果是主键自增长,删除之后,再次添加,编号不会重新编号,会接着被删除的那个编号往下继续编
2.truncate:摧毁表结构,主键自增长列,会重新编号
```

<img src="image/image-20260203154937162.png" alt="image-20260203154937162" style="zoom:80%;" />

## 3.非空约束

```mysql
1.关键字:NOT NULL
2.特点:
  非空约束的列中的数据不能为NULL
```

```mysql
CREATE TABLE student(
  sid INT PRIMARY KEY AUTO_INCREMENT,
  sname VARCHAR(10) NOT NULL,
  score INT
);

INSERT INTO student(sname,score) VALUES ('tom',100);


-- 相当于 String s = null
-- INSERT INTO student(sname,score) VALUES (null,98);


-- 相当于 String s = ""
INSERT INTO student(sname,score) VALUES ('',99);

-- 相当于 String s = "null"
INSERT INTO student(sname,score) VALUES ('null',97);
```

## 4.唯一约束

```mysql
1.关键字:UNIQUE
2.特点:
  被唯一约束修饰的列中的数据不能重复
3.主键约束和唯一约束区别:
  a.相同点:都是唯一的
  b.不同点:
    一个表中能有多个唯一约束,而且可以存null
    一个表中只能有一个主键约束,而且主键约束代表一条数据,不能存null
```

```mysql
CREATE TABLE role(
   rid INT PRIMARY KEY AUTO_INCREMENT,
   rname VARCHAR(10) UNIQUE
);

INSERT INTO role (rname) VALUES ('护士');
INSERT INTO role (rname) VALUES ('教师');
INSERT INTO role (rname) VALUES ('皇上');
INSERT INTO role (rname) VALUES ('娘娘');
-- INSERT INTO role (rname) VALUES ('娘娘');
```

```mysql
删除唯一约束:
 ALTER TABLE 表名 DROP INDEX 名称   [名称是CONSTRAINT后面的名称]
```

# 第六章.单表查询

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
1.关键字: select from
2.语法:
  a.select * from 表名 -> 从指定表中查询所有数据,*代表的是展示所有列
  b.select 列名,列名 from 表名 -> 从指定表中查询所有数据,展示指定的列
3.注意:
  我们查询出来的结果,也是表的格式,但是它是一张"伪表"

  "伪表"也可以当成一个表和其他的表做多表联查
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
SELECT pname,price+100 FROM product;


/*
  给列和表取别名

  as 别名

  as可以省略
*/
SELECT pname,price+100 `newprice` FROM product;

-- 也可以给表取别名,但是不涉及到多表查询,给表取别名看不出效果来
SELECT * FROM product p;
```
