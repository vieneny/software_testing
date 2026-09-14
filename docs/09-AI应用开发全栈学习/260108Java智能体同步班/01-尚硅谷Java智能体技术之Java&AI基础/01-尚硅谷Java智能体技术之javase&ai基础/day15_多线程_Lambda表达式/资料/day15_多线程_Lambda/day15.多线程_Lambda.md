# day15.多线程_Lambda

```java
课前回顾:如下图
今日重点:
  1.会使用继承Thread类的方式实现多线程程序
  2.会使用实现Runnable接口的方式实现多线程程序
  3.会使用同步代码块和同步方法解决线程不安全问题
  4.会写单例模式
  5.知道如何写一个Lambda表达式
```

> 课程配图（未随笔记提交）

# 第一章.多线程基本了解

## 1.多线程_线程和进程

```java
进程:进入到内存运行的应用程序
```

> 课程配图（未随笔记提交）

```java
线程:进程中的一个执行单元
2.线程作用:负责当前进程中程序的运行.一个进程中至少有一个线程,一个进程还可以有多个线程,这样的应用程序就称之为多线程程序
3.简单理解:进程中的一个功能就需要一条线程去执行
```

> 课程配图（未随笔记提交）

> 使用场景:软件中的耗时操作 -> 拷贝大文件, 加载大量的资源
>
> ​                     所有的聊天软件
>
> ​                     所有的后台服务器
>
> 多线程程序同时干多件事儿,提高了CPU使用率

## 2.并发和并行

```java
并行:在同一个时刻,有多个指令在多个CPU上(同时)执行(好比是多个人做不同的事儿)
    比如:多个厨师在炒多个菜
```

> 课程配图（未随笔记提交）

```java
并发:在同一个时刻,有多个指令在单个CPU上(交替)执行
    比如:一个厨师在炒多个菜
```

> 课程配图（未随笔记提交）

```java
细节:
  1.之前CPU是单核,但是在执行多个程序的时候好像是在同时执行,原因是CPU在多个线程之间做高速切换
  2.现在咱们的CPU都是多核多线程的了,比如2核4线程,那么CPU可以同时运行4个线程,此时不用切换,但是如果多了,CPU就要切换了,所以现在CPU在执行程序的时候并发和并行都存在
```

## 3.CPU调度

```java
1.分时调度:让所有的线程轮流获取CPU使用权,并且平均分配每个线程占用CPU的时间片
2.抢占式调度:多个线程抢占CPU使用权,哪个线程优先级越高,先抢到CPU使用权的几率就大,但是不是说每次先抢到CPU使用权的都是优先级高的线程,只是优先级高的线程先抢到CPU使用权的几率会大一些 -> java代码
```

## 4.主线程介绍

```java
1.概述:专门为main方法服务的线程
```

> 课程配图（未随笔记提交）

# 第二章.创建线程的方式(重点)

> 创建多线程有四种方式:
>
>    1.继承Thread类
>
>    2.实现Runnable接口
>
>    3.实现Callable接口
>
>    4.线程池

## 1.第一种方式_extends Thread

```java
1.创建自定义类(自定义线程类)继承Thread
2.重写Thread类中的run方法,设置线程任务(这个线程需要干啥事儿)
3.创建自定义线程类的对象
4.调用Thread类中的start方法(开启线程,jvm自动调用run方法)
```

```java
public class MyThread extends Thread{
    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println("MyThread正在执行..."+i);
        }
    }
}
```

```java
public class Demo01Thread {
    public static void main(String[] args) {
        //创建自定义线程对象
        MyThread t1 = new MyThread();
        //调用start方法开启线程,jvm自动执行run方法
        t1.start();

        for (int i = 0; i < 5; i++) {
            System.out.println("Main正在执行......" + i);
        }

    }
}
```

> 注意:如果直接调用run方法,并不代表将线程开启,仅仅是简单的调用方法
>
> ​         只有调用start方法,线程才会真正开启

## 2.多线程在内存中的运行原理

> 课程配图（未随笔记提交）

```java
同一个线程对象,只能调用一次start,不要调用多次;如果想开新的线程,需要重新new自定义线程类对象,单独再调用start方法
```

