# day03.函数_jdbc

```mysql
课前回顾:
  1.条件查询: select 列名 from 表名 where 条件
  2.排序查询: select 列名 from 表名 order by 排序字段 排序规则(ASC|DESC)
  3.分组查询: select 列名 from 表名 group by 分组字段 having 条件
  4.聚合查询: select 聚合函数(列名) from 表名 where 条件
  5.分页查询: select 列名 from 表名 limit m,n
    m:每一页起始位置 -> (当前页-1)*n
    n:每页显示条数
    总记录数:用count函数统计
    总页数: 总记录数/每页显示条数 -> 不能整除向上取整
  6.多表关系:
    一对一  一对多   多对多
  7.内连接查询:
    a.隐式: select 列名 from 表A,表B where 条件
    b.显示: select 列名 from 表A join 表B on 条件
  8.外连接查询:
    a.左外连接: select 列名 from 表A left join 表B on 条件
    b.右外连接: select 列名 from 表A right join 表B on 条件
  9.子查询:select语句嵌套

今日重点:
  1.会字符串和流程函数
  2.第三章,第四章 -> JDBC的使用
```

# 第一章.MySQL的常用函数

```java
mysql中的函数,都是纵向操作
```

##  1.字符串函数

### 1.1 字符串函数列表概览

| 函数                                  | 用法                                          |
| ------------------------------------- | --------------------------------------------- |
| CONCAT(S1,S2,......,Sn)               | 连接S1,S2,......,Sn为一个字符串               |
| CONCAT_WS(separator, S1,S2,......,Sn) | 连接S1一直到Sn，并且中间以separator作为分隔符 |
| UPPER(s) 或 UCASE(s)                  | 将字符串s的所有字母转成大写字母               |
| LOWER(s)  或LCASE(s)                  | 将字符串s的所有字母转成小写字母               |
| TRIM(s)                               | 去掉字符串s开始与结尾的空格                   |
| SUBSTRING(s,index,len)                | 返回从字符串s的index位置其len个字符           |

### 1.2 环境准备

```mysql
-- 用户表
CREATE TABLE t_user (
  id int(11) NOT NULL AUTO_INCREMENT,
  uname varchar(40) DEFAULT NULL,
  age int(11) DEFAULT NULL,
  sex int(11) DEFAULT NULL,
  PRIMARY KEY (id)
);
insert  into t_user values (null,'zs',18,1);
insert  into t_user values (null,'ls',20,0);
insert  into t_user values (null,'ww',23,1);
insert  into t_user values (null,'zl',24,1);
insert  into t_user values (null,'lq',15,0);
insert  into t_user values (null,'hh',12,0);
insert  into t_user values (null,'wzx',60,null);
insert  into t_user values (null,'lb',null,null);
```

### 1.3 字符串连接函数

字符串连接函数主要有2个：

| 函数或操作符                          | 描述                                     |
| ------------------------------------- | ---------------------------------------- |
| concat(str1, str2, ...)               | 字符串连接函数，可以将多个字符串进行连接 |
| concat_ws(separator, str1, str2, ...) | 可以指定间隔符将多个字符串进行连接；     |

练习1：使用concat函数显示出 你好uname 的结果

```mysql
/*
  concat(str1, str2, ...)
  字符串连接函数，可以将多个字符串进行连接

  concat_ws(separator, str1, str2, ...)->可以指定间隔符将多个字符串进行连接
*/
-- 拼接字符串练习 练习1：使用concat函数显示出 你好uname 的结果

```

```sql
SELECT CONCAT('你好',uname) uname,age,sex FROM t_user;
```

练习2：使用concat_ws函数显示出 你好,uname 的结果

```mysql
-- 练习2：使用concat_ws函数显示出 你好,uname 的结果
```

```mysql
SELECT CONCAT_WS(',','你好',uname) uname,age,sex FROM t_user;
```

### 1.4 字符串大小写处理函数

字符串大小写处理函数主要有2个：

| 函数或操作符 | 描述              |
| ------------ | ----------------- |
| upper(str)   | 得到str的大写形式 |
| lower(str)   | 得到str的小写形式 |

