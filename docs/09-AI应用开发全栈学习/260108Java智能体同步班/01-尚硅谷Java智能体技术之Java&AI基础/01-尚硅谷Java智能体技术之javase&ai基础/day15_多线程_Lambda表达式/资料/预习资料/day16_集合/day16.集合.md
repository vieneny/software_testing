# day16.集合

```java
课前回顾:
  1.实现多线程方式1:继承Thread
  2.实现多线程方式2:实现Runnable
  3.Thread中的方法:
    a.run:设置线程任务
    b.start:启动线程,jvm自动调用run方法
    c.setName:给线程设置名字
    d.getName:获取名字
    e.currentThread:获取当前正在执行的线程对象
    f.sleep线程睡眠
  4.线程同步:
    a.同步代码块:
      synchronized(锁对象){}
    b.非静态同步方法:  this
      public synchronized 返回值类型 方法名(形参){}
    c.静态同步方法:  类名.class
      public static synchronized 返回值类型 方法名(形参){}
  5.Lambda:
    a.格式:
      ()->{}
    b.前提:
      必须是函数式接口做方法参数传递或者返回值返回
    c.省略规则:
      重写方法的参数类型可以省略
      如果参数就一个,所在的小括号可以省略
      如果方法体只有一句,大括号和分号可以省略
      如果方法体只有一句,并且带return的,return,以及所在大括号以及分号都可以干掉
  6.如何判断这个接口是函数式接口:
    @FunctionalInterface

今日重点:
  1.会使用Stream流对象
  2.将单列集合的集合体系背下来
  3.会使用Collection集合中的方法
  4.会使用迭代器遍历集合
  5.会使用增强for遍历集合
  6.知道ArrayList集合的特点以及基本使用
```

# 第一章.函数式接口

```java
1.概述:必须有,且只能有一个抽象方法的接口
2.检测:@FunctionalInterface
```

## 1.Supplier

```java
1.Supplier接口
   java.util.function.Supplier<T>接口，它意味着"供给"->我们想要什么就给什么
2.方法:
  T get() -> 我们想要什么,get方法就可以返回什么

3.需求:
   使用Supplier接口作为方法的参数
   用Lambda表达式求出int数组中的最大值

4.泛型:
  <引用数据类型>-> 规定了我们操作的数据是什么类型
  <>中只能写引用数据类型,不能写基本数据类型
  泛型的作用就是为了统一类型
```

| 基本类型 | 包装类    |
| -------- | --------- |
| byte     | Byte      |
| short    | Short     |
| int      | Integer   |
| long     | Long      |
| float    | Float     |
| double   | Double    |
| char     | Character |
| boolean  | Boolean   |

```java
public class Demo01Supplier {
    public static void main(String[] args) {
        method(new Supplier<Integer>() {
            @Override
            public Integer get() {
                int[] arr = {3,4,2,32,5,6};
                return ArrayUtil.max(arr);
            }
        });
        System.out.println("===========================");
        method(()->{
                int[] arr = {3,4,2,32,5,6};
                return ArrayUtil.max(arr);
        });
    }

    public static void method(Supplier<Integer> supplier){
        Integer data = supplier.get();
        System.out.println("data = " + data);
    }
}

```

> 课程配图（未随笔记提交）

## 2.Consumer

```java
java.util.function.Consumer<T>->消费型接口->操作
  方法:
    void accept(T t)，意为消费一个指定泛型的数据

"消费"就是"操作",至于怎么操作,就看重写accept方法之后,方法体怎么写了
```

```java
public class Demo02Consumer {
    public static void main(String[] args) {
        show(new Consumer<String>() {
            @Override
            public void accept(String s) {
                System.out.println(s.length());
            }
        },"abcdefg");
        System.out.println("========================");
        show(s-> System.out.println(s.length()),"abcdefg");
    }
    public static void show(Consumer<String> consumer, String s){
        consumer.accept(s);
    }
}

```

