# day04.连接池-DBUtils-事务

```java
课前回顾:
  1.mysql函数:
    if  ifnull case when
  2.DCL:分配用户和权限
  3.注册驱动:
    Class.forName("Driver的全限定名")
  4.获取连接:
    getConnection(数据库url,数据库用户名,数据库密码)
  5.写sql
  6.获取执行平台:
    createStatement()
  7.执行sql:
    executeUpdate(sql) -> 针对于增删改操作
    executeQuery(sql) -> 针对于查询
  8.处理结果集:
    a.增删改不需要处理结果集
    b.查询处理结果集:ResultSet接口
      next
      getxxx
  9.关闭资源:close方法
  10.PreparedStatement:预处理对象
     a.获取:preparedStatement(sql)
     b.给?赋值
       setxxx(指定第几个?,具体的值)
     c.执行sql:
       executeUpdate() -> 针对于增删改操作
       executeQuery() -> 针对于查询

今日重点:
  除了C3P0连接池以及事务特性都是重点
```

# 第一章.PreparedStatement预处理对象

## 1.PreparedStatement实现批量添加

```mysql
CREATE TABLE category(
  cid INT PRIMARY KEY AUTO_INCREMENT,
  cname VARCHAR(10)
);
```

```java
1.注意:
  我们mysql默认情况下是一条一条执行的,如果我们要做批量添加,就会比较慢,所以我们希望一次性将我们想要的数据添加到mysql中,但是mysql默认不会批量添加的,所以想要实现批量添加,我们需要手动开启批量添加操作
2.怎么开启:
  在数据库的url后面加上?rewriteBatchedStatements=true

  a.完整的请求:  请求路径?请求参数
  b.请求参数:都是key = value形式  ,多个键值对之间用&连接
    比如: localhost:8080/web应用名称/某个资源?username=tom&password=123

3.方法:用到PreparedStatement中的方法:
  void addBatch() -> 将一组数据保存起来,给数据打包,放到内存中
  executeBatch() -> 将打包好的数据一起发送给mysql
```

```properties
driverClass=com.mysql.cj.jdbc.Driver
url=jdbc:mysql://localhost:3306/250312_database03?rewriteBatchedStatements=true
username=root
password=root
```

```java
public class JDBCUtils {
    private static String url = null;
    private static String user = null;
    private static String password = null;
    private JDBCUtils() {
    }

    static {
        try {
            Properties properties = new Properties();
            properties.load(JDBCUtils.class.getClassLoader().getResourceAsStream("jdbc.properties"));
            Class.forName(properties.getProperty("driverclass"));
            url = properties.getProperty("url");
            user = properties.getProperty("username");
            password = properties.getProperty("password");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    //获取连接
    public static Connection getConnection(){
        Connection connection = null;
        try {
            connection = DriverManager.getConnection(url, user, password);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
        return connection;
    }

    //关闭资源
    public static void close(Connection connection, Statement statement, ResultSet resultSet){
        if(resultSet != null){
            try {
                resultSet.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        if(statement != null){
            try {
                statement.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        if(connection != null){
            try {
                connection.close();
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
        //获取连接
        Connection connection = JDBCUtils.getConnection();
        //准备sql
        String sql = "insert into category (cname) values (?)";
        //获取执行平台
        PreparedStatement pst = connection.prepareStatement(sql);
        for (int i = 0; i < 1000; i++) {
            pst.setObject(1, "蔬菜" + i);
            //将要添加的数据打包,放到内存中
            pst.addBatch();
        }
        //执行sql,将打包好的数据发送给mysql
        pst.executeBatch();
        JDBCUtils.close(connection, pst, null);
    }
```

# 第二章.连接池

```xml
<!--
   mysql核心依赖
 -->
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>8.0.26</version>
</dependency>

<!--
    Druid依赖
-->
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>druid</artifactId>
    <version>1.1.10</version>
</dependency>

<!--
    DBUtils依赖
-->
<dependency>
    <groupId>commons-dbutils</groupId>
    <artifactId>commons-dbutils</artifactId>
    <version>1.6</version>
</dependency>
```

