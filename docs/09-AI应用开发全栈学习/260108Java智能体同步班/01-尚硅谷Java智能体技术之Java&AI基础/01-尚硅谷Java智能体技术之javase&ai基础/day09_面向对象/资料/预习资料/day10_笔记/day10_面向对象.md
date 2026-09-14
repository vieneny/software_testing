# day10_面向对象

```java
课前回顾:
  1.super和this:
    a.super:代表的父类引用
      调用父类构造
      调用父类成员变量
      调用父类方法
    b.this:代表的当前对象
      调用当前对象的构造
      调用当前对象的成员变量
      调用当前对象的方法
  2.抽象类的定义:public abstract class 类名{}
  3.抽象方法的定义:修饰符 abstract 返回值类型 方法名(形参);
  4.使用:
    定义子类,继承父类
    重写抽象方法
    创建子类对象,调用重写方法
  5.接口:标准,规则
    a.定义接口: public interface 接口名{}
    b.实现接口: public class 类名 implements 接口名{}
  6.抽象方法:->必须重写实现
    默认方法:带default的方法 -> 可重写可不重写
    静态方法:带static的 -> 接口名调用
    成员变量:带public static final
    私有方法:带private的方法
  7.接口特点:
    a.接口能多继承
    b.接口能多实现
    c.一个子类继承父类的同时可以实现一个或者多个接口
今日重点:
  1.多态的前提
  2.知道多态的好处
  3.知道多态的向下转型(强转)
  4.知道如何判断类型
  5.会静态代码块
  6.会匿名内部类(待定)
```

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

```java
public abstract class Employee {
    private int id;
    private String name;

    public Employee() {
    }

    public Employee(int id, String name) {
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
    public abstract void work();
}

public abstract class Developer extends Employee{
    public Developer() {
    }

    public Developer(int id, String name) {
        super(id, name);
    }
}

public class JavaEE extends Developer{
    public JavaEE() {
    }

    public JavaEE(int id, String name) {
        super(id, name);
    }

    @Override
    public void work() {
        System.out.println("员工编号为:"+getId()+"的"+getName()+"正在开发电商网站");
    }
}

public class Test01 {
    public static void main(String[] args) {
        JavaEE javaEE = new JavaEE();
        javaEE.setId(1);
        javaEE.setName("涛哥");
        javaEE.work();

        System.out.println("===================");
        JavaEE javaEE1 = new JavaEE(2,"许姐");
        javaEE1.work();
    }
}

```

> 课程配图（未随笔记提交）

> 1.封装:将细节隐藏起来(不让外界直接使用),对外提供一套公共的接口(让外界通过这个公共接口间接调用隐藏起来的细节)
>
> ​    a.有代表性的关键字:private  -> 私有化
>
> ​    b.get/set方法 -> 提供的公共接口
>
> ​    c.构造:
>
> ​       无参构造:new对象
>
> ​       有参构造:new对象的同时,为属性赋值
>
> 2.继承:将子类中共有的内容抽取到父类中,子类直接继承父类,就可以直接使用父类中非私有成员
>
>    a.关键字:extends
>
>    b.成员变量:看等号左边是谁
>
> ​       成员方法:看new的是谁
>
> 3.抽象:定义抽象类,里面定义抽象方法
>
>    a.定义子类,继承抽象父类
>
>    b.重写所有抽象方法
>
>    c.创建子类对象,调用重写的方法

# 第一章.多态

```java
1.面向对象三大特征:封装    继承     多态
2.怎么学多态:
  a.不要从字面意思去学
  b.直接从多态的前提和使用方面来学多态
```

## 1.多态的介绍

```java
1.多态的前提:
  a.必须有子父类继承关系或者接口实现关系
  b.必须有方法的重写
  c.父类引用指向子类对象-> Fu fu = new Zi()
```

## 2.多态的基本使用

```java
public abstract class Animal {
    public abstract void eat();
}

```

```java
public class Dog extends Animal{
    @Override
    public void eat() {
        System.out.println("狗啃骨头");
    }

    //特有方法
    public void lookHome(){
        System.out.println("狗看家");
    }
}

```

