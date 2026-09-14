# day10_课后练习

# 代码阅读分析题

## 第1题

考核知识点：属性与多态无关

```java
package com.atguigu.test01;

public class Test01 {
    public static void main(String[] args) {
        A a = new B();
        System.out.println(a.num);
        System.out.println(((B)a).num);
        System.out.println(((A)((B)a)).num);
        System.out.println("-------------------");
        B b = new B();
        System.out.println(b.num);
        System.out.println(((A)b).num);
        System.out.println(((B)((A)b)).num);
    }
}
class A{
    int num = 1;
}
class B extends A{
    int num = 2;
}
```

```java
/*
 * 多态性现象：编译时类型与运行时类型不一致
 * 但是多态性是针对方法来说，方法有动态绑定一说。
 * 属性没有多态性。属性都是按照编译时类型处理的。
 */
public class Test01 {
    public static void main(String[] args) {
        A a = new B();// 多态
        System.out.println(a.num);//a编译时类型就是A  1
        System.out.println(((B)a).num);//编译后，因为a被强制成B类，是B类型  2
        System.out.println(((A)((B)a)).num);//编译后，a转成B又转成A，是A类型   1
        System.out.println("-------------------");
        B b = new B();
        System.out.println(b.num);//b编译时类型就是B   2
        System.out.println(((A)b).num);//b被强制升级为A类型，按A类型处理， 1
        System.out.println(((B)((A)b)).num);//b先转A又转B，最终是B类型  2
    }
}
class A{
    int num = 1;
}
class B extends A{
    int num = 2;
}
```

## 第2题

考核知识点：多态，重写，实例初始化过程

```java
package com.atguigu.test03;

public class Test03 {
    public static void main(String[] args) {
        /*
        1.new 的是父类对象,走父类构造
        直接调用了父类的method
        输出 base:100
        */
        Base b1 = new Base();
        /*
        2.多态new对象  new了子类对象 执行子类无参时先走父类无参构造
        此时父类中无参构造调用的method为重写后的method,然后传了一个100
        所以先输出 sub:100

        然后再执行super.method(70)调用父类method,并传递70
        所以输出 base:70
        */
        Base b2 = new Sub();
    }
}

class Base {
    Base() {
        method(100);
    }

    public void method(int i) {
        System.out.println("base : " + i);
    }
}

class Sub extends Base {
    Sub() {
        super.method(70);
    }

    public void method(int j) {
        System.out.println("sub : " + j);
    }
}
```

```java
package com.atguigu.test03;
/*
 * 1、Base b1 = new Base();
 * 父类的实例初始化，和子类无关
 *
 * <init>(){
 * 		method(100);
 * 			System.out.println("base : " + i);  base:100
 * }
 *
 * 2、Base b2 = new Sub();
 * （1） 父类的实例初始化
 *
 * <init>(){
 * 		method(100);//执行了子类重写的method()
 * 			System.out.println("sub : " + j);  sub:100
 * }
 *
 * （2）子类的实例初始化
 * <init>(){
 * 		super.method(70);
 * 			System.out.println("base : " + i);	base:70
 * }
 */
public class Test03 {
    public static void main(String[] args) {
        Base b1 = new Base();
        Base b2 = new Sub();
    }
}

class Base {
    Base() {
        method(100);
    }

    public void method(int i) {
        System.out.println("base : " + i);
    }
}

class Sub extends Base {
    Sub() {
        super.method(70);
    }

    public void method(int j) {
        System.out.println("sub : " + j);
    }
}
```



## 第3题

考核知识点：属性与多态无关

```java
public class Test06 {
    public static void main(String[] args) {
        Base b = new Sub();
        System.out.println(b.x);
    }
}
class Base{
    int x = 1;
}
class Sub extends Base{
    int x = 2;
}
```

```java
package com.atguigu.test06;

/*
 * 属性没有多态性，只看编译时类型
 */
public class Test06 {
    public static void main(String[] args) {
        Base b = new Sub();
        System.out.println(b.x);
    }
}
class Base{
    int x = 1;
}
class Sub extends Base{
    int x = 2;
}
```

## 第4题

知识点：抽象类

案例：

​	1、声明抽象父类Person，包含抽象方法public abstract void eat();

​	2、声明子类中国人Chinese，重写抽象方法，打印用筷子吃饭

​	3、声明子类美国人American，重写抽象方法，打印用刀叉吃饭

​	4、声明子类印度人Indian，重写抽象方法，打印用手抓饭

​	5、声明测试类Test11，创建Person数组，存储各国人对象，并遍历数组，调用eat()方法

```java
package com.atguigu.test11;

public class Test11 {

    public static void main(String[] args) {
        Person[] all = new Person[3];
        all[0] = new Chinese();
        all[1] = new American();
        all[2] = new Indian();

        for (int i = 0; i < all.length; i++) {
            all[i].eat();
        }
    }

}
abstract class Person{
    public abstract void eat();
}
class Chinese extends Person{

    @Override
    public void eat() {
        System.out.println("中国人用筷子吃饭");
    }

}
class American extends Person{

    @Override
    public void eat() {
        System.out.println("美国人用刀叉吃饭");
    }

}
class Indian extends Person{

    @Override
    public void eat() {
        System.out.println("印度人用手抓饭");
    }

}
```



## 题目一

```
请使用代码描述:
   奥迪车(Audi)都具有跑的功能，但是智能奥迪车(SmartAudi)除了具有跑的功能外，还具有自动泊车(automaticParking)和无人驾驶(automaticDrive)的功能！

   要求:使用多态形式创建对象
```

### 训练目标

```
多态,向下转型
```

### 训练提示

