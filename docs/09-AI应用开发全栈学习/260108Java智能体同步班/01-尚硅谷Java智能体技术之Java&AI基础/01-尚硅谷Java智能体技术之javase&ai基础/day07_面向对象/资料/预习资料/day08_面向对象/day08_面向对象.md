# day08_面向对象

```java
课前回顾:
  1.类:实体类
    属性:成员变量
    行为:成员方法
  2.对象:
    a.导包
    b.new对象
    c.调用方法
  3.匿名对象:
    没有等号左边的部分,只有new的部分
    注意:涉及到赋值别用
  4.封装:
    a.概述:将细节隐藏起来,对外提供公共的接口
    b.方法是一种封装的体现:方法体就是隐藏起来的细节,方法名就是对外提供的公共接口
    c.关键字:private私有化的
  5.get/set方法
    getxxx()获取值
    setxxx()赋值
  6.构造方法:
    a.无参构造:new对象
      每个类都有一个无参构造,即使不写,默认也有
    b.有参构造:
      new对象的同时为属性赋值
   7.this关键字:代表当前对象
     区分重名的成员变量和局部变量
   8.标准javabean:
     私有属性,构造方法,get/set方法
今日重点:
  all

```

# 第一章.JavaBean的作用

```java
1.javabean将来都是和数据库中的表联系起来的,将来都是先有表,再根据表创建javabean类
  类名  ->   表名
  属性名  -> 字段名(列名)
  属性类型 -> 字段类型
  属性值 -> 单元格中的数据
  javabean对象 -> 数据库中的每一行数据

  数据库第一行数据: Student s1 = new Student(1,"zhangsan",10)
  数据库第二行数据: Student s2 = new Student(2,"lisi",12)
  数据库第三行数据: Student s3 = new Student(3,"wangwu",14)
```

> 课程配图（未随笔记提交）

### 1.1.javabean在开发中的实际运用_添加功能

> 课程配图（未随笔记提交）

> 封装页面上发送过来的数据,一层一层传递到dao层,在dao层中调用javabean对象中的getxxx方法,将属性值获取出来,放到sql语句中

### 1.2.javabean在实际开发中运用_查询功能

> 课程配图（未随笔记提交）

> 封装从数据库中查询出来的数据,然后一层一层返回给页面上进行展示

# 第二章.对象数组

```java
需求:定义一个数组,存3个Person对象,遍历数组,将Person对象中的属性值获取出来
```

> 课程配图（未随笔记提交）

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
           元素是int型:int[]
           元素是double型:double[]
           元素是字符串型:String[]
           元素是Person:Person[]
         */
        Person[] arr = new Person[3];
        Person p1 = new Person("张三", 10);
        Person p2 = new Person("李四", 12);
        Person p3 = new Person("王五", 14);

        //将三个对象存储到数组中
        arr[0] = p1;
        arr[1] = p2;
        arr[2] = p3;

        //遍历
        for (int i = 0; i < arr.length; i++) {
            System.out.println(arr[i].getName()+"..."+arr[i].getAge());
        }
    }
}
```

> 练习:定义一个学生类,声明姓名,年龄,分数,创建5个学生对象为属性赋值,然后按照分数排序

# 第三章.继承

## 1.什么是继承

> java面向对象三大特征:封装,继承,多态

```java
1.父类怎么形成:
   抽取多个类中共同的成员,其他类想使用就可以直接继承父类

2.使用:
  a.定义父类
  b.定义子类 extends 父类{}

3.特点:
  a.子类继承父类之后,可以继承父类中私有以及非私有成员,但是只可以使用父类中"非私有成员"
  b.构造方法不能被继承
  c.静态方法能被继承,不能被重写

4.问题:我们子类继承父类之后,可以继承私有的
   按常理来说,继承过来了,就可以使用,但是
   私有的还不能使用,有点矛盾

   想学好继承,不要从是否"拥有"来学习
   要从是否"能使用"来学习
```

> 课程配图（未随笔记提交）

## 2.继承如何使用

```java
public class Employee {
    String name;
    int age;
    public void work(){
        System.out.println("员工正在工作...");
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
        Teacher teacher = new Teacher();
        teacher.name = "金莲";
        teacher.age = 32;
        System.out.println(teacher.name+"..."+teacher.age);
        teacher.work();
    }
}
```

## 3.继承中,成员变量和成员方法的访问特点

### 3.1  成员变量

#### 3.1.1 子类和父类中的成员变量不重名:

```java
public class Fu {
    int numFu = 10;
}

