# day04.连接池-事务

```java
课前回顾:
  1.函数:
    a.字符串函数: concat  substring Upper  Lower trim
    b.判断函数:
      if  ifnull case when
  2.jdbc:java连接数据库,操作数据库的一套标准(一堆接口)
  3.原生jdbc开发步骤
    a.注册驱动: Class.forName("Driver的全限定名")
    b.获取连接: DriverManager.getConnection(url,username,password)
    c.准备sql语句
    d.获取执行平台
      conn.preparedStatement(sql)
    e.为?赋值
      setObject(指定第几个问号,赋什么值)
    f.执行sql
      executeUpdate()针对于增删改操作
      executeQuery()针对于查询
    g.处理结果集:ResultSet
      next()判断结果集中有没有下一个结果
      getObject("列名")获取数据
    h.关闭资源:close()
今日重点:
  1.会批量添加
  2.会使用连接池的使用
  3.会获取一个类的class对象
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
driverclass=com.mysql.cj.jdbc.Driver
url=jdbc:mysql://localhost:3306/250312_database03?rewriteBatchedStatements=true
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
    public void testBatch() throws Exception {
        //1.获取连接
        Connection conn = JDBCUtils.getConnection();
        //2.准备sql语句
        String sql = "insert into category (cname) values (?)";
        //3.获取执行平台
        PreparedStatement pst = conn.prepareStatement(sql);
        for (int i = 0; i < 1000; i++) {
            pst.setObject(1, "蔬菜" + i);
            //4.将数据打包放到内存中
            pst.addBatch();
        }

        //5.执行批量操作
        pst.executeBatch();
        //6.关闭资源
        JDBCUtils.close(conn, pst, null);
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
```

