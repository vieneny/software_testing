# day09_面向对象

```java
课前回顾:
  1.可变参数:
    a.格式: 数据类型...变量名
    b.注意:
      参数列表中只能有一个可变参数,而且需要放到最后
    c.本质:数组
  2.递归:方法内部自己调用自己
    a.注意:必须要有出口,而且不要递归太多次
  3.冒泡排序:相邻两个元素进行比较,互换位置
  4.二分查找:每次查找都取中间索引,然后找不到,下次就要干掉一半
    a.前提:数组是升序的
  5.对象数组:存的是对象,取出来的还是对象
  6.基本类型做方法参数传递:传递的是值,不是变量本身
    引用类型做方法参数传递:传递的是地址值

今日重点:
  1.知道什么时候用继承
  2.知道继承的作用
  3.知道如何使用继承
  4.会调用成员变量和成员方法 -> 在继承的前提下
  5.知道继承中的方法的重写
  6.知道继承的特点
  7.会使用super关键字调用父类成员;this关键字调用当前对象成员
  8.会实现抽象类
```

# 第一章.抽象

> 课程配图（未随笔记提交）

## 1.抽象的介绍

```java
1.抽象类怎么形成的:
   抽取的方法在父类中没法具体实现,所以这个方法就可以定义成"抽象方法",而"抽象方法"所在的类一定是抽象类

2.抽象类和抽象方法的定义: abstract
  a.抽象类:  public abstract class 类名{}
  b.抽象方法: 修饰符 abstract 返回值类型 方法名(形参);

3.如何使用抽象类和抽象方法:
  a.定义子类,继承抽象父类
  b.在子类中,重写父类中所有的抽象方法 -> alt+回车 -> 选择Implement Methods
  c.创建子类对象(抽象类不能new对象)
  d.调用重写之后的方法

4.问题:继承是为了少写代码,但是抽象父类中的抽象方法,必须要在子类中重写,反正都要在子类中重写方法,那么我们何必非要将抽象方法抽取到抽象类中呢?
   其实抽象类也是一种代码的"设计思想"
   抽象类可以理解为是一类事物的规范,标准 -> 属于这一类事物,必须要拥有这类事物规定的功能,怎么算拥有,重写,具体实现
```

```java
public abstract class Animal {
    public abstract void eat();//吃
    public abstract void drink();//喝
    public abstract void howl();//叫
}

```

```java
public class Dog extends Animal{
    @Override
    public void eat() {
        System.out.println("狗吃屎");
    }

    @Override
    public void drink() {
        System.out.println("狗用舌头卷着水喝");
    }

    @Override
    public void howl() {
        System.out.println("汪汪汪");
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
        System.out.println("猫舔水喝");
    }

    @Override
    public void howl() {
        System.out.println("喵喵喵");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Dog dog = new Dog();
        dog.eat();
        dog.drink();
        dog.howl();
    }
}

```

> 课程配图（未随笔记提交）

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
        System.out.println("涛哥在忽悠人");
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Teacher t1 = new Teacher("涛哥", 18);
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

> 课程配图（未随笔记提交）

## 2.接口的定义以及使用

```java
1.接口的定义:接口其实就是一套标准,规则

2.接口的定义:interface
  public interface 接口名{}

3.实现:implements
  a.定义实现类 实现(implements) 接口
  b.重写接口中所有的抽象方法
  c.创建实现类对象(接口不能直接new对象)
  d.调用实现类中重写的方法
4.接口中的成员:
   a.在jdk8之前:
     抽象方法:不写public abstract,默认也有
     成员变量:必须是public static final的,不写默认也有

   b.在jdk8开始:
     默认方法:定义方法的时候在方法声明上写上default关键字
                    public default 返回值类型 方法名(形参){方法体;return 结果}
     静态方法:和之前定义的静态方法一样

   c.在jdk9的时候:
      私有方法:将public改成private
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
        System.out.println("鼠标打开了");
    }

    @Override
    public void close() {
        System.out.println("鼠标关闭了");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Mouse mouse = new Mouse();
        mouse.open();
        mouse.close();
    }
}

```

## 3.接口中的成员

### 3.1抽象方法

```java
1.格式:
  public abstract 返回值类型 方法名(形参);
2.特点:
  不写public abstract默认也有
3.使用:
  a.定义实现类 实现(implements) 接口
  b.重写接口中所有的抽象方法
  c.创建实现类对象(接口不能直接new对象)
  d.调用实现类中重写的方法
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
        System.out.println("鼠标打开了");
    }

    @Override
    public void close() {
        System.out.println("鼠标关闭了");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Mouse mouse = new Mouse();
        mouse.open();
        mouse.close();
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
  可重写可不重写
  但是需要通过创建实现类对象调用
```

