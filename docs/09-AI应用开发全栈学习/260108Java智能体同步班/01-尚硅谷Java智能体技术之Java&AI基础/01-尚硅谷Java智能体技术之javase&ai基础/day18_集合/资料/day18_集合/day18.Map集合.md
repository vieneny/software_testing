# day18.Map集合

```java
课前回顾:
  1.ArrayList:底层是一个数组
    a.第一次add的时候创建一个长度为10的数组
    b.如果超出范围,会自动扩容
    c.扩容1.5倍
  2.LinkedList:
    a.特点:
      有序 无索引 元素可重复 线程不安全
    b.数据结构:双向链表
    c.方法:大量直接操作首尾的方法
  3.Collections:集合工具类
    addAll  shuffle  sort sort(List list,比较器)
  4.泛型:
    a.含有泛型的类:  public class 类名<E>
    b.含有泛型的方法: 修饰符 <E> 返回值类型 方法名(参数){}
    c.含有泛型的接口: public interface 接口名<E>{}
  5.泛型的上限和下限:
    <? extends 类名>
    <? super 类名>
  6.HashSet:
    无序 无索引 元素不可重复 线程不安全
    哈希表
  7.LinkedHashSet
    有序 无索引 元素不可重复 线程不安全
    哈希表+双向链表
  8.set集合如何保证元素唯一的:  元素底层必须重写hashCode和equals方法
    先比较哈希值,再比较内容
    如果哈希值不一样,存
    如果哈希值一样,内容不一样,存
    如果哈希值一样,内容也一样,去重复

今日重点:
  1.知道HashMap和LinkedHashMap的特点以及使用
  2.知道TreeSet和TreeMap的特点以及基本使用
  3.知道HashMap和Hashtable的区别
  4.会使用Properties集合以及它的使用场景
  5.知道哈希表存元素的细节
```

# 第一章.Map集合

<img src="image/image-20260202093255244.png" alt="image-20260202093255244" style="zoom:80%;" />

## 1.Map的介绍

```java
1.概述:双列集合的顶级接口
2.实现类:
  HashMap LinkedHashMap TreeMap Hashtable Properties
3.啥叫双列集合:一个元素由两部分构成
  key和value(键值对)
```

## 2.HashMap的介绍和使用

```java
1.概述:是Map接口的实现类
2.特点:
  a.无序
  b.无索引
  c.key唯一,value可重复
  d.线程不安全
  e.可以存null
3.数据结构:
  哈希表
4.方法:
  V put(K key, V value)  -> 添加元素,返回的是被替换的value值
  V remove(Object key)  ->根据key删除键值对,返回的是被删除的value
  V get(Object key) -> 根据key获取value
  boolean containsKey(Object key)  -> 判断集合中是否包含指定的key
  Collection<V> values() -> 获取集合中所有的value,转存到Collection集合中
  Set<K> keySet()->将Map中的key获取出来,转存到Set集合中
  Set<Map.Entry<K,V>> entrySet()->获取Map集合中的键值对,转存到Set集合中
```

```java
    @Test
    public void test01() {
        HashMap<String, String> map = new HashMap<>();
        //V put(K key, V value)  -> 添加元素,返回的是被替换的value值
        map.put("1","张三");
        map.put("2","李四");
        map.put("2", "王五");
        map.put("3", "赵六");
        map.put("4", "田七");
        map.put("5", "朱八");
        //map.put(null,null);
        System.out.println(map);
        //V remove(Object key)  ->根据key删除键值对,返回的是被删除的value
        String value = map.remove("1");
        System.out.println(value);
        System.out.println(map);
        //V get(Object key) -> 根据key获取value
        String value1 = map.get("2");
        System.out.println(value1);
        //boolean containsKey(Object key)  -> 判断集合中是否包含指定的key
        boolean b = map.containsKey("2");
        System.out.println(b);
        //Collection<V> values() -> 获取集合中所有的value,转存到Collection集合中
        Collection<String> values = map.values();
        System.out.println(values);
    }
```

