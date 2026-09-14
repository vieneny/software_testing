# day07_面向对象

```java
课前回顾:
  1.方法的重载:方法名相同,参数列表不同 -> 侧重同一个类
  2.可变参数:
    a.格式: 数据类型...变量名
    b.本质: 数组
    c.注意:参数列表中只能有一个可变参数并且需要放到最后
  3.递归:方法自己调用自己
    注意:要有出口,否则会出现栈内存溢出
  4.方法参数传递:
    a.传递基本类型:传递的是值
    b.传递引用类型:传递的是地址值
  5.面向对象:
    a.什么是面向对象:java的核心编程思想
    b.为啥要使用面向对象思想编程:减少代码量
    c.啥时候使用:在一个类中想要使用别的类中的成员
    d.怎么使用:
      new对象,点
      类名直接点 -> 成员带static关键字的
今日重点:
  1.会用代码描述世间万物的分类:人类,动物类,狗类,猫类
  2.会使用new对象的方式调用别的类中的成员
  3.知道成员变量和局部变量的区别
  4.知道啥样的代码写出来就是封装思想
  5.会使用get/set方法操作属性
  6.会使用this关键字区分重名的成员变量和局部变量
  7.会使用构造方法
  8.会实现一个标准的javabean类
```

# 第一章.类和对象

## 1.匿名对象的使用

> ```java
> 1.int i = 10;
>   int:数据类型
>   i:变量名
>   10:具体的数据
>
> 2.Person p = new Person()
>   等号左边的Person:数据类型
>   p:变量名(对象名)
>   new Person():具体的数据 -> new对象
> ```

```java
1.概述:
  没有等号左边的类型和对象名,只有new对象这半句代码
2.注意:
  a.匿名对象是一次性的,如果简单想让一个方法执行一下子,可以使用
  b.但是如果涉及到赋值,千万别使
```

```java
public class Person {
    String name;
    public void eat(){
        System.out.println("人要吃饭");
    }
}

```

```java
public class Test {
    public static void main(String[] args) {
        //原始方法new法
        Person person = new Person();
        person.name = "张三";
        System.out.println(person.name);
        person.eat();

        System.out.println("=======================");
        //匿名对象
        new Person().eat();
        new Person().name = "大郎";
        System.out.println(new Person().name);
    }
}

```

> 课程配图（未随笔记提交）

## 2.一个对象的内存图

```java
public class Phone {
    String brand;
    int price;
    public void call(){
        System.out.println("打电话");
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Phone phone = new Phone();
        System.out.println(phone);//地址值
        System.out.println(phone.brand);// null
        System.out.println(phone.price);// 0
        phone.brand = "小米";
        phone.price = 4999;
        System.out.println(phone.brand);//小米
        System.out.println(phone.price);//4999
        phone.call();
    }
}
```

> 课程配图（未随笔记提交）

## 3.两个对象的内存图

> 课程配图（未随笔记提交）

> 咱们new了两次,开辟两个不同的空间,修改一个对象中的数据不会影响另外一个对象

## 4.两个对象指向同一片空间内存图

> 课程配图（未随笔记提交）

> phone2是phone1直接赋值的,所以两个对象的地址值是一样的,操作的是同一片空间中的数据

# 第二章.成员变量和局部变量区别

```java
1.定义位置不同:
  a.成员:类中方法外
  b.局部:方法内
2.作用范围不同:
  a.成员:作用于整个类
  b.局部:只作用于自己的方法内部
3.初始化值不同:
  a.成员:有默认值
  b.局部:没有默认值,必须手动赋值才能使用
4.内存位置不同:
  a.成员:堆中
  b.局部:栈中
5.生命周期不同:
  a.成员:随着对象的创建而产生,随着对象的消失而消失
  b.局部:随着方法的调用而产生,随着方法的调用完毕而消失
```

```java
 public class Animal {
    //属性
    String name;
    int age;
    String color;

    public void eat() {
        System.out.println("吃");
        System.out.println(name);
        //局部变量
        int i = 10;
        System.out.println(i);
    }
    public void drink() {
        //System.out.println(i);
        System.out.println("喝");
        System.out.println(name);
    }
    public void run() {
        System.out.println("跑");
        System.out.println(name);
    }
}

```

# 第三章.练习

```java
现在自己做
```

```java
1.定义一个类MyDate,代表生日,类中定义三个属性,分别为 year  month  day,并为三个属性赋值
```

