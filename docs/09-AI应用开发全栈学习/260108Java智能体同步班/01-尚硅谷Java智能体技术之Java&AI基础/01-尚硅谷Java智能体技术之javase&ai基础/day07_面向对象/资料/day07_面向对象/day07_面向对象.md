# day07_面向对象

```java
课前回顾:
  1.参数传递基本类型:传递的是值,不是变量本身
    参数传递引用类型:传递的是地址值
  2.方法的重载:方法名相同,参数列表不同(和参数名以及返回值无关)
  3.可变参数:
    a.格式:数据类型...变量名
    b.本质:数组
    c.注意:参数列表只能有一个可变参数,而且放到最后
  4.递归:方法内部自己调用自己
    a.注意:递归要有出口,否则会出现栈内存溢出现象
  5.面向对象:
    a.是什么:java的核心编程思想
    b.为啥用:为了减少代码量
    c.啥时候用:在一个类中想使用别的类中的成员
    d.怎么用:
      new对象,点
      类名直接点:类名直接点的成员在定义的时候带static关键字
  6.实体类的定义:
    属性(成员变量,字段)
    行为(成员方法): 不带static关键字的方法
  7.对象的使用:
    a.导包:
      如果两个类在同一个包下,不用导包
      如果两个类不在同一个包下,就需要导包
    b.创建对象:类名 对象名 = new 类名()
    c.用对象名点成员:对象名.成员名

今日重点:
  1.会使用匿名对象
  2.知道成员变量和局部变量的区别
  3.知道什么是封装
  4.知道private关键字的作用
  5.知道getxxx/setxxx方法的作用
  6.知道this关键字的作用
  7.知道构造方法的作用
  8.会快速编写一个标准的javabean类
```

# 第一章.类和对象

## 1.匿名对象的使用

> ```java
> int i = 10
> int:具体的数据类型
> i:变量名
> 等号右边的:就是这变量具体的值
>
> =============================
> Person p = new Person()
> 等号左边的Person:相当于int,就是一个数据类型
> p:变量名,对象名
> new Person():就是p的具体的值 -> 只不过这个值是一个对象而已
> ```

```java
1.匿名对象:没有名字的对象(说白了,只有new 对象(),没有等号左边的部分)
2.使用:
  new 类名().成员名
3.注意:
  如果涉及到赋值了,千万不要用匿名对象
4.使用场景:
  如果想简单调用一个方法,让这个方法简单执行一下子,可以考虑使用匿名对象去调用
```

```java
public class Person {
    String name;
    public void eat(){
        System.out.println("吃饭");
    }
}
```

```java
public class Demo01Object {
    public static void main(String[] args) {
        //原始方式new对象 -> 有名对象
        Person p1 = new Person();
        p1.name = "张三";
        System.out.println(p1.name);
        p1.eat();

        System.out.println("==================");

        //匿名对象
        new Person().eat();

        new Person().name = "李四";
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
public class Demo01Object {
    public static void main(String[] args) {
        Phone phone1 = new Phone();
        System.out.println(phone1);//地址值
        System.out.println(phone1.brand);//null
        System.out.println(phone1.price);//0
        phone1.brand = "华为";
        phone1.price = 8888;
        System.out.println(phone1.brand);//华为
        System.out.println(phone1.price);//8888
        phone1.call();
    }
}

```

> 课程配图（未随笔记提交）

## 3.两个对象的内存图

> 课程配图（未随笔记提交）

> 我们new了两次对象,在堆内存中开辟了两个不同的空间,修改一个空间中的数据不会影响到另外一个空间的数据

## 4.两个对象指向同一片空间内存图

> 课程配图（未随笔记提交）

> phone2是phone1给的,会将phone1的地址值给phone2,此时phone1和phone2地址值是一样的,操作同一个空间中的数据,所以修改一个对象的数据会影响另外一个对象

# 第二章.成员变量和局部变量区别