练习1： 将字符串 uname 转换为大写显示

```mysql
-- 将hello转成大写


-- 查询t_user,uname变成大写

```

```sql
-- 将hello转成大写
SELECT UPPER('hello');

-- 查询t_user,uname变成大写
SELECT UPPER(uname) uname,age,sex FROM t_user;
```

练习2：将uname 转换为小写显示

```mysql
-- 查询t_user,uname变成小写
```

```sql
自己写
```

### 1.5 移除空格函数

可以对字符串进行按长度填充满、也可以移除空格符

| 函数或操作符 | 描述                  |
| ------------ | --------------------- |
| trim(str)    | 将str两边的空白符移除 |

练习1： 将用户id为9的用户的姓名的两边空白符移除

```mysql
-- 将用户id为9的用户的姓名的两边空白符移除
```

```sql
SELECT TRIM(uname),age,sex FROM t_user WHERE id = 9;
```

### 1.6 子串函数

字符串也可以按条件进行截取，主要有以下可以截取子串的函数;

| 函数或操作符          | 描述                                                         |
| --------------------- | ------------------------------------------------------------ |
| substr()、substring() | 获取子串： 1：substr(str, pos) 、substring(str, pos)； 2：substr(str, pos, len)、substring(str, pos, len) |

```mysql
/*
  substring(str, pos)
            str:被截取的字符串
            pos:从第几个字符开始截取
  substring(str, pos, len)
            str:被截取的字符串
            pos:从第几个字符开始截取
            len:截取多少个
*/

```

```mysql
SELECT SUBSTRING('abcdefg',2);
SELECT SUBSTRING('abcdefg',2,2);
```

练习1：获取 hello,world 从第二个字符开始的完整子串

```mysql
自己写
```

练习2：获取 hello,world 从第二个字符开始但是长度为4的子串

```mysql
自己写
```

## 2.数值函数

### 2.1. 数值函数列表

| 函数     | 用法                  |
| -------- | --------------------- |
| ABS(x)   | 返回x的绝对值         |
| CEIL(x)  | 返回大于x的最小整数值 |
| FLOOR(x) | 返回小于x的最大整数值 |
| RAND()   | 返回0~1的随机值       |
| POW(x,y) | 返回x的y次方          |

### 2.2. 常用数值函数练习

```mysql
-- 练习1： 获取 -12 的绝对值


-- 练习2： 将 -11.2 向上取整


-- 练习3： 将 1.6 向下取整


-- 练习4： 获得2的2次幂的值

-- 练习5： 获得一个在0-100之间的随机数

```

```sql
-- 练习1： 获取 -12 的绝对值
SELECT ABS(-12);

-- 练习2： 将 -11.2 向上取整
SELECT CEIL(-11.2);

-- 练习3： 将 1.6 向下取整
SELECT FLOOR(1.6);


-- 练习4： 获得2的2次幂的值
SELECT POW(2,2);
-- 练习5： 获得一个在0-100之间的随机数
SELECT RAND()*100;
```

## 3.日期函数

### 3.1 日期函数列表

| 函数                                                         | 用法                                                      |
| ------------------------------------------------------------ | --------------------------------------------------------- |
| **CURDATE()** 或 CURRENT_DATE()                              | 返回当前日期  年月日                                      |
| **CURTIME()** 或 CURRENT_TIME()                              | 返回当前时间  时分秒                                      |
| **NOW()** / SYSDATE() / CURRENT_TIMESTAMP() / LOCALTIME() / LOCALTIMESTAMP() | 返回当前系统日期时间                                      |
| DATEDIFF(date1,date2) / TIMEDIFF(time1, time2)               | 返回date1 - date2的日期间隔 / 返回time1 - time2的时间间隔 |

### 3.2 常用日期函数的练习

```mysql
-- 练习1：获取当前的日期(仅仅需要年月日)


-- 练习2： 获取当前的时间（仅仅需要时分秒）


-- 练习3： 获取当前日期时间（包含年月日时分秒）



-- 练习4: 获取到12月1日还有多少天

```

