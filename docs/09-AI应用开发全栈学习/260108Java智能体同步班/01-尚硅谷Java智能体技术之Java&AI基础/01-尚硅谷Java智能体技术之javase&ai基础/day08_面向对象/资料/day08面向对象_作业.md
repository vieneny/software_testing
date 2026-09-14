#                                 day08面向对象

# 简答题:

### 1.面向对象和面向过程的区别?

```
   面向过程就是分析出解决问题所需要的步骤，然后用函数把这些步骤一步一步实现，使用的时候一个一个依次调用就可以了。

   面向对象是把构成问题事务分解成各个对象，建立对象的目的不是为了完成一个步骤，而是为了描叙某个事物在整个解决问题的步骤中的行为。
```

### 2.继承的特点?

```
a.只支持单继承
b.不能多继承
c.支持单层继承
```



# 编程题:

## 题目一

```
每一款手机都有自己的品牌和价格,原来的手机只能打电话,发短信;现在的新手机,在打电话和发短信的基础上还能玩儿游戏,请设计程序,完成手机的升级!
```

### 训练目标

```
继承
```

### 训练提示

```
新手机在老手机基本的功能上添加新功能,新功能就是新手机特有的内容
```

### 参考方案

```
1.定义新手机类 extends 老手机类
2.在新手机中定义特有的方法
```

### 操作步骤

```
1.定一个OldPhone类,定义两个私有属性brand和price,定义空参和有参构造方法,get/set方法
2.在OldPhone类中,定义一个打电话的方法,传递姓名的参数,方法体内输出给谁打电话
3.在OldPhone类中,定义一个发短信的方法,直接输出"发短信"
4.定一个子类NewPhone,继承OldPhone类,在子类中定义玩游戏的特有方法,直接输出内容"玩游戏"
5.定义测试类,创建NewPhone类对象,调用set方法为属性赋值,调用get方法获取属性值
6.调用从父类中继承过来的方法以及自己特有的方法.
```

### 参考答案

```java
//父类-->OldPhone
public class OldPhone {
    private String brank;
    private double price;

    public OldPhone() {
    }

    public OldPhone(String brank, double price) {
        this.brank = brank;
        this.price = price;
    }

    public String getBrank() {
        return brank;
    }

    public void setBrank(String brank) {
        this.brank = brank;
    }

    public double getPrice() {
        return price;
    }

    public void setPrice(double price) {
        this.price = price;
    }

    //打电话
    public void call(String name){
        System.out.println("给"+name+"打电话!");
    }

    //发短信
    public void message(){
        System.out.println("发短信!");
    }
}

```

```java
//子类->NewPhone
public class NewPhone extends OldPhone{
    //特有内容
    public void playGame(){
        System.out.println("玩儿游戏");
    }
}
```

```java
//测试类
public class Test {
    public static void main(String[] args) {
        //创建NewPhone类对象
        NewPhone newPhone = new NewPhone();
        //调用set方法为属性赋值
        newPhone.setBrank("苹果");
        newPhone.setPrice(6399);
        //调用get方法获取属性值
        System.out.println("新手机的品牌为:"+newPhone.getBrank()+",新手机的价格为:"+newPhone.getPrice());
        //调用从父类中继承过来的方法
        newPhone.call("小黑");
        newPhone.message();
        //调用自己的特有方法
        newPhone.playGame();
    }
}
```

### 视频讲解

```
另附avi格式视频.
```

## 题目二

```
每一款手机都有自己的品牌和价格,原来的手机只能打电话,发短信,来电显示只能显示手机号;现在的新手机针对于来电显示做了功能的升级,还能显示头像,还能显示归属地,请设计程序,完成手机的升级!
```

### 训练目标

```
继承,重写
```

### 训练提示

```
新手机在老手机的基本功能基础上,针对老手机的某个功能进行重新实现
```

### 参考方案

```
定义一个老手机类,包含品牌和价格两个属性,对应的构造,get/set方法,还有打电话,和发短信的方法,来电显示的方法
定义一个新手机,继承老手机类,重写来电显示方法进行升级
最后在测试类中为属性赋值,调用继承过来的方法以及来电显示方法
```

### 操作步骤

```
1.定一个OldPhone类,定义两个私有属性brand和price,定义空参和有参构造方法,get/set方法
2.在OldPhone类中,定义一个打电话的方法,传递姓名的参数,方法体内输出给谁打电话
3.在OldPhone类中,定义一个发短信的方法,直接输出"发短信"
4.定义一个来电显示的方法,输出内容为"显示手机号",
4.定一个子类NewPhone,继承OldPhone类,在子类中重写来电显示的方法,输出内容为"显示手机号","显示归属地","显示头像"
5.定义测试类,创建NewPhone类对象,调用set方法为属性赋值,调用get方法获取属性值
6.调用从父类中继承过来的方法以及重写的方法
```