## 3.Function

```java
java.util.function.Function<T,R>接口用来根据一个类型的数据得到另一个类型的数据
  方法:
     R apply(T t)根据类型T参数获取类型R的结果
```

```java
public class Demo03Function {
    public static void main(String[] args) {
        method(new Function<Integer, String>() {
            @Override
            public String apply(Integer integer) {
                return integer+"";
            }
        },100);
        System.out.println("===========================");
        method(a->a+"",100);
    }
    public  static void method(Function<Integer,String> function, int a){
        String apply = function.apply(a);
        System.out.println(apply);
    }
}

```

## 4.Predicate

```java
java.util.function.Predicate<T>接口。->判断型接口
    boolean test(T t)->用于判断的方法,返回值为boolean型
```

```java
public class Demo04Predicate {
    public static void main(String[] args) {
        method(s->s.length()>5,"hello world");
    }

    public  static void method(Predicate<String> predicate,String s){
        boolean b = predicate.test(s);
        System.out.println(b);
    }
}
```

# 第二章.Stream流

```java
1.概述:Stream流中的流,不是IO流的流,可以理解为"流水线"的流
```

> 课程配图（未随笔记提交）

```java
public class Demo01Stream {
    public static void main(String[] args) {
        ArrayList<String> list = new ArrayList<>();
        list.add("古力娜扎");
        list.add("迪丽热巴");
        list.add("马尔扎哈");
        list.add("张三");
        list.add("张无忌");
        list.add("马帅");
        list.add("张杰");
        list.add("鹿晗");
        list.add("蔡徐坤");
        list.add("张三丰");
        list.add("张友人");

    }
}

```

```java
public class Demo01Stream {
    @Test
    public void test01() {
        ArrayList<String> list = new ArrayList<>();
        list.add("古力娜扎");
        list.add("迪丽热巴");
        list.add("马尔扎哈");
        list.add("张三");
        list.add("张无忌");
        list.add("马大帅");
        list.add("张杰");
        list.add("鹿晗");
        list.add("蔡徐坤");
        list.add("张三丰");
        list.add("张友人");

      /*  //1.筛选出姓张的人
        ArrayList<String> list1 = new ArrayList<>();
        for (String s : list) {
            if (s.startsWith("张")) {
                list1.add(s);
            }
        }
        System.out.println(list1);

        //2.筛选出3个字的
        ArrayList<String> list2 = new ArrayList<>();
        for (String s : list1) {
            if (s.length() == 3) {
                list2.add(s);
            }
        }
        System.out.println(list2);

        //打印
        for (String s : list2) {
            System.out.println(s);
        }*/

        //将list集合变成Stream流对象
        Stream<String> stream = list.stream();
        stream.filter(s -> s.startsWith("张")).filter(s -> s.length() == 3).forEach(s -> System.out.println(s));
    }
}

```

## 1.Stream的获取

```java
1.针对于数组:
  of(T...t)
2.针对于集合:Collection接口中有一个方法
  stream()
```

```java
    @Test
    public void test02(){
        //针对于数组
        Stream<String> stream = Stream.of("张三", "李四", "王五", "赵六");
        System.out.println(stream);

        //针对于集合
        ArrayList<String> list = new ArrayList<>();
        list.add("张三");
        list.add("李四");
        list.add("王五");
        list.add("赵六");
        Stream<String> stream1 = list.stream();
        System.out.println(stream1);

    }
```

## 2.Stream的方法

### 2.1.Stream中的forEach方法:void forEach(Consumer<? super T> action);

```java
forEach : 逐一处理->遍历
void forEach(Consumer<? super T> action);

注意:forEach方法是一个[终结方法],使用完之后,Stream流不能用了
```

```java
    @Test
    public void test03(){
        Stream<String> stream = Stream.of("张三", "李四", "王五", "赵六");
/*        stream.forEach(new Consumer<String>() {
            @Override
            public void accept(String s) {
                System.out.println(s);
            }
        });*/
        stream.forEach(s -> System.out.println(s));
    }
```

