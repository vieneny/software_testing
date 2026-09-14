# day06  方法  面向对象

```java
课前回顾:
  1.二维数组:
    a.定义: 数据类型[][] 数组名 = new 数据类型[m][n]  -> m:代表的是二维数组长度,n代表的是每一个一维数组的长度
           数据类型[][] 数组名 = {{元素1,元素2...},{元素1,元素2...}...}
    b.获取数组长度:数组名.length
    c.存值: 数组名[i][j] = 值
           i:代表的是一维数组在二维数组中的索引位置
           j:代表的是元素在一维数组中的索引位置
    d.取值: 数组名[i][j]
    e.遍历:嵌套循环 -> 先将一维数组从二维数组中获取出来,然后再遍历每一个一维数组
  2.方法:拥有功能性代码的代码块
    将来一个按钮就对应一个功能,一个功能就应该对应一个方法

  3.通用定义格式:
    修饰符 返回值类型 方法名(形参){
        方法体
        return 结果
    }

  4.无参无返回值方法:
    public static void 方法名(){
        方法体
    }
    直接调用:方法名()

  5.有参无返回值方法:
    public static void 方法名(形参){
        方法体
    }
    直接调用: 方法名(实参)

  6.无参有返回值方法:
    public static 返回值类型 方法名(){
        方法体
        return 结果
    }
    打印调用:sout(方法名())
    赋值调用:数据类型 变量名 = 方法名()

  7.有参有返回值方法:
    public static 返回值类型 方法名(形参){
        方法体
        return 结果
    }
    打印调用:sout(方法名(实参))
    赋值调用:数据类型 变量名 = 方法名(实参)


今日重点:
  1.会使用可变参数
  2.理解面向对象
  3.会定义类,以及使用对象调用成员
```

# 第一章.方法

## 1.方法注意事项终极版

```java
1.方法不调用不执行
2.方法的执行顺序只和调用顺序有关
3.[void]不能和[return 结果]共存,但是能和[return]共存
  void:代表的方法无返回值
  return 结果:代表有返回值,会将结果返回,结束方法
  return:仅仅代表结束方法,不代表有返回值
4.调用方法,要有这个方法,调用的方法和有的方法要完全一致(方法名,参数个数,参数类型,参数类型顺序等都要一致)
5.一个方法中只能有一个返回值,不能连续写多个return(if...else除外)
```

```java
public class Demo01Method {
    public static void main(String[] args) {
        int result = method01();
        System.out.println(result);

        //method02(10,20);
    }

    public static int[] method04(){
       int a = 10;
       int b = 20;
       int sum = a + b;
       int sub = a-b;
       int[] arr = {sum,sub};
       return arr;
    }

    public static String method03(int a,int b){
        //return "hello world";
        //return "hello world";
        if (a>b){
            return "a>b";
        }else{
            return "a<=b";
        }

        /*if (a>b){
            return "a>b";
        }else if (a<=b){
            return "a<=b";
        }*/
    }


    public static void method02() {
        System.out.println("方法02");
    }

    public static int method01() {
        int a = 10;
        int b = 20;
        int sum = a + b;
        return sum;//将结果返回,然后结束方法
        //return;//结束方法
    }
}

```

# 第二章.方法练习

## 1.方法练习1(判断奇偶性)

```java
需求:
   键盘录入一个整数,将整数传递到另外一个方法中,在此方法中判断这个整数的奇偶性
   如果是偶数,方法返回"偶数"  否则返回"奇数"

参数:要
返回值:要
方法名:要
```

```java
public class Demo02Method {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int data = sc.nextInt();
        System.out.println(method(data));
    }
    public static String method(int data){
        if (data%2==0){
            return "偶数";
        }else{
            return "奇数";
        }
    }
}
```

## 2.方法练习2(1-100的和)

```java
需求 :  求出1-100的和,并将结果返回
参数:不要
返回值:要
方法名:要
```

```java
public class Demo03Method {
    public static void main(String[] args) {
        int method = method();
        System.out.println(method);
    }
    public static int method(){
       int sum = 0;
       for (int i = 1; i <= 100; i++) {
           sum += i;
       }
       return sum;

    }
}

```

## 3.方法练习3(不定次数打印)

```java
需求:
   定义一个方法,给这个方法传几,就让这个方法循环打印几次"我是一个有经验的JAVA+智能体开发工程师"
参数:要
返回值:不要
方法名:要
```