```
利用多态方式创建对象,然后向下转型调用子类特有方法
```

### 参考方案

```
1.定义奥迪车为父类,定义跑的方法
2.定义只能奥迪车,继承父类,定义两个自动泊车和无人驾驶的特有方法
3.利用多态创建对象,利用向下转型调用特有方法
```

### 操作步骤

```
1.定义奥迪车类(Audi),定义一个跑的方法(run)
2.定义一个智能奥迪车类(SmartAudi),继承父类,然后定义两个方法
  自动泊车方法(automaticParking)无人驾驶的方法         (automaticDrive)
3.定义一个测试类,使用多态形式创建对象,调用从父类继承过来的run方法
  向下转型之后,调用子类特有的自动泊车方法和无人驾驶方法
```

### 参考答案

```java
//父类
public class Audi {
    public void run(){
        System.out.println("奥迪车在跑");
    }
}
```

```java
//子类
public class SmartAudi extends Audi{
    public void automaticParking() {
        System.out.println("智能奥迪车在自动泊车");
    }

    public void automaticDrive() {
        System.out.println("智能奥迪车在自动驾驶");
    }
}
```

```java
//测试类
public class Test {
    public static void main(String[] args) {
        //使用多态形式创建对象
        Audi audi = new SmartAudi();
        //调用从父类中继承过来的方法
        audi.run();
        //向下转型,调用子类特有的方法
        SmartAudi smartAudi = (SmartAudi)audi;
        smartAudi.automaticParking();
        smartAudi.automaticDrive();
    }
}
```

## 题目二

```
 白色4条腿的北极熊(Bear)会吃(吃蜂蜜)和抓鱼(catchFish)
 黑色4条腿的大熊猫(Panda)会吃(吃竹子)和爬树(climbTree)
 要求: 把北极熊和大熊猫的共性提取动物类(Animal)中,使用抽象类
```

### 训练目标

```
继承,抽象,方法的重写
```

### 训练提示

```
1.将两种动物共性抽取出来,形成动物类,然后Bear和Panda继承动物类
2.重写共性方法,并定义特有方法
```

### 参考方案

```
1.定义一个动物类,里面有颜色和腿的条数,两个动物的共性就是吃的方法,所以可以把共性的吃的方法抽取出来,由于这个吃的方法内容无法确定,所以定义成抽象方法
2.定义出来的Bear类和Panda类都要继承动物类,重写吃的方法
3.定义北极熊和大熊猫的特有方法
4.在测试类中创建两个动物的对象,为属性赋值,并调用方法
```

### 操作步骤

```
1.定义一个Animal类,定义两个私有属性(颜色:color,个数:numOfLegs).对应的构造以及get/set方法
2.在Animal中定义一个抽象方法eat()
3.定义子类Bear(北极熊) 继承Animal类,重写父类中的抽象方法eat(),方法体输出 "白色4腿的北极熊在吃蜂蜜"
  定义特有方法catchFish(),方法体输出"白色4腿的北极熊在抓鱼"
4.定义子类Panda(熊猫)继承Animal类,重写父类中的抽象方法eat(),方法体输出 "黑色4条腿的大熊猫在吃竹子"
  定义特有方法climbTree(),方法体输出"黑色4条腿的大熊猫在爬树"
5.定义测试类,创建北极熊对象,为属性赋值,调用重写的方法以及特有方法
  创建大熊猫对象,为属性赋值,调用重写的方法以及特有方法
```

### 参考答案

```java
//动物类
public abstract class Animal {
    //动物颜色
    private String color;
    //动物腿的个数
    private int numOfLegs;

    //提供带参构造和setXxx和getXxx方法
    public Animal() {
        super();
    }
    public Animal(String color, int numOfLegs) {
        super();
        this.color = color;
        this.numOfLegs = numOfLegs;
    }
    public String getColor() {
        return color;
    }
    public void setColor(String color) {
        this.color = color;
    }
    public int getNumOfLegs() {
        return numOfLegs;
    }
    public void setNumOfLegs(int numOfLegs) {
        this.numOfLegs = numOfLegs;
    }

    //定义吃东西的抽象方法
    public abstract void eat();

}
```

```java
//北极熊类
public class Bear extends Animal {

    public Bear() {
        super();
    }

    public Bear(String color, int numOfLegs) {
        super(color, numOfLegs);
    }

    public void eat() {
        System.out.println(getColor() + getNumOfLegs() + "腿的北极熊在吃蜂蜜");
    }

    public void catchFish() {
        System.out.println(getColor() + getNumOfLegs() + "腿的北极熊在抓鱼");
    }
}
```

```java
//大熊猫类
public class Panda extends Animal {

    public Panda() {
        super();
    }

    public Panda(String color, int numOfLegs) {
        super(color, numOfLegs);
    }

    public void eat() {
        System.out.println(getColor() + getNumOfLegs() + "条腿的大熊猫在吃竹子");
    }

    public void climbTree() {
        System.out.println(getColor() + getNumOfLegs() + "条腿的大熊猫在爬树");
    }
}
```

```java
//测试类
public class Test {
    public static void main(String[] args) {
        //1. 创建北极熊对象 b,颜色赋值为白色,腿的个数赋值为4
        Bear b = new Bear("白色", 4);
        //2. 调用北极熊对象b的吃方法
        b.eat();
        //3.调用北极熊对象b的抓鱼方法
        b.catchFish();
        //4. 创建大熊猫对象 p,颜色赋值为黑色,腿的个数赋值为4
        Panda p = new Panda("黑色", 4);
        //5. 调用大熊猫对象p的吃方法
        p.eat();
        //6. 调用大熊猫对象p的爬树方法
        p.climbTree();
    }
}
```

###