### 2.2.Stream中的long count()方法

```java
1.作用:统计元素个数
2.注意:count也是一个终结方法
```

```java
    @Test
    public void test04(){
        Stream<String> stream = Stream.of("张三", "李四", "王五", "赵六");
        long count = stream.count();
        System.out.println(count);
    }
```

### 2.3.Stream中的Stream<T> filter(Predicate<? super T> predicate)方法

```java
1.方法:Stream<T> filter(Predicate<? super T> predicate)方法,返回一个新的Stream流对象
2.作用:根据某个条件进行元素过滤
```

```java
  @Test
    public void test05(){
        Stream<String> stream = Stream.of("张三", "李四", "王五", "赵六","张无忌","张三丰");
       /* Stream<String> stream1 = stream.filter(new Predicate<String>() {
            @Override
            public boolean test(String s) {
                return s.length() > 2;
            }
        });

        stream1.forEach(new Consumer<String>() {
            @Override
            public void accept(String s) {
                System.out.println(s);
            }
        });*/

        /*stream.filter(new Predicate<String>() {
            @Override
            public boolean test(String s) {
                return s.length() > 2;
            }
        }).forEach(new Consumer<String>() {
            @Override
            public void accept(String s) {
                System.out.println(s);
            }
        });*/
        stream.filter(s -> s.length() > 2).forEach(s -> System.out.println(s));
    }
```

### 2.4.Stream<T> limit(long maxSize):获取Stream流对象中的前n个元素,返回一个新的Stream流对象

```java
1.Stream<T> limit(long maxSize):获取Stream流对象中的前n个元素,返回一个新的Stream流对象
```

```java
    @Test
    public void test06(){
        Stream<String> stream = Stream.of("张三", "李四", "王五", "赵六","张无忌","张三丰");
       /* Stream<String> stream1 = stream.limit(3);
        stream1.forEach(s -> System.out.println(s));*/
        stream.limit(3).forEach(s -> System.out.println(s));
    }
```

### 2.5.Stream<T> skip(long n): 跳过Stream流对象中的前n个元素,返回一个新的Stream流对象

```java
Stream<T> skip(long n): 跳过Stream流对象中的前n个元素,返回一个新的Stream流对象
```

```java
    @Test
    public void test07(){
        Stream<String> stream = Stream.of("张三", "李四", "王五", "赵六","张无忌","张三丰");
        stream.skip(3).forEach(s -> System.out.println(s));
    }
```

### 2.6.static <T> Stream<T> concat(Stream<? extends T> a, Stream<? extends T> b):两个流合成一个流

```java
1.方法:static <T> Stream<T> concat(Stream<? extends T> a, Stream<? extends T> b):两个流合成一个流
```

```java
 @Test
    public void test08(){
        Stream<String> stream1 = Stream.of("张三", "李四", "王五", "赵六","张无忌","张三丰");
        Stream<String> stream2 = Stream.of("赵四","刘能","广坤");

        Stream<String> stream = Stream.concat(stream1, stream2);
        stream.forEach(s -> System.out.println(s));
    }
```

### 2.7.将Stream流变成集合

```java
从Stream流对象转成集合对象，使用Stream接口方法collect()
```

```java
 @Test
    public void test09(){
        Stream<String> stream = Stream.of("张三", "李四", "王五", "赵六","张无忌","张三丰");
        List<String> list = stream.collect(Collectors.toList());
        System.out.println(list);
    }
```

### 2.8.dinstinct方法

```java
Stream<T> distinct()
元素去重复,重写hashCode和equals方法
```

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Person {
    private String name;
    private Integer age;
}

