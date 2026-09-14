# day09_面向对象

```java
课前回顾:
  1.对象数组:存的是对象,获取出来的还是对象
  2.继承:
    a.格式: 子类 extends 父类
    b.成员访问特点:
      成员变量:看等号左边是谁,先调用谁中的成员变量;子类没有找父类
      成员方法:看等号右边是谁,先调用谁中的方法,子类没有找父类
    c.方法的重写:子类中有一个和父类方法名以及参数列表都一样的方法
      检测: @Override
      使用场景:对父类中的方法进行升级改造
    d.继承中构造方法的特点:创建子类对象时先初始化父类 -> 构造第一行默认有一个super(),调用父类无参构造
    e.super关键字:代表的是父类引用
      super():调用父类构造方法
      super.变量名:调用父类成员变量
      super.方法名:调用父类成员方法
    f.this关键字:代表的是当前对象,哪个对象调用的this所在的方法,this就代表哪个对象
      this():调用本类(其实是当前对象)构造
      this.变量名:调用本类(其实是当前对象)成员变量
      this.方法名:调用本类(其实是当前对象)方法
    g:继承特点:
      继承不能多继承,只能单继承
      继承能多层继承
      一个父类可以有多个子类

今日重点:
  1.会定义抽象类以及抽象方法
  2.会重写抽象方法,进行实现
  3.会定义接口以及实现类
  4.会实现接口
  5.会在接口中定义抽象方法以及实现抽象方法
  6.知道接口的特点
```

# 第一章.抽象

<img src="image/image-20260120094930283.png" alt="image-20260120094930283" style="zoom:80%;" />

## 1.抽象的介绍

```java
1.抽象方法和抽象类的形成:
  抽取出来的方法无法做具体实现,需要延伸到子类中做具体是实现,就可以定义成抽象方法,抽象方法所在的了一定是抽象类

2.抽象类定义:abstract
   public abstract class 类名{}
3.抽象方法定义:
   修饰符 abstract 返回值类型 方法名(形参);

4.使用:
   a.定义子类,继承抽象父类
   b.必须重写父类中所有抽象方法
   c.创建子类对象(抽象类不能new对象)
      调用重写方法

 5.问题:继承是为了少写重复代码,但是在
    继承的基础上加了抽象方法,还必须在
    子类中重写,那么继承还有意义吗?有
 6.抽象是一种"代码的设计理念",可以将
    抽象类看做是一类事物的"标准",只要是我的子类,都必须要遵守我的规范,拥有我的功能,怎么算遵守了?->重写
```

```java
public abstract class Animal {
    public abstract void eat();
    public abstract void drink();
}
```

```java
public class Dog extends Animal{
    @Override
    public void eat() {
        System.out.println("狗啃骨头");
    }

    @Override
    public void drink() {
        System.out.println("狗用舌头卷水喝");
    }
}

```

```java
public class Cat extends Animal{
    @Override
    public void eat() {
        System.out.println("猫吃鱼");
    }

    @Override
    public void drink() {
        System.out.println("猫用舌头舔水喝");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Dog dog = new Dog();
        dog.eat();
        dog.drink();
        System.out.println("===============");
        Cat cat = new Cat();
        cat.eat();
        cat.drink();
    }
}

```

## 2.抽象的注意事项

```java
1.抽象类不能直接new对象,只能创建非抽象子类的对象
2.抽象类中,可以有构造方法,是供子类创建对象时,初始化父类中属性使用的
3.抽象类中可以有成员变量,构造,成员方法
4.抽象类中不一定非得有抽象方法,但是有抽象方法的类一定是抽象类
5.抽象类的子类,必须重写父类中的所有抽象方法,否则,编译无法通过.除非该子类也是抽象类
```

```java
public abstract class Employee {
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

    public abstract void work();
}

```

```java
public class Teacher extends Employee{
    public Teacher() {
    }

    public Teacher(String name, int age) {
        super(name, age);
    }

    @Override
    public void work() {
        System.out.println("涛哥在台上叭叭叭讲课");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Teacher t1 = new Teacher("涛哥", 14);
        System.out.println(t1.getName()+"..."+t1.getAge());
        t1.work();
    }
}

```