```java
public class Cat extends Animal{
    @Override
    public void eat() {
        System.out.println("猫吃鱼");
    }

    //特有方法
    public void catchMouse(){
        System.out.println("猫抓老鼠");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        //多态形式
        Animal animal = new Dog();
        animal.eat();
        //多态前提下,不能调用子类特有功能
        //animal.lookHome();
    }
}
```

## 3.多态的条件下成员的访问特点

### 3.1成员变量

```java
1.看等号左边是谁,先调用谁中的成员变量  -> 也可以记编译看左边,运行看左边(成员变量无法覆盖)
```

```java
public class Fu {
    int num = 10;

}

```

```java
public class Zi extends Fu{
    int num = 20;

}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Fu fu = new Zi();
        System.out.println(fu.num);
    }
}

```

### 3.2成员方法

```java
1.看new的是谁,先调用谁中的成员方法 -> 也可以记编译看左边,运行看右边(父类方法可以被子类重写覆盖)
```

```java
public class Fu {
    int num = 10;
    public void show(){
        System.out.println("Fu show()");
    }
}
```

```java
public class Zi extends Fu{
    int num = 20;

    @Override
    public void show() {
        System.out.println("Zi show()");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Fu fu = new Zi();
        System.out.println(fu.num);
        fu.show();
    }
}
```

## 4.多态的好处(为什么学多态)

```java
1.原始方式:
  a.优点:既能调用继承的,还能调用子类特有的,还能调用重写的
  b.缺点:扩展性差
2.多态方式:
  a.优点:扩展性强
  b.缺点:不能直接调用子类特有功能
```

```java
public abstract class Animal {
    public abstract void eat();
}
```

```java
public class Dog extends Animal {
    @Override
    public void eat() {
        System.out.println("狗啃骨头");
    }

    //特有方法
    public void lookHome(){
        System.out.println("狗看家");
    }
}

```

```java
public class Cat extends Animal {
    @Override
    public void eat() {
        System.out.println("猫吃鱼");
    }

    //特有方法
    public void catchMouse(){
        System.out.println("猫抓老鼠");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Dog dog = new Dog();
        method(dog);

        Cat cat = new Cat();
        method(cat);

        /*Pig pig = new Pig();
        method(pig);*/
    }

    public static void method(Dog dog){
        dog.eat();
    }

    public static void method(Cat cat){
        cat.eat();
    }
}

```

```java
public class Test02 {
    public static void main(String[] args) {
        Dog dog = new Dog();
        method(dog);
        Cat cat = new Cat();
        method(cat);
    }

    /**
     * 形参是父类类型,就可以接收任意它的子类对象
     * 传递哪个子类对象,就接收哪个子类对象
     * 就指向哪个子类对象,就会动态的调用哪个子类对象重写的方法
     * @param animal
     */
    public static void method(Animal animal){//Animal animal = dog;Animal animal = cat
        animal.eat();
    }
}

```

## 5.多态中的转型

### 5.1向上转型_自动类型转换

```java
父类引用指向子类对象
```

### 5.2向下转型_强转

```java
将父类类型转成子类类型
```

```java
public class Test03 {
    public static void main(String[] args) {
        Animal animal = new Dog();
        animal.eat();
        //向下转型
        Dog dog = (Dog) animal;
        dog.lookHome();
    }
}

```

## 6.转型可能会出现的问题

```java
1.转型时容易出现的异常:ClassCastException ->类型转换异常
2.原因:转型的过程中等号左右两边类型不一致
3.解决:强转之前先判断类型
  a.关键字:  instanceof
  b.使用:  对象名 instanceof 类型 -> 判断关键字前面的对象是否属于关键字后面的类型
  c.判断类型新特性
    对象名 instanceof 类型 对象名 -> 自动强转
```

```java
public class Test04 {
    public static void main(String[] args) {
        Dog dog = new Dog();
        method(dog);

        Cat cat = new Cat();
        method(cat);
    }
    public static void method(Animal animal){
        animal.eat();
       /* if (animal instanceof Dog){
            Dog dog = (Dog) animal;
            dog.lookHome();
        }

        if (animal instanceof Cat){
            Cat cat = (Cat) animal;
            cat.catchMouse();
        }*/

        //新特性
        if (animal instanceof Dog dog){
            dog.lookHome();
        }
        if (animal instanceof Cat cat){
            cat.catchMouse();
        }

    }
}
```

## 7.综合练习_作业