```

```java
    @Test
    public void test10(){
        Stream<String> stream = Stream.of("张三", "李四", "王五", "赵六","张无忌","张三丰","张三");
        stream.distinct().forEach(s -> System.out.println(s));
        System.out.println("============================");
        Stream<Person> stream1 = Stream.of(new Person("张三", 16), new Person("张三", 16));
        stream1.distinct().forEach(p -> System.out.println(p));

    }
```

### 2.9.转换流中的类型

```java
Stream<R> map(Function<T,R> mapper)-> 转换流中的数据类型
```

```java
    @Test
    public void test11(){
        Stream<Integer> stream = Stream.of(1, 2, 3, 4, 5);
       /* Stream<String> stream2 = (Stream<String>) stream.map(new Function<Integer, String>() {

            @Override
            public String apply(Integer integer) {
                return integer + "";
            }
        });
        stream2.forEach(s -> System.out.println(s+1));*/
        stream.map(i -> i + "").forEach(s -> System.out.println(s+1));
    }
```

### 2.10.Stream流练习

```java
   1. 第一个队伍只要名字为3个字的成员姓名；//filter

   2. 第一个队伍筛选之后只要前3个人；// limit

   3. 第二个队伍只要姓张的成员姓名； //filter

   4. 第二个队伍筛选之后不要前2个人；//skip

   5. 将两个队伍合并为一个队伍；//concat

   6. 打印整个队伍的姓名信息;//foreach
```

```java
public class Demo12Stream {
    public static void main(String[] args) {
        ArrayList<String> one = new ArrayList<>();
        one.add("迪丽热巴");
        one.add("宋远桥");
        one.add("苏星河");
        one.add("老子");
        one.add("庄子");
        one.add("孙子");
        one.add("洪七公");

        ArrayList<String> two = new ArrayList<>();
        two.add("古力娜扎");
        two.add("张无忌");
        two.add("张三丰");
        two.add("赵丽颖");
        two.add("张二狗");
        two.add("张天爱");
        two.add("张三");
    }
}

```

```java
    @Test
    public void test12(){
        ArrayList<String> one = new ArrayList<>();
        one.add("迪丽热巴");
        one.add("宋远桥");
        one.add("苏星河");
        one.add("老子");
        one.add("庄子");
        one.add("孙子");
        one.add("洪七公");

        ArrayList<String> two = new ArrayList<>();
        two.add("古力娜扎");
        two.add("张无忌");
        two.add("张三丰");
        two.add("赵丽颖");
        two.add("张二狗");
        two.add("张天爱");
        two.add("张三");

        Stream<String> streamA = one.stream();
        Stream<String> streamB = two.stream();

       Stream<String> stream1 = streamA.filter(s -> s.length() == 3).limit(3);
       Stream<String> stream2 = streamB.filter(s -> s.startsWith("张")).skip(2);

       //合并
       Stream.concat(stream1, stream2).forEach(s -> System.out.println(s));

        //Stream.concat(streamA.filter(s -> s.length() == 3).limit(3), streamB.filter(s -> s.startsWith("张")).skip(2)).forEach(s -> System.out.println(s));

    }
```

# 第三章.方法引用&其他新特性

## 1.方法引用的介绍

```java
1.概述:就是在Lambda表达式的基础上再次简化
2.条件:
  a.被引用的方法需要在重写的方法中被引用
  b.被引用的方法从参数上以及返回值上要和所在的重写的方法一样
    open(){//无参无返回值的
      引用过eat()//无参无返回值的
    }
  c.干掉重写方法的参数位置以及->,以及被引用方法的参数,将调用方法的.改成::
```

## 2.方法引入的体验

```java
    @Test
    public void test01(){
        Stream<String> stream = Stream.of("张三", "李四", "王五", "赵六");
      /*  stream.forEach(new Consumer<String>() {

            *//**
             *  accept是重写的方法:有String的参数,无返回值
             *  在accept中有一个println方法.println参数是String的,无返回值
             *  可以看干成方法引用
             *//*
            @Override
            public void accept(String s) {
                System.out.println(s);
            }
        });*/
        stream.forEach(System.out::println);
    }