```java
1.LinkedHashMap概述:是HashMap的子类
2.特点:
  a.有序
  b.无索引
  c.key唯一,value可重复
  d.线程不安全
3.数据结构:
  哈希表+双向链表
4.使用:和HashMap一样
```

```java
    @Test
    public void test02() {
        LinkedHashMap<String, String> map = new LinkedHashMap<>();
        map.put("1","张三");
        map.put("2","李四");
        map.put("2", "王五");
        map.put("5", "朱八");
        map.put("4", "田七");
        map.put("3", "赵六");
        System.out.println(map);
    }
```

## 3.HashMap的两种遍历方式

### 3.1.方式1:获取key,根据key再获取value

```java
Set<K> keySet()->将Map中的key获取出来,转存到Set集合中
```

```java
    @Test
    public void test03() {
        HashMap<String, String> map = new HashMap<>();
        map.put("大郎","金莲");
        map.put("岩朔","王婆");
        map.put("硕鑫","雨姐");
        Set<String> set = map.keySet();
        for (String key : set) {
            String value = map.get(key);
            System.out.println(key + "=" + value);
        }
    }
```

### 3.2.方式2:同时获取key和value

<img src="image/image-20260202102923316.png" alt="image-20260202102923316" style="zoom:80%;" />

```java
Set<Map.Entry<K,V>> entrySet()->获取Map集合中的键值对,转存到Set集合中
```

```java
    @Test
    public void test04() {
        HashMap<String, String> map = new HashMap<>();
        map.put("大郎","金莲");
        map.put("岩朔","王婆");
        map.put("硕鑫","雨姐");
        Set<Map.Entry<String, String>> set = map.entrySet();
        for (Map.Entry<String, String> entry : set) {
            String key = entry.getKey();
            String value = entry.getValue();
            System.out.println(key + "=" + value);
        }
    }
```

## 4.Map存储自定义对象时如何保证key唯一

```java
1.注意:Set集合存储元素都是存到了map集合的key的位置,所以Set集合保证元素唯一和Map集合保证key唯一的方式一样
      key需要重写hashCode和equals方法
2.去重复过程:
  先比较key的哈希值,再比较key的内容
  如果哈希值不一样,存
  如果哈希值一样,内容不一样,存
  如果哈希值一样,内容也一样,去重复(value覆盖)
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
    public void test05() {
        HashMap<Person, String> map = new HashMap<>();
        map.put(new Person("涛哥", 18), "廊坊");
        map.put(new Person("硕鑫", 20), "济南");
        map.put(new Person("岩朔",22), "通辽");
        map.put(new Person("彭思",16),"辽宁");
        map.put(new Person("彭思",16),"北京");
        System.out.println(map);
    }
```

## 5.Map的练习

```java
需求:用Map集合统计字符串中每一个字符出现的次数
步骤:
  1.指定一个字符串
  2.创建一个map集合,key指定为String代表字符,value为Integer代表字符个数
  3.遍历字符串,用每一个字符去判断,Map中是否包含字符
  4.如果不包含,将字符和1存到map中
  5.如果包含,根据字符将对应的value获取出来,让其+1,并重新存入
  6.输出map
```

<img src="image/image-20260202105006286.png" alt="image-20260202105006286" style="zoom:80%;" />

```java
 @Test
    public void test06() {
        //1.指定一个字符串
        String s = "adfasdfas";
        //2.创建一个map集合,key指定为String代表字符,value为Integer代表字符个数
        HashMap<String, Integer> map = new HashMap<>();
        //3.遍历字符串,用每一个字符去判断,Map中是否包含字符
        char[] chars = s.toCharArray();
        for (char c : chars) {
            String key = c + "";
            //4.如果不包含,将字符和1存到map中
            if (!map.containsKey(key)) {
                map.put(key, 1);
            } else {
                //5.如果包含,根据字符将对应的value获取出来,让其+1,并重新存入
                Integer value = map.get(key);
                value++;
                map.put(key, value);
            }
        }
        //6.输出map
        System.out.println(map);
    }
```

# 第二章.TreeSet