## 3.Thread类中的方法

```java
void run()  :设置线程任务,这个线程能干啥
void start()  : 使该线程开始执行；Java 虚拟机调用该线程的 run 方法
void setName(String name)  : 给线程设置名字
String getName() : 获取线程名字
static Thread currentThread()  : 获取当前正在执行的线程对象-> 这个方法在哪个线程中用,就获取的是哪个线程对象
static void sleep(long millis) :线程睡眠,设置的是毫秒值,超时之后线程会自动醒来,继续执行
```

```java
public class Demo01Thread {
    public static void main(String[] args) throws InterruptedException {
        //创建自定义线程对象
        MyThread t1 = new MyThread();

        //设置线程名称
        t1.setName("广坤");

        //调用start方法开启线程,jvm自动执行run方法
        t1.start();

        for (int i = 0; i < 5; i++) {
            Thread.sleep(2000L);
            System.out.println(Thread.currentThread().getName()+":Main正在执行......" + i);
        }
    }
}
```

```java
public class MyThread extends Thread{
    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            try {
                Thread.sleep(2000L);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println(Thread.currentThread().getName()+":MyThread正在执行..."+i);
        }
    }
}
```

> 问题:
>
>    为啥run方法中有编译时期异常只能try,不能throws?
>
>  原因: Thread类中的run没有抛异常,所以我们重写之后就不能抛,只能try

## 4.第二种方式_实现Runnable接口

```java
1.创建自定义线程类,实现Runnable接口
2.重写run方法,设置线程任务
3.利用Thread类中的构造方法:
  Thread(Runnable r)
  Thread(Runnable r,String name)可以设置线程名字
4.调用Thread类中的start方法开启线程
```

```java
public class MyRunnable implements Runnable{
    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println(Thread.currentThread().getName() + ":正在执行..." + i);
        }
    }
}
```

```java
public class Demo01Runnable {
    public static void main(String[] args) throws InterruptedException {
        MyRunnable myRunnable = new MyRunnable();
        //创建Thread对象,传递MyRunnable
        Thread t1 = new Thread(myRunnable);
        t1.start();

        for (int i = 0; i < 5; i++) {
            System.out.println(Thread.currentThread().getName()+":Main正在执行......" + i);
        }
    }
}

```

## 5.两种实现多线程的方式区别

```java
1.继承Thread方式:继承支持单继承,不能多继承,有局限性
2.实现Runnable接口方式:接口可以多继承,多实现,还可以一个类继承一个父类的同时实现一个或者多个接口,局限性小
```

## 6.匿名内部类创建多线程

```java
属于实现多线程的第二种方式
```

```java
public class Demo02Runnable {
    public static void main(String[] args) {
        /*
           Thread(Runnable r)
           Thread(Runnable r,String name)
         */
        new Thread(new Runnable() {
            @Override
            public void run() {
                for (int i = 0; i < 5; i++) {
                    System.out.println(Thread.currentThread().getName()+":正在执行......" + i);
                }
            }
        },"广坤").start();

        new Thread(new Runnable() {
            @Override
            public void run() {
                for (int i = 0; i < 5; i++) {
                    System.out.println(Thread.currentThread().getName()+":正在执行......" + i);
                }
            }
        },"刘能").start();
    }
}
```

> 课程配图（未随笔记提交）

# 第三章.线程安全

```java
1.发生的场景:多个线程共享同一个资源的时候
```

## 1.线程安全问题-->线程不安全的代码

```java
public class Demo01Ticket {
    public static void main(String[] args) {
        MyTicket myTicket = new MyTicket();
        Thread t1 = new Thread(myTicket,"广坤");
        Thread t2 = new Thread(myTicket,"刘能");
        Thread t3 = new Thread(myTicket,"赵四");
        t1.start();
        t2.start();
        t3.start();
    }
}
```

```java
public class MyTicket implements Runnable{
    private int ticket = 100;
    @Override
    public void run() {
        while (true){
            try {
                Thread.sleep(100L);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            if (ticket > 0){
                System.out.println(Thread.currentThread().getName() + "正在卖第" + ticket + "张票");
                ticket--;
            }
        }
    }
}
```

## 2.解决线程安全问题的第一种方式(使用同步代码块)

