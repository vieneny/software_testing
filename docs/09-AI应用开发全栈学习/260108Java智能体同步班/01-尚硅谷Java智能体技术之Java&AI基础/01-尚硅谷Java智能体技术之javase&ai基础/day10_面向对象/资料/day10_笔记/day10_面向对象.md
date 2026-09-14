# day10_面向对象

```java
课前回顾:
 1.抽象类:public abstract class 类名{}
 2.抽象方法: 修饰符 abstract 返回值类型 方法名(形参);
 3.怎么实现:
   a.子类继承抽象父类
   b.重写抽象方法
   c.创建子类对象,调用重写方法
 4.接口:一类事物的标准
   a.定义:public interface 接口名{}
   b.实现:
     public class 类名 implements 接口名{}
 5.接口中成员:抽象方法
   public abstract 返回值类型 方法名(形参) -> 即使不写public abstract默认也有
 6.接口中成员:默认方法
   public default 返回值类型 方法名(形参){
       方法体
       return 结果
   }
 7.接口中成员:静态方法
   public static 返回值类型 方法名(形参){
       方法体
       return 结果
   }
 8.成员变量
   public static final 数据类型 变量名 = 值
   即使不写public static final默认也有
 9.私有方法:将public 改成 private
 10.接口的特点:
    a.接口可以多继承
    b.接口可以多实现
    c.一个子类继承一个父类的同时可以实现一个或者多个接口
 11.final关键字:
   a.修饰类:不能被继承
   b.修饰方法:不能被重写
   c.修饰成员变量:不能二次赋值
   d.修饰局部变量:不能二次赋值
   e.修饰对象:地址值不能改变,但是对象中的属性值可以改变

 12.权限修饰符:  public protected 默认 private


今日重点:
  1.知道多态的前提
  2.分清楚什么代码格式是多态
  3.知道多态的好处
  4.会向下转型
  5.知道如何判断类型
  6.会静态代码块
  7.会写匿名内部类
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
1.面向对象三大特征:封装    继承    多态
2.多态怎么学:
  a.不要从字面意思上来学
  b.知道形成多态的前提是啥
  c.多态是个什么形式
  d.多态有啥好处
```

## 1.多态的介绍

```java
1.概述:一种事物有不同的形态
2.前提:
  a.必须有子父类继承关系或者接口实现关系
  b.必须有方法的重写(没有方法的重写,多态没有意义)
  c.父类引用指向子类对象 ->  Fu fu = new Zi()

3.多态的弊端:不能直接调用子类特有成员
```

## 2.多态的基本使用

```java
public class Animal {
    public void eat(){
        System.out.println("吃吃吃");
    }
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
    public void catchMouse() {
        System.out.println("猫抓老鼠");
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        //多态形式的创建对象
        Animal animal1 = new Dog();
        animal1.eat();
        //animal1.lookHome();多态前提下,无法调用子类特有内容

        Animal animal2 = new Cat();
        animal2.eat();
    }
}

```

> ```JAVA
> public interface USB {
>     void open();
>     void close();
> }
>
> ```
>
> ```JAVA
> public class Mouse implements USB{
>     @Override
>     public void open() {
>         System.out.println("打开鼠标");
>     }
>
>     @Override
>     public void close() {
>         System.out.println("关闭鼠标");
>     }
> }
>
> ```
>
> ```java
> public class KeyBoard implements  USB{
>     @Override
>     public void open() {
>         System.out.println("键盘打开");
>     }
>
>     @Override
>     public void close() {
>         System.out.println("键盘关闭");
>     }
> }
>
> ```
>
> ```java
> public class Test01 {
>     public static void main(String[] args) {
>        USB usb = new Mouse();
>        usb.open();
>        usb.close();
>
>        USB usb2 = new KeyBoard();
>        usb2.open();
>        usb2.close();
>     }
> }
> ```

## 3.多态的条件下成员的访问特点

### 3.1成员变量

```java
看等号左边是谁,先调用谁中的成员变量
```

```java
public class Fu {
    int num =100;
}

```

```java
public class Zi extends Fu{
    int num = 10;
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Fu fu = new Zi();
        System.out.println(fu.num);//父类中的num
    }
}

```

### 3.2成员方法

```java
看new的是谁,就先调用谁中的方法
```

```java
public class Fu {
    int num =100;
    public void show(){
        System.out.println("Fu");
    }
}
```

```java
public class Zi extends Fu{
    int num = 10;
    @Override
    public void show(){
        System.out.println("Zi");
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Fu fu = new Zi();
        System.out.println(fu.num);//父类中的num
        fu.show();
    }
}
```

## 4.多态的好处(为什么学多态)

```java
1.原始方式:
  a.好处:既能调用重写的,还能调用继承的,还能调用子类特有的
  b.弊端:扩展性差
2.多态方式:
  a.好处:扩展性强
  b.弊端:不能直接调用子类特有功能
```