```sql
-- 练习1：获取当前的日期(仅仅需要年月日)
SELECT CURDATE();

-- 练习2： 获取当前的时间（仅仅需要时分秒）
SELECT CURTIME();


-- 练习3： 获取当前日期时间（包含年月日时分秒）
SELECT NOW();


-- 练习4: 获取到2月10日还有多少天
SELECT DATEDIFF('2026-2-10',NOW());
```

## 4.流程函数_判断

| 函数                                                         | 用法                                         |
| ------------------------------------------------------------ | -------------------------------------------- |
| IF(比较,t ,f)<br>里面的t和f是两个结果                        | 如果比较是真，返回t，否则返回f               |
| IFNULL(value1, value2)                                       | 如果value1不为空，返回value1，否则返回value2 |
| CASE WHEN 条件1 THEN result1 WHEN 条件2 THEN result2 .... [ELSE resultn] END | 相当于Java的if...else if...else...           |

* 练习1：获取用户的姓名、性别，如果性别为1则显示'男'，否则显示'女'；要求使用if函数查询：

  ```mysql
  SELECT uname,IF(sex=1,'男','女') sex FROM t_user;
  ```


* 练习2：获取用户的姓名、性别，如果性别为null则显示为0；要求使用ifnull函数查询：

  ```mysql
  SELECT uname,IFNULL(sex,0) sex FROM t_user;
  ```


* 练习3：如果age<=12,显示儿童,如果age<=18,显示少年,如果age<=40,显示中年,否则显示老年

  ```mysql
  SELECT
    uname,
    CASE
      WHEN age <= 12
      THEN '儿童'
      WHEN age <= 18
      THEN '少年'
      WHEN age <= 40
      THEN '青年'
      ELSE '中老年'
    END age,
    sex
  FROM
    t_user ;
  ```

# 第二章 DCL语句

我们现在默认使用的都是root用户，超级管理员，拥有全部的权限。但是，一个公司里面的数据库服务器上面可能同时运行着很多个项目的数据库。所以，我们应该根据不同的项目建立不同的用户，分配不同的权限来管理和维护数据库。

<img src="image/image-20260206102646174.png" alt="image-20260206102646174" style="zoom:80%;" />

## 2.1 创建用户

```mysql
CREATE USER '用户名'@'主机名' IDENTIFIED BY '密码';
```

**关键字说明：**

```java
1.用户名:创建的用户名
2.主机名:指定该用户在哪个主机上可以登录,如果是本地用户,可以用'localhost',如果想让该用户可以任意远程主机登录,可以使用通配符%
3.密码:该用户登录的密码,密码可以为空,如果为空,该用户可以不输入密码就可以登录mysql
```

**具体操作：**

```sql
-- user1用户只能在localhost这个IP登录mysql服务器
CREATE USER 'user1'@'localhost' IDENTIFIED BY '123';
-- user2用户可以在任何电脑上登录mysql服务器
CREATE USER 'user2'@'%' IDENTIFIED BY '123';
```

## 2.2 授权用户

用户创建之后，基本没什么权限！需要给用户授权
![](img/DCL02.png)

**授权格式**：

```sql
GRANT 权限1, 权限2... ON 数据库名.表名 TO '用户名'@'主机名';
```

**关键字说明**：

```java
a.GRANT:授权关键字
b.授予用户的权限,比如  'select' 'insert' 'update'等,如果要授予所有的权限,使用 'ALL'
c.数据库名.表名:该用户操作哪个数据库的哪些表,如果要授予该用户对所有数据库和表的相关操作权限,就可以用*表示: *.*
d.'用户名'@'主机名':给哪个用户分配权限
```

**具体操作：**

1. 给user1用户分配对test这个数据库操作的权限

   ```sql
   GRANT CREATE,ALTER,DROP,INSERT,UPDATE,DELETE,SELECT ON test.* TO 'user1'@'localhost';
   ```

   ![](img/DCL03.png)

2. 给user2用户分配对所有数据库操作的权限

   ```sql
   GRANT ALL ON *.* TO 'user2'@'%';
   ```

   ![](img/DCL04.png)