```java
1.同步代码块:
  synchronized(任意对象){
      线程不安全的代码
  }
2.任意对象:就是锁对象
3.执行流程:
  线程先抢到锁的话,才能进入到同步代码块中执行,其他线程等待,等着线程出了同步代码块自动将锁释放,其他线程才能抢锁,抢到了执行,抢不到继续等待
```

```java
public class MyTicket implements Runnable{
    private int ticket = 100;
    Object obj = new Object();
    @Override
    public void run() {
        while (true){
            try {
                Thread.sleep(100L);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            synchronized (obj){
                if (ticket > 0){
                    System.out.println(Thread.currentThread().getName() + "正在卖第" + ticket + "张票");
                    ticket--;
                }
            }

        }
    }
}

```

```java
public class Demo01Ticket {
    public static void main(String[] args) {
        MyTicket myTicket = new MyTicket();
        Thread t1 = new Thread(myTicket,"广坤");
        Thread t2 = new Thread(myTicket,"刘能");
        Thread t3 = new Thread(myTicket,"赵四");
        t1.start();
        t2.start();
        t3.start();
    }
}

```

## 3.解决线程安全问题的第二种方式:同步方法

### 3.1.普通同步方法_非静态

``` java
1.格式:
  修饰符 synchronized 返回值类型 方法名(形参){
       方法体
       return 结果
  }
2.默认锁:this
```

```java
public class Demo01Ticket {
    public static void main(String[] args) {
        MyTicket myTicket = new MyTicket();
        Thread t1 = new Thread(myTicket,"广坤");
        Thread t2 = new Thread(myTicket,"刘能");
        Thread t3 = new Thread(myTicket,"赵四");
        t1.start();
        t2.start();
        t3.start();
    }
}

```

```java
public class MyTicket implements Runnable{
    private int ticket = 100;
    //Object obj = new Object();
    @Override
    public void run() {
        while (true){
            try {
                Thread.sleep(100L);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            method01();

        }
    }

    public synchronized void method01(){
        if (ticket > 0){
            System.out.println(Thread.currentThread().getName() + "正在卖第" + ticket + "张票");
            ticket--;
        }
    }

   /* public void method01(){
        synchronized (this){
            if (ticket > 0){
                System.out.println(Thread.currentThread().getName() + "正在卖第" + ticket + "张票");
                ticket--;
            }
        }

    }*/

}

```

### 3.2.静态同步方法

```java
1.格式:
  修饰符 static synchronized 返回值类型 方法名(形参){
       方法体
       return 结果
  }
2.默认锁:当前类.class
```

```java
public class Demo01Ticket {
    public static void main(String[] args) {
        MyTicket myTicket = new MyTicket();
        Thread t1 = new Thread(myTicket,"广坤");
        Thread t2 = new Thread(myTicket,"刘能");
        Thread t3 = new Thread(myTicket,"赵四");
        t1.start();
        t2.start();
        t3.start();
    }
}
```

```java
public class MyTicket implements Runnable{
    private static int ticket = 100;
    //Object obj = new Object();
    @Override
    public void run() {
        while (true){
            try {
                Thread.sleep(100L);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            method01();

        }
    }

    public static synchronized void method01(){
        if (ticket > 0){
            System.out.println(Thread.currentThread().getName() + "正在卖第" + ticket + "张票");
            ticket--;
        }
    }

  /*  public static void method01(){
        synchronized (MyTicket.class){
            if (ticket > 0){
                System.out.println(Thread.currentThread().getName() + "正在卖第" + ticket + "张票");
                ticket--;
            }
        }

    }*/
}
```

# 第四章.单例模式

```properties
单:一个
例:实例 -> 对象
单例模式的目的:让一个类只产生一个对象供外界使用
```

### 1.1.饿汉式：

```properties
饿汉式:我好饿呀,我很急需一个对象
所以:饿汉式需要赶紧让对象new出来,而且将其变成静态的,让这个对象随着类的加载而直接创建
```