```java
public class Animal {
    public void eat(){
        System.out.println("吃吃吃");
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
    public void catchMouse() {
        System.out.println("猫抓老鼠");
    }
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
public class Test01 {
    public static void main(String[] args) {
        Dog dog = new Dog();
        method(dog);

        Cat cat = new Cat();
        method(cat);

/*        Pig pig = new Pig();
        method(pig);

        Duck duck = new Duck();
        method(duck);*/
    }

    public static void method(Dog dog) {
        dog.eat();
    }

    public static void method(Cat cat){
        cat.eat();
    }

/*
    public static void method(Pig pig){
        pig.eat();
    }

    public static void method(Duck duck){
        duck.eat();
    }
*/
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
     * Animal animal = dog
     * Animal animal = cat
     * @param animal
     *
     * 形参搞一个父类类型,就可以动态接收任意它的子类对象
     * 接收哪个子类对象,就会指向哪个子类对象
     * 就会动态的调用哪个子类对象重写的方法
     */
    public static void method(Animal animal){
        animal.eat();
    }
}
```

## 5.多态中的转型

### 5.1向上转型_自动类型转换

```java
父类引用指向子类对象 -> 默认 -> Fu fu = new Zi()
```

### 5.2向下转型_强转

```java
1.将父类类型转成子类类型
  Fu fu = new Zi()   -> 好比是 double b = 10
  Zi zi = (Zi)fu     -> 好比是 int a = (int)b
2.作用:
  可以调用子类特有功能了
```

```java
public class Test03 {
    public static void main(String[] args) {
        Dog dog = new Dog();
        method(dog);
    }

    private static void method(Animal animal) {
        animal.eat();
        //向下转型
        Dog dog = (Dog) animal;
        dog.lookHome();
    }
}

```

## 6.转型可能会出现的问题

```java
1.ClassClassException:类型转换异常
2.出现原因:
  转型的时候,等号左右两边类型不一致
3.解决:强转之前判断类型
  a.关键字:instanceof
  b.用法: 对象名 instanceof 类型 -> 判断关键字前面的对象是否属于关键字后面的类型
  c.判断类型新特性(新语法) : 对象名 instanceof 类型 对象名    -> 隐含了一个强转
```

```java
public class Test03 {
    public static void main(String[] args) {
        Dog dog = new Dog();
        method(dog);
        System.out.println("==============");
        Cat cat = new Cat();
        method(cat);
    }

    private static void method(Animal animal) {
        animal.eat();
        /*if (animal instanceof Dog){
            //向下转型
            Dog dog = (Dog) animal;
            dog.lookHome();
        }else if (animal instanceof Cat){
            Cat cat = (Cat) animal;
            cat.catchMouse();
        }else{
            System.out.println("没有这样的子类");
        }*/
        if (animal instanceof Dog dog){
            dog.lookHome();
        }else if (animal instanceof Cat cat){
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

> 课程配图（未随笔记提交）

# 第二章.代码块

### 1.1构造代码块

```java
1.格式:
  {
      代码
  }
2.执行特点:
  优先于构造方法执行,而且每new一次,构造代码块就执行一次
```

```java
public class Person {
    public Person() {
        System.out.println("无参构造方法");
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
        Person person = new Person();
        Person person1 = new Person();
    }
}
```

### 1.2静态代码块

```java
1.格式:
  static{
      代码
  }
2.执行特点:
  优先于构造代码块和构造方法执行,只执行一次
```

```java
public class Person {
    public Person() {
        System.out.println("无参构造方法");
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
        Person person = new Person();
        Person person1 = new Person();
    }
}
```

> 执行顺序:
>
>    静态代码块>构造代码块>构造方法

### 1.3.静态代码块使用场景

```java
如果说将来有一些数据只需要初始化一次,而且需要先初始化,这些数据就可以放到静态代码块中
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
        System.out.println("吃饭");
        new Heart().jump();
    }

    //静态成员内部类
    static class Heart{
        public void jump(){
            System.out.println("心脏在咣咣咣跳");

        }
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Person.Heart heart = new Person.Heart();
        heart.jump();
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
        System.out.println("吃饭");
        //new Heart().jump();
    }

    /*//静态成员内部类
    static class Heart{
        public void jump(){
            System.out.println("心脏在咣咣咣跳");

        }
    }*/

    //非静态成员内部类
    class Heart{
        public void jump(){
            System.out.println("心脏在咣咣咣跳");
        }
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
/*        Person.Heart heart = new Person.Heart();
        heart.jump();*/

        Person.Heart heart = new Person().new Heart();
        heart.jump();
    }
}

```

> 外部类成员变量和内部类成员变量以及内部类的局部变量重名时,如何区分?
>
> ```java
> public class Student {
>     String name = "张三";
>     class Inner{
>         String name = "李四";
>         public void display(){
>             String name = "王五";
>             System.out.println(name);//王五
>             System.out.println(this.name);//李四
>             System.out.println(Student.this.name);//张三
>         }
>     }
> }
>
> ```
>
> ```java
> public class Test02 {
>     public static void main(String[] args) {
>         Student.Inner inner = new Student().new Inner();
>         inner.display();
>     }
> }
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
            public void jump(){
                System.out.println("跳");
            }
        }

        new Heart().jump();
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