```

## 3.对象名--引用成员方法

```java
1.使用对象名引用成员方法
  格式:
    对象::成员方法名

2.需求:
    函数式接口:Supplier
        java.util.function.Supplier<T>接口
    抽象方法:
        T get()。用来获取一个泛型参数指定类型的对象数据。
        Supplier接口使用什么泛型,就可以使用get方法获取一个什么类型的数据
```

```java
public class Demo02MethodCite {
    public static void main(String[] args) {
        method(() -> " abcde ".trim());
        System.out.println("=============");
        method(" abcde "::trim);
    }

    public static void method(Supplier<String> supplier){
        String data = supplier.get();
        System.out.println(data);
    }
}
```

## 4.类名--引用静态方法

```java
类名--引用静态方法
    格式:
      类名::静态成员方法
```

```java
public class Demo03MethodCite {
    public static void main(String[] args) {
      /* method(new Supplier<Double>() {
           @Override
           public Double get() {
               return Math.random();
           }
       });*/
        method(() -> Math.random());
        System.out.println("==============");
        method(Math::random);
    }

    public static void method(Supplier<Double> supplier){
        Double result = supplier.get();
        System.out.println(result);
    }
}
```

## 5.类--构造引用

```java
1. 类--构造方法引用
   格式:
     构造方法名称::new

2.需求:
    函数式接口:Function
        java.util.function.Function<T,R>接口
    抽象方法:
        R apply(T t)，根据类型T的参数获取类型R的结果。用于数类型转换
```

```java
public class Demo04MethodCite {
    public static void main(String[] args) {
        method(new Function<String, Person>() {
            @Override
            public Person apply(String s) {
                return new Person(s);
            }
        },"张三");
        System.out.println("==================");
        method(s -> new Person(s),"张三");
        System.out.println("==================");
        method(Person::new,"张三");
    }

    public  static void method(Function<String, Person>  function, String name){
        Person person = function.apply(name);
        System.out.println(person);
    }
}
```

## 6.数组--数组引用

```java
数组--数组引用
     格式:
          数组的数据类型[]::new
          int[]::new  创建一个int型的数组
          double[]::new  创建于一个double型的数组
```

```java
public class Demo05MethodCite {
    public static void main(String[] args) {
        method(new Function<Integer, int[]>() {
            @Override
            public int[] apply(Integer integer) {
                return new int[integer];
            }
        },10);
        System.out.println("==================");
        method(integer-> new int[integer],10);
        System.out.println("==================");
        method(int[]::new,10);
    }
    public static void method(Function<Integer,int[]> function,int a){
        int[] arr = function.apply(a);
        System.out.println(arr.length);
    }
}
```

> github -> 搜索毕设

# 第四章.集合框架(单列集合)

```java
1.概述:是一种容器
2.作用:一次性存储多个数据
3.特点:
  a.元素只能存引用类型
  b.长度可变
  c.集合中有很多方法直接操作元素

4.分类:
  a.单列集合:一个元素只由一部分组成
    list.add("张三")
  b.双列集合:一个元素由两部分组成
    map.put(1,"张三") -> key,value -> 跟key和value这种数据格式叫做键值对
```

> 课程配图（未随笔记提交）

# 第五章.Collection接口

```java
1.概述:单列集合的顶级接口
2.创建:创建其实现类对象
  Collection<E> 集合名 = new 实现类对象<>()
3.<E>:泛型,用于统一集合中元素的数据类型的
      a.只能写引用类型,如果不写默认元素类型为Object类型
      b.在创建集合对象的时候,等号前面的泛型必须明确,等号后面的泛型可以不明确