```java
public class Singleton {
    /**
     * 我们需要将构造私有化
     * 这样外界就不能随便根据构造new对象了
     */
    private Singleton(){

    }

    /**
     * 由于是饿汉式,迫不及待的想要对象创建出来
     * 所以我们需要将对象变成静态的
     *
     * 为了不让外界直接用类名调用对象,我们需要将其变成私有的
     */
    private static Singleton singleton = new Singleton();

    /**
     * 对外提供公共的接口,将内部的对象给外界使用
     */
    public static Singleton getSingleton(){
        return singleton;
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        for (int i = 0; i < 5; i++) {
            Singleton singleton = Singleton.getSingleton();
            System.out.println(singleton);
        }
    }
}
```

### 1.2.懒汉式：

```properties
1.概述:不需要提前new对象,等到啥时候用的时候,啥时候new出来给我,当然还需要保证这个类只产生一个对象
```

```java
public class Singleton {
    private Singleton() {

    }

    private static Singleton singleton = null;

    public static Singleton getSingleton() {
        if (singleton == null){
            synchronized (Singleton.class){
                if (singleton == null) {
                    singleton = new Singleton();
                }
            }
        }
        return singleton;
    }
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                Singleton singleton = Singleton.getSingleton();
                System.out.println(singleton);
            }
        }).start();

        new Thread(new Runnable() {
            @Override
            public void run() {
                Singleton singleton = Singleton.getSingleton();
                System.out.println(singleton);
            }
        }).start();
    }
}

```

# 第五章.Lambda表达式

## 1.函数式编程思想和Lambda表达式定义格式

```java
1.java核心编程思想:面向对象
  强调的是先new对象,然后调用方法 -> 为啥new对象呀,目的是为了调用对象中的方法 -> 过多的强调new对象这个事儿了
2.函数式编程思想:
  强调的是目的(调用对象的方法),不强调过程(new对象)
3.Lambda表达式:
  格式: () -> {}
  解释说明:
    ():代表的是重写方法的参数位置
    ->:将重写方法的参数传递给重写方法的方法体
    {}:重写方法的方法体
```

```java
public class Demo01Lambda {
    public static void main(String[] args) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                System.out.println("正在执行...");
            }
        }).start();

        System.out.println("==========================");
        //Lambda表达式
        new Thread(()-> System.out.println("正在执行...")).start();
    }
}
```

## 2.Lambda表达式使用前提

```java
1.前提:必须是函数式接口做方法参数传递或者返回值返回
2.函数式接口:
  必须有,且只能有一个抽象方法的接口
3.如何快速知道此接口是否是函数式接口:接口上用一个注解
  @FunctionalInterface
```

```java
@FunctionalInterface
public interface USB {
    void open();
}
```

```java
public class Demo02Lambda {
    public static void main(String[] args) {
        method(new USB() {
            @Override
            public void open() {
                System.out.println("usb打开了");
            }
        });

        System.out.println("========================");
        method(() -> System.out.println("lambda打开"));
    }

    public static void method(USB usb){
        usb.open();
    }
}
```

## 3.Lambda表达式省略规则

```java
1.涛哥秘籍:
  a.先观察,是否是函数式接口做方法参数传递或者返回值返回
  b.如果是,调用方法,以匿名内部类传参或者返回
  c.从new接口开始到重写方法的方法名结束,选中,删除,然后别忘记多删除一个右半个大括号
  e.在重写方法的参数和重写方法的方法体之间加 ->

2.省略规则:
  a.重写方法的参数类型可以省略
  b.重写方法的参数如果只有一个参数,数据类型和所在的小括号可以省略
  c.如果重写方法的方法体只有一句,所在的大括号和分号可以省略
  d.如果重写方法的方法体只有一句,并且带return的,那么所在的大括号,分号以及return都可以省略
```

```java
@FunctionalInterface
public interface USB {
    String open(String name);
}
```

```java
public class Test01 {
    public static void main(String[] args) {
        method(new USB() {
            @Override
            public String open(String name) {
                return name + "打开了";
            }
        });
        System.out.println("========================");
        method(name-> name + "打开了");

        System.out.println("===================");
        String result = method02().open("键盘");
        System.out.println(result);
    }

    public static void method(USB usb) {
        String result = usb.open("鼠标");
        System.out.println(result);
    }

    public static USB method02(){
        return name-> name + "打开了";
    }
}
```