```java
1.定义位置不同(掌握)
  a.成员变量:类中方法外
  b.局部变量:方法内或者形参位置
2.初始化值不同(掌握)
  a.成员变量:有默认值
  b.局部变量:没有默认值,必须手动赋值之后才能使用
3.作用范围不同(掌握)
  a.成员变量:作用于整个类
  b.局部变量:只作用于自己方法内部,其他方法不能直接使用
4.内存位置不同(了解)
  a.成员变量:在堆中 -> 侧重于从哪里起作用(初始化)
  b.局部变量:在栈中 -> 因为局部变量跟着方法走,方法在栈中,所以局部变量也在栈中
5.生命周期不同(了解)
  a.成员变量:随着对象的创建而创建,随着对象的消失而消失
  b.局部变量:随着方法的执行而创建,随着方法的消失而消失
```

```java
public class Person {
    //成员变量
    String name;

    public void eat() {
        System.out.println(name);
        //局部变量
        int i = 10;
        System.out.println(i);
    }

    public void show() {
        System.out.println(name);
        //System.out.println(i);i是eat方法中定义的,只作用于eat方法
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
1.面向对象三大特征: 封装   继承   多态
2.面向对象和三大特征的关系:
  面向对象思想是为了减少代码量,而封装,继承,多态就是从三个不同的方面来减少代码量
```

## 1.封装的介绍以及使用

```java
1.封装的概述:
  隐藏细节(不让外界随便调用),对外提供公共的接口(让外界通过这个公共接口间接使用封装起来的细节)

  我们可以通过公共的接口使用隐藏起来的细节,其实对于细节我们无需过多关注,我们只关注根据公共的接口就能让隐藏起来的细节运行起来,至于细节怎么实现的,我们不用关注

2.封装的体现:
  a.将一段代码放到一个方法中
  b.封装思想中有一个代表性的关键字:private(私有访问权限)
    被private修饰的成员只能在本类中直接使用,别的类中不能直接使用

3.使用:
  a.将一段代码放到一个方法中,封装的体现->之前大家写的方法都是封装的体现,今天不过多讲
  b.我们主要讲另外一种封装的体现:private关键字

4.用private修饰之后是隐藏细节,我们需要提供公共的接口,让外界通过这个公共的接口间接使用private的细节
  公共接口:
     getxxx():获取属性值
     setxxx():为属性赋值
```

```java
 public class Person {
    //隐藏细节
    private String name;
    private int age;

    /**
     * 对外提供公共的接口
     */

    /**
     * 为私有化的name提供公共的接口
     * setName()和getName()
     */
    public void setName(String xingMing) {
        name = xingMing;
    }
    public String getName() {
        return name;
    }

    /**
     * 为私有化的age提供公共的接口
     * setAge()和getAge()
     */
    public void setAge(int nianLing) {
       /* if(nianLing < 0 || nianLing > 120) {
            System.out.println("你输入的年龄有误");
            return;
        }*/
        age = nianLing;
    }
    public int getAge() {
        return age;
    }
}

```

```java
 public class Demo01Private {
    public static void main(String[] args) {
        Person p1 = new Person();
        //p1.name = "张三";
        //p1.age = -18;
        //System.out.println(p1.name);
        //System.out.println(p1.age);

        p1.setName("张三");
        p1.setAge(18);
        System.out.println(p1.getName()+"..."+p1.getAge());
    }
}
```

 > 课程配图（未随笔记提交）

> 一个类中如果有私有属性,get/set方法基本就是配套提供的

## 2.this的介绍

```java
1.注意:如果成员变量和局部变量重名时,我们遵循"就近原则",先使用局部变量
2.概述:代表的是当前对象(哪个对象调用的this所在的那个方法,this就代表哪个对象)
3.this的作用:可以区分重名的成员变量和局部变量 ->this.后面的就是成员的
```

```java
public class Person {
    String name;
    public void speak(String name){
        System.out.println(this+"...............");
        System.out.println(this.name+"您好,我是"+name);
    }
}
```

```java
 public class Test01 {
    public static void main(String[] args) {
        Person person = new Person();
        System.out.println(person+"...");
        person.name = "哪吒";
        person.speak("李靖");

        System.out.println("================");
        Person person2 = new Person();
        System.out.println(person2+"...");
        person2.name = "沉香";
        person2.speak("刘彦昌");
    }
}

```

 > 课程配图（未随笔记提交）