# 第二章.综合案例_作业

```java
某IT公司有多名员工，按照员工负责的工作不同，进行了部门的划分（研发部、维护部）。
研发部(Developer)根据所需研发的内容不同，又分为 JavaEE工程师 、Android工程师 ；
维护部(Maintainer)根据所需维护的内容不同，又分为 网络维护工程师(Network) 、硬件维护工程师(Hardware) 。

公司的每名员工都有他们自己的员工编号、姓名，并要做他们所负责的工作。

工作内容:
- JavaEE工程师： 员工号为xxx的 xxx员工，正在研发电商网站
- Android工程师：员工号为xxx的 xxx员工，正在研发电商的手机客户端软件
- 网络维护工程师：员工号为xxx的 xxx员工，正在检查网络是否畅通
- 硬件维护工程师：员工号为xxx的 xxx员工，正在修复电脑主板

请根据描述，完成员工体系中所有类的定义，并指定类之间的继承关系。进行XX工程师类的对象创建，完成工作方法的调用。
```

## 方式1:利用set赋值

```java

```

```java

```

```java

```

```java

```

## 方式2:利用构造赋值

```java

```

```java

```

```java

```

```java

```

>
>

# 第三章.接口

## 1.接口的介绍

<img src="image/image-20260120112300450.png" alt="image-20260120112300450" style="zoom:80%;" />

## 2.接口的定义以及使用

```java
1.接口:是一种标准,规范
2.接口定义:interface
   public interface 接口名{}
3.实现类定义:implements
   public class 实现类 implements 接口{}
4.接口中的成员:
   a.jdk8之前:
     抽象方法:public abstract 返回值类型 方法名(形参) -> 即使不写public abstract,默认也有
     成员变量:public static final 数据类型 变量名 = 值 -> 即使不写public static final 默认也有
   b.jdk8开始:
     默认方法:
          public default 返回值类型 方法名(形参){
                    方法体
                    return 结果
          }
     静态方法:
          public static 返回值类型 方法名(形参){
                  方法体
                  return 结果
          }
     c.jdk9开始:
        私有方法 -> 将public改成private
```

```java
使用:
  1.定义接口
  2.定义实现类,实现接口
  3.重写接口中的所有抽象方法
  4.创建实现类对象(接口不能new对象)
  5.调用重写方法
```

```java
public interface USB {
    public abstract void open();
    public abstract void close();
}

```

```java
public class Mouse implements USB{
    @Override
    public void open() {
        System.out.println("鼠标打开");
    }

    @Override
    public void close() {
        System.out.println("鼠标关闭");
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Mouse m = new Mouse();
        m.open();
        m.close();
    }
}

```

## 3.接口中的成员

### 3.1抽象方法

```java
1.格式:
  public abstract 返回值类型 方法名(形参);
2.注意:
  即使不写public abstract 默认也有
3.使用:
  通过实现类重写去使用
```

```java
public interface USB {
    public abstract void open();
    void close();
}
```

```java
public class Mouse implements USB{
    @Override
    public void open() {
        System.out.println("鼠标打开");
    }

    @Override
    public void close() {
        System.out.println("鼠标关闭");
    }

}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Mouse m = new Mouse();
        m.open();
        m.close();
    }
}
```

### 3.2默认方法

```java
1.格式:
  public default 返回值类型 方法名(形参){
      方法体
      return 结果
  }
2.使用:
  a.定义实现类,实现接口/
  b.默认方法可重写可不重写
  c.创建实现类对象,调用默认方法
```

```java
public interface USB {
    //默认方法
    public default void methodDef(){
        System.out.println("接口中的默认方法");
    }
}
```

```java
public class Mouse implements  USB{
    @Override
    public void methodDef(){
        System.out.println("重写的接口中的默认方法");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Mouse mouse = new Mouse();
        mouse.methodDef();
    }
}
```