## 2.3 撤销授权

```sql
REVOKE  权限1, 权限2... ON 数据库.表名 FROM '用户名'@'主机名';
```

**具体操作：**

* 撤销user1用户对test操作的权限

  ```sql
  REVOKE ALL ON test.* FROM 'user1'@'localhost';
  ```

  ![](img/DCL05.png)

## 2.4 查看权限

```sql
SHOW GRANTS FOR '用户名'@'主机名';
```

**具体操作：**

* 查看user1用户的权限

  ```sql
  SHOW GRANTS FOR 'user1'@'localhost';
  ```

  ![](img/DCL06.png)

## 2.5 删除用户

```sql
DROP USER '用户名'@'主机名';
```

**具体操作：**

* 删除user2

  ```sql
   DROP USER 'user2'@'%';
  ```

  ![](img/DCL07.png)

```mysql
/*
  分配用户:
    create:创建
    user:用户
    'user1'@'localhost' : 用户名以及可以访问的主机地址
    IDENTIFIED BY '123' : 分配密码

    %:可以在任意远程主机上登录
*/
-- user1用户只能在localhost这个IP登录mysql服务器
CREATE USER 'user1'@'localhost' IDENTIFIED BY '123';
-- user2用户可以在任何电脑上登录mysql服务器
CREATE USER 'user2'@'%' IDENTIFIED BY '123';


/*
   grant:分配权限关键字
   grant后面跟的就是具体的操作权限:select insert update等,如果分配所有权限就写ALL

   on:后面跟的是数据库名字 -> 指定啥数据库那么用此用户登录就只能看到哪个数据库名字

   `220706_mysql03`.* -> 指定库中所有的表 * 代表所有,如果想要看到所有的库以及所有的表我们就写*.*

   to:指明此权限要给的用户
*/
-- 给用户1分配权限
GRANT SELECT ON `230222_day02_2`.* TO 'user1'@'localhost';

-- 给用户2分配权限
GRANT ALL ON *.* TO 'user2'@'%';

/*
  drop:删除用户关键字
*/
DROP USER 'user2'@'%';
DROP USER 'user1'@'localhost';
```

## 2.6 修改用户密码

### 2.6.1 修改管理员密码

```sql
mysqladmin -uroot -p password 新密码  -- 新密码不需要加上引号
```

>注意：需要在未登陆MySQL的情况下操作。

**具体操作：**

   ```sql
mysqladmin -uroot -p password root
输入老密码
   ```

   ![](img/DCL08.png)

### 2.6.2 修改普通用户密码

```sql
set password for '用户名'@'主机名' = password('新密码');
```

>注意：需要在登陆MySQL的情况下操作。

**具体操作：**

   ```sql
set password for 'user1'@'localhost' = password('666666');
   ```

   ![](img/DCL09.png)

# 第三章.JDBC

## 1.JDBC介绍

```java
1.概述:Java Database Connectivity(java数据库连接),他是java连接数据库,操作数据库的一套标准
```

<img src="image/image-20260206104331483.png" alt="image-20260206104331483" style="zoom:80%;" />

## 2.JDBC准备(导入jdbc依赖)

```java
JDBC核心依赖:
```

```xml
<!--
   mysql核心依赖
 -->
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>8.0.26</version>
</dependency>
```

```java
jdbc四大核心对象:
  1.DriverManager类: 注册驱动
  2.Connection接口: 连接数据库
  3.Statement接口:  执行sql语句
  4.ResultSet接口:  处理结果集 -> 只针对于查询,增删改不需要处理结果集
```

## 3.JDBC开发步骤以及详解

```java
1.注册驱动:DriverManager类

2.获取连接:Connection
  DriverManager.getConnection(url, username, password)

3.准备sql:写sql语句

4.获取执行平台:Statement  -> Connection中的方法
  Statement createStatement()

5.执行sql:Statement中的方法
  int executeUpdate(sql) 针对于增删改操作的
  ResultSet executeQuery(sql) 针对于查询,返回的是结果集

6.处理结果集:ResultSet -> 增删改操作不用处理结果集

7.关闭资源:close方法
```

