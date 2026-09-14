# day08_面向对象

```java
课前回顾:
  1.匿名对象:没有等号左边的名字,只有new
    a.注意:如果涉及到赋值,别用
  2.封装:
    a.概述:将细节隐藏起来(不让外界直接使用,随便使用),对外提供一个公共的接口(让外界通过这个接口间接使用封装起来的细节)
    b.体现:
      将一段代码放到一个方法中
      比较有代表性的关键字:private
  3.快速掌握封装:
    a.知道private作用嘛?隐藏细节,外界不能直接使用
    b.知道set/get方法吗?setxxx是赋值,getxxx是取值
    c.知道this关键字的作用嘛?区分重名的成员变量和局部变量 -> this.后面的一定是成员的
    d.知道无参构造作用嘛?new对象,初始化成员 -> 每个类中默认都有一个空参构造,不写jvm自带一个
    e.知道有参构造作用嘛?new对象的同时为属性赋值 -> 如果写了有参构造,jvm将不再提供无参构造了,所以建议都手写出来
    f.知道如何生成一个标准javabean嘛?包含了私有的属性,有构造方法,有get/set方法 -> alt+insert
今日重点:
  1.all
```

# 第一章.JavaBean的作用

```java
1.javabean的作用:封装数据(说白了就是将数据给javabean中的属性赋值)
2.在实际开发过程中:
  javabean类都是和数据库的表对应

3.javabean和表的对应关系:
  表名 -> 类名
  列名 -> 属性名
  列的类型 -> 属性的数据类型
  每一行数据 -> javabean的对象
    a.第一行数据 -> User user1 = new User(1,"tom","111")
    b.第二行数据 -> User user2 = new User(2,"jack","222")
```

<img src="image/image-20260119090907542.png" alt="image-20260119090907542" style="zoom:80%;" />

### 1.1.javabean在开发中的实际运用_添加功能

<img src="image/image-20251025094007621.png" alt="image-20251025094007621" style="zoom:80%;" />

> 封装页面上发送过来的数据,一层一层传递到dao层,在dao层中调用javabean对象中的getxxx方法,将属性值获取出来,放到sql语句中

### 1.2.javabean在实际开发中运用_查询功能

<img src="image/image-20251025095448752.png" alt="image-20251025095448752" style="zoom:80%;" />

> 封装从数据库中查询出来的数据,然后一层一层返回给页面上进行展示

# 第二章.对象数组

```java
需求:定义一个数组,存3个Person对象,遍历数组,将Person对象中的属性值获取出来
```

<img src="image/image-20260119093707477.png" alt="image-20260119093707477" style="zoom:80%;" />

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

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        /*
           Person p = new Person()
           1.如果定义存储int型整数的数组: int[]
           2.如果定义存储double型的整数:double[]
           3.如果定义存储String型数据:String[]
           4.如果定义存储Person类型数据的数组:Person[]
         */

        //1.定义存储Person对象的数组
        Person[] arr1 = new Person[3];
        //2.创建三个Person对象
        Person p1 = new Person("小王", 10);
        Person p2 = new Person("小张", 20);
        Person p3 = new Person("小李", 30);
        //3.将三个对象放到数组中
        arr1[0] = p1;
        arr1[1] = p2;
        arr1[2] = p3;

        //4.遍历数组
        /*
           i = 0;arr[0]就是p1 -> Person p = p1
           i = 1;arr[1]就是p2 -> Person p = p2
           i = 2;arr[2]就是p3 -> Person p = p3
         */
        for (int i = 0; i < arr1.length; i++) {
            //System.out.println(arr1[i].getName() + "..." + arr1[i].getAge());
            Person p = arr1[i];
            System.out.println(p.getName() + "..." + p.getAge());
        }
    }
}
```

> 练习:定义一个学生类,声明姓名,年龄,分数,创建5个学生对象为属性赋值,放数组中,然后按照分数排序

# 第三章.继承

## 1.什么是继承

> 面向对象三大特征:  封装   继承  多态

```java
1.父类怎么形成的:多个类中有相同的成员,我们就定义了一个父类,将相同的成员抽取到父类中,子类直接继承父类
然后直接使用父类抽取出来的成员