```java
public class Demo04Method {
    public static void main(String[] args) {
        method(5);
    }

    public static void method(int n){
        for (int i = 0; i < n; i++) {
            System.out.println("我是一个有经验的java+智能体开发工程师");
        }
    }
}

```

## 4.方法练习4(遍历数组)

```java
需求:
  在main方法中定义一个数组,将数组传递到方法中,在此方法中遍历数组

```

```java
public class Demo05Method {
    public static void main(String[] args) {
        int[] arr1 = {1,2,3};
        method(arr1);
    }
    public static void method(int[] arr2){
        System.out.println(Arrays.toString(arr2));
    }
}

```

> <img src="image/image-20260116092746692.png" alt="image-20260116092746692" style="zoom:80%;" />
>
> 1.方法运行:压栈
>
> 2.方法运行完毕:弹栈 -> 清栈内存



## 5.方法练习5(求数组最大值)

```java
需求:
  在main方法中定义数组,传递到另外一个方法中,在此方法中实现获取数组最大值
```

```java
自己做
```

## 6.方法练习6(按照指定格式输出数组元素)

```java
需求:
  1.定义一个数组 int[] arr = {1,2,3,4}
  2.遍历数组,输出元素按照[1,2,3,4]
```

```java
自己做
```

## 7.练习7

```java
数组作为返回值返回
```

```java
public class Demo06Method {
    public static void main(String[] args) {
       int[] arr2 = method(10,20);//int[] arr2 = arr1
        System.out.println(Arrays.toString(arr2));
    }
    public static int[] method(int a,int b){
        int sum = a+b;
        int sub = a-b;
        int[] arr1 = {sum,sub};
        return arr1;
    }
}

```

<img src="image/image-20260116093542077.png" alt="image-20260116093542077" style="zoom:80%;" />



# 第三章.方法参数传递

## 1.基本类型做方法参数传递

```java
如果基本类型做方法参数传递,传递的是值,不是变量本身
```

<img src="image/image-20260116094235832.png" alt="image-20260116094235832" style="zoom:80%;" />

## 2.引用类型做方法参数传递

```java
如果引用类型做方法参数传递,传递的是地址值
```

<img src="image/image-20260116094837902.png" alt="image-20260116094837902" style="zoom:80%;" />

# 第四章.方法的重载(Overload)

```java
需求:定义三个方法,实现两个整数相加,三个整数相加,四个整数相加
```

```java
public class Demo01Overload {
    public static void main(String[] args) {
        sum(10,20);
        sum(10,20,30);
        sum(10,20,30,40);
    }

    public static void sum(int a,int b){
        int sum = a+b;
        System.out.println(sum);
    }

    public static void sum(int a,int b,int c){
        int sum = a+b+c;
        System.out.println(sum);
    }

    public static void sum(int a,int b,int c,int d){
        int sum = a+b+c+d;
        System.out.println(sum);
    }
}

```

```java
1.概述:方法名相同,参数列表不同的方法,叫做重载的方法(主要是指在同一个类中)
2.什么叫做参数列表不同:
  a.参数个数不同
  b.参数类型不同
  c.参数类型的顺序不同
3.判断两个方法是否构成了重载和什么无关:
  a.和参数名无关
  b.和返回值无关
```

> 小技巧:如何找打我们调用的方法或者创建的对象对应的位置
>
> 按住ctrl不放,鼠标点击对象名,方法名等->会跳到对应的位置

```java
public static void open(){}
public static void open(int a){}
static void open(int a,int b){}
public static void open(double a,int b){}
public static void open(int a,double b){}
public void open(int i,double d){}
public static void OPEN(){}
public static void open(int i,int j){}
```

<img src="image/image-20260116103346294.png" alt="image-20260116103346294" style="zoom:80%;" />

```java
使用场景:在同一个类中,功能一样,但是实现细节不一样,可以考虑用重载的方法
```

<img src="image/image-20260116103525633.png" alt="image-20260116103525633" style="zoom:80%;" />

# 第五章.可变参数

```java
1.需求:定义一个方法,实现若干个整数相加 -> 参数类型确定了,但是个数不确定
```

## 1介绍和基本使用

```java
1.格式:
  数据类型...变量名
2.注意:
  a.可变参数的本质是数组
  b.参数列表中只能有一个可变参数,而且需要放到参数列表的最后
```

<img src="image/image-20260116105602809.png" alt="image-20260116105602809" style="zoom:80%;" />