```java
1.概述:是Set接口的实现类
2.特点:
  a.可以对元素进行排序
  b.无索引
  c.元素不可重复
  d.线程不安全
3.数据结构:
  红黑树
4.方法:和HashSet一样
5.构造:
  TreeSet() :对元素进行自然排序(ASCII码值)
  TreeSet(Comparator<? super E> comparator) :按照指定规则排序
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
    public void test01() {
        TreeSet<String> set = new TreeSet<>();
        set.add("b.曲项向天歌");
        set.add("a.鹅鹅鹅");
        set.add("d.红掌拨清波");
        set.add("c.白毛浮绿水");
        System.out.println(set);
    }

    @Test
    public void test02() {
        TreeSet<Person> set = new TreeSet<>(new Comparator<Person>() {
            @Override
            public int compare(Person o1, Person o2) {
                return o1.getAge()-o2.getAge();
            }
        });
        set.add(new Person("张三", 18));
        set.add(new Person("李四", 15));
        set.add(new Person("王五", 20));
        System.out.println(set);
    }
```

# 第三章.TreeMap

```java
1.概述:是Map接口的实现类
2.特点:
  a.可以对key进行排序
  b.无索引
  c.key唯一,value可重复
  d.线程不安全
3.数据结构:
  红黑树
4.方法:和HashMap一样
5.构造:
  TreeMap() 将key按照自然排序(ASCII码)
  TreeMap(Comparator<? super K> comparator) 将key按照指定的顺序排序
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
    public void test01() {
        TreeMap<String, String> map = new TreeMap<>();
        map.put("b", "汗滴禾下土");
        map.put("a", "锄禾日当午");
        map.put("c", "谁知盘中餐");
        map.put("d", "粒粒皆辛苦");
        System.out.println(map);
    }

    @Test
    public void test02() {
        TreeMap<Person, String> map = new TreeMap<>(new Comparator<Person>() {
            @Override
            public int compare(Person o1, Person o2) {
                return o2.getAge()-o1.getAge();
            }
        });
        map.put(new Person("张三", 18), "杭州");
        map.put(new Person("李四", 15), "上海");
        map.put(new Person("王五", 20), "北京");
        System.out.println(map);
    }
```

# 第四章.Hashtable和Vector集合(了解)

## 1.Hashtable集合

```java
1.概述:是Map接口的实现类
2.特点:
  a.无序
  b.无索引
  c.key唯一,value可重复
  d.线程安全
  e.不能存null
3.数据结构:
  哈希表
4.方法:
  和HashMap一样
```

```java
    @Test
    public void test01() {
        Hashtable<String, String> table = new Hashtable<>();
        table.put("1", "张三");
        table.put("2", "李四");
        table.put("3", "王五");
        //table.put(null,null);
        System.out.println(table);
    }
```

> Hashtable和HashMap区别:
>
> 相同点:元素无序,无索引,key唯一,都是哈希表
>
> 不同点:HashMap线程不安全,Hashtable线程安全
>
> ​               HashMap可以存储null键null值;Hashtable不能

## 2.Vector集合

```java
1.概述:是List的实现类
2.特点:
  a.元素有序
  b.有索引
  c.元素可重复
  d.线程安全
3.数据结构:
  数组

4.源码分析:
  a.用无参构造new对象,会直接创建一个长度为10的数组,如果超出了数组容量,自动扩容,扩容2倍
  b.用有参构造new对象,会创建一个指定长度的数组,如果超出了数组容量,自动扩容,按照指定的容量增量扩容
```

```java
     @Test
    public void test01() {
        Vector<String> vector = new Vector<>();
        vector.add("张三");
        vector.add("李四");
        vector.add("王五");
        System.out.println(vector);
        for (String s : vector) {
            System.out.println(s);
        }
    }
```