## 4.JDBC注册驱动

```mysql
CREATE TABLE `user`(
  uid INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(20),
  `password` VARCHAR(20)
);
```

```java
        /*
           1.注册驱动:DriverManager
             static void registerDriver(Driver driver)  注册驱动
             a.参数Driver:  Driver是一个接口,需要传递实现类
               Driver接口的实现类:com.mysql.cj.jdbc.Driver

           2.写法:DriverManager.registerDriver(new Driver()) -> 其实不推荐
             new Driver之后里面的静态代码块会执行,静态代码块里面有注册驱动的代码
             所以,如果我们自己这么写,会注册两次

           3.推荐注册驱动的写法:用反射
             Class.forName("com.mysql.cj.jdbc.Driver");传递类的全限定名(包名.类名)
             这句话是获取指定类的Class对象的,一旦获取Class对象,这个类也会自动加载到内存
             这个类一旦加载到内存,静态代码块就会执行,静态代码块里面有注册驱动的代码,直接注册
         */
        Class.forName("com.mysql.cj.jdbc.Driver");
```

> 其实我们不需要注册驱动,因为现在jdbc可以自动注册,但是为了迎合后面课程的配置文件中的配置,我们加上注册驱动

## 5.JDBC获取连接

```java
1.DriverManager类中的方法:
  Connection getConnection(数据库url,数据库用户名,数据库密码)

2.参数解释:
  a.数据库url(请求路径):jdbc:mysql://localhost:3306/数据库名
    请求路径?请求参数1&请求参数2   -> 请求参数都是key=vaule形式
  b.用户名:mysql用户名
  c.密码:mysql密码
```

```java
String url = "jdbc:mysql://localhost:3306/bj20260108_3";
String username = "root";
String password = "root";
Connection connection = DriverManager.getConnection(url, username, password);
```

## 6.JDBC实现增删改操作

```java
@Test
    public void insert() throws Exception {
        /*
           1.注册驱动:DriverManager
             static void registerDriver(Driver driver)  注册驱动
             a.参数Driver:  Driver是一个接口,需要传递实现类
               Driver接口的实现类:com.mysql.cj.jdbc.Driver

           2.写法:DriverManager.registerDriver(new Driver()) -> 其实不推荐
             new Driver之后里面的静态代码块会执行,静态代码块里面有注册驱动的代码
             所以,如果我们自己这么写,会注册两次

           3.推荐注册驱动的写法:用反射
             Class.forName("com.mysql.cj.jdbc.Driver");传递类的全限定名(包名.类名)
             这句话是获取指定类的Class对象的,一旦获取Class对象,这个类也会自动加载到内存
             这个类一旦加载到内存,静态代码块就会执行,静态代码块里面有注册驱动的代码,直接注册
         */
        Class.forName("com.mysql.cj.jdbc.Driver");

        //2.获取连接
        String url = "jdbc:mysql://localhost:3306/bj20260108_3";
        String username = "root";
        String password = "root";
        Connection connection = DriverManager.getConnection(url, username, password);
        //System.out.println(connection);

        /*
          3.准备sql
         */
        String sql = "insert into user (username,password) values ('tom','111')";

        /*
          4.获取执行平台:Statement
            a.获取: Connection中的方法
              Statement createStatement()
         */
        Statement statement = connection.createStatement();

        /*
          5.执行sql:Statement中的方法
            int executeUpdate(sql) 针对于增删改操作的
            ResultSet executeQuery(sql) 针对于查询,返回的是结果集
         */
        statement.executeUpdate(sql);

        //关闭资源
        statement.close();
        connection.close();
    }
```

```java
 @Test
    public void delete() throws Exception {
        //1.注册驱动
        Class.forName("com.mysql.cj.jdbc.Driver");
        //2.获取连接
        String url = "jdbc:mysql://localhost:3306/bj20260108_3";
        String username = "root";
        String password = "root";
        Connection connection = DriverManager.getConnection(url, username, password);
        //3.准备sql
        String sql = "delete from user where uid = 5";
        //4.获取执行平台:Statement
        Statement statement = connection.createStatement();
        //5.执行sql:Statement中的方法
        statement.executeUpdate(sql);
        //6.关闭资源
        statement.close();
        connection.close();
    }
```