4.常用方法:
  boolean add(E e) : 将给定的元素添加到当前集合中(我们一般调add时,不用boolean接收,因为add一定会成功)
  boolean addAll(Collection<? extends E> c) :将另一个集合元素添加到当前集合中 (集合合并)
  void clear():清除集合中所有的元素
  boolean contains(Object o)  :判断当前集合中是否包含指定的元素
  boolean isEmpty() : 判断当前集合中是否有元素->判断集合是否为空
  boolean remove(Object o):将指定的元素从集合中删除
  int size() :返回集合中的元素个数。
  Object[] toArray(): 把集合中的元素,存储到数组中
```

```java
 @Test
    public void test01(){
        Collection<String> collection = new ArrayList<>();
        //boolean add(E e) : 将给定的元素添加到当前集合中(我们一般调add时,不用boolean接收,因为add一定会成功)
        collection.add("燃灯古佛");
        collection.add("如来佛祖");
        collection.add("弥勒佛");
        collection.add("斗战胜佛");
        collection.add("旃檀功德佛");
        System.out.println(collection);
        //boolean addAll(Collection<? extends E> c) :将另一个集合元素添加到当前集合中 (集合合并)
        Collection<String> collection1 = new ArrayList<>();
        collection1.add("观音菩萨");
        collection1.add("文殊菩萨");
        collection1.add("普贤菩萨");
        collection.addAll(collection1);
        System.out.println(collection);
        //void clear():清除集合中所有的元素
        collection1.clear();
        System.out.println(collection1);
        //boolean contains(Object o)  :判断当前集合中是否包含指定的元素
        boolean b = collection.contains("燃灯古佛");
        System.out.println(b);
        //boolean isEmpty() : 判断当前集合中是否有元素->判断集合是否为空
        System.out.println(collection.isEmpty());
        System.out.println(collection1.isEmpty());
        //boolean remove(Object o):将指定的元素从集合中删除
        collection.remove("燃灯古佛");
        System.out.println(collection);
        //int size() :返回集合中的元素个数。
        System.out.println(collection.size());
        //Object[] toArray(): 把集合中的元素,存储到数组中
        Object[] arr = collection.toArray();
        for (int i = 0; i < arr.length; i++) {
            System.out.println(arr[i]);
        }
    }
```

# 第六章.迭代器

## 1.迭代器基本使用

```java
1.概述:Iterator接口
2.作用:遍历集合
3.获取:
  Iterator<E> iterator()
4.方法:
  boolean hasNext()
  E next()
```

```java
    @Test
    public void test01() {
        ArrayList<String> list = new ArrayList<>();
        list.add("金莲");
        list.add("三上");
        list.add("松下");
        list.add("井上");
        list.add("涛哥");
        //获取迭代器对象
        Iterator<String> iterator = list.iterator();
        while(iterator.hasNext()){
            System.out.println(iterator.next());
        }
    }
```

> ```java
>     @Test
>     public void test01() {
>         ArrayList<String> list = new ArrayList<>();
>         list.add("金莲");
>         list.add("三上");
>         list.add("松下");
>         list.add("井上");
>         list.add("涛哥");
>         //获取迭代器对象
>         Iterator<String> iterator = list.iterator();
>         while(iterator.hasNext()){
>             System.out.println(iterator.next());
>             //System.out.println(iterator.next());
>         }
>     }
> ```
>
> > 课程配图（未随笔记提交）

## 2.迭代器迭代过程

> 课程配图（未随笔记提交）

## 3.迭代器底层原理

```java
1.问题:Iterator<String> iterator = list.iterator(),等号左边是Iterator接口,那么等号右边肯定是Iterator接口的某个实现类,那么Iterator接口到底接收的是哪个实现类