2.格式: 子类 extends 父类

3.注意:
  a.子类可以继承父类中私有和非私有成员,但是不能直接使用私有成员
  b.构造方法不能继承
  c.静态方法可以继承但是不能被重写

4.如何学继承:
  a.要从"是否能使用"方面来学;不要从"是否拥有"
    方面来学
  b.继承是"代码的设计理念",所以可用可不用
     但是用了就比不用强,所以建议使用
```

<img src="image/image-20260119104354594.png" alt="image-20260119104354594" style="zoom:80%;" />

## 2.继承如何使用

```java
public class Employee {
    String name;
    int age;

    public void work() {
        System.out.println("员工正在工作...");
    }

    private void eat(){
        System.out.println("员工正在吃...");
    }
}

```

```java
public class Teacher extends Employee{
}
```

```java
public class Manager extends Employee{
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Teacher t1 = new Teacher();
        t1.name = "涛哥";
        t1.age = 16;
        System.out.println(t1.name+"..."+t1.age);
        t1.work();
        //t1.eat();继承之后也不能直接使用父类中私有成员

        System.out.println("======================");
        Manager m1 = new Manager();
        m1.name = "许姐";
        m1.age = 18;
        System.out.println(m1.name+"..."+m1.age);
        m1.work();
        //m1.eat();继承之后也不能直接使用父类中私有成员
    }
}

```

## 3.继承中,成员变量和成员方法的访问特点

### 3.1  成员变量

#### 3.1.1 子类和父类中的成员变量不重名:

```java
public class Fu {
    public int numFu = 100;
}

```

```java
public class Zi extends Fu{
    public int numZi = 10;
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Fu fu = new Fu();
        System.out.println(fu.numFu);

        Zi zi = new Zi();
        System.out.println(zi.numFu);
        System.out.println(zi.numZi);
    }
}

```

#### 2.1.2.子类和父类中的成员变量重名

```java
public class Fu {
    public int numFu = 100;

    public int num = 10000;
}

```

```java
public class Zi extends Fu{
    public int numZi = 10;

    public int num = 1000;
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Fu fu = new Fu();
        System.out.println(fu.numFu);
        System.out.println(fu.num);//父类中的
        System.out.println("===========================");
        Zi zi = new Zi();
        System.out.println(zi.numFu);
        System.out.println(zi.numZi);
        System.out.println(zi.num);//子类中的

        System.out.println("============================");
        //多态
        Fu f = new Zi();
        System.out.println(f.num);
    }
}
```

> 看等号左边是谁,先调用谁中的成员变量;子类没有找父类

### 2.2 成员方法

#### 2.2.1.子类和父类中的成员方法不重名:

```java
public class Fu {
    public void numFu(){
        System.out.println("父类numFu方法");
    }
}
```

```java
public class Zi extends Fu{
    public void numZi(){
        System.out.println("子类numZi方法");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Fu fu = new Fu();
        fu.numFu();

        System.out.println("===========================");
        Zi zi = new Zi();
        zi.numZi();
        zi.numFu();
    }
}
```

#### 2.2.2.子类和父类中的成员方法重名

```java
public class Fu {
    public void numFu(){
        System.out.println("父类numFu方法");
    }

    public void num(){
        System.out.println("父类num方法");
    }
}

```

```java
public class Zi extends Fu{
    public void numZi(){
        System.out.println("子类numZi方法");
    }

    public void num(){
        System.out.println("子类num方法");
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Fu fu = new Fu();
        fu.numFu();
        fu.num();//父类num方法

        System.out.println("===========================");
        Zi zi = new Zi();
        zi.numZi();
        zi.numFu();
        zi.num();//子类num方法

        System.out.println("===========================");

        //多态
        Fu f = new Zi();
        f.num();
    }
}

```

> 看new的是谁,先调用谁中的成员方法;子类没有,找父类

## 4.方法的重写

```java
1.概述:
  子类中有一个和父类方法名以及参数列表都一样的方法,这个方法叫做重写的方法