```java
public class Person {
    private String name;
    private int age;

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
 public class Demo01Object {
    public static void main(String[] args) {
        Person p1 = new Person();
        p1.setName("张三");
        p1.setAge(18);
        System.out.println(p1.getName()+"..."+p1.getAge());
        System.out.println("==========================");
        Person p2 = new Person();
        p2.setName("李四");
        p2.setAge(19);
        System.out.println(p2.getName()+"..."+p2.getAge());
    }
}
```

 > 课程配图（未随笔记提交）

>  问题:属性如果没有被私有化,我们能不能提供get/set方法呢?
>
>  ​          可以,但是没有意义

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
  new对象,初始化对象的属性
3.特点:
  每个类中都默认有一个无参构造,即使不写,jvm也会默认提供一个
```

```java
public class Person {
    private String name;
    private int age;

    /**
     * 空参构造
     */
    public Person(){
        //System.out.println("空参构造");
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

```java
public class Demo01Object {
    public static void main(String[] args) {
        Person p1 = new Person();
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

3.注意:
  如果写了有参构造,jvm将不再提供无参构造,所以建议无参的,有参的构造都写出来
```

```JAVA
public class Person {
    private String name;
    private int age;

    /**
     * 空参构造
     */
    public Person(){
        //System.out.println("空参构造");
    }

    /**
     * 带参构造
     */
    public Person(String name, int age) {
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
public class Demo01Object {
    public static void main(String[] args) {
        Person p1 = new Person();
        p1.setName("张三");
        p1.setAge(18);
        System.out.println(p1.getName()+"..."+p1.getAge());
        System.out.println("===================");
        //利用有参构造创建对象并为属性赋值
        Person p2 = new Person("涛哥", 18);
        System.out.println(p2.getName()+"..."+p2.getAge());
    }
}

```

 > 课程配图（未随笔记提交）

>  问题:有参构造既可以new对象,还可以为属性赋值,那么有了有参构造,我们能不能不写setxxx方法了呢?
>
>  ```java
>  建议将set也写上:
>    如果我们要单独修改一个属性的值,我们没有必要重新new对象,我们直接利用这个对象的set方法就可以单独为属性改值
>  ```
>
>  ```java
>  public class Demo02Object {
>      public static void main(String[] args) {
>          Person p1 = new Person("张三", 18);
>          System.out.println(p1.getName()+"..."+p1.getAge());
>          p1.setAge(19);
>          System.out.println(p1.getName()+"..."+p1.getAge());
>      }
>  }
>  ```
>

## 4.标准JavaBean

JavaBean` 是 Java语言编写类的一种标准规范。符合`JavaBean` 的类，要求：

（1）类必须是具体的(非抽象 abstract)和公共的，public class 类名

（2）并且具有无参数的构造方法

（3）成员变量私有化，并提供用来操作成员变量的`set` 和`get` 方法。

> com.atguigu.controller -> 存放和页面打交道的类
>
> com.atguigu.service -> 存放业务类
>
> com.atguigu.dao -> 存放和数据库打交道的类
>
> com.atguigu.pojo/entity -> 存放的都是javabean类
>
> com.atguigu.utils -> 存放的都是工具类

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
public class Test01 {
    public static void main(String[] args) {
        Student s1 = new Student();
        s1.setSid(1);
        s1.setName("张三");
        System.out.println(s1.getSid()+"..."+s1.getName());

        System.out.println("==================");
        Student s2 = new Student(2, "李四");
        System.out.println(s2.getSid()+"..."+s2.getName());
    }
}
```

```java
小结:
  1.知道private的作用嘛?私有之后别的类不能直接调
  2.知道get/set方法的作用嘛?赋值取值
  3.知道this关键字的作用吗?区分重名的成员变量和局部变量,this后面的就是成员的
  4.知道无参构造作用嘛?new对象
  5.知道有参构造作用嘛?new对象的同时为属性赋值
  6.知道如何快速生成一个标准javabean嘛?
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

# 第五章.static关键字

## 1.static关键字的介绍和使用

> 课程配图（未随笔记提交）

```java
1.概述:static是静态关键字
2.可以修饰一个方法,修饰一个成员变量
   a.修饰方法: 权限修饰符 static 返回值类型 方法名(形参){
                              方法体
                              return 结果
                     }

   b.修饰一个成员变量:
     权限修饰符 static 数据类型 变量名


3.static关键字的特点:
   a.静态成员属于类成员,不属于对象成员,非静态成员属于对象成员
   b.静态成员会随着类的加载而加载
   c.静态成员优先于对象存在
   d.凡是根据static关键字所在的类创建出来的对象,都可以共享这个静态成员

4.调用:
   类名直接调用
```

```java
public class Student {
    int id;
    String name;
    static String classRoom;
}
```

```java
public class Demo01Static {
    public static void main(String[] args) {
        Student.classRoom = "教研室6";

        Student s1 = new Student();
        s1.id = 1;
        s1.name = "张三";
        //s1.classRoom = "教研室7";
        System.out.println(s1.id+"..."+s1.name+"..."+Student.classRoom);
        System.out.println("=======================================");
        Student s2 = new Student();
        s2.id = 2;
        s2.name = "李四";
        //s2.classRoom = "教研室7";
        System.out.println(s2.id+"..."+s2.name+"..."+Student.classRoom);
    }
}
```

## 2.static成员的访问特点

```java
1.在静态方法中能直接访问非静态成员嘛?不能
  想访问:new对象访问

2.在静态方法中能直接访问静态成员嘛?能
  a.在同一个类中:直接调用
  b.不在同一个类中:类名调用

3.在非静态方法中能直接访问静态成员嘛?能
  a.在同一个类中:直接调用
  b.不在同一个类中:类名调用

4.在非静态方法中能直接访问非静态成员嘛?能
  a.在同一个类中:直接调用
  b.不在同一个类中:new对象调用
```

> 1.只要是访问静态成员,能直接调用就直接调用,不能直接调用就类名调用
>
> 2.只要是访问非静态成员,能直接调用就直接调用,不能直接调用就new对象调用

## 3.static使用场景

```java
1.问题:既然静态成员这么好使用,那么将来能不能将所有的成员都定义成静态的呢? -> 不能
2.原因:如果将所有成员都定义成静态成员,那么静态成员不管是有用的,没用的,都会随着类的加载而加载,会占用内存
3.static成员什么时候使用呢?
  定义工具类的时候,工具类中的成员都是静态成员

4.啥是工具类:拥有多个通用性功能的类
5.工具类怎么形成:
  将来我们发现在多个类中都要频繁实现某个功能,我们就不用在每个类中写重复代码,重复实现同一个功能了,我们可以这些通用的代码封装到工具类中

6.工具类要求:
  a.构造私有化
  b.成员都是静态的
```

```java
public class ArrayTools {
    //构造私有
    private ArrayTools(){}

    /**
     * 提供一个方法,专门求int数组的元素和
     */
    public static int getSum(int[] arr) {
        int sum = 0;
        for (int i = 0; i < arr.length; i++) {
            sum += arr[i];
        }
        return sum;
    }
}

```

```java
public class Test01 {
    public static void main(String[] args) {
        int[] arr = {10, 20, 30, 40, 50};
       /* int sum = 0;
        for (int i = 0; i < arr.length; i++) {
            sum+=arr[i];
        }
        System.out.println(sum);*/
        System.out.println(ArrayTools.getSum(arr));
    }
}

```

```java
public class Test02 {
    public static void main(String[] args) {
        int[] arr = {1,2,3,4,5};
/*        int sum = 0;
        for (int i = 0; i < arr.length; i++) {
            sum+=arr[i];
        }
        System.out.println(sum);*/
        System.out.println(ArrayTools.getSum(arr));
    }
}
```

> 除了工具类的成员是静态的,其他的成员一般都是非静态的