2.如果迭代的是ArrayList集合,Iterator接口指向的就是ArrayList底层的内部类Itr
```

> 课程配图（未随笔记提交）

> ```java
> 如果迭代HashSet集合,Iterator指向的是keyIterator对象
>    ```
>
>    > 课程配图（未随笔记提交）

## 4.并发修改异常

```java
需求:定义一个集合,存储 唐僧,孙悟空,猪八戒,沙僧,遍历集合,如果遍历到猪八戒,往集合中添加一个白龙马
```

```java
    @Test
    public void test03() {
        ArrayList<String> list = new ArrayList<>();
        list.add("唐僧");
        list.add("悟空");
        list.add("八戒");
        list.add("沙僧");
        Iterator<String> iterator = list.iterator();
        while(iterator.hasNext()){
            String element = iterator.next();
            if ("八戒".equals(element)){
                list.add("白龙马");
            }
        }
        System.out.println(list);
    }
```

> > 课程配图（未随笔记提交）
>
> 结论:在使用迭代器的过程中不要随意修改集合长度

```java
int expectedModCount = modCount;
=================================
modCount:实际操作次数
expectedModCount:预期操作次数
=================================
iterator.next()
 public E next() {
    checkForComodification();
 }

final void checkForComodification() {
    if (modCount != expectedModCount)
        throw new ConcurrentModificationException();//并发修改异常
}

出现并发修改异常的底层原因:当实际操作次数和预期操作次数不相等时,出现并发修改异常
```

```java
我们干啥了,导致了实际操作次数和预期操作次数不相等了
=============================================
list.add("白龙马")
public boolean add(E e) {
    modCount++;
}
```

```java
完整的结论:我们在迭代的过程中,调用了add方法,add底层修改了实际操作次数,那么导致了预期操作次数和实际操作次数不相等了,就出现了并发修改异常
```

> 扩展:ListIterator
>
> ```java
>     @Test
>     public void test04() {
>         ArrayList<String> list = new ArrayList<>();
>         list.add("唐僧");
>         list.add("悟空");
>         list.add("八戒");
>         list.add("沙僧");
>         ListIterator<String> iterator = list.listIterator();
>         while(iterator.hasNext()){
>             String element = iterator.next();
>             if ("八戒".equals(element)){
>                 iterator.add("白龙马");
>             }
>         }
>         System.out.println(list);
>     }
> ```
>

# 第七章.数据结构

```properties
数据结构是一种具有一定逻辑关系，在计算机中应用某种存储结构，并且封装了相应操作的数据元素集合。它包含三方面的内容，逻辑关系、存储关系及操作。
```

### 为什么需要数据结构

```properties
随着应用程序变得越来越复杂和数据越来越丰富，几百万、几十亿甚至几百亿的数据就会出现，而对这么大对数据进行搜索、插入或者排序等的操作就越来越慢，数据结构就是用来解决这些问题的。
```

> 课程配图（未随笔记提交）：课堂配图

> 课程配图（未随笔记提交）：课堂配图



数据的逻辑结构指反映数据元素之间的逻辑关系，而与他们在计算机中的存储位置无关：

* 集合（数学中集合的概念）：数据结构中的元素之间除了“同属一个集合” 的相互关系外，别无其他关系；
* 线性结构：数据结构中的元素存在一对一的相互关系；
* 树形结构：数据结构中的元素存在一对多的相互关系；
* 图形结构：数据结构中的元素存在多对多的相互关系。

> 课程配图（未随笔记提交）：课堂配图

数据的物理结构/存储结构：是描述数据具体在内存中的存储（如：顺序结构、链式结构、索引结构、哈希结构）等，一种数据逻辑结构可表示成一种或多种物理存储结构。

数据结构是一门完整并且复杂的课程，那么我们今天只是简单的讨论常见的几种数据结构，让我们对数据结构与算法有一个初步的了解。

## 1.栈

```java
先进后出-> 手枪压子弹
```

## 2.队列

```java
先进先出 -> 排队
```

## 3.数组

```java
1.特点:查询快,增删慢
2.查询快:有索引,可以直接根据索引找到对应的元素
  增删慢:定长
```

## 4.链表

```java
1.特点:查询慢,增删快
2.分类:
  单向链表
  双向链表