2.怎么确定此方法是不是重写的:
  @Override -> 在方法上写 -> 如果这个单词不报错就是重写的,否则就不是重写的方法
3.使用:
  如果new的是子类对象,首先要调用子类重写的方法
```

```java
public class Fu {
    public void numFu(){
        System.out.println("父类numFu方法");
    }

    public void num(){
        System.out.println("父类num方法");
    }
}

```

```java

public class Zi extends Fu{
    public void numZi(){
        System.out.println("子类numZi方法");
    }

    /**
     * 重写的方法
     */
    @Override
    public void num(){
        System.out.println("子类num方法");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Fu fu = new Fu();
        fu.numFu();
        fu.num();//父类num方法

        System.out.println("===========================");
        Zi zi = new Zi();
        zi.numZi();
        zi.numFu();
        zi.num();//子类num方法

        System.out.println("===========================");

        //多态
        Fu f = new Zi();
        f.num();
    }
}
```

### 4.1.注意事项

```java
1. 子类方法重写父类方法，必须要保证权限大于等于父类权限。(权限修饰符)
   public  -> protected -> 默认 -> private
2. 子类方法重写父类方法,方法名和参数列表都要一模一样。
3. 私有方法不能被重写,构造方法不能被重写,静态方法也不能重写
4. 子类重写父类方法之后,返回值类型应该是父类方法返回值类型的子类类型
   一般情况下,子类重写父类方法之后,都一样
5.私有方法可以继承但是不能被重写,构造方法不能被继承,也不能被重写,静态的能继承,但不能重写
```

```JAVA
public class Fu {
    public void method(){
        System.out.println("父类方法");
    }

    public Fu method01(){
        return null;
    }
}

```

```java
public class Zi extends Fu{
    @Override
    public void method(){
        System.out.println("父类方法");
    }

    @Override
    public Zi method01(){
        //返回的null没有什么特殊含义,仅仅是让方法有一个返回值而已
        return null;
    }
}

```

### 4.2.使用场景

```java
1.在子类中对父类中的方法进行升级改造
```

<img src="image/image-20260119142705633.png" alt="image-20260119142705633" style="zoom:80%;" />

```java
public class OldPhone {
    public void call(){
        System.out.println("打电话");
    }
    public void sendMessage(){
        System.out.println("发短信");
    }
    public void show(){
        System.out.println("显示手机号");
    }
}
```

```java
public class NewPhone extends OldPhone{
    public void show(){
        System.out.println("显示手机号");
        System.out.println("显示归属地");
        System.out.println("显示头像");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        OldPhone oldPhone = new OldPhone();
        oldPhone.call();
        oldPhone.sendMessage();
        oldPhone.show();
        System.out.println("======================");
        NewPhone newPhone = new NewPhone();
        newPhone.call();
        newPhone.sendMessage();
        newPhone.show();
    }
}
```

## 5.继承的特点

```java
1.继承支持单继承,不能多继承
  public class Zi extends Fu{}
  public class Fu extends Ye{}

  pubilc Zi extends Fu,Ye{} -> 不正确,不能多继承

2.继承支持多层继承:
  public class Zi extends Fu{}
  public class Fu extends Ye{}

3.继承支持一个父类有多个子类
  public class Zi extends Fu{}
  public class Bro extends Fu{}
```

## 6.继承中构造方法的特点

```java
1.特点:创建子类对象时,先初始化父类
2.原因:每一个类中的构造方法第一行默认有一个super(),不写jvm自动提供一个
3.super():代表的是调用父类无参构造
```

```java
public class Fu{
    public Fu(){
        //super()
        System.out.println("父类无参构造方法");
    }
}
```

```java
public class Zi extends Fu{
    public Zi(){
        //super();
        System.out.println("子类无参构造方法");
    }