```java

```

```java
2.定义一个公民类Citizen,类中定义三个属性,分别为cardId(String),name(String),MyDate(MyDate),并为三个属性赋值

  注意:如果属性为自定义的类型,赋值是需要new对象赋值,不然直接调用时会出现空指针异常

```

```java

```

```java

```

# 第四章.封装

```java
面向对象三大特征:  [封装]    继承    多态
```

## 1.封装的介绍以及使用

```java
1.概述:将细节隐藏起来(为了不让外界直接随意调用),对外提供一套公共的接口(为了让外界通过这个公共接口间接使用封装起来的细节)
2.具体表现形式:
  a.将一段代码放到一个方法中
  b.代表性的关键字: private
    私有权限关键字
    被private修饰的成员只能在本类中访问,其他位置无法访问

3.private的使用:
  a.成员变量:在前面加private
  b.方法:将前面的public 改成 private

  c.怎么使用被private封装起来的细节(属性),提供公共接口
    getxxx()
    setxxx()
```

```java
 public class Person {
    //封装细节
    private String name;
    private int age;

    /**
     * 为name提供get/set方法
     */
    public void setName(String xingMing){
        name = xingMing;
    }

    public String getName(){
        return name;
    }

    /**
     * 为age提供get/set方法
     */
    public void setAge(int nianLing){
        age = nianLing;
    }

    public int getAge(){
        return age;
    }

}

```

```java
 public class Test01 {
    public static void main(String[] args) {
        Person person = new Person();
        //person.name = "张三";
        //person.age = 18;
        //System.out.println(person.name+"..."+person.age);
        person.setName("张三");
        person.setAge(18);

        String name = person.getName();
        int age = person.getAge();
        System.out.println(name+"..."+age);
    }
}

```

 > 课程配图（未随笔记提交）

## 2.this的介绍

```java
1.概述:this代表的是当前对象->哪个对象调用的this所在的方法,this就代表哪个对象
2.注意:如果局部变量和成员变量重名时,我们遵循"就近原则",先访问局部的
3.this作用:可以区分重名的成员变量和局部变量,this后面的一定是成员的
```

```java
 public class Person {
    String name;
    public void speak(String name){
        System.out.println(this+".............");
        System.out.println(this.name+"您好,我是"+name);
    }
}
```

```java
 public class Test01 {
    public static void main(String[] args) {
        Person person1 = new Person();
        System.out.println(person1+"...");
        person1.name = "沉香";
        person1.speak("刘彦昌");
        System.out.println("=====================");
        Person person2 = new Person();
        System.out.println(person2+"...");
        person2.name = "王思聪";
        person2.speak("王健林");

    }
}

```

 > 课程配图（未随笔记提交）

```java
 public class Phone {
    private String brand;
    private int price;

    public void setBrand(String brand) {
        this.brand = brand;
    }

    public String getBrand() {
        return brand;
    }

    public void setPrice(int price) {
        this.price = price;
    }

    public int getPrice() {
        return price;
    }
}

```

```java
 public class Test02 {
    public static void main(String[] args) {
        Phone p1 = new Phone();
        p1.setBrand("华为");
        p1.setPrice(8999);
        System.out.println(p1.getBrand()+"..."+p1.getPrice());

        System.out.println("=====================");
        Phone p2 = new Phone();
        p2.setBrand("苹果");
        p2.setPrice(7999);
        System.out.println(p2.getBrand()+"..."+p2.getPrice());
    }
}
```

 > 课程配图（未随笔记提交）

>  问题:属性如果没有被私有化,我们能不能提供get/set方法呢?
>
> ​          可以,但是没有意义

## 3.构造方法_构造器

```java
1.特点:
  a.方法名和类名一致
  b.构造方法没有返回值,连void都没有
  c.我们一new就相当于调用了构造方法
```

### 3.1空参构造

```java
1.格式:
  public 类名(){

  }
2.作用:
  new对象

3.特点:
  每个类中都会默认有一个无参构造,即使不写,jvm默认提供一个
```

```java
public class Person {
    private String name;
    private int age;

    /**
     * 无参构造方法
     *
     */
/*    public Person(){
        System.out.println("无参构造方法");
    }*/

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
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        Person person1 = new Person();

    }
}
```

### 3.2有参构造