### 3.3静态方法

```java
1.格式:
  public static 返回值类型 方法名(形参){
      方法体
      return 结果
  }
2.使用:
  接口名直接调用
```

```java
public interface USB {
    //静态方法
    public static void methodSta(){
        System.out.println("接口中的静态方法");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        USB.methodSta();
    }
}
```

> 默认方法和静态方法的使用有啥意义:
>
> 将来我们开发都是面向接口编程-->都是先定义一个接口,这个接口相当于是"功能的大集合",接口中定义的都是我们要实现的功能,然后在具体的实现类中实现,但是如果我们要临时加一个小功能,这个小功能不需要几行代码,此时我们就没必要在接口中定义抽象方法了,再去实现类中实现了,所以我们就可以在接口中直接定义默认方法或者静态方法,在接口中直接实现了就完事了!

### 3.4.成员变量

```java
1.格式:
  public static final 数据类型 变量名 = 值
2.注意:
  a.即使不写public static final,默认也有
  b.习惯上我们将static final修饰的变量名写成大写
  c.成员变量需要自己手动赋值
3.使用:
  接口名直接调用
```

```java
public interface USB {
    public static final int NUM = 10;
    int NUM2 = 20;
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        System.out.println(USB.NUM);
        System.out.println(USB.NUM2);
    }
}
```

### 3.5.私有方法

```java
1.格式:
  将public改成private
```

```java
public interface USB {
    private void method(){
        System.out.println("接口中的私有方法");
    }

/*    public static void methodSta(){
        method();
    }*/

    public default void methodDef(){
        method();
    }
}
```

```java
public class Mouse implements  USB{

}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Mouse mouse = new Mouse();
        mouse.methodDef();
    }
}

```

> 特殊语法:   接口名.super.方法名()
>
>
>
> public class 实现类  implements 接口A,接口B{
>
> ​     public void method(){
>
> ​         接口名.super.方法名()
>
> ​      }
>
> }
>
> public interface 接口A{
>
> ​    default void method(){
>
> ​     }
>
> }
>
> public interface 接口B{
>
> ​    default void method(){
>
> ​     }
>
> }

## 4.接口的特点

```java
1.接口一个多继承-> 一个接口可以继承一个或者多个接口
  public interface 接口A extends 接口B,接口C{}
2.接口可以多实现-> 一个实现类可以同时实现一个或者多个接口
  public class 实现类 implements 接口A,接口B{}
3.一个子类可以继承一个父类的同时实现一个或者多个接口
  public class Zi extends Fu implements 接口A,接口B{}
```

> 当一个类实现多个接口时,如果接口中的抽象方法有重名且参数一样的,只需要重写一次
>
> ```java
> public interface InterfaceA {
>     public abstract void method();
>     public abstract void method2();
> }
> ```
>
> ```java
> public interface InterfaceB {
>     public abstract void method();
>     public abstract void method2(int num);
> }
>
> ```
>
> ```java
> public class InterfaceImpl implements InterfaceA, InterfaceB{
>
>     @Override
>     public void method() {
>         System.out.println("重写的默认方法");
>     }
>
>     @Override
>     public void method2(int num) {
>         System.out.println("重写的有参的method02");
>     }
>
>     @Override
>     public void method2() {
>         System.out.println("重写的无参的method02");
>     }
> }
>
> ```
>
> 当一个类实现多个接口时,如果默认方法有重名的,参数一样,默认方法必须要重写一次
>
> ```java
> public interface InterfaceA {
>     public abstract void method();
>     public abstract void method2();
>
>     public default void methodDef(){
>         System.out.println("接口A中的默认方法");
>     }
> }
>
> ```
>
> ```java
> public interface InterfaceB {
>     public abstract void method();
>     public abstract void method2(int num);
>
>     public default void methodDef(){
>         System.out.println("接口B中的默认方法");
>     }
> }
> ```
>
> ```java
> public class InterfaceImpl implements InterfaceA, InterfaceB{
>
>     @Override
>     public void method() {
>         System.out.println("重写的默认方法");
>     }
>
>     @Override
>     public void method2(int num) {
>         System.out.println("重写的有参的method02");
>     }
>
>     @Override
>     public void method2() {
>         System.out.println("重写的无参的method02");
>     }
>
>     @Override
>     public void methodDef() {
>         System.out.println("重写的默认方法");
>     }
> }
>
> ```