```java
1.为啥要使用连接池:我们做一个操作,就需要获取一条连接对象,用完销毁,如果频繁地获取和销毁,会耗费内存资源的
2.解决:我们搞一个容器(连接池),在这个容器中创建多条Connection对象,来了任务之后从连接池中获取Connection对象去使用,用完还回去,达到一个循环利用的效果
```

> 课程配图（未随笔记提交）

## 1.连接池之Druid(德鲁伊)

```xml
<!--
    Druid依赖
-->
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>druid</artifactId>
    <version>1.1.10</version>
</dependency>
```

```java
1.概述:是一款连接池,是alibaba开发的
2.配置文件:xxx.properties -> druid.properties
  driver=com.mysql.cj.jdbc.Driver
  url=jdbc:mysql://localhost:3306/250717_database4?rewriteBatchedStatements=true
  username=root
  password=root
  initialSize=5
  maxActive=10
  maxWait=1000
3.获取实现类:
  DruidDataSourceFactory.createDataSource(properties集合) -> 也会自动解析配置文件
```

```java
public class DruidUtils {
    private static DataSource dataSource = null;
    private static String url = null;
    private static String user = null;
    private static String password = null;
    private DruidUtils() {
    }

    static {
        try {
            Properties properties = new Properties();
            properties.load(DruidUtils.class.getClassLoader().getResourceAsStream("druid.properties"));
            dataSource = DruidDataSourceFactory.createDataSource(properties);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    //获取连接
    public static Connection getConnection(){
        Connection connection = null;
        try {
            connection = dataSource.getConnection();
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
        return connection;
    }

    //关闭资源
    public static void close(Connection connection, Statement statement, ResultSet resultSet){
        if(resultSet != null){
            try {
                resultSet.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        if(statement != null){
            try {
                statement.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        if(connection != null){
            try {
                //归还连接
                connection.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}
```

```java
public class Demo02Druid {
    @Test
    public void insert()throws Exception{
        Connection connection = DruidUtils.getConnection();
        String sql = "insert into category (cname) values (?)";
        PreparedStatement pst = connection.prepareStatement(sql);
        pst.setObject(1, "水果");
        pst.executeUpdate();
        DruidUtils.close(connection,pst,null);

    }
}
```

# 第三章.反射

## 1.class类的以及class对象的介绍以及反射介绍

```java
万物皆对象:
 1.class文件有对象-> class对象 -> 描述class对象的类叫做class类

 2.构造有对象 -> Constructor对象 -> 描述Constructor对象的类叫做Constructor类

 3.属性有对象 -> Field对象 -> 描述Field对象的类叫做Field类

 4.方法有对象 -> Method对象 -> 描述Method对象的类叫做Method类
```

```java
1.什么是反射:用于解剖class对象的技术
2.能解剖class对象的啥?
   a.解剖出属性->赋值取值
   b.解剖出构造 -> new对象或者new对象的同时为属性赋值
   c.解剖出方法 -> 调用执行
3.问题:以上操作其实不用反射也能行,为啥用反射呢?
   因为反射做这些操作更灵活,更通用
4.用最后的涛哥案例体会反射的代码灵活度,剩下的就按照API思路学习
5.玩儿反射第一步要干啥:
   获取class对象
```

> 课程配图（未随笔记提交）

## 2.反射之获取Class对象

```java
方式1:调用Object中的getClass方法
方式2:jvm为基本类型和引用类型提供了一个静态的属性class
方式3:Class类中的静态方法
     Class.forName("包名.类名")
```

```java
public class Person {
    private String name;
    private Integer age;

    public Person() {
    }

    public Person(String name, Integer age) {
        this.name = name;
        this.age = age;
    }

    /**
     * 添加一个私有构造
     * @return
     */
    private Person(String name){
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    /**
     * 添加一个私有方法
     */
    private void eat(){
        System.out.println("吃吃吃");
    }

    @Override
    public String toString() {
        return "Person{" +
                "name='" + name + '\'' +
                ", age=" + age +
                '}';
    }
}
```

```java
    @Test
    public void test01() throws Exception {
        //方式1:
        Person person = new Person();
        Class<? extends Person> aClass1 = person.getClass();
        System.out.println(aClass1);

        //方式2:
        Class<Person> aClass2 = Person.class;
        System.out.println(aClass2);

        //方式3:
        Class<?> aClass3 = Class.forName("com.atguigu.d_reflect.Person");
        System.out.println(aClass3);

        System.out.println(aClass1 == aClass2);
    }
```