```java
定义笔记本类，具备开机，关机和使用USB设备的功能。具体是什么USB设备，笔记本并不关心，只要符合USB规格的设备都可以。鼠标和键盘要想能在电脑上使用，那么鼠标和键盘也必须遵守USB规范，不然鼠标和键盘生产出来无法使用;
进行描述笔记本类，实现笔记本使用USB鼠标、USB键盘

- USB接口，包含开启功能、关闭功能
- 笔记本类，包含运行功能、关机功能、使用USB设备功能
- 鼠标类，要符合USB接口
- 键盘类，要符合USB接口
```

```java

```

```java

```

```java

```

```java

```

```java

```

# 第二章.代码块

### 1.1构造代码块

```java
1.格式:
  {
    代码
  }
2.特点:
 优先于构造方法执行,构造方法执行几次,构造代码块就执行几次
```

```java
public class Person {
    public Person(){
        System.out.println("构造方法");
    }

    //构造代码块
    {
        System.out.println("构造代码块");
    }
}

```

```java

public class Test01 {
    public static void main(String[] args) {
        Person p1 = new Person();
        Person p2 = new Person();
    }
}

```

### 1.2静态代码块

```java
1.格式:
  static{
      代码
  }
2.特点:
  优先于构造代码块和构造方法执行,只执行一次
```

```java
public class Person {
    public Person(){
        System.out.println("构造方法");
    }

    //构造代码块
    {
        System.out.println("构造代码块");
    }

    //静态代码块
    static{
        System.out.println("静态代码块");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Person p1 = new Person();
        Person p2 = new Person();
    }
}

```

> 执行顺序:
>
>   静态代码块>构造代码块>构造方法

### 1.3.静态代码块使用场景

```java
如果有一些数据需要最先初始化,而且是需要初始化一次,就可以放到静态代码块中
```

> 课程配图（未随笔记提交）

# 第三章.内部类

```java
1.什么时候使用内部类:
  当一个事物的内部,还有一个部分需要完整的结构进行描述,而这个内部的完整的结构又只为外部事物提供服务,那么整个内部的完整结构最好使用内部类
  比如:人类都有心脏,人类本身需要用属性,行为去描述,那么人类内部的心脏也需要心脏特殊的属性和行为来描述,此时心脏就可以定义成内部类,人类中的一个内部类

  当一个类内部的成员也需要用属性和行为描述时,就可以定义成内部类了

2.在java中允许一个类的定义位于另外一个类内部,前者就称之为内部类,后者称之为外部类
  class A{
      class B{

      }
  }
  A就是B的外部类
  B就是A的内部类

3.分类:
  成员内部类(静态,非静态)
  局部内部类
  匿名内部类(重点) -> 匿名内部类属于局部内部类一种
```

## 1 静态成员内部类

```java
1.格式:直接在定义内部类的时候加上static关键字即可
  public class A{
      static class B{

      }
  }

2.注意:
  a.内部类中可以定义属性,方法,构造等
  b.静态内部类可以被final或者abstract修饰
    给final修饰,不能被继承
    被abstract修饰,不能new
  c.静态内部类不能调用外部的非静态成员
  d.内部类还可以被四种权限修饰符修饰

3.调用静态内部类成员:
  外部类.内部类 对象名 = new 外部类.内部类()
```

```java
public class Person {
    public void eat(){
        System.out.println("吃吃吃");
        //beat();
        //new Heart().beat();
    }

    //静态成员内部类
    static class Heart{
        public void beat(){
            System.out.println("心脏跳动");
        }
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Person.Heart heart = new Person.Heart();
        heart.beat();
    }
}
```

## 2 非静态成员内部类

```java
1.格式:
  public class 类名{
      class 类名{

      }
  }

2.注意:
  a.内部类中可以定义属性,方法,构造等
  b.静态内部类可以被final或者abstract修饰
    给final修饰,不能被继承
    被abstract修饰,不能new
  c.静态内部类不能调用外部的非静态成员
  d.内部类还可以被四种权限修饰符修饰

3.调用非静态成员内部类
  外部类.内部类 对象名 = new 外部类().new 内部类()
```

```java
public class Person {
    public void eat(){
        System.out.println("吃吃吃");
        //beat();
        //new Heart().beat();
    }

    //非静态成员内部类
    class Heart{
        public void beat(){
            System.out.println("心脏跳动");
        }
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Person.Heart heart = new Person().new Heart();
        heart.beat();
    }
}
```

