# 	day14.IO流

```java
课前回顾:
  1.String:代表的是字符串
  2.构造:
    String()
    String(String str)
    String(byte[] bytes)
    String(char[] chars)
    String(byte[] bytes,int offset,int count)
    String(char[] chars,int offset,int length)
  3.比较功能:
    equals  equalsIgnoreCase
  4.获取功能:
    concat charAt indexOf subString subString length
  5.转换功能:
    toCharArray getBytes getBytes(String charsetName) replace
  6.分割功能:
    split
  7.其他功能:
    contains endsWith startsWith toLowerCase toUpperCase trim
  8.StringBuilder:主要用于拼接字符串
    append reverse toString
  9.正则表达式:matches("正则表达式")
  10.文本块:"""

           """

今日重点:
  all
```

# 第一章.字节流

## 1.IO流介绍以及输入输出以及流向的介绍

```java
1.从专业角度概述,什么叫做IO流:将数据从一个设备上传到另外一个设备上的技术
  a.输出(Output):谁发数据谁就是输出
  b.输入(Input):谁接数据谁就是输入

2.从javase角度概述,什么叫做IO流:将数据从内存上写到硬盘上,然后还能从硬盘上将数据读回来的技术
  a.输出(Output):将数据从内存中写到硬盘上
  b.输入(Input):将数据从硬盘上读到内存中
```

> 课程配图（未随笔记提交）

## 2.IO流分类

```java
1.字节流:一切皆字节(万能流),但是这个万能流侧重复制操作来说的
  字节输出流:OutputStream(抽象类)
  字节输入流:InputStream(抽象类)
2.字符流:主要对文本文档进行读写操作
  字符输出流:Writer(抽象类)
  字符输入流:Reader(抽象类)
```

> IO流四大基类:
>
>   OutputStream InputStream Writer Reader

## 4.OutputStream中子类[FileOutputStream]的介绍以及方法的简单介绍

```java
1.概述:字节输出流 -> OutputStream(抽象类) -> 子类:FileOutputStream
2.作用:往硬盘上写数据
3.构造:
  a.FileOutputStream(File file)
  b.FileOutputStream(String path)
  c.FileOutputStream(String path,boolean append) -> 如果append为true,就是追加,续写,每次运行老数据不会被覆盖
4.方法:
  write(int a) 一次写一个字节
  write(byte[] bytes) 一次写一个字节数组
  write(byte[] bytes,int offset,int count)一次写一个字节数组一部分
  close():关闭资源
5.特点:
  a.如果之前没有创建指定的文件,运行时会自动创建
  b.默认情况下,每执行一次都会产生一个新文件,覆盖老文件
```

```java
     /**
     * 一次写一个字节
     */
    private static void method01() throws Exception {
        FileOutputStream fos = new FileOutputStream("day14_io/1.txt");
        fos.write(97);
        fos.close();
    }
```

> 课程配图（未随笔记提交）

```java
    /**
     * 一次写一个字节数组
     */
    private static void method02()throws Exception {
        FileOutputStream fos = new FileOutputStream("day14_io/1.txt");
        byte[] bytes = {97,98,99,100};
        fos.write(bytes);
        fos.close();
    }
```

```java
    /**
     * 一次写一个字节数组一部分
     */
    private static void method03() throws Exception{
        FileOutputStream fos = new FileOutputStream("day14_io/1.txt");
        byte[] bytes = {97,98,99,100};
        fos.write(bytes,0,2);
        fos.close();
    }
```

```java

    private static void method04()throws Exception {
        FileOutputStream fos = new FileOutputStream("day14_io/1.txt");
        byte[] bytes = "我爱中国".getBytes();
        fos.write(bytes);
        fos.close();
    }
```

```java
1.换行 -> 往文件中写一个换行符
  a.window: \r\n
  b.linux:\n
  c.mac os:\r

2.续写追加:
  FileOutputStream(String path,boolean append) -> 如果append为true,就是追加,续写,每次运行老数据不会被覆盖
```

```java
    /**
     * 续写追加
     * @throws Exception
     */
    private static void method05() throws Exception {
        FileOutputStream fos = new FileOutputStream("day14_io/1.txt",true);
        fos.write("白日依山尽\r\n".getBytes());
        fos.write("黄河入海流\r\n".getBytes());
        fos.write("欲穷千里目\r\n".getBytes());
        fos.write("更上一层楼\r\n".getBytes());
        fos.close();
    }
```

## 5.InputStream子类[FileInputStream]的介绍以及方法的使用

```java
1.概述:字节输入流->InputStream(抽象类) -> 子类:FileInputStream
2.作用:读数据->将硬盘上的数据读到内存中
3.构造:
  FileInputStream(File file)
  FileInputStream(String path)
4.方法:
  int read()一次读一个字节,返回的是读取的字节
  int read(byte[] bytes)一次读一个字节数组,返回的是读取字节的个数
  int read(byte[] bytes,int offset,int count)一次读一个字节数组的一部分,返回的是读取字节的个数
  close()关闭资源
```