```java
public class Demo01Var {
    public static void main(String[] args) {
        sum(1,2,3,4);
        sum(1,2,3);
    }

    public static void sum(int a,int...arr){
        int sum = 0;
        for (int i = 0; i < arr.length; i++) {
            sum+=arr[i];
        }
        System.out.println(sum);
    }
}
```

## 2.练习

### 2.1.字符串拼接

需求一：返回n个字符串拼接结果，如果没有传入字符串，那么返回空字符串""

```java
public class Demo02Var {
    public static void main(String[] args) {
        String result01 = concat("张无忌", "周芷若", "赵敏", "宋青书");
        System.out.println(result01);
    }
    public static String concat(String...arr){
        String str = "";
        for (int i = 0; i < arr.length; i++) {
            str+=arr[i];
        }
        return str;
    }
}
```

### 2.2.字符串拼接分隔符

```java
n个字符串进行拼接，每一个字符串之间使用某字符进行分隔，如果没有传入字符串，那么返回空字符串""
sum("-","张三","李四","王五")   -> 张三-李四-王五
```

```java
public class Demo03Var {
    public static void main(String[] args) {
        String result01 = concat("-", "张无忌", "周芷若", "赵敏", "宋青书");
        System.out.println(result01);
    }

    public static String concat(String s, String... arr) {
        String str = "";
        for (int i = 0; i < arr.length; i++) {
            if (i == arr.length - 1) {
                str += arr[i];
            } else {
                str += arr[i] + s;
            }
        }
        return str;
    }
}
```

# 第六章.递归

> 从前有座山,山上有座庙,庙里有个老和尚,老和尚在给小和尚讲故事,讲的啥呢?
>
>    从前有座山,山上有座庙,庙里有个老和尚,老和尚在给小和尚讲故事,讲的啥呢?
>
> ​    从前有座山,山上有座庙,庙里有个老和尚,老和尚在给小和尚讲故事,讲的啥呢?...

```java
1.概述:方法内部自己调用自己
2.注意:
  a.递归要有出口,否则会出现栈内存溢出
  b.即使有出口,也不要递归太多次,否则也会出现栈内存溢出
```

```java
public class Demo01DiGui {
    public static void main(String[] args) {
        method();
    }
    public static void method(){
        method();
    }
}
```

<img src="image/image-20260116113918233.png" alt="image-20260116113918233" style="zoom:80%;" />

### 1.用递归输出3到1

```java
public class Demo02DiGui {
    public static void main(String[] args) {
        method(3);
    }
    public static void method(int n){
        if (n==0){
            return;//结束方法
        }
        System.out.println(n);
        n--;
        method(n);
    }
}
```

<img src="image/image-20260116114431341.png" alt="image-20260116114431341" style="zoom:80%;" />

### 2.求n!

``` java
1.需求:求3的阶乘
  3*2*1

2.分析:定义一个方法,代表阶乘的功能,参数代表几的阶乘  -> method(3)
  method(1)  1
  method(2)  2*1 -> 2*method(1)
  method(3)  3*method(2)
  method(4)  4*method(3)

  规律:n得阶乘 -> n*method(n-1)
```

```java
public class Demo03DiGui {
    public static void main(String[] args) {
        int result = method(3);
        System.out.println(result);
    }
    public static int method(int n){
        if (n==1){
            return 1;
        }
        return n*method(n-1);
    }
}

```

<img src="image/image-20260116141931403.png" alt="image-20260116141931403" style="zoom:80%;" />

### 示例三：计算斐波那契数列（Fibonacci）的第n个值

```java
不死神兔
故事得从西元1202年说起，话说有一位意大利青年，名叫斐波那契。
在他的一部著作中提出了一个有趣的问题：假设一对刚出生的小兔一个月后就能长成大兔，再过一个月就能生下一对小兔，并且此后每个月都生一对小兔，一年内没有发生死亡
问：一对刚出生的兔子，一年内繁殖成多少对兔子?  144
```

规律：一个数等于前两个数之和，比如: 1 1 2 3 5 8 13 21 34 55....

<img src="image/image-20260116143447181.png" alt="image-20260116143447181" style="zoom:80%;" />

```java
1.分析:假如定义给方法method代表生兔子,参数代表月份
  method(1)    1
  method(2)    1
  method(3)    2 -> method(1)+method(2)
  method(4)    3 -> method(2)+method(3)
  method(5)    5 -> method(3)+method(4)

  method(n) -> method(n-1)+method(n-2)
```