```

### 4.1单向链表

```java
1.一个节点由2部分构成
  a.数据域
  b.指针域
2.特点:
  前面节点记录后面节点地址
  后面节点不记录前面节点地址
3.注意:
  集合底层如果是单向链表,无法保证元素有序
```

> 课程配图（未随笔记提交）

### 4.2双向链表

```java
1.一个节点由3部分构成
  a.指针域
  b.数据域
  c.指针域
2.特点:
  前面节点记录后面节点地址
  后面节点记录前面节点地址
3.注意:
  集合底层如果是双向链表,可以保证元素有序
```

> 课程配图（未随笔记提交）

# 第八章.List接口

```java
1.概述:Collection下的子接口
2.实现类:
  ArrayList   LinkedList   Vector
```

# 第九章.List集合下的实现类

## 1.ArrayList集合

```java
1.概述:List接口的实现类
2.特点:
  a.元素有序
  b.有索引
  c.元素可重复
  d.线程不安全
3.数据结构:数组
```

### 1.1.ArrayList集合使用

```java
方法:
  boolean add(E e)  -> 将元素添加到集合中->尾部(add方法一定能添加成功的,所以我们不用boolean接收返回值)
  void add(int index, E element) ->在指定索引位置上添加元素
  boolean remove(Object o) ->删除指定的元素,删除成功为true,失败为false
  E remove(int index) -> 删除指定索引位置上的元素,返回的是被删除的那个元素
  E set(int index, E element) -> 将指定索引位置上的元素,修改成后面的element元素
  E get(int index) -> 根据索引获取元素
  int size()  -> 获取集合元素个数
```

```java
    @Test
    public void test01() {
        ArrayList<String> list = new ArrayList<>();
        //boolean add(E e)  -> 将元素添加到集合中->尾部(add方法一定能添加成功的,所以我们不用boolean接收返回值)
        list.add("张无忌");
        list.add("张三");
        list.add("张三丰");
        list.add("张浩");
        System.out.println(list);
        //void add(int index, E element) ->在指定索引位置上添加元素
        list.add(1, "张翠山");
        System.out.println(list);
        //boolean remove(Object o) ->删除指定的元素,删除成功为true,失败为false
        list.remove("张三");
        System.out.println(list);
        //E remove(int index) -> 删除指定索引位置上的元素,返回的是被删除的那个元素
        String element = list.remove(1);
        System.out.println(element);
        System.out.println(list);
        //E set(int index, E element) -> 将指定索引位置上的元素,修改成后面的element元素
        String element2 = list.set(0, "小昭");
        System.out.println(element2);
        System.out.println(list);
        //E get(int index) -> 根据索引获取元素
        System.out.println(list.get(0));
        //int size()  -> 获取集合元素个数
        System.out.println(list.size());
    }

    @Test
    public void test02() {
        ArrayList<String> list = new ArrayList<>();
        list.add("张三");
        list.add("李四");
        list.add("王五");
        for (int i = 0; i < list.size(); i++) {
            System.out.println(list.get(i));
        }

        System.out.println("=====================");
        for (String s : list) {
            System.out.println(s);
        }
    }
```

## 2.增强for

```java
1.格式:
  for(元素类型 变量名 : 被遍历的集合名或者数组名){
      这个变量名就代表每一个元素
  }
2.作用:遍历数组或者集合
3.快捷键:
  集合名或者数组名.for
4.注意:在使用增强for遍历集合的过程中,不要随意修改集合长度
  a.使用增强for遍历集合,底层实现原理为迭代器
  b.使用增强for遍历数组,底层实现原理为普通for
```

```java
     @Test
    public void test01() {
        ArrayList<String> list = new ArrayList<>();
        list.add("张三");
        list.add("李四");
        list.add("王五");
        for (String s : list) {
            System.out.println(s);
        }
    }
```

> 课程配图（未随笔记提交）