## 5.接口和抽象类的区别

```java
相同点:
  a.都位于继承的顶端,用于被其他类实现或者继承
  b.都不能new
  c.都包含抽象方法,其子类都必须重写这些抽象方法

不同点:
  a.抽象类:一般作为父类使用,可以有成员变量,构造,成员方法,抽象方法等
  b.接口:成员单一,一般抽取接口,抽取的都是方法,是功能的大集合
  c.类不能多继承,接口可以
```

<img src="image/image-20260120154108647.png" alt="image-20260120154108647" style="zoom:80%;" />

# 第四章.final关键字

```java
1.概述:代表的是最终的
2.使用:
  a.修饰一个类
  b.修饰一个方法
  c.修饰一个成员变量
  d.修饰一个局部变量
  e.修饰一个对象
```

## 1.修饰类

```java
1.格式:public final class 类名{}
2.特点:
  被final修饰的类不能被继承
```

```java
public /*final*/ class Animal {
}
```

```java
public class Dog extends Animal{
}
```

## 2.修饰方法

```java
1.格式:
  修饰符 final 返回值类型 方法名(形参){
      方法体
      return 结果
  }

2.特点:
  a.被final修饰的方法不能被重写
  b.final和abstract不能一起使用
```

```java
public /*final*/ class Animal {
    public final void eat(){
        System.out.println("吃吃吃");
    }

    //public abstract final void drink();
}

```

```java
public class Dog extends Animal{
/*    public final void eat(){
        System.out.println("吃吃吃");
    }*/
}

```

## 3.修饰成员变量

```java
1.格式: final 数据类型 变量名
2.特点:
  被final修饰的成员变量,不能二次赋值,相当于常量
```

```java
public class Person {
    public final String name = "张三";

    public Person() {
    }

/*    public Person(String name) {
        this.name = name;
    }*/

    public String getName() {
        return name;
    }

/*    public void setName(String name) {
        this.name = name;
    }*/
}
```

## 4.修饰局部变量

```java
1.格式: final 数据类型 变量名 = 值
2.特点:不能二次赋值
```

```java
public class Test01 {
    public static void main(String[] args) {
        final int i = 10;
        //i = 20;
        System.out.println(i);
    }
}

```

## 5.修饰对象

```java
1.格式: final 类名 对象名 = new 类名()
2.特点:被final修饰的对象,地址值不能改变,但是对象的属性值可以改变
```

```java
public class Student {
    private int id;
    private String name;

    public Student() {
    }

    public Student(int id, String name) {
        this.id = id;
        this.name = name;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}

```

```java
public class Test02 {
    public static void main(String[] args) {
        final Student s1 = new Student(1,"张三");
        System.out.println(s1);
        //s1 = new Student();
        s1.setName("李四");
        System.out.println(s1.getName());
    }
}
```

# 第五章.权限修饰符

```java
1.概述:在java中,有四种权限修饰符
  public:公共的访问权限,被public修饰的在哪里都能使用
  protected:受保护的
  默认:成员变量和方法前面的权限修饰符啥也不用,不写
  private:私有的,只能在本类中使用
```

|                | public | protected | 默认 | private |
| -------------- | ------ | --------- | ---- | ------- |
| 同类           | yes    | yes       | yes  | yes     |
| 同包不同类     | yes    | yes       | yes  | no      |
| 不同包子父类   | yes    | yes       | no   | no      |
| 不同包非子父类 | yes    | no        | no   | no      |

```java
将来四种权限修饰符使用方式:
  1.属性:private修饰 -> 封装思想
  2.构造:public修饰 -> 便于创建对象(工具类除外)
  3.方法:public修饰 -> 便于调用
```