```java
public interface USB {
    public abstract void open();
    void close();

    //默认方法
    public default void methodDef(){
        System.out.println("我是USB接口的默认方法");
    }
}
```

```java
public class KeyBoard implements USB{
    @Override
    public void open() {
        System.out.println("键盘开启");
    }

    @Override
    public void close() {
        System.out.println("键盘关闭");
    }

/*    @Override
    public void methodDef(){
        System.out.println("我是重写的USB接口的默认方法");
    }*/
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Mouse mouse = new Mouse();
        mouse.open();
        mouse.close();

        System.out.println("=============");
        KeyBoard keyBoard = new KeyBoard();
        keyBoard.methodDef();
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
    public abstract void open();
    void close();

    //默认方法
    public default void methodDef(){
        System.out.println("我是USB接口的默认方法");
    }

    //静态方法
    public static void methodSta(){
        System.out.println("我是USB接口的静态方法");
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        System.out.println("=============");
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
  public static final 数据类型 变量名 = 值  -> 不写public static final默认也有
2.final关键字:
  代表的是最终的 -> 被final修饰的变量不能二次赋值,相当于常量
3.使用:
  接口名直接调用
4.注意:
  我们习惯上会将public static final修饰的变量名写成大写
```

```java
public interface USB {
    public abstract void open();
    void close();

    //默认方法
    public default void methodDef(){
        System.out.println("我是USB接口的默认方法");
    }

    //静态方法
    public static void methodSta(){
        System.out.println("我是USB接口的静态方法");
    }

    //成员变量
    public static final int NUM = 10;
    int NUM1 = 100;
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Mouse mouse = new Mouse();
        mouse.open();
        mouse.close();

        System.out.println("=============");
        KeyBoard keyBoard = new KeyBoard();
        keyBoard.methodDef();

        System.out.println("=============");
        USB.methodSta();

        System.out.println("=============");
        System.out.println(USB.NUM);
        System.out.println(USB.NUM1);
    }
}
```

### 3.5.私有方法

```java
1.定义:
  private 返回值类型 方法名(形参){
      方法体
      return 结果
  }
```

```java
public interface USB {
    private static void  methodPrivate() {
        System.out.println("我是接口中的私有方法");
    }

    private void methodPrivate02(){
        System.out.println("我是接口中的私有方法");
    }

    public static void methodSta(){
        methodPrivate();
    }

    public default void methodDef(){
        methodPrivate02();
    }
}
```

```java
public class Mouse implements USB{
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        USB.methodSta();
        System.out.println("=================");
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
1.接口可以多继承
  public interface A extends 接口B,接口C{}
2.接口可以多实现 -> 一个实现类可以同时实现一个或者多个接口
  public class InterfaceImpl implements InterfaceA, InterfaceB{}
3.一个子类可以继承一个父类的同时实现一个或者多个接口
  public class Zi extends Fu implements InterfaceA, InterfaceB{}
```

> 当一个类实现多个接口时,如果接口中的抽象方法有重名且参数一样的,只需要重写一次
>
> ```java
> public interface InterfaceA {
>  public abstract void method01();
> }
>
> ```
>
> ```java
> public interface InterfaceB {
>  public abstract void method01();
> }
> ```
>
> ```java
> public class InterfaceImpl implements InterfaceA, InterfaceB{
>  @Override
>  public void method01() {
>      System.out.println("重写的method01");
>  }
> }
>
> ```
>
> 当一个类实现多个接口时,如果默认方法有重名的,参数一样,默认方法必须要重写一次
>
> ```java
> public interface InterfaceA {
>  public abstract void method01();
>
>  public default void methodDef(){
>      System.out.println("接口A中的默认方法");
>  }
> }
> ```
>
> ```java
> public interface InterfaceB {
>  public abstract void method01();
>
>  public default void methodDef(){
>      System.out.println("接口B中的默认方法");
>  }
> }
>
> ```
>
> ```java
> public class InterfaceImpl implements InterfaceA, InterfaceB{
>  @Override
>  public void method01() {
>      System.out.println("重写的method01");
>  }
>
>  @Override
>  public void methodDef() {
>      InterfaceA.super.methodDef();
>  }
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

> 课程配图（未随笔记提交）