```java
 @Test
    public void update() throws Exception {
        //1.注册驱动
        Class.forName("com.mysql.cj.jdbc.Driver");
        //2.获取连接
        String url = "jdbc:mysql://localhost:3306/bj20260108_3";
        String username = "root";
        String password = "root";
        Connection connection = DriverManager.getConnection(url, username, password);
        //3.准备sql
        String sql = "update user set password = '4441' where uid = 4";
        //4.获取执行平台:Statement
        Statement statement = connection.createStatement();
        //5.执行sql:Statement中的方法
        statement.executeUpdate(sql);
        //6.关闭资源
        statement.close();
        connection.close();
    }
```

> 我们的sql语句可以先在sqlyog中写一遍测一测,然后再粘贴到咱们得java代码中

## 7.JDBC实现查询操作

```java
1.用到的方法:Statement中的方法
  ResultSet executeQuery(sql) 针对于查询,返回的是结果集

2.ResultSet接口:代表的是结果集,存放查询出来的数据
  a.next() 判断有没有下一个结果
  b.int getInt(int columnIndex) 获取int型数据的,指定的第几列->获取第几列的数据就写几
    int getInt(String columnLabel) 获取int型数据的,指定的是列名
    String getString(int columnIndex) 获取varchar类型数据的,指定的第几列
    String getString(String columnLabel) 获取varchar类型数据的,指定的是列名

    Object getObject(int columnIndex)  指定第几列
    Object getObject(String columnLabel)  指定列名
```

```java
    @Test
    public void select() throws Exception {
        //1.注册驱动
        Class.forName("com.mysql.cj.jdbc.Driver");
        //2.获取连接
        String url = "jdbc:mysql://localhost:3306/bj20260108_3";
        String username = "root";
        String password = "root";
        Connection connection = DriverManager.getConnection(url, username, password);
        //3.准备sql
        String sql = "select * from user";
        //4.获取执行平台:Statement
        Statement statement = connection.createStatement();
        //5.执行sql:Statement中的方法
        ResultSet rs = statement.executeQuery(sql);
        //6.处理结果:ResultSet
        while (rs.next()) {
            int uid = rs.getInt("uid");
            String name = rs.getString("username");
            String pwd = rs.getString("password");
            System.out.println(uid + " " + name + " " + pwd);
        }
        //7.关闭资源
        rs.close();
        statement.close();
        connection.close();
    }
```

## 8.JDBC工具类使用

```properties
driverclass=com.mysql.cj.jdbc.Driver
url=jdbc:mysql://localhost:3306/bj20260108_3
username=root
password=root
```

```java
public class JDBCUtils {
    //构造私有化
    private JDBCUtils(){}
    private static String url;
    private static String username;
    private static String password;

    /*
      由于注册驱动,准备数据库url,用户名,密码需要最先初始化
      而且只初始化一次,所以将其放到static代码块中
     */
    static{
        try {
            Properties properties = new Properties();
            InputStream in = JDBCUtils.class.getClassLoader().getResourceAsStream("jdbc.properties");
            properties.load(in);
            Class.forName(properties.getProperty("driverclass"));
            url = properties.getProperty("url");
            username = properties.getProperty("username");
            password = properties.getProperty("password");
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    //获取连接
    public static Connection getConnection(){
        Connection connection = null;
        try {
            connection = DriverManager.getConnection(url, username, password);
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return connection;
    }

    public static void close(Connection conn, Statement st, ResultSet rs){
        if(rs != null){
            try {
                rs.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        if(st != null){
            try {
                st.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        if(conn != null){
            try {
                conn.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}

```