```java
public class Demo04DiGui {
    public static void main(String[] args) {
        int result = method(12);
        System.out.println(result);
    }

    public static int method(int n) {
        if (n==1 || n==2){
            return 1;
        }
        return method(n - 1) + method(n - 2);
    }
}

```

# 第七章.类和对象

```java
1.面向对象三大特征:封装    继承    多态
```

## 1.面向对象的介绍

```java
1.是什么:java的核心编程思想
2.有啥作用:减少代码 -> 很多功能别人帮我们实现好了,我们直接找来这个对象,然后直接调用这个对象实现好的功能即可
3.什么时候用:当在一个类中想使用别的类中实现好的功能,就需要使用面向对象思想
4.怎么用:
  a.new呀,new完了点 -> 比如Scanner,Random
  b.类名直接调用 -> 如果调用某个类中的成员,这个成员是带static关键的,我们直接类名点,不用new
```

```java
public class Demo01Object {
    public static void main(String[] args) {
        int[] arr = {1,2,3,4};
        System.out.print("[");
        for (int i = 0; i < arr.length; i++) {
            if (i == arr.length - 1){
                System.out.print(arr[i] + "]");
            }else {
                System.out.print(arr[i] + ",");
            }
        }
        System.out.println();

        /*
          Arrays:就是我们找来的对象
          toString方法:就是这个对象实现好的功能
         */
        System.out.println(Arrays.toString(arr));

        Scanner sc = new Scanner(System.in);
        String data = sc.next();

        Random rd = new Random();
        int data2 = rd.nextInt();

    }
}

```

> 面向对象是一个大的编程思想,具体目的减少代码量
>
> 怎么减少代码量:通过封装    继承    多态这三个具体的方面来想方设法的少写代码

## 2.类

```java
1.java中的类有三种类:
  a.测试类:带main方法的类
  b.逻辑类:专门写一些逻辑的
  c.实体类:用来描述一类事物的:人类,动物类,电脑类等

2.实体类概述:一类事物的抽象表示形式
  属性(成员变量) -> 这一类事物有啥
      a.定义位置:类中方法外
      b.作用范围:作用于整个类
      c.定义格式:数据类型 变量名
      d.有默认值:
        整数  0
        小数  0.0
        字符  '\u0000'
        布尔  false
        引用  null
  行为(成员方法) -> 这一类事物能干啥
        将之前定义的方法中的static关键字干掉,其他的不用动
```

```java
public class Person {
    //属性 成员变量
    String name;//默认值是null
    int age;//默认值是0

    //行为 成员方法
    public void eat(){
        System.out.println("吃饭");
    }
    public void drink(){
        System.out.println("喝水");
    }

    public void la(){
        System.out.println("拉屎");
    }

    public void sa(){
        System.out.println("撒尿");
    }
}
```

```java
public class Phone {
    //属性
    String brand;
    int price;
    String color;

    /**
     * 打电话
     */
    public void call(String name){
        System.out.println("给"+name+"打电话");
    }

    /**
     * 发短信
     */
    public String sendMessage(String name,String message){
        return "给"+name+"发短信，内容是："+message;
    }
}

```

## 3.对象

```java
1.概述:一类事物的具体体现
2.使用:
  a.导包:import 包名.类名
    a.如果两个类在同一个包下,使用对方的成员就不需要导包
    b.如果两个类不在同一个包下,使用对方的成员前就需要import导包
  b.new对象:想要调用哪个类的成员,就new哪个类的对象
    类名 对象名 = new 类名()
  c.调用成员:想要使用哪个类的成员,就用哪个类的对象去点哪个成员
    对象名.成员名
```

```java
public class Demo02Object {
    public static void main(String[] args) {
        Person p1 = new Person();
        System.out.println(p1.name);// null
        System.out.println(p1.age);// 0

        //给属性赋值
        p1.name = "张三";
        p1.age = 18;
        System.out.println(p1.name);
        System.out.println(p1.age);

        //调用方法
        p1.eat();
        p1.drink();
        p1.la();
        p1.sa();

        System.out.println("============================");

        Phone phone1 = new Phone();
        phone1.brand = "华为";
        phone1.price = 8888;
        phone1.color = "白色";
        System.out.println(phone1.brand);
        System.out.println(phone1.price);
        System.out.println(phone1.color);

        phone1.call("金莲");
        String result = phone1.sendMessage("涛哥","金莲:涛哥,在吗?");
        System.out.println(result);
    }
}
```

<img src="image/image-20260116162804254.png" alt="image-20260116162804254" style="zoom:80%;" />