> ```java
> Vector<Integer> vector = new Vector<>();
> public Vector() {
>     this(10);
> }
> public Vector(int initialCapacity) {
>     this(initialCapacity, 0);
> }
>
> public Vector(int initialCapacity->10, int capacityIncrement->0) {
>     super();
>     if (initialCapacity < 0)
>         throw new IllegalArgumentException("Illegal Capacity: "+
>                                            initialCapacity);
>     //this.elementData = new Object[10]
>     this.elementData = new Object[initialCapacity];
>     this.capacityIncrement = capacityIncrement;
> }
>
> ======================================
> 假如我们add了第11个元素,需要自动扩容,每次2倍
> vector.add(1);
> public synchronized boolean add(E e) {
>     modCount++;
>     add(e, elementData, elementCount);
>     return true;
> }
> private void add(E e, Object[] elementData, int s) {
>     if (s == elementData.length)
>         elementData = grow();
>     elementData[s] = e;
>     elementCount = s + 1;
> }
> private Object[] grow() {
>     return grow(elementCount + 1);
> }
> private Object[] grow(int minCapacity) {
>     int oldCapacity = elementData.length;
>     int newCapacity = ArraysSupport.newLength(oldCapacity,
>             minCapacity - oldCapacity, /* minimum growth */
>             capacityIncrement > 0 ? capacityIncrement : oldCapacity
>                                        /* preferred growth */);
>     return elementData = Arrays.copyOf(elementData, newCapacity);
> }
> ```
>
> ```java
> Vector<Integer> vector = new Vector<>(10,5);
> public Vector(int initialCapacity, int capacityIncrement) {
>     super();
>     if (initialCapacity < 0)
>         throw new IllegalArgumentException("Illegal Capacity: "+
>                                            initialCapacity);
>     this.elementData = new Object[initialCapacity];
>     this.capacityIncrement = capacityIncrement;
> }
>
> ==========================================================
> 假如我们add了第11个元素,需要自动扩容,每次扩容按照老容量+容量增量
> vector.add(1);
> public synchronized boolean add(E e) {
>     modCount++;
>     add(e, elementData, elementCount);
>     return true;
> }
> private void add(E e, Object[] elementData, int s) {
>     if (s == elementData.length)
>         elementData = grow();
>     elementData[s] = e;
>     elementCount = s + 1;
> }
> private Object[] grow() {
>     return grow(elementCount + 1);
> }
> private Object[] grow(int minCapacity) {
>     int oldCapacity = elementData.length;
>     int newCapacity = ArraysSupport.newLength(oldCapacity,
>             minCapacity - oldCapacity, /* minimum growth */
>             capacityIncrement > 0 ? capacityIncrement : oldCapacity
>                                        /* preferred growth */);
>     return elementData = Arrays.copyOf(elementData, newCapacity);
> }
> ```
>

# 第五章.Properties集合(属性集)

```java
1.概述:是Hashtable的子类
2.特点:
  a.无序
  b.无索引
  c.key唯一,value可重复
  d.线程安全
  e.key和value固定为String
3.数据结构:
  哈希表
4.特有方法:
  a.setProperty(String key, String value)  存键值对
  b.String getProperty(String key)  根据key获取value
  c.Set<String> stringPropertyNames()  获取所有的key保存到set集合中,类似于keySet
  d.void load(InputStream inStream)  -> 将流中的数据加载到properties集合中
```

```java
    @Test
    public void test01() {
        Properties properties = new Properties();
        properties.setProperty("username", "tom");
        properties.setProperty("password", "123456");

        Set<String> set = properties.stringPropertyNames();
        for (String key : set) {
            String value = properties.getProperty(key);
            System.out.println(key + "=" + value);
        }
    }
```