> 1.接口作为形参使用:需要传递实现类对象
>
> 2.接口作为返回值使用:返回的是实现类对象

```java
public interface USB {
    void open();
}
```

```java
public class Mouse implements USB{
    @Override
    public void open() {
        System.out.println("打开鼠标");
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Mouse mouse = new Mouse();
        method(mouse);
        USB usb = method01();
        usb.open();
    }

    /**
     * 接口做为方法的参数传递
     */
    public static void method(USB usb){
        usb.open();
    }

    /**
     * 接口做为方法返回值
     */
    public static USB method01(){
        Mouse mouse = new Mouse();
        return mouse;
    }
}

```

#### 3.2.2.抽象类作为方法参数和返回值

> 1.抽象类作为方法形参:传递的是子类对象
>
> 2.抽象类作为方法返回值返回:返回的是子类对象

```java
public abstract class Animal {
    public abstract void eat();
}

```

```java
public class Dog extends Animal{
    @Override
    public void eat() {
        System.out.println("狗吃骨头");
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        Dog dog = new Dog();
        method01(dog);
        Animal animal = method02();
        animal.eat();
    }

    /**
     * 抽象类作为方法的形参
     */
    public static void method01(Animal animal){
        animal.eat();
    }

    /**
     * 抽象类作为方法的返回值
     */
    public static Animal method02(){
        Dog dog = new Dog();
        return dog;
    }
}

```

#### 3.2.3.普通类做方法参数和返回值

> 1.普通类作为方法形参:传递对象
>
> 2.普通类作为方法返回值:返回的也是对象

```java
public class Person {
    public void eat(){
        System.out.println("人要吃饭");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Person person = new Person();
        method01( person);

        Person person1 = method02();
        person1.eat();
    }
    /**
     * 普通类作为方法形参
     */
    public static void method01(Person person){
        person.eat();
    }

    /**
     * 普通类做为方法返回值
     */
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
        class Mouse implements USB{

            @Override
            public void open() {
                System.out.println("打开鼠标");
            }
        }

        Mouse mouse = new Mouse();
        return mouse;
    }
}

```

## 4.局部内部类之匿名内部类

```java
1.通过局部内部类的实际使用我们可以看出
  a.我们明确的定义了一个局部内部类,当了接口的实现类使用,这种明确的定义出来的局部内部类,我们可以叫做"有名的局部内部类"
2.匿名内部类:
  a.概述:说白了没有明确将这个局部内部类定义出来,也就是说这个局部内部类没有名字(定义这个事儿不用我们管,我们只管创建对象)
  b.我们不管定义局部内部类这个事儿了,我们只管new这个局部内部类的对象即可
3.匿名内部类怎么学:
  我们只需要学如何new这个匿名内部类的对象即可,jvm会根据我们new的对象,自动生成一个局部内部类
4.如何new匿名内部类的对象:
  a.匿名对象方式new匿名内部类的对象:
    new 接口名/抽象类名(){
        重写抽象方法
    }.重写的方法名();   -> 类似于:new Mouse().open()

  b.有名对象方式new匿名内部类的对象:
    接口名/抽象类名 对象名 =  new 接口名/抽象类名(){
        重写抽象方法
    }
    对象名.重写的方法名()
```

```java
public interface USB {
    void open();
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        /*
            a.匿名对象方式new匿名内部类的对象:
              new 接口名/抽象类名(){
                  重写抽象方法
              }.重写的方法名();   -> 类似于:new Mouse().open()
         */
        new USB(){
            @Override
            public void open() {
                System.out.println("usb打开");
            }
        }.open();

        System.out.println("=============================");

        /*
          b.有名对象方式new匿名内部类的对象:
            接口名/抽象类名 对象名 =  new 接口名/抽象类名(){
                重写抽象方法
            }
            对象名.重写的方法名()
         */
        USB usb = new USB() {
            @Override
            public void open() {
                System.out.println("usb打开了");
            }
        };
        usb.open();
    }
}
```

### 4.1.匿名内部类复杂用法_当参数传递

```java
public interface USB {
    void open();
}

```

```java
public class Test01 {
    public static void main(String[] args) {
       method(new USB() {
           @Override
           public void open() {
               System.out.println("usb打开了");
           }
       });
    }

    public static void method(USB usb){
        usb.open();
    }
}

```

 > 课程配图（未随笔记提交）

### 4.2.匿名内部类复杂用法_当返回值返回

```java
public interface USB {
    void open();
}
```

```java
public class Test02 {
    public static void main(String[] args) {
        USB usb = method();
        usb.open();
    }

    public static USB method(){
        return new USB() {
            @Override
            public void open() {
                System.out.println("打开USB");
            }
        };
    }
}
```

> 课程配图（未随笔记提交）