```java
 1.格式:
  public 类名(形参){
      为属性赋值
  }
2.作用:
  a.new对象
  b.为属性赋值

3.特点:
  jvm不提供有参构造,但是我们自己写了有参构造,jvm将不再提供无参构造,所以建议我们都写上
```

```JAVA
public class Person {
    private String name;
    private int age;

    /**
     * 无参构造方法
     */
    public Person(){
        System.out.println("无参构造方法");
    }

    /**
     * 有参构造
     * @param name
     */
    public Person(String name,int age){
        this.name = name;
        this.age = age;
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
}

```

```JAVA
 public class Test01 {
    public static void main(String[] args) {
        Person person1 = new Person();
        person1.setName("小王");
        person1.setAge(18);
        System.out.println(person1.getName()+"..."+person1.getAge());

        System.out.println("=========================");
        Person person2 = new Person("小潘",24);
        System.out.println(person2.getName()+"..."+person2.getAge());

    }
}
```



>
>
> ```java
> 1.问题:既然有参构造既能new对象,还能为属性赋值,那么我们就不提供set方法了,行不行?
> 2.解决:不行
>   将来我们想要单独修改一个对象中的属性值,我们肯定会用到set方法
> ```
>
> ```java
> public class Person {
>     private String name;
>     private int age;
>
>     /**
>      * 无参构造方法
>      */
>     public Person(){
>         System.out.println("无参构造方法");
>     }
>
>     /**
>      * 有参构造
>      * @param name
>      */
>     public Person(String name,int age){
>         this.name = name;
>         this.age = age;
>     }
>
>     public void setName(String name) {
>         this.name = name;
>     }
>
>     public String getName() {
>         return name;
>     }
>
>     public void setAge(int age) {
>         this.age = age;
>     }
>
>     public int getAge() {
>         return age;
>     }
> }
>
> ```
>
> ```java
>  public class Test01 {
>     public static void main(String[] args) {
>        //Person person1 = new Person();
>        //person1.setName("小王");
>        //person1.setAge(18);
>        //System.out.println(person1.getName()+"..."+person1.getAge());
>
>         System.out.println("=========================");
>         Person person2 = new Person("小潘",24);
>         person2.setAge(25);
>         System.out.println(person2.getName()+"..."+person2.getAge());
>     }
> }
> ```

## 4.标准JavaBean

JavaBean` 是 Java语言编写类的一种标准规范。符合`JavaBean` 的类，要求：

（1）类必须是具体的(非抽象 abstract)和公共的，public class 类名

（2）并且具有无参数的构造方法

（3）成员变量私有化，并提供用来操作成员变量的`set` 和`get` 方法。

```java
public class Person {
    private String name;
    private int age;

    /**
     * 无参构造方法
     */
    public Person(){
        System.out.println("无参构造方法");
    }

    /**
     * 有参构造
     * @param name
     */
    public Person(String name,int age){
        this.name = name;
        this.age = age;
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
}

```

> com.atguigu.controller
>
> com.atguigu.service
>
> com.atguigu.dao
>
> com.atguigu.pojo/entity  -> javabean类
>
> com.atguigu.utils

编写符合`JavaBean` 规范的类，以学生类为例，标准代码如下：

```java
 public class Student {
    private int sid;
    private String name;

    public Student() {
    }

    public Student(int sid, String name) {
        this.sid = sid;
        this.name = name;
    }

    public int getSid() {
        return sid;
    }

    public void setSid(int sid) {
        this.sid = sid;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}

```

> 通用快捷键:
>
>   alt+insert
>
>   alt+fn+insert
>
> > 课程配图（未随笔记提交）

> 1.无参构造
>
> > 课程配图（未随笔记提交）
>
> 2.有参构造
>
> > 课程配图（未随笔记提交）
>
> 3.get/set方法
>
> > 课程配图（未随笔记提交）
>
>
>
>
>

```java
小结:
  1.知道private的作用嘛?成员私有化,不让外界直接使用
  2.知道set方法作用嘛?赋值
  3.知道get方法作用嘛?取值
  4.知道this作用嘛?区分重名的成员变量和局部变量
  5.知道无参构造作用嘛?new对象
  6.知道有参构造作用嘛?new对象的同时为属性赋值
  7.你知道如何用快捷键生成一个标准javabean嘛?  alt+insert
```

> 烧烤:一措再措
>
> 火锅:阳坊
>
> 螺蛳粉:肥姨妈
>
> 烤肉:嘿大福自助烤肉
>
> 配眼镜:潘家园北京眼镜城