> 外部类的成员变量和内部类的成员变量以及内部类的局部变量重名时,怎么区分?
>
> ```java
> public class Student {
>        String name = "张三";
>        class Heart{
>            String name = "李四";
>            public void beat(){
>                String name = "王五";
>                System.out.println(name);//王五
>                System.out.println(this.name);//李四
>                System.out.println(Student.this.name);//张三
>            }
>        }
>    }
>
> ```

## 3.局部内部类

### 3.1.局部内部类基本操作

```java
1.可以定义在方法中,代码块中,构造方法中
```

```java
public class Person {
    public void eat(){
        //局部内部类
        class Heart{
            public void beat(){
                System.out.println("心脏跳动");
            }
        }
        new Heart().beat();
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Person person = new Person();
        person.eat();
    }
}
```

### 3.2.局部内部类实际操作

#### 3.2.1.接口类型作为方法参数传递和返回

> 1.接口作为方法参数传递,传递的是实现类对象
>
> 2.接口作为方法返回值返回,返回的是实现类对象

```java
public interface USB {
    void open();
}
```

```java
public class Mouse implements USB{
    @Override
    public void open() {
        System.out.println("鼠标打开");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Mouse mouse = new Mouse();
        method(mouse);
        System.out.println("====================");
        /*
            method02()接收的是返回来的mouse对象
            用USB类型的对象接收了属于多态
         */
        USB usb = method02();
        usb.open();
    }
    /**
     * 接口作为方法的参数传递
     * 参数展开: USB usb = mouse
     */
    public static void method(USB usb){
        usb.open();
    }

    /**
     * 接口作为方法的返回值返回
     */
    public static USB method02(){
        Mouse mouse = new Mouse();
        return mouse;
    }
}
```

#### 3.2.2.抽象类作为方法参数和返回值

> 1.抽象类作为方法参数传递,传递的是子类对象
>
> 2.抽象类作为方法返回值返回,返回的是子类对象

```java
public abstract class Animal {
    public abstract void eat();
}
```

```java
public class Dog extends Animal{
    @Override
    public void eat() {
        System.out.println("狗吃屎");
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Dog dog = new Dog();
        method01(dog);
        System.out.println("==================");
        Animal animal = method02();
        animal.eat();
    }

    public static void method01(Animal animal){
        animal.eat();
    }

    public static Animal method02(){
        Dog dog = new Dog();
        return dog;
    }
}
```

#### 3.2.3.普通类做方法参数和返回值

> 1.普通类做方法参数传递,传递的是对象
>
> 2.普通类做方法返回值返回,返回的是对象

```java
public class Person {
    public void eat(){
        System.out.println("吃吃吃");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Person person = new Person();
        method01(person);
        System.out.println("=================");
        Person person1 = method02();
        person1.eat();
    }
    public static void method01(Person person){
        person.eat();
    }

    public static Person method02(){
        Person person = new Person();
        return person;
    }
}
```

#### 2.2.4.局部内部类实际操作

```java
public interface USB {
    void open();
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        USB usb = method();
        usb.open();
    }

    public static USB method(){
        /**
         * 局部内部类
         * 当实现类使用了
         */
        class Mouse implements USB{
            @Override
            public void open() {
                System.out.println("鼠标打开");
            }
        }



        return mouse;
    }
}

```

> 1.以上代码:明确将局部内部类定义了出来,当成了实现类使用,我们可以理解为这种叫做有名字的局部内部类
>
> 2.匿名内部类:说白了就是没有明确定义出来的局部内部类
>
>    我们只管new对象,jvm在编译的时候会根据我们new的对象自动将这个局部内部类生成
>
> 3.所以:我们只需要学会如何创建匿名内部类的对象即可,反正jvm会根据我们new的对象自动生成这个匿名内部类

## 4.局部内部类之匿名内部类

```java
1.格式1:利用创建匿名对象的方式来创建匿名内部类的对象
  new 接口/抽象类(){
      重写方法
  }.重写的方法();

2.方式2:利用创建有名对象的方式来创建匿名内部类的对象
  接口名/抽象类名 对象名 = new 接口/抽象类(){
      重写方法
  }

  对象名.重写的方法();
```

```

```