```java
1.问题描述:我们每做一个操作,我们都要获取一条Connection对象,用完之后close销毁,如果频繁创建并销毁就比较耗费内存资源
2.解决方案:
  先找一个容器,预先在里面创建好指定条数的Connection对象,然后使用的时候从容器中获取Connection对象,用完将Connection还回去 -> 池的概念 (连接池,线程池)

3.连接池好几款:
  Druid
  C3P0
  DBCP

4.连接池都有一个共同的接口:
  DataSource
```

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
    //构造私有化
    private DruidUtils(){}
    private static DataSource dataSource;


    /*
      由于注册驱动,准备数据库url,用户名,密码需要最先初始化
      而且只初始化一次,所以将其放到static代码块中
     */
    static{
        try {
            Properties properties = new Properties();
            InputStream in = DruidUtils.class.getClassLoader().getResourceAsStream("druid.properties");
            properties.load(in);
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
                //释放连接,放回连接池
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
        Connection conn = DruidUtils.getConnection();
        String sql = "insert into category (cname) values (?)";
        PreparedStatement pst = conn.prepareStatement(sql);
        pst.setObject(1, "蔬菜");
        pst.executeUpdate();
        DruidUtils.close(conn, pst, null);
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
1.反射概述:用于解剖class对象的技术
2.能从class对象中解剖出啥来:
   a.解剖出属性 -> 赋值取值
   b.解剖出构造 -> new对象
   c.解剖出方法 -> 调用执行
3.反射怎么学:
  a.知道反射是解剖谁的,能解剖出啥来,然后解剖出来之后怎么用
  b.将反射知识看成是一套纯api来学
  c.根据涛哥设计的案例,体会反射代码的灵活性,通用性

4.学反射之前第一步要干啥呀?
    获取class对象

```

<img src="image/image-20260207103921365.png" alt="image-20260207103921365" style="zoom:80%;" />

## 2.反射之获取Class对象

```java
1.方式1:调用Object中的getClass()
2.方式2:jvm为基本类型以及引用类型都提供一个共同的静态属性
       class -> 比如int.class    Person.class   String.class 等
3.方式3:利用Class类中的静态方法 -> forName()
       Class.forName("类的全限定名")   -> 所谓的类的全限定名就是包名.类名
```

```java
public class Person {
    private String name;
    private int age;

    public Person() {
    }
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    //单独加的私有构造
    private Person(String name){
        this.name = name;
    }

    public void setName(String name) {
        this.name = name;
    }
    public String getName() {
        return name;
    }
    public void setAge(int age) {
        this.age = age;
    }
    public int getAge() {
        return age;
    }

    @Override
    public String toString() {
        return name+","+age;
    }

    //单独加一个私有方法
    private void show(){
        System.out.println("show...");
    }
}

```

```java
    @Test
    public void test01() throws Exception {
        Person person = new Person();
        Class<? extends Person> aclass1 = person.getClass();
        System.out.println(aclass1);

        System.out.println("=============================");

        Class<Person> aclass2 = Person.class;
        System.out.println(aclass2);

        System.out.println("=============================");
        Class<?> aclass3 = Class.forName("com.atguigu.b_reflect.Person");
        System.out.println(aclass3);

        System.out.println("=============================");

        //class对象在内存中只有一个
        System.out.println(aclass1 == aclass2);
    }
```

> 包名.类名 -> 类的全限定名

### 2.1.三种获取Class对象的方式最通用的一种

```java
Class.forName("类的全限定名")   -> 所谓的类的全限定名就是包名.类名
```

```properties
classname=com.atguigu.b_reflect.Student
```

```java
    @Test
    public void test02() throws Exception {
        Properties properties = new Properties();
        InputStream in = Demo01Reflect.class.getClassLoader().getResourceAsStream("getclass.properties");
        properties.load(in);
        String className = properties.getProperty("classname");
        Class<?> aClass = Class.forName(className);
        System.out.println(aClass);
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
  Constructor<?>[] getDeclaredConstructors() 获取所有的构造包括public以及private
  Constructor<T> getDeclaredConstructor(Class<?>... parameterTypes) 获取指定构造,包括public以及private
                                        parameterTypes:参数类型的class对象

Constructor类中的方法:
  T newInstance(Object... initargs)  : 根据构造创建对象
               initargs:为构造方法的参数传递的实参

AccessibleObject类:Constructor, Field, Method 都是它的子类
  void setAccessible(boolean flag)  -> flag如果为true,就是解除私有权限 -> 暴力反射
```

```java
    @Test
    public void test01() throws Exception {
        Class<Person> pClass = Person.class;
        Constructor<?>[] dc = pClass.getDeclaredConstructors();
        for (Constructor<?> constructor : dc) {
            System.out.println(constructor);
        }
    }

    @Test
    public void test02() throws Exception {
        Class<Person> pClass = Person.class;
        Constructor<Person> dc = pClass.getDeclaredConstructor();
        //创建对象
        //相当于Person person = new Person()
        Person person = dc.newInstance();
        //相当于直接输出对象名,默认调用toString
        System.out.println(person);
    }

    @Test
    public void test03() throws Exception {
        Class<Person> pClass = Person.class;
        Constructor<Person> dc = pClass.getDeclaredConstructor(String.class,int.class);
        //相当于Person person = new Person("张三",18)
        Person person = dc.newInstance("张三", 18);
        //相当于直接输出对象名,默认调用toString
        System.out.println(person);
    }

    @Test
    public void test04() throws Exception {
        Class<Person> pClass = Person.class;
        Constructor<Person> dc = pClass.getDeclaredConstructor(String.class);

        //解除私有权限
        dc.setAccessible(true);

        //相当于Person person = new Person("张三",18)
        Person person = dc.newInstance("张三");
        //相当于直接输出对象名,默认调用toString
        System.out.println(person);
    }
```

## 4.反射方法_Method

### 4.1.反射之操作方法

```java
1.Class类中的方法:
  Method[] getDeclaredMethods() 获取全部方法包括public以及private
  Method getDeclaredMethod(String name, Class<?>... parameterTypes)  获取指定方法
                           name:代表的是方法名
                           parameterTypes:方法参数类型的class对象

2.Method类中的方法:
  Object invoke(Object obj, Object... args) 执行方法
                obj:对象
                args:为方法赋的实参
                返回值Object:接收的是被调用方法的返回值,如果方法没有返回值,会返回null,此时我们不需要返回值接收
```

```java
    @Test
    public void test01() throws Exception {
        Class<Person> personClass = Person.class;
        Method[] dm = personClass.getDeclaredMethods();
        for (Method method : dm) {
            System.out.println(method);
        }
    }

    @Test
    public void test02() throws Exception {
        Class<Person> personClass = Person.class;
        Method setName = personClass.getDeclaredMethod("setName", String.class);
        //Constructor<Person> dc = personClass.getDeclaredConstructor();
        //Person person = dc.newInstance();

        /*
           创建对象的快捷方式:Class类中的方法
             newInstance()
           想使用快捷方式创建对象的前提:类中必须有空参构造
         */
        Person person = personClass.newInstance();
        setName.invoke(person,"张三");

        //反射getName方法
        Method getName = personClass.getDeclaredMethod("getName");
        Object o = getName.invoke(person);
        System.out.println(o);
    }

    @Test
    public void test03() throws Exception {
        Class<Person> personClass = Person.class;
        Method show = personClass.getDeclaredMethod("show");
        show.setAccessible(true);//解除私有权限
        Person person = personClass.newInstance();
        show.invoke(person);
    }
```

## 5.反射成员变量_Field

### 5.1.获取属性

```java
Class类中的方法:
  Field[] getDeclaredFields()获取所有的属性包括public的以及private的
  Field getDeclaredField(String name)获取指定属性,包括public以及private的
                         name:属性名

Field类中的方法:
  Object get(Object obj) 获取属性值
  void set(Object obj, Object value) 为属性赋值
           obj:对象
           value:值
```

```java
    @Test
    public void test01() throws Exception {
        Class<Person> personClass = Person.class;
        Field[] df = personClass.getDeclaredFields();
        for (Field field : df) {
            System.out.println(field);
        }
    }

    @Test
    public void test02() throws Exception {
        Class<Person> personClass = Person.class;
        Field name = personClass.getDeclaredField("name");
        name.setAccessible(true);
        Person person = personClass.newInstance();
        name.set(person, "张三");
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
classname=com.atguigu.b_reflect.Student
methodname=eat
```

```java
    @Test
    public void test01() throws Exception {
        //1.解析配置文件
        Properties properties = new Properties();
        InputStream in = Demo05Reflect.class.getClassLoader().getResourceAsStream("reflect.properties");
        properties.load(in);
        //2.获取类的全限定名和方法名
        String className = properties.getProperty("classname");
        String methodName = properties.getProperty("methodname");
        //3.根据获取出来的className创建class对象
        Class<?> aClass = Class.forName(className);
        //4.根据class对象获取method对象
        Method method = aClass.getMethod(methodName);
        //5.通过method对象创建对象
        Object obj = aClass.newInstance();
        method.invoke(obj);
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

# 第四章.注解

## 1.注解的介绍

```java
1.引用数据类型:
  类 数组 接口 枚举 注解 Record

2.jdk1.5版本出现的->一个引用数据类型
       和类,接口,枚举是同一个层次的

       引用数据类型:类 数组  接口 枚举 注解  Record
3.作用:
        说明:对代码进行说明,生成API文档

        检查:检查代码是否符合条件   @Override(会用) @FunctionalInterface

        分析:对代码进行分析,起到了代替配置文件的作用(会用)

4.JDK中的注解:
        @Override  ->  检测此方法是否为重写方法
           jdk1.5版本,支持父类的方法重写
           jdk1.6版本,支持接口的方法重写
        @Deprecated -> 方法已经过时,不推荐使用
                       调用方法的时候,方法上会有横线,但是能用
        @SuppressWarnings->消除警告  @SuppressWarnings("all")
```

<img src="image/image-20260207152841581.png" alt="image-20260207152841581" style="zoom:80%;" />

```java
public class Person {
    @Deprecated
    public void eat(){
        System.out.println("吃饭");
    }
}
```

```java
@SuppressWarnings("all")
public class Demo01Annotation {
    @Test
    public void test01() throws Exception {
        ArrayList list = new ArrayList();
    }
}
```

## 2.注解的定义以及属性的定义格式

```java
1.定义格式:
  public @interface 注解名{}

2.定义注解中的属性:为了增强注解的作用
  数据类型 属性名() -> 没有默认值,在使用注解的时候必须为其赋值
  数据类型 属性名() default 值 -> 有默认值,在使用注解的时候可赋值可不赋值

3.注解中能定义什么类型的属性呢?
  a.8种基本类型
  b.String类型,class类型,枚举类型,注解类型
  c.以及以上类型的一维数组
```

```java
public @interface Book {
    String bookName();
    String[] author();
    int price();
    int count() default 10;
}

```

> 我们要知道注解中的属性其实都是一个一个的抽象方法,但是在使用的时候跟属性使用方式一样,所以我们就按照属性去记

## 3.注解的使用(重点)

```java
1.概述:说白了使用注解其实就是给注解中的属性赋值
2.使用位置: 类上 属性上 构造上 方法上 参数上都可以使用
3.使用方式:
  @注解名(属性名 = 属性值,属性名 = 属性值,属性名 = {元素1,元素2})
```

```java
public @interface Book {
    String bookName();
    String[] author();
    int price();
    int count() default 10;
}

```

```java
@Book(bookName = "金瓶梅",author = {"涛哥","金莲"},price = 19)
public class BookShelf {
}
```

```java
注解注意事项:
      1.空注解可以直接使用->空注解就是注解中没有任何的属性
      2.不同的位置可以使用一样的注解,但是同样的位置不能使用一样的注解
      3.使用注解时,如果此注解中有属性,注解中的属性一定要赋值,如果有多个属性,用,隔开
        如果注解中的属性有数组,使用{}
      4.如果注解中的属性值有默认值,不用重新赋值,反之必须赋值
      5.如果注解中只有一个属性,并且属性名叫value,那么使用注解的时候,属性名不用写,直接写值
        (包括单个类型,还包括数组)
```

```java
public @interface Book1 {
    String value();
}
```

```java
@Book1("金瓶梅")
public class BookShelf {
    @Book1("金瓶梅")
    public void show() {

    }
}
```

## 4.注解的解析

```java
1.注解解析用到的接口:
  AnnotatedElement接口
       实现类:AccessibleObject, Class, Constructor, Field, Method

2.方法:
  boolean isAnnotationPresent(Class<? extends Annotation> annotationClass) 判断指定的位置上是否有指定的注解
                              annotationClass:传递的是注解的class对象
          比如:Class aclass = BookShelf.class
              aclass.isAnnotationPresent(Book.class) -> 判断BookShelf类上是否有Book注解

  T getAnnotation(Class<T> annotationClass)-> 获取指定的注解,传递的注解的class对象
```

```java
@Book(bookName = "金瓶梅", author = {"涛哥", "金莲"}, price = 19)
public class BookShelf {
}

```

```java
public class Demo01Annotation {
    @Test
    public void test01() throws Exception {
        Class<BookShelf> bookShelfClass = BookShelf.class;
        boolean b = bookShelfClass.isAnnotationPresent(Book.class);
        System.out.println(b);
        if (b){
            Book book = bookShelfClass.getAnnotation(Book.class);
            System.out.println(book.bookName());
            System.out.println(Arrays.toString(book.author()));
            System.out.println(book.price());
        }
    }
}
```

> 以上代码没有解析出来
>
> 涛哥猜想:
>
> ​    代码都先进内存,然后运行,那么Book注解是不是没有在内存中出现呢?如果Book注解在内存中出现了,而且咱们还用上了,我们不可能判断不出来

## 5.元注解

```java
1.概述:管理注解的注解
2.从哪些方面管理呢:
  a.管理注解的使用位置
  b.管理注解的生命周期
3.常用的元注解:
  @Target:管理注解的使用位置: ElementType[] value()
      a.ElementType:是一个枚举
        TYPE:控制注解能在类上使用
        FIELD:控制注解能在属性上使用
        METHOD:控制注解能在方法上使用
        PARAMETER:控制注解能在参数上使用
        CONSTRUCTOR:控制注解能在构造上使用


  @Retention:管理注解的生命周期:RetentionPolicy value()
      a.RetentionPolicy:是一个枚举
        SOURCE:控制注解能在源码中出现
        CLASS:控制注解能在class文件中出现
        RUNTIME:控制注解能在内存中出现
```

```java
@Target({ElementType.METHOD,ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface Book {
    String bookName();
    String[] author();
    int price();
    int count() default 10;
}
```

```java
@Book(bookName = "金瓶梅", author = {"涛哥", "金莲"}, price = 19)
public class BookShelf {
/*    @Book(bookName = "金瓶梅", author = {"涛哥", "金莲"}, price = 19)
    public void show(){}*/
}

```

```java
@Test
public void test01() throws Exception {
    Class<BookShelf> bookShelfClass = BookShelf.class;
    boolean b = bookShelfClass.isAnnotationPresent(Book.class);
    System.out.println(b);
    if (b){
        Book book = bookShelfClass.getAnnotation(Book.class);
        System.out.println(book.bookName());
        System.out.println(Arrays.toString(book.author()));
        System.out.println(book.price());
    }
}
```