### 参考答案

```java
//父类-->老手机
public class OldPhone {
    private String brand;
    private double price;

    public OldPhone() {
    }

    public OldPhone(String brand, double price) {
        this.brand = brand;
        this.price = price;
    }

    public String getBrand() {
        return brand;
    }

    public void setBrand(String brand) {
        this.brand = brand;
    }

    public double getPrice() {
        return price;
    }

    public void setPrice(double price) {
        this.price = price;
    }

    //定义打电话方法
    public void call(String name){
        System.out.println("给"+name+"打电话!");
    }

    //发短信
    public void message(){
        System.out.println("发短信!");
    }

    //来电显示
    public void show(){
        System.out.println("显示手机号!");
    }

}
```

```java
//新手机
public class NewPhone extends OldPhone {
    //来电显示功能升级方法
    public void show() {
        super.show();
        System.out.println("显示归属地!");
        System.out.println("显示头像!");
    }
}
```

```java
//测试类
public class Test {
    public static void main(String[] args) {
        //创建子类对象
        NewPhone newPhone = new NewPhone();
        //调用set方法为属性赋值
        newPhone.setBrand("苹果");
        newPhone.setPrice(9800);
        //调用get方法获取属性值
        System.out.println("手机品牌为:"+newPhone.getBrand()+",价格为:"+newPhone.getPrice());
        //调用继承过来的方法
        newPhone.call("柳岩");
        newPhone.message();
        //调用重写后的方法
        newPhone.show();
    }
}
```

### 视频讲解

```
另附avi格式视频.
```



## 题目三

```
 白色4条腿的北极熊(Bear)会吃(吃蜂蜜)和抓鱼(catchFish)
 黑色4条腿的大熊猫(Panda)会吃(吃竹子)和爬树(climbTree)
 要求: 把北极熊和大熊猫的共性提取动物类(Animal)中,使用抽象类
```

### 训练目标

```
继承方法的重写
```

### 训练提示

```
1.将两种动物共性抽取出来,形成动物类,然后Bear和Panda继承动物类
2.重写共性方法,并定义特有方法
```

### 参考方案

```
1.定义一个动物类,里面有颜色和腿的条数,两个动物的共性就是吃的方法,所以可以把共性的吃的方法抽取出来,
2.定义出来的Bear类和Panda类都要继承动物类,重写吃的方法
3.定义北极熊和大熊猫的特有方法
4.在测试类中创建两个动物的对象,为属性赋值,并调用方法
```

### 操作步骤

```java
1.定义一个Animal类,定义两个私有属性(颜色:color,个数:numOfLegs).对应的构造以及get/set方法
2.在Animal中定义一个方法eat()
3.定义子类Bear(北极熊) 继承Animal类,重写父类中的抽象方法eat(),方法体输出 "白色4腿的北极熊在吃蜂蜜"
  定义特有方法catchFish(),方法体输出"白色4腿的北极熊在抓鱼"
4.定义子类Panda(熊猫)继承Animal类,重写父类中的抽象方法eat(),方法体输出 "黑色4条腿的大熊猫在吃竹子"
  定义特有方法climbTree(),方法体输出"黑色4条腿的大熊猫在爬树"
5.定义测试类,创建北极熊对象,为属性赋值,调用重写的方法以及特有方法
  创建大熊猫对象,为属性赋值,调用重写的方法以及特有方法


```

#### 注意:答案是super,我们没具体说,赋值还是用继承过来的set方法赋值

### 参考答案

```java
//动物类
public class Animal {
    //动物颜色
    private String color;
    //动物腿的个数
    private int numOfLegs;

    //提供带参构造和setXxx和getXxx方法
    public Animal() {

    }
    public Animal(String color, int numOfLegs) {

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
    public  void eat()(System.out.println("动物要吃东西"));

}
```

```java
//北极熊类
public class Bear extends Animal {

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
        Bear b = new Bear();
        b.setColor("白色");
        b.setNumOfLegs(4);
        //2. 调用北极熊对象b的吃方法
        b.eat();
        //3.调用北极熊对象b的抓鱼方法
        b.catchFish();
        //4. 创建大熊猫对象 p,颜色赋值为黑色,腿的个数赋值为4
        Panda p = new Panda();
        p.setColor("黑色");
        p.setNumOfLegs(4);
        //5. 调用大熊猫对象p的吃方法
        p.eat();
        //6. 调用大熊猫对象p的爬树方法
        p.climbTree();
    }
}
```

### 视频讲解

```
另附avi格式视频.
```