```java
    @Test
    public void insert() throws Exception {
        //1.获取连接
        Connection conn = JDBCUtils.getConnection();
        //2.准备sql
        String sql = "insert into user (username,password) values ('taoge','555')";
        //3.获取执行平台:Statement
        Statement statement = conn.createStatement();
        //4.执行sql:Statement中的方法
        statement.executeUpdate(sql);
        //5.关闭资源
        JDBCUtils.close(conn, statement,null);
    }

    @Test
    public void delete() throws Exception {
        //1.获取连接
        Connection conn = JDBCUtils.getConnection();
        //2.准备sql
        String sql = "delete from user where uid = 6";
        //3.获取执行平台:Statement
        Statement statement = conn.createStatement();
        //4.执行sql:Statement中的方法
        statement.executeUpdate(sql);
        //5.关闭资源
        JDBCUtils.close(conn, statement,null);
    }

    @Test
    public void update() throws Exception {
        //1.获取连接
        Connection conn = JDBCUtils.getConnection();
        //2.准备sql
        String sql = "update user set password = '444' where uid = 4";
        //3.获取执行平台:Statement
        Statement statement = conn.createStatement();
        //4.执行sql:Statement中的方法
        statement.executeUpdate(sql);
        //5.关闭资源
        JDBCUtils.close(conn, statement,null);
    }

    @Test
    public void select() throws Exception {
        //1.获取连接
        Connection conn = JDBCUtils.getConnection();
        //2.准备sql
        String sql = "select * from user";
        //3.获取执行平台:Statement
        Statement statement = conn.createStatement();
        //4.执行sql:Statement中的方法
        ResultSet rs = statement.executeQuery(sql);
        //5.处理结果:ResultSet
        while (rs.next()) {
            int uid = rs.getInt("uid");
            String name = rs.getString("username");
            String pwd = rs.getString("password");
            System.out.println(uid + " " + name + " " + pwd);
        }
        //6.关闭资源
        JDBCUtils.close(conn, statement,rs);
    }

```

## 9.获取最新添加的数据的id

```mysql
1.用到的函数:
  SELECT LAST_INSERT_ID();
2.注意:
  数据的id需要主键自增,而且添加的时候我们不要自己维护id
```

```java
    @Test
    public void lastInsertId()throws Exception{
        //1.获取连接
        Connection conn = JDBCUtils.getConnection();
        //2.准备sql
        String addSql = "insert into user (username,password) values ('jerry','444')";
        String lastInsertIdSql = "select last_insert_id()";
        //3.获取执行平台
        Statement st = conn.createStatement();
        //4.执行sql
        st.executeUpdate(addSql);
        ResultSet rs = st.executeQuery(lastInsertIdSql);
        while(rs.next()){
            int id = rs.getInt(1);
            System.out.println(id);
        }
        JDBCUtils.close(conn,st,rs);
    }
```

> ```mysql
> INSERT INTO `user` (username,`password`) VALUES ('tom','111');
>
> INSERT INTO `user` (username,`password`) VALUES ('jack','222');
>
> INSERT INTO `user` (username,`password`) VALUES ('rose','333');
>
> SELECT LAST_INSERT_ID();
> ```

# 第四章.PreparedStatement预处理对象

## 1.sql注入的问题以及解决方式(预处理对象)

```java
public class Demo04JDBC {
    public static void main(String[] args)throws Exception {
        //1.创建Scanner对象
        Scanner sc = new Scanner(System.in);
        //2.输入用户名和密码
        System.out.println("请输入用户名:");
        String username = sc.nextLine();
        System.out.println("请输入密码:");
        String password = sc.nextLine();
        //3.获取连接
        Connection conn = JDBCUtils.getConnection();
        //4.准备sql
        String sql = "select * from user where username = '"+username+"' and password = '"+password+"'";
        //5.获取执行平台执行sql
        Statement st = conn.createStatement();
        ResultSet rs = st.executeQuery(sql);
        if (rs.next()){
            System.out.println("登录成功");
        }else{
            System.out.println("登录失败");
        }
        //6.关闭资源
        JDBCUtils.close(conn,st,rs);
    }
}
```

<img src="image/image-20260206153208422.png" alt="image-20260206153208422" style="zoom:80%;" />

> 密码输入:222' or '1' = '1  以上程序不行了->sql注入

## 1.使用预处理对象(PreparedStatement)实现操作