> 包名.类名 -> 类的全限定名

### 2.1.三种获取Class对象的方式最通用的一种

```java
Class.forName("包名.类名") -> forName方法参数是字符串,可以配合配置文件使用
```

```properties
className=com.atguigu.d_reflect.Student
```

```java
    @Test
    public void test02() throws Exception {
        //创建Properties集合
        Properties properties = new Properties();
        //读取配置文件
        properties.load(Demo01Reflect.class.getClassLoader().getResourceAsStream("reflect.properties"));
        String className = properties.getProperty("className");
        Class<?> aClass = Class.forName(className);
        System.out.println("aClass = " + aClass);
    }
```

### 2.2.开发中最常用的是哪一种

```java
类名.class
```

## 3.获取Class对象中的构造方法_Constructor

### 3.1.利用反射获取构造

```java
Class类中的方法:
   Constructor<?>[] getDeclaredConstructors() 获取所有的public以及private的构造方法
   Constructor<T> getDeclaredConstructor(Class<?>... parameterTypes)获取指定的构造方法
                                         parameterTypes:传递的是参数类型的class对象

Constructor类中的方法:
   T newInstance(Object... initargs) -> 根据构造方法创建对象,同时为属性赋值
                 initargs:传递的就是具体的值

解除私有权限:Constructor Field Method有一个共同的父类AccessibleObject,AccessibleObject里面有一个方法:
  void setAccessible(boolean flag)->如果flag为true,证明解除了私有权限
```

```java
    /**
     * 获取所有构造
     * @throws Exception
     */
    @Test
    public void test03() throws Exception {
        Class<Person> personClass = Person.class;
        Constructor<?>[] dc = personClass.getDeclaredConstructors();
        for (Constructor<?> constructor : dc) {
            System.out.println(constructor);
        }
    }

    /**
     * 获取空参的构造
     * @throws Exception
     */
    @Test
    public void test04() throws Exception {
        Class<Person> personClass = Person.class;
        Constructor<?> dc = personClass.getDeclaredConstructor();
        //好比是:Person p = new Person()
        Object o = dc.newInstance();
        //好比是:直接输出p.默认调用toString方法
        System.out.println(o);
    }

    /**
     * 获取有参构造
     * @throws Exception
     */
    @Test
    public void test05() throws Exception {
        Class<Person> personClass = Person.class;
        Constructor<?> dc = personClass.getDeclaredConstructor(String.class, Integer.class);
        //System.out.println(dc);
        //好比是:Person p = new Person("张三",18)
        Object o = dc.newInstance("张三", 18);
        //好比是:直接输出p.默认调用toString方法
        System.out.println(o);
    }

    /**
     * 获取私有构造
     *
     * 如果想要玩儿私有的,需要解除私有权限 -> 暴力反射
     * @throws Exception
     */
    @Test
    public void test06() throws Exception {
        Class<Person> personClass = Person.class;
        Constructor<?> dc = personClass.getDeclaredConstructor(String.class);
        //解除私有权限
        dc.setAccessible(true);
        Object o = dc.newInstance("张三");
        System.out.println(o);
    }

```

## 4.反射方法_Method

### 4.1.反射之操作方法

```java
Class对象中的方法:
  Method[] getDeclaredMethods()  : 获取public的以及private的成员方法
  Method getDeclaredMethod(String name, Class<?>... parameterTypes)获取指定的public的或者private的成员方法
         a.参数1:name -> 方法名
         b.参数2:parameterTypes->方法参数类型的class对象

Method类中的方法:
  Object invoke(Object obj, Object... args)  执行方法
                a.参数1->obj:对象
                b.参数2->args:给方法传递的实参
                c.返回值:用于接收被反射的方法的返回值
                        如果被反射的方法没有返回值,调用invoke之后不用返回值接收
                        否则,就需要返回值接收
解除私有权限:Constructor Field Method有一个共同的父类AccessibleObject,AccessibleObject里面有一个方法:
  void setAccessible(boolean flag)->如果flag为true,证明解除了私有权限

```