> ```java
> 使用场景:用于解析配置文件(xxx.properties     xxx.xml    xxx.yml)
>
> 配置文件:存放一些"硬数据"的文件,比如用户名,密码,地址等这些数据我们不能直接放到源码中,将来我们的密码改了,地址改了,我们不能反复去修改源码,我们需要将这些硬数据放到配置文件中,到时候我们直接用代码动态读取配置文件中的内容;好处就是将来如果我们修改这些数据,我们直接去配置文件中修改,不用修改源代码
> ```
>
> ```java
> 1.需要在resources资源目录下创建xxx.properties的文件 -> 右键 -> file -> xxx.properties
> 2.在properties配置文件中配置数据
>   a.数据都是key=value形式
>   b.一个键值对写完需要换行写下一对
>   c.key和value都是字符串的,但是不要加""
>   d.尽量不要写中文
> ```
>
> ```properties
> username=root
> password=1234
> ```
>
> ```java
>     @Test
>     public void test02()throws Exception {
>         Properties properties = new Properties();
>         /*
>            类名.class -> 获取的是这个类的Class对象
>            Class对象中有一个方法:getClassLoader() -> 获取的是类的加载器 -> 返回的是ClassLoader对象
>            ClassLoader对象中有一个方法:getResourceAsStream("resources资源目录下的配置文件名"),返回的是InputStream对象
>
>            这种操作可以直接扫描resources资源目录下的配置文件
>          */
>         InputStream in = Demo01Properties.class.getClassLoader().getResourceAsStream("pro.properties");
>
>         //利用load方法将流中的数据加载到Properties集合中
>         properties.load(in);
>
>         String username = properties.getProperty("username");
>         String password = properties.getProperty("password");
>         System.out.println(username + ":" + password);
>     }
> ```

# 第六章.集合嵌套

## 1.List嵌套List

```java
需求:创建2个List集合,每个集合中分别存储一些字符串,将2个集合存储到第3个List集合中
```

```java
    @Test
    public void listInList(){
        ArrayList<String> list1 = new ArrayList<>();
        list1.add("张三");
        list1.add("李四");

        ArrayList<String> list2 = new ArrayList<>();
        list2.add("王五");
        list2.add("赵六");

        ArrayList<ArrayList<String>> list = new ArrayList<>();
        list.add(list1);
        list.add(list2);

        for (ArrayList<String> arrayList : list) {
            for (String s : arrayList) {
                System.out.println(s);
            }
        }
    }
```

## 2.List嵌套Map

```java
1班级有三名同学，学号和姓名分别为：1=张三，2=李四，3=王五，2班有三名同学，学号和姓名分别为：1=黄晓明，2=杨颖，3=刘德华,请将同学的信息以键值对的形式存储到2个Map集合中，再将2个Map集合存储到List集合中。
```

```java
    @Test
    public void listInMap(){
        HashMap<Integer, String> map1 = new HashMap<>();
        map1.put(1, "张三");
        map1.put(2, "李四");

        HashMap<Integer, String> map2 = new HashMap<>();
        map2.put(3, "王五");
        map2.put(4, "赵六");

        ArrayList<HashMap<Integer, String>> list = new ArrayList<>();
        list.add(map1);
        list.add(map2);

        for (HashMap<Integer, String> map : list) {
            Set<Map.Entry<Integer, String>> set = map.entrySet();
            for (Map.Entry<Integer, String> entry : set) {
                System.out.println(entry.getKey() + "=" + entry.getValue());
            }
        }
    }
```

## 3.Map嵌套Map_作业

```java
- JavaSE  集合 存储的是 学号 键，值学生姓名
  - 1(key)  张三(value)
  - 2  李四

- JavaEE 集合 存储的是 学号 键，值学生姓名
  - 1  王五
  - 2  赵六
```

```java
作业
  小map的key为学号,value为姓名
  大map的key为字符串(javase,javaee),value为小map
```

```java

```

> ArrayList
>
> ```java
>1.元素有序
> 2.有索引
> 3.元素可重复
> 4.线程不安全
> 5.数据结构:数组
> ```
>
> LinkedList
>
> ```java
>1.元素有序
> 2.无索引
> 3.元素可重复
> 4.线程不安全
> 5.数据结构:双向链表
> ```
>
> Vector
>
> ```java
>1.元素有序
> 2.有索引
> 3.元素可重复
> 4.线程安全
> 5.数据结构:数组
> ```
>
> HashSet
>
> ```java
>1.元素无序
> 2.无索引
> 3.元素唯一
> 4.线程不安全
> 5.数据结构:哈希表
> ```
>
> LinkedHashSet
>
> ```java
>1.元素有序
> 2.无索引
> 3.元素唯一
> 4.线程不安全
> 5.数据结构:哈希表+双向链表
> ```
>
> TreeSet
>
> ```java
>1.对元素进行排序
> 2.无索引
> 3.元素唯一
> 4.线程不安全
> 5.数据结构:红黑树
> ```

> HashMap
>
> ```java
> 1.无序
> 2.无索引
> 3.key唯一,value可重复
> 4.线程不安全
> 5.可以存null键null值
> 6.数据结构:哈希表
> ```
>
> LinkedHashMap
>
> ```java
> 1.有序
> 2.无索引
> 3.key唯一,value可重复
> 4.线程不安全
> 5.可以存null
> 6.数据结构:哈希表+双向链表
> ```
>
> TreeMap
>
> ```java
> 1.可以对key进行排序
> 2.无索引
> 3.key唯一,value可重复
> 4.线程不安全
> 5.key不能为null
> 6.数据结构:红黑树
> ```
>
> Hashtable
>
> ```java
> 1.无序
> 2.无索引
> 3.key唯一,value可重复
> 4.线程安全
> 5.不能存null
> 6.数据结构:哈希表
> ```
>
> Properties
>
> ```java
> 1.无序
> 2.无索引
> 3.key唯一,value可重复
> 4.线程安全
> 5.key和value只能是String
> 6.数据结构:哈希表
>
> 是唯一一个能和IO流结合使用的集合,解析配置文件使用
> ```

# 第七章.哈希表

```java
  a.哈希表底层数组默认长度为16,是第一次put的时候才会创建长度为16的数组
  b.哈希表有一个默认的加载因子(扩容临界值)0.75F,代表的是数组存储达到百分之75的时候
扩容
  c.每次扩容:2倍
  d.链表长度达到8并且数组容量大于等于64时,链表会转成红黑树,否则两个条件有一个不满足,会扩容
  e.如果在同一个索引下删除元素,元素个数小于等于6了,红黑树会自动转回链表
```

<img src="img/1744099603792.png" alt="1744099603792" style="zoom:80%;" />

> 1.问题:哈希表中有数组的存在,但是为啥说没有索引呢?
>
> 将来存元素,同一个索引位置上可能存储多个元素,如果按照索引来获取元素的话,咱们不知道要获取哪个元素
>
> 所以哈希表取消了按照索引操作元素的方法
>
> 2.问题:为啥说HashMap是无序的,LinkedHashMap是有序的呢?
>
> 原因:HashMap的链表是单向链表
>
> <img src="image/1754987223185.png" alt="1754987223185" style="zoom:80%;" />
>
> ​        LinkedHashMap链表是双向链表
>
> <img src="image/1754987257465.png" alt="1754987257465" style="zoom:80%;" />

# 第八章.AI开发工具_代码生成器

## 1 几款AI 原生 IDE_讲

以下是几款与 **Trae**（字节跳动的 AI 原生 IDE）同类型的 **AI 开发工具**，它们均采用 **AI 原生设计**，支持自然语言编程、智能代码生成和全流程开发辅助：

| **工具名称**   | **开发公司**                  | **AI 模型**                                      | **核心优势**                                                 | **适用场景**                       | **定价**                   |
| :------------- | :---------------------------- | :----------------------------------------------- | :----------------------------------------------------------- | :--------------------------------- | :------------------------- |
| **Cursor**     | Anysphere                     | Claude 5 Sonnet、GPT-4o、DeepSeek-V3（可自定义） | - **项目级代码理解**（@Codebase） - **Composer 多文件编辑** - **智能预测 & 自动修复** | 全栈开发、复杂项目重构、企业级应用 | **$20/月**（Pro 版）       |
| **Windsurf**   | Codeium                       | Cascade（自研）、Claude 5、GPT-4o                | - **Agent 模式**（多步任务执行） - **上下文固定（Context Pinning）** - **新手友好 UI** | 中小型项目、团队协作、快速迭代开发 | **$15/月**（Pro 版）       |
| **Bolt.new**   | StackBlitz                    | 自研模型（未公开）                               | - **浏览器内全栈开发** - **对话式 AI 编程** - **云端协作**   | Web 开发、快速原型验证             | **$20/月**（Pro 版）       |
| **Copilot++**  | GitHub（微软）                | GPT-4 Turbo、Claude 5（可选）                    | - **GitHub 深度集成** - **CI/CD 自动化** - **企业级安全**    | GitHub 生态、企业 DevOps 流程      | **$10/月**（个人版）       |
| **Continue**   | Continue 团队（国际开源社区） | 支持 **Llama 3、DeepSeek、Ollama**（本地部署）   | - **完全离线运行** - **隐私优先** - **可微调本地模型**       | 金融/军工等高安全需求开发          | **免费**（需本地算力）     |
| **Trae**       | 字节跳动                      | 豆包1.5-pro、DeepSeek R1/V3、GPT-4o（国际版）    | - **Builder 模式**（自然语言生成项目） - **中文优化** - **腾讯/阿里云集成** | 国内开发者、全栈 AI 开发           | **免费**（国内版）         |
| **CodeFlying** | 码上飞团队                    | 自研模型（低代码优化）                           | - **低代码 + AI 生成** - **全流程自动化** - **适配微信小程序/H5** | 快速应用开发、初创团队             | **免费试用**（企业版收费） |

## 2 插件管理

```java
直接安装
    Language Support for Java
    Extension Pack for Java
    JetBrains Idea Product Icon Theme
    JetBrains Idea Product
```

## 3 内置大模型

Trae 预置了一系列业内表现比较出色的模型，你可以直接切换不同的模型进行使用。此外，Trae 还支持通过 API 密钥（API Key）接入自定义模型，从而满足个性化的需求。

> 切换模型

在 AI 对话输入框的右下角，点击当前模型名称，打开模型列表，然后选择你想使用的模型。各个模型的能力不同，你可以将鼠标悬浮至模型名称上，然后查看该模型支持的能力。

![image-20250625175954080](image/image-20250625175954080.png)

> **添加自定义模型**

如果你希望使用预置模型之外的其它模型，或者想使用自己的模型资源，则可以通过 API 密钥连接你自己的模型资源或其他第三方模型服务商。

- 在 AI 对话框右上角，点击 **设置** 图标 > **模型**，
- 点击 **+ 添加模型** 按钮。

![image-20250625180046942](image/image-20250625180046942.png)

- 选择 **服务商**。可选项有：Anthropic、DeepSeek、OpenRouter、火山引擎、硅基流动、阿里云、腾讯云、模力方舟、BytePlus、Gemini。

- 选择 **模型**：

  - 直接从列表中选择 Trae 为每个服务商预置的模型（均为默认版本）。


  - 若你希望使用其他模型或使用特定版本的模型，点击列表中的 **使用其他模型**，然后在输入框中填写模型 ID。


- 填写 **API 密钥**。

  - Trae 将调用服务商的接口来检测 API 密钥是否有效。可能的结果如下：


  - 若连接成功，该自定义模型会被添加。


  - 若连接失败，**添加模型** 窗口中展示错误信息和服务商返回的错误日志，你可以参考这些信息排查问题。

## 4 功能演示_讲

提示词1：

```java
我是一个Java初学者，基于JDK17帮我实现一个客户管理系统。
包含增删改查功能
(1)只用数组，不要用集合、数据库
(2)分为com.atguigu.bean、
com.atguigu.service、
com.atguigu.view、
com.atguigu.main包，主类放到main包中
(3)基于文本界面实现
```

提示词2：

```txt
我是一个Java初学者，基于JDK17帮我实现一个客户管理系统。
并且帮我实现增删改查功能
(1)可以用集合，但是不用数据库
(2)分为com.atguigu.bean、
com.atguigu.service、
com.atguigu.view、
com.atguigu.main包，主类放到main包中
(3)基于文本界面实现
(4)可以使用maven，依赖lombok
```

## 5.Trae结合idea中的maven工程生成代码

```java
1.在idea中创建一个maven工程
2.在Trae中打开idea中的maven工程
  文件->打开文件夹->选择在idea中创建的maven工程
```