```

```java
public class Zi extends Fu{
    int numZi = 100;
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
    int numFu = 10;
    int num = 20;
}
```

```java
public class Zi extends Fu{
    int numZi = 100;
    //int num = 200;
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Fu fu = new Fu();
        System.out.println(fu.numFu);
        System.out.println(fu.num);

        Zi zi = new Zi();
        System.out.println(zi.numFu);
        System.out.println(zi.numZi);
        System.out.println(zi.num);

        System.out.println("==============");
        //多态形式
        Fu fu1 = new Zi();
        System.out.println(fu1.num);
    }
}

```

> 看等号左边是谁,就先调用谁中的成员变量

### 2.2 成员方法

#### 2.2.1.子类和父类中的成员方法不重名:

```java
public class Fu {
    public void methodFu(){
        System.out.println("父类方法");
    }
}

```

```java
public class Zi extends Fu{
    public void methodZi(){
        System.out.println("子类方法");

    }
}
```

```java
public class Test {
    public static void main(String[] args) {
        Fu fu = new Fu();
        fu.methodFu();

        Zi zi = new Zi();
        zi.methodZi();
        zi.methodFu();
    }
}

```

#### 2.2.2.子类和父类中的成员方法重名

```java
public class Fu {
    public void methodFu(){
        System.out.println("父类方法");
    }

    public void method(){
        System.out.println("父类method方法");
    }
}

```

```java
public class Zi extends Fu{
    public void methodZi(){
        System.out.println("子类方法");

    }

    public void method(){
        System.out.println("子类method方法");
    }
}
```

```java
public class Test {
    public static void main(String[] args) {
        Fu fu = new Fu();
        fu.methodFu();
        fu.method();

        Zi zi = new Zi();
        zi.methodZi();
        zi.methodFu();
        zi.method();

        //多态
        Fu fu1 = new Zi();
        fu1.method();
    }
}
```

> 看new的是谁,先调用谁中的成员方法,子类没有找父类

## 4.方法的重写

```java
1.概述:子类中有一个和父类方法名以及参数列表一样的方法
2.如何检测:在方法上用注解
  @Override
```

```java
public class Animal {
    public void eat(){
        System.out.println("吃");
    }
}
```

```java
public class Dog extends Animal{
    @Override
    public void eat(){
        System.out.println("狗吃骨头");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
       Dog dog = new Dog();
       dog.eat();
    }
}
```

### 4.1.注意事项

```java
1. 子类方法重写父类方法，必须要保证权限大于等于父类权限。(权限修饰符)
    public -> protected -> 默认 -> private
2. 子类方法重写父类方法,方法名和参数列表都要一模一样。
3. 私有方法不能被重写,构造方法不能被重写,静态方法也不能重写
4. 子类重写父类方法之后,返回值类型应该是父类方法返回值类型的子类类型
   一般情况下,子类重写父类方法之后,都一样
5.私有方法可以继承但是不能被重写,构造方法不能被继承,也不能被重写,静态的能继承,但不能重写
```

```JAVA
public class Fu {
    void show(){
        System.out.println("父类方法");
    }

    public Object method(){
        //此返回值没有任何意义,主要是让这个方法有个返回值,不让方法报错
        return null;
    }
}

```

```java
public class Zi extends Fu{
    @Override
    public void show(){
        System.out.println("父类方法");
    }

    @Override
    public String method(){
        //此返回值没有任何意义,主要是让这个方法有个返回值,不让方法报错
        return null;
    }
}

```

### 4.2.使用场景

```java
子类需要对父类中的某个方法进行升级改造,就需要在子类中重写,重新实现一下子
```

> 课程配图（未随笔记提交）

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
    @Override
    public void show(){
        System.out.println("显示手机号");
        System.out.println("显示归属地");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        NewPhone newPhone = new NewPhone();
        newPhone.call();
        newPhone.sendMessage();
        newPhone.show();
    }
}
```

## 5.继承的特点

```java
1.继承只支持单继承,不能多继承(一个子类只能有一个亲爹)
  public class A extends B{}
2.继承支持多层继承
  public class A extends B{}
  public class B extends C{}
3.一个父类可以有多个子类
  public class A extends B{}
  public class C extends B{}
```