```java
    /**
     * 获取所有public以及private的方法
     * @throws Exception
     */
    @Test
    public void test07() throws Exception {
        Class<Person> personClass = Person.class;
        Method[] dm = personClass.getDeclaredMethods();
        for (Method method : dm) {
            System.out.println(method);
        }
    }

    /**
     * 获取指定的private以及public的方法
     */
    @Test
    public void test08() throws Exception {
        Class<Person> personClass = Person.class;

        /*
           根据空参构造创建对象的快捷方式
             Class类中的newInstance()
           前提:被反射的类中必须有空参构造
         */
        //好比是Person person = new Person();
        Person person = personClass.newInstance();

        Method setName = personClass.getDeclaredMethod("setName", String.class);
        //System.out.println(setName);

        //好比是:person.setName("张三")
        setName.invoke(person,"张三");

        //好比是直接输出对象名,默认调用toString方法
        System.out.println(person);

        System.out.println("=======================================");
        Method getName = personClass.getDeclaredMethod("getName");
        Object o = getName.invoke(person);
        System.out.println(o);

    }

    /**
     * 反射私有方法
     * @throws Exception
     */
    @Test
    public void test09() throws Exception {
        Class<Person> personClass = Person.class;
        Person person = personClass.newInstance();
        Method eat = personClass.getDeclaredMethod("eat");
        //解除私有权限
        eat.setAccessible(true);
        eat.invoke(person);
    }

```

## 5.反射成员变量_Field

### 5.1.获取属性

```java
Class类中的方法:
  Field[] getDeclaredFields()  获取所有public以及private的成员变量
  Field getDeclaredField(String name)  获取指定的public以及private的成员变量
                         name:写的是获取的成员变量名

Field类中的方法:
   void set(Object obj, Object value) :为属性赋值
           obj:对象
           value:属性值
   Object get(Object obj)  :获取属性值
           obj:对象
           返回值:获取的属性值

```

```java
    /**
     * 获取所有public以及private的成员变量
     */
    @Test
    public void test10() throws Exception {
        Class<Person> personClass = Person.class;
        //获取所有成员变量
        Field[] df = personClass.getDeclaredFields();
        for (Field field : df) {
            System.out.println(field);
        }
    }


    /**
     * 获取指定的private以及public的成员变量
     */
    @Test
    public void test11() throws Exception {
        Class<Person> personClass = Person.class;

        Person person = personClass.newInstance();

        Field name = personClass.getDeclaredField("name");

        //解除私有权限
        name.setAccessible(true);

        name.set(person,"tom");
        System.out.println(name.get(person));
    }
```

## 6.反射练习(编写一个小框架)

```java
public interface 接口{
    public Employee getEmployeeById(int id);
}


xml配置文件:

<select id = "getEmployeeById" resultType = "Employee的全限定名">
     select 列名 from 表名 where 条件
</select>

框架可以根据指定的类获取对应的class对象,然后根据配置好的方法名获取此方法,执行此方法
========================================================================
1.要求:创建一个properties配置文件
      配置className = 类的全限定名
      配置methodName = 方法名

      解析配置文件,根据className拿到methodName,让其执行起来
```

```properties
className=com.atguigu.c_reflect.Person
methodName=eat
```

```java
public class Test01 {
    public static void main(String[] args)throws Exception {
        //1.读取配置文件
        Properties properties = new Properties();
        InputStream in = Test01.class.getClassLoader().getResourceAsStream("pro.properties");
        properties.load(in);
        //获取的是类的全限定名
        String className = properties.getProperty("className");
        //获取的是方法名
        String methodName = properties.getProperty("methodName");
        //2.根据获取出来的className创建Class对象
        Class<?> aClass = Class.forName(className);
        Object o = aClass.newInstance();
        //3.根据获取出来的methodName获取方法对象
        Method method = aClass.getMethod(methodName);
        method.invoke(o);
    }
}
```

> 反射咋学:
>
> 1.知道反射是解剖class对象的
>
> 2.知道反射解剖出class对象中的构造,属性,方法都要干啥
>
> 3.了解调用哪些方法是操作属性的,调用哪些方法是操作构造的,调用哪些方法是操作方法的->当一套api学
>
> 4.根据最后的练习,体会反射的代码的通用性,灵活性