```java
1.概述:PreparedStatement是一个接口
      PreparedStatement extends Statement
2.获取:Connection中的方法
  PreparedStatement preparedStatement(sql)
3.特点:
  支持sql语句中使用?占位符  -> sql语句中只要是写[表中的数据],都可以用?占位
4.给?赋值 -> PreparedStatement方法
  setInt(指定给第几个?赋值,具体赋的什么值)
  setString(指定给第几个?赋值,具体赋的什么值)
  setObject(指定给第几个?赋值,具体赋的什么值)
5.执行sql:
  int executeUpdate() 针对于增删改操作的
  ResultSet executeQuery() 针对于查询,返回的是结果集
```

<img src="image/image-20260206154043865.png" alt="image-20260206154043865" style="zoom:80%;" />

## 2.使用预处理对象(PreparedStatement)实现增删改查操作

```java
    @Test
    public void insert() throws Exception {
        Connection conn = JDBCUtils.getConnection();
        String sql = "insert into user (username,password) values (?,?)";
        PreparedStatement ps = conn.prepareStatement(sql);
        ps.setObject(1, "zhangsan");
        ps.setObject(2, "555");
        ps.executeUpdate();
        JDBCUtils.close(conn, ps, null);
    }

    @Test
    public void update() throws Exception {
        Connection conn = JDBCUtils.getConnection();
        String sql = "update user set password = ? where uid = ?";
        PreparedStatement ps = conn.prepareStatement(sql);
        ps.setObject(1, "666");
        ps.setObject(2, 5);
        ps.executeUpdate();
        JDBCUtils.close(conn, ps, null);
    }

    @Test
    public void delete() throws Exception {
        Connection conn = JDBCUtils.getConnection();
        String sql = "delete from user where uid = ?";
        PreparedStatement ps = conn.prepareStatement(sql);
        ps.setObject(1, 5);
        ps.executeUpdate();
        JDBCUtils.close(conn, ps, null);
    }

    @Test
    public void select() throws Exception {
        Connection conn = JDBCUtils.getConnection();
        String sql = "select * from user";
        PreparedStatement ps = conn.prepareStatement(sql);
        //ps.setObject(1, 5);
        ResultSet rs = ps.executeQuery();
        while (rs.next()) {
            int uid = rs.getInt("uid");
            String name = rs.getString("username");
            String pwd = rs.getString("password");
            System.out.println(uid + " " + name + " " + pwd);
        }
        JDBCUtils.close(conn, ps, rs);
    }
```

> ?只能代表值,不能代表其他的内容

```java
public class Demo06JDBC {
    public static void main(String[] args)throws Exception {
        //1.创建Scanner对象
        Scanner sc = new Scanner(System.in);
        //2.输入用户名和密码
        System.out.println("请输入用户名:");
        String username = sc.nextLine();
        System.out.println("请输入密码:");
        String password = sc.nextLine();
        //3.获取连接
        Connection conn = JDBCUtils.getConnection();
        //4.准备sql
        String sql = "select * from user where username = ? and password = ?";
        //5.获取执行平台执行sql
        PreparedStatement ps = conn.prepareStatement(sql);
        ps.setObject(1, username);
        ps.setObject(2, password);
        ResultSet rs = ps.executeQuery();
        if (rs.next()){
            System.out.println("登录成功");
        }else{
            System.out.println("登录失败");
        }
        //6.关闭资源
        JDBCUtils.close(conn,ps,rs);
    }
}

```

```java
select * from user where username = 'tom' and password = '111' or '1' = '1'

如果用的是PreparedStatement即使传入了111' or '1' = '1,拼接到了sql语句中会自动将输入'转义
变成了:
select * from user where username = 'tom' and password = '111\' or \'1\' = \'1'
123\' or \'1\' = \'1 是一整个大的字符串,被包裹在了''中
```

> 完成注册功能:作业
>
> ​    输入用户名和密码
>
> ​     根据用户名查询,是否有该用户
>
> ​     如果有,注册失败
>
> ​     否则,将用户名和密码insert到数据库中,显示注册成功