## 6.一次读取一个字节

```java
  /**
     * 一次读一个字节,返回读取的字节
     */
    private static void method01()throws Exception {
        FileInputStream fis = new FileInputStream("day14_io/2.txt");
/*        int data1 = fis.read();
        System.out.println(data1);
        int data2 = fis.read();
        System.out.println(data2);
        int data3 = fis.read();
        System.out.println(data3);
        int data4 = fis.read();
        System.out.println(data4);*/

        //定义一个变量,接收读取的字节
        int len = 0;
        while((len = fis.read())!=-1){
            System.out.println((char) len);
        }
        fis.close();

    }
```

> 1.流中的数据读完之后,就不能再继续读了,如果还想重新读,就再new一个对象
>
> 2.读取的过程中,不要连续写多个read
>
> 3.流关闭之后,不能再次使用,否则会报错
>
> ```java
> Exception in thread "main" java.io.IOException: Stream Closed
> 	at java.base/java.io.FileInputStream.read0(Native Method)
> 	at java.base/java.io.FileInputStream.read(FileInputStream.java:228)
> 	at com.atguigu.b_input.Demo01FileInputStream.method01(Demo01FileInputStream.java:37)
> 	at com.atguigu.b_input.Demo01FileInputStream.main(Demo01FileInputStream.java:7)
> ```

## 7.一次读取一个字节数组以及过程

```java
    /**
     * 一次读一个字节数组
     * @throws Exception
     */
    private static void method02()throws Exception {
        FileInputStream fis = new FileInputStream("day14_io/2.txt");
        /*
          数组相当于一个临时存储区域,数组定多长,每次就读取多少个数据
          我们读取的数据会先保存到数组中,然后我们从数组中读取数据
          如果剩下的数据不够数组长度了,那么剩下多少个数据就一次读多少个数据
         */
        byte[] bytes = new byte[2];

/*        int len1 = fis.read(bytes);
        System.out.println(len1);

        int len2 = fis.read(bytes);
        System.out.println(len2);

        int len3 = fis.read(bytes);
        System.out.println(len3);*/

        //定义一个变量,接收读取的字节个数
        int len = 0;
        while((len = fis.read(bytes))!=-1){
            System.out.println(new String(bytes,0,len));
        }
        fis.close();
    }
```

> > 课程配图（未随笔记提交）

## 8.字节流实现图片复制分析

> 课程配图（未随笔记提交）

## 9.字节流实现图片复制代码实现

```java
public class Demo03Copy {
    public static void main(String[] args)throws Exception {
        //1.创建FileInputStream用于将本地上的图片读到内存中
        FileInputStream fis = new FileInputStream("F:\\idea\\io\\8.jpg");
        //2.创建FileOutputStream用于将内存中的图片写出到磁盘中
        FileOutputStream fos = new FileOutputStream("F:\\idea\\io\\智妍.jpg");
        //3.创建数组,数组长度一般都是1024或者其倍数
        byte[] bytes = new byte[1024];
        //4.边读边写
        int len = 0;
        while((len = fis.read(bytes))!=-1){
            fos.write(bytes,0,len);
        }
        //5.关流->先开的后关
        fos.close();
        fis.close();
    }
}
```

# 第二章.字符流

## 1.字节流读取中文的问题

```java
1.注意:
  a.一个汉字在GBK中,占2个字节
  b.一个汉字在UTF-8中,占3个字节
2.字节流是万能流,但是侧重文件复制,不要边读边看,因为整不好读取的汉字就不完整了,出来就是乱码
  不管编码和解码是否一致,用字节流读取中文,边读边看,整不好都会出现乱码
3.解决:
  我们将文本文档中的内容看成一个一个的字符,按照字符就操作就行了 -> 字符流
```

> 注意:
>
> ​    字符流读取文本文档,如果编码和解码不一致,也会出现乱码
>
> ​    但是用字符流读取文本文档,在编码和解码一致的情况下是不会出现乱码的

## 2.FileReader的介绍以及使用

```java
1.概述:字符输入流->Reader(抽象类) -> 子类:FileReader
2.作用:读数据
3.构造:
  FileReader(File file)
  FileReader(String path)
4.方法:
  int read()一次读一个字符
  int read(char[] chars)一次读一个字符数组,返回的是读取个数
  int read(char[] chars,int offset,int count) 一次读一个字符数组一部分
  close()关流
```

```java
    /**
     * 一次读一个字符
     * @throws Exception
     */
    public static void method02()throws Exception {
        FileReader fr = new FileReader("day14_io/3.txt");
        int len = 0;
        while((len = fr.read())!=-1){
            System.out.println((char)len);
        }
        fr.close();
    }
```

```java
    /**
     * 一次读一个字符数组
     * @throws Exception
     */
    private static void method03()throws Exception{
        FileReader fr = new FileReader("day14_io/3.txt");
        char[] chars = new char[1024];
        int len = 0;
        while((len = fr.read(chars))!=-1){
            System.out.println(new String(chars,0,len));
        }
        fr.close();
    }

```

## 3.FileWriter的介绍以及使用

```java
1.概述:字符输出流 -> Writer(抽象类) -> 子类:FileWriter
2.作用:写数据
3.构造:
  FileWriter(File file)
  FileWriter(String path)
  FileWriter(String path,boolean append) 如果append是true,就是续写追加
4.方法:
  write(int c) 一次写一个字符
  write(char[] cbuf) 一次写一个字符数组
  write(char[] cbuf, int off, int len)一次写一个字符数组一部分
  write(String str) 一次写一个字符串
  close()关闭资源
  flush()刷新缓冲区,将缓冲区中的数据刷到文件中
5.注意:
  字符输出流底层有一个缓冲区,我们需要将我们要写的内容从缓冲区中刷到文件中
```

```java
    private static void method01() throws Exception {
        FileWriter fw = new FileWriter("day14_io/4.txt",true);
        fw.write("风萧萧兮易水寒\r\n");
        fw.write("壮士一去兮不复还\r\n");
        //fw.flush();
        fw.close();
    }
```

## 4.FileWriter的刷新功能和关闭功能

```java
1.flush():将缓冲区中的数据刷到文件中,后续流对象还能用
2.close():先刷新,后关闭,后续流对象不能使用了
```

```java
    private static void method01() throws Exception {
        FileWriter fw = new FileWriter("day14_io/4.txt",true);
        fw.write("风萧萧兮易水寒\r\n");
        fw.write("壮士一去兮不复还\r\n");
        //fw.flush();
        fw.close();
        //fw.write("白日依山尽\r\n");
    }
```

## 5.IO异常处理的方式

```java
private static void method01() {
        FileWriter fw = null;
        try{
            fw = new FileWriter("day14_io/4.txt");
            fw.write("我爱祖国");
        }catch (Exception e){
           e.getStackTrace() ;
        }finally {
            if (fw != null){
                try {
                    fw.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
```

## 6.JDK7之后io异常处理方式

```java
1.格式:
  try(newIO流对象){
      可能出现异常的代码
  }catch(异常类型 对象名){
      异常处理
  }

2.自动关流
```

```java
    private static void method02() {
        try(FileWriter fw = new FileWriter("day14_io/4.txt")){
            fw.write("我爱我的祖国");
        }catch (Exception e){
            e.printStackTrace();
        }
    }
```

## 7.JDK9之后的IO异常处理方式

之前我们讲过JDK 1.7引入了trywith-resources的新特性，可以实现资源的自动关闭，此时要求：

- 该资源必须实现java.io.Closeable接口
- 在try子句中声明并初始化资源对象
- 该资源对象必须是final的

```java
try(IO流对象1声明和初始化;IO流对象2声明和初始化){
    可能出现异常的代码
}catch(异常类型 对象名){
    异常处理方案
}
```

JDK1.9又对trywith-resources的语法升级了

- 该资源必须实现java.io.Closeable接口
- 在try子句中声明并初始化资源对象，也可以直接使用已初始化的资源对象
- 该资源对象必须是final的

```java
IO流对象1声明和初始化;
IO流对象2声明和初始化;

try(IO流对象1;IO流对象2){
    可能出现异常的代码
}catch(异常类型 对象名){
    异常处理方案
}
```

```java
    private static void method03()throws  Exception {
        FileWriter fw = new FileWriter("day14_io/4.txt");
        try(fw){
            fw.write("我爱我的祖国111");
        }catch (Exception e){
            e.printStackTrace();
        }
    }
```

# 第三章.序列化流&打印流

> 课程配图（未随笔记提交）

## 1.序列化流

```java
1.作用:读写对象
2.序列化流:ObjectOutputStream -> 写对象
3.反序列化流:ObjectInputStream -> 读对象
```

### 1.1.序列化流

```java
1.概述:ObjectOutputStream
2.作用:写对象
3.构造:
  ObjectOutputStream(OutputStream os)
4.方法:
  writeObject(对象)
5.注意:
  如果想要序列化一个对象,此对象必须实现Serializable接口
```

```java
public class Person implements Serializable {
    private String name;
    private Integer age;

    public Person() {
    }

    public Person(String name, Integer age) {
        this.name = name;
        this.age = age;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    @Override
    public String toString() {
        return "Person{" +
                "name='" + name + '\'' +
                ", age=" + age +
                '}';
    }
}

```

```java
private static void writer() throws Exception {
    ObjectOutputStream oos =
            new ObjectOutputStream(new FileOutputStream("day14_io/person.txt"));
    Person p1 = new Person("张三", 18);
    oos.writeObject(p1);
    oos.close();
}
```

### 1.2.反序列化流

```java
1.概述:反序列化 -> ObjectInputStream
2.作用:读对象
3.构造:
  ObjectInputStream(InputStream is)
4.方法:
  readObject()
```

```java
    private static void reader()throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new FileInputStream("day14_io/person.txt"));
        Object o = ois.readObject();
        Person p = (Person) o;
        System.out.println(p);
        ois.close();
    }
```

### 1.3.序列号冲突问题

```java
1.问题描述:如果我们修改了对象的源码,没有重新序列化,直接就反序列化,会出现"序列号冲突问题"
2.原因:当我们修改了源代码之后,没有重新序列化,直接反序列化的时候class文件中的新的序列号和文件中存的序列号不一样了
3.解决:
  a.修改源码之后,重新序列化一下子
  b.在被操作的对象中将序列号定死 -> 推荐
    static final long serialVersionUID = 42L;
```

> 课程配图（未随笔记提交）

### 1.4.反序列化多个对象操作

```java
1.问题描述:
  如果我们读取对象的次数和存的对象的个数不一致,会出现EOFException(文件意外到达结尾异常)
2.解决:
  将多个对象放到一个集合对象中,然后将这一个集合对象序列化到文件里面
  这样我们在反序列化的时候,只需要反序列化一次就能将这个集合对象读取出来
  集合对象是有长度的,存了多少个元素长度就是多少,我们就直接循环读取多少次
```

```java
public class Demo02Serializable {
    public static void main(String[] args)throws Exception {
        //writer();
        reader();
    }

    private static void reader()throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new FileInputStream("day14_io/person.txt"));
        /*Object o = ois.readObject();
        Object o1 = ois.readObject();
        Object o2 = ois.readObject();
        Object o3 = ois.readObject();
        Person p = (Person) o;
        Person p1 = (Person) o1;
        Person p2 = (Person) o2;
        Person p3 = (Person) o3;
        System.out.println(p);
        System.out.println(p1);
        System.out.println(p2);
        System.out.println(p3);*/

        Object o = ois.readObject();
        ArrayList<Person> list = (ArrayList<Person>) o;
        for (Person person : list) {
            System.out.println(person);
        }
        ois.close();
    }

    private static void writer() throws Exception {
        ObjectOutputStream oos =
                new ObjectOutputStream(new FileOutputStream("day14_io/person.txt"));
        Person p1 = new Person("张三", 18);
        Person p2 = new Person("李四", 20);
        Person p3 = new Person("王五", 22);

        //创建一个集合ArrayList
        ArrayList<Person> list = new ArrayList<>();
        //调用add方法将三个对象放到集合中
        list.add(p1);
        list.add(p2);
        list.add(p3);

        oos.writeObject(list);
        //oos.writeObject(p1);
        //oos.writeObject(p2);
        //oos.writeObject(p3);
        oos.close();
    }
}

```

## 2.打印流

### 2.1.PrintStream基本使用

```java
1.概述:PrintStream extends OutputStream
2.作用:将数据打印到控制台上或者打印到指定文件中
3.构造:
  PrintStream(String path)
4.方法:
  println():原样输出,自带换行效果
  print():原样输出,不带换行效果
```

```java
    private static void method01()throws Exception {
        PrintStream ps = new PrintStream("day14_io/print.txt");
        ps.println("床前明月光");
        ps.println("疑是地上霜");
        ps.println("举头望明月");
        ps.println("低头思故乡");
        ps.close();
    }
```

```java
1.改变流向:System.out.println()这句话会将输出结果打印到控制台上,我们需要让这句话从控制台输出结果转成去日志文件中输出结果
2.方法:System类中的方法
  setOut(PrintStream对象)
```

```java
 private static void method02()throws Exception {
        PrintStream ps = new PrintStream("day14_io/log.txt");

        //改变流向
        System.setOut(ps);

        System.out.println("出现了一个问题:NullPointerException");
        System.out.println("问题出现在代码的第10行");
        System.out.println("原因是字符串为null了");
    }
```

> 使用场景:
>
> 可以将输出的内容以及详细信息放到日志文件中,永久保存
>
> 以后我们希望将输出的内容永久保存,但是输出语句会将结果输出到控制台上,控制台是临时显示,如果有新的程序运行,新程序的运行结果会覆盖之前的结果,这样无法达到永久保存,到时候我们想看看之前的运行结果信息就看不到了,所以我们需要将输出的结果保存到日志文件中,就可以使用setOut改变流向