    public Zi(int num){
        //super();
        System.out.println("子类有参构造方法");
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Zi zi = new Zi();
        System.out.println("======================");

        Zi zi1 = new Zi(10);
    }
}
```

## 7.super和this的具体使用

```java
1.super的概述:代表的是父类引用
```

### 7.1 super的具体使用

```java
1.调用父类构造:只能在子类的构造中使用
  super():调用父类无参构造
  super(实参):调用父类有参构造
2.调用父类成员变量:
  super.成员变量名
3.调用父类方法
  super.方法名()
```

```java
public class Fu {
    public int num = 100;
    public Fu(){
        System.out.println("父类无参构造");
    }
    public Fu(int num){
        System.out.println("父类有参构造");
    }
    public void show(){
        System.out.println("父类show方法");
    }
}
```

```java
public class Zi extends Fu{
    public int num = 10;
    public Zi(){
        super();//调用父类无参构造
        System.out.println("子类无参构造");
    }
    public Zi(int num){
        super(10);//调用父类有参构造
        System.out.println("子类有参构造");
    }
    @Override
    public void show(){
        super.show();//调用父类方法

        System.out.println(num);//子类num
        System.out.println(super.num);//父类num

        System.out.println("子类show方法");
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Zi zi = new Zi();
        System.out.println("======================");
        Zi zi1 = new Zi(10);
        zi1.show();
    }
}
```

> 注意:在构造中的super关键字,必须在构造第一行写

### 7.2 this的具体使用

```java
1.概述:this代表的是当前对象->哪个对象调用的this所在的方法,this就代表哪个对象
```

```java
1.调用当前对象的构造:在本类的构造中使用
  this() 调用本类无参构造
  this(实参) 调用本类的有参构造
2.调用当前对象的成员变量
  this.成员变量名
3.调用当前对象的方法
  this.方法名()
```

```java
public class Zi {
    public int num = 10;
    public Zi(){
        this(10);//调用本类有参构造方法
        System.out.println("无参构造方法");
    }
    public Zi(int num){
        //this();//调用本类无参构造方法
        System.out.println("有参构造方法");
    }

    public void show(){
        int num = 100;
        System.out.println(num);//100
        System.out.println(this.num);//10
    }
}
```

> 注意:在构造中使用this,那么this关键字也要求在构造第一行
>
> ​         在构造中,不能this和super一起出现

## 8.问题:如何为父类中private的成员变量赋值

### 8.1.利用set赋值

```java
public class Employee {
    private String name;
    private int age;

    public Employee() {
    }

    public Employee(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }
}

```

```java
public class Teacher extends Employee{
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Teacher t1 = new Teacher();
        t1.setName("涛哥");
        t1.setAge(16);
        System.out.println(t1.getName()+"..."+t1.getAge());
    }
}

```

### 8.2.利用构造方法赋值

```java
public class Employee {
    private String name;
    private int age;

    public Employee() {
    }

    public Employee(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }
}

```

```java
public class Teacher extends Employee{
    public Teacher() {
    }

    public Teacher(String name, int age) {
        super(name, age);
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Teacher t1 = new Teacher();
        t1.setName("涛哥");
        t1.setAge(16);
        System.out.println(t1.getName()+"..."+t1.getAge());

        System.out.println("======================");
        Teacher t2 = new Teacher("小王", 18);
        System.out.println(t2.getName()+"..."+t2.getAge());
    }
}

```

> 昨天课后作业:
>
> ```java
> public class MyDate {
>     int year;
>     int month;
>     int day;
> }
> public class Citizen {
>     String idCard;
>     String name;
>     MyDate birthday;
> }
> public class Test01 {
>     public static void main(String[] args) {
>         Citizen citizen = new Citizen();
>         citizen.idCard = "111";
>         citizen.name = "小王";
>         MyDate myDate = citizen.birthday;
>         myDate = new MyDate();
>         myDate.year = 1999;
>         myDate.month = 10;
>         myDate.day = 10;
>         System.out.println(citizen.idCard);
>         System.out.println(citizen.name);
>         System.out.println(myDate.year);
>         System.out.println(myDate.month);
>         System.out.println(myDate.day);
>     }
> }
> ```
