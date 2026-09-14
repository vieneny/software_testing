# day13_String_StringBuilder

```java

```

# 第一章.String

## 1.String介绍

```java
1.概述:String 类代表字符串
2.特点:
  a.Java 程序中的所有字符串字面值（如 "abc" ）都作为此类的实例实现
    凡是带双引号的都是String的对象
  b.字符串是常量,它们的值在创建之后不能更改
  c.由于字符串不能更改,所以可以共享
```

> 课程配图（未随笔记提交）

## 2.String的实现原理

```java
1.底层原理:String底层其实是一个被final修饰的数组,创建之后数组的地址值直接定死,不能更改
  a.jdk8之后:private final byte[] value   -> byte占内存1个字节 -> 省内存
  b.jdk8以及之前:private final char[] value - char占内存2个字节
```

## 3.String的创建

```java
1.构造:
  a.String() -> 直接创建String的对象
  b.String(String s) -> 根据字符串创建String的对象
  c.String(byte[] bytes) -> 根据byte数组创建String的对象
  d.String(char[] chars)  -> 根据char数组创建字符串的对象
2.简化:
  String 变量名 = ""
```

```java
    @Test
    public void test01(){
        //a.String() -> 直接创建String的对象
        String s1 = new String();
        System.out.println(s1);
        //b.String(String s) -> 根据字符串创建String的对象
        String s2 = new String("hello");
        System.out.println(s2);
        //c.String(byte[] bytes) -> 根据byte数组创建String的对象
        byte[] bytes = {97, 98, 99};
        String s3 = new String(bytes);
        System.out.println(s3);
        //d.String(char[] chars)  -> 根据char数组创建字符串的对象
        char[] chars = {'a', 'b', 'c'};
        String s4 = new String(chars);
        System.out.println(s4);
        //简化
        String s5 = "abc";
        System.out.println(s5);
    }
```

```java
扩展构造:
 String(byte[] bytes,int offset,int count):将byte数组的一部分转成String对象
       bytes:被转的数组
       offset:从数组的哪个索引开始转
       count:转多少个

 String(char[] chars,int offset,int length):将char数组的一部分转成String对象
       chars:被转的数组
       offset:从数组的哪个索引开始转
       length:转多少个
```

```java
    @Test
    public void test02() {
        byte[] bytes = {97, 98, 99, 100, 101, 102};
        String s = new String(bytes,0,2);
        System.out.println(s);

        System.out.println("=====================");
        char[] chars = {'a', 'b', 'c', 'd', 'e', 'f'};
        String s1 = new String(chars,0,2);
        System.out.println(s1);
    }
```

# 第二章.String的方法

## 1.判断方法

```java
boolean equals(Objec obj) 判断字符串内容是否一样
boolean equalsIgnoreCase(String str) 判断字符串内容是否一样,忽略大小写
```

```java
    /**
     * boolean equals(Objec obj) 判断字符串内容是否一样
     * boolean equalsIgnoreCase(String str) 判断字符串内容是否一样,忽略大小写
     */
    @Test
    public void test01(){
        String s1  = "abc";
        String s2 = new String("abc");
        System.out.println(s1.equals(s2));
        System.out.println("========================");
        String s3 = "ABC";
        System.out.println(s1.equalsIgnoreCase(s3));
    }
```

> ```java
> 小经验:
>    判断字符串内容的时候习惯上将确定的放equals前面  -> 防空指针
> ```
>
> ```java
>     @Test
>     public void test02(){
>         String str = null;
>         if ("abc".equals(str)){
>             System.out.println("字符串内容一样");
>         }else{
>             System.out.println("字符串内容不一样");
>         }
>     }
> ```

## 3.获取功能

```java
1.String concat(String str) 字符串拼接,返回的是新的字符串
2.char charAt(int index) 获取指定索引位置上的字符
3.int indexOf(String str) 获取指定字符在老串儿中第一次出现的索引位置
4.String subString(int beginIndex) 从指定索引开始截取字符串到最后
5.String subString(int beginIndex,int endIndex) 从指定索引位置开始截取到endIndex->含头不含尾
6.int length()获取字符串长度
```

```java
    @Test
    public void test03(){
        String str = "abcdefg";
        //1.String concat(String str) 字符串拼接,返回的是新的字符串
        String newStr1 = str.concat("123");
        System.out.println(newStr1);
        //2.char charAt(int index) 获取指定索引位置上的字符
        System.out.println(str.charAt(1));
        //3.int indexOf(String str) 获取指定字符在老串儿中第一次出现的索引位置
        System.out.println(str.indexOf("d"));
        //4.String subString(int beginIndex) 从指定索引开始截取字符串到最后
        System.out.println(str.substring(2));
        //5.String subString(int beginIndex,int endIndex) 从指定索引位置开始截取到endIndex->含头不含尾
        System.out.println(str.substring(2,4));
        //6.int length()获取字符串长度
        System.out.println(str.length());
    }
```

## 4.练习

```java
遍历字符串
```

```java
     /**
     * 遍历字符串
     */
    @Test
    public void test04(){
        String str = "abcdefg";
        for (int i = 0; i < str.length(); i++) {
            char c = str.charAt(i);
            System.out.println(c);
        }
    }
```

## 5.转换功能

```java
1.char[] toCharArray()将字符串转成char数组
2.byte[] getBytes()将字符串转成byte数组
3.byte[] getBytes(String charsetName)根据指定的编码集将字符串转成byte数组
4.String replace(CharSequence target, CharSequence replacement) ->将前面参数替换成后面的参数
```

```java
    /**
     * 转换功能
     */
    @Test
    public void test05() throws UnsupportedEncodingException {
        String str = "abcdefg";
        //1.char[] toCharArray()将字符串转成char数组
        char[] chars = str.toCharArray();
        System.out.println(chars);
        System.out.println("===============");
        //2.byte[] getBytes()将字符串转成byte数组
        byte[] bytes = str.getBytes();
        System.out.println(Arrays.toString(bytes));
        System.out.println("===============");
        //3.byte[] getBytes(String charsetName)根据指定的编码集将字符串转成byte数组
        byte[] bytes1 = "你".getBytes("gbk");
        System.out.println(Arrays.toString(bytes1));
        System.out.println("===============");
        //4.String replace(CharSequence target, CharSequence replacement) ->将前面参数替换成后面的参数
        String newStr = str.replace("abc", "123");
        System.out.println(newStr);
    }
```

> ```java
> CharSequence是String的接口
> ```

## 7.练习4

```java
随便给一个字符串,统计该字符串中大写字母字符，小写字母字符，数字字符出现的次数(不考虑其他字符)
```

```java
@Test
    public void test06() {
        String str = "asdfadsWERWE2134321";
        //1.定义三个变量用于统计大写字母,小写字母,和数字的个数
        int big = 0;
        int small = 0;
        int number = 0;
        //2.遍历字符串
        char[] chars = str.toCharArray();
        for (int i = 0; i < chars.length; i++) {
            char data = chars[i];
            //3.判断
            if (data >= 'A' && data <= 'Z'){
                big++;
            }else if (data >= 'a' && data <= 'z'){
                small++;
            }else if (data >= '0' && data <= '9'){
                number++;
            }else{
                System.out.println("其他字符");
            }
        }
        System.out.println("大写字母的个数:" + big);
        System.out.println("小写字母的个数:" + small);
        System.out.println("数字的个数:" + number);
    }
```

## 8.分割功能

```java
String[] split(String regex)按照指定的规则分割字符串
```

```java
 /**
     * 分割功能
     */
    @Test
    public void test07() {
        //String[] split(String regex)按照指定的规则分割字符串
        String str = "a,b,c,d";
        String[] arr = str.split(",");
        System.out.println(Arrays.toString(arr));

        System.out.println("===================");
        String str1 = "a.b.c.d";
        String[] arr2 = str1.split("\\.");
        System.out.println(Arrays.toString(arr2));
    }
```

# 第三章.其他方法

```java
1.boolean contains(String s):判断老串中是否包含指定的串儿
2.boolean endsWith(String s):判断是否以指定的串儿结尾
3.boolean startsWith(String s):判断是否以指定的串儿开头
4.String toLowerCase()将字母转成小写
5.String toUpperCase()将字母转成大写
6.String trim()去掉字符串两端空格
```

```java
    /**
     * 其他方法
     */
    @Test
    public void test08() {
        String str = "abcdefg";
        //1.boolean contains(String s):判断老串中是否包含指定的串儿
        System.out.println(str.contains("abc"));
        //2.boolean endsWith(String s):判断是否以指定的串儿结尾
        System.out.println(str.endsWith("fg"));
        //3.boolean startsWith(String s):判断是否以指定的串儿开头
        System.out.println(str.startsWith("abc"));
        //4.String toLowerCase()将字母转成小写
        String lowerCase = "ADFASD".toLowerCase();
        System.out.println(lowerCase);
        //5.String toUpperCase()将字母转成大写
        String upperCase = "adfadf".toUpperCase();
        System.out.println(upperCase);
        String upperCase1 = "一二三四".toUpperCase();
        System.out.println(upperCase1);
        //6.String trim()去掉字符串两端空格
        String trim = " abc haha  ".trim();
        System.out.println(trim);

        String replace = " sfads  sadfasd   dafds ".replace(" ", "");
        System.out.println(replace);
    }
```

# 第四章. String新特性_文本块

预览的新特性文本块在Java 15中被最终确定下来，Java 15之后我们就可以放心使用该文本块了。

JDK 12引入了Raw String Literals特性，但在其发布之前就放弃了这个特性。这个JEP与引入多行字符串文字（文本块）在意义上是类似的。Java 13中引入了文本块（预览特性），这个新特性跟Kotlin中的文本块是类似的。

**现实问题**

在Java中，通常需要使用String类型表达HTML，XML，SQL或JSON等格式的字符串，在进行字符串赋值时需要进行转义和连接操作，然后才能编译该代码，这种表达方式难以阅读并且难以维护。

文本块就是指多行字符串，例如一段格式化后的XML、JSON等。而有了文本块以后，用户不需要转义，Java能自动搞定。因此，**文本块将提高Java程序的可读性和可写性。**{username:"tom",password="111"}

**目标**

- 简化跨越多行的字符串，避免对换行等特殊字符进行转义，简化编写Java程序。
- 增强Java程序中字符串的可读性。

**举例**

会被自动转义，如有一段以下字符串：

```html
<html>
  <body>
      <p>Hello, 尚硅谷</p>
  </body>
</html>
```

将其复制到Java的字符串中，会展示成以下内容：

```java
"<html>\n" +
"    <body>\n" +
"        <p>Hello, 尚硅谷</p>\n" +
"    </body>\n" +
"</html>\n";
```

即被自动进行了转义，这样的字符串看起来不是很直观，在JDK 13中，就可以使用以下语法了：

```java
"""
<html>
  <body>
      <p>Hello, world</p>
  </body>
</html>
""";
```

使用“”“作为文本块的开始符和结束符，在其中就可以放置多行的字符串，不需要进行任何转义。看起来就十分清爽了。

文本块是Java中的一种新形式，它可以用来表示任何字符串，并且提供更多的表现力和更少的复杂性。

（1）文本块由零个或多个字符组成，由开始和结束分隔符括起来。

- 开始分隔符由三个双引号字符表示，后面可以跟零个或多个空格，最终以行终止符结束。
- 文本块内容以开始分隔符的行终止符后的第一个字符开始。
- 结束分隔符也由三个双引号字符表示，文本块内容以结束分隔符的第一个双引号之前的最后一个字符结束。

以下示例代码是错误格式的文本块：

```java
String err1 = """""";//开始分隔符后没有行终止符,六个双引号最中间必须换行

String err2 = """  """;//开始分隔符后没有行终止符,六个双引号最中间必须换行
```

如果要表示空字符串需要以下示例代码表示：

```java
String emp1 = "";//推荐
String emp2 = """
   """;//第二种需要两行，更麻烦了
```

（2）允许开发人员使用“\n”“\f”和“\r”来进行字符串的垂直格式化，使用“\b”“\t”进行水平格式化。如以下示例代码就是合法的。

```java
String html = """
    <html>\n
      <body>\n
        <p>Hello, world</p>\n
      </body>\n
    </html>\n
    """;
```

（3）在文本块中自由使用双引号是合法的。

```java
String story = """
Elly said,"Maybe I was a bird in another life."

Noah said,"If you're a bird , I'm a bird."
 """;
```

```java
public class Demo14String {
    public static void main(String[] args) {
        String s = "<!DOCTYPE html>\n" +
                "<html lang=\"en\">\n" +
                "<head>\n" +
                "    <meta charset=\"UTF-8\">\n" +
                "    <title>性感涛哥,在线发牌</title>\n" +
                "</head>\n" +
                "<body>\n" +
                "    哈哈哈\n" +
                "</body>\n" +
                "</html>";
        System.out.println(s);

        System.out.println("================================");

        String s1 = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>性感涛哥,在线发牌</title>
                </head>
                <body>
                    哈哈哈
                </body>
                </html>
                """;
        System.out.println(s1);
        System.out.println("================================");
    }
}

```

# 第五章.StringBuilder类

## 1.StringBuilder的介绍

```java
1.概述:是一个可变的字符序列
2.作用:主要用于拼接字符串
3.问题:我们已经学了直接用String拼接字符串,为啥还要学StringBuilder呢?
      原因:String在拼接的过程中很容易出现新的字符串对象,频繁拼接会占用内存资源
          而StringBuilder在拼接的过程中不会随意产生新的字符串对象,效率也高,省内存
```

## 2.StringBuilder的使用

```java
构造:
  StringBuilder()
  StringBuilder(String str)
```

```java
    @Test
    public void test1() {
        //StringBuilder sb = new StringBuilder();
        StringBuilder sb = new StringBuilder("hello");
        System.out.println(sb);
    }
```

## 3.StringBuilder的常用方法

```java
1.StringBuilder append(任意类型) 拼接,返回的是StringBuilder自己
2.StringBuilder reverse()字符串翻转,返回的是StringBuilder自己
3.String toString() 将StringBuilder转成String
```

```java
 @Test
    public void test2() {
        //1.StringBuilder append(任意类型) 拼接,返回的是StringBuilder自己
        StringBuilder sb = new StringBuilder();
        StringBuilder sb2 = sb.append("张无忌");
        //System.out.println(sb == sb2);//true
        System.out.println(sb);

        //链式调用
        sb.append("赵敏").append("周芷若").append("小昭");
        System.out.println(sb);

        //2.StringBuilder reverse()字符串翻转,返回的是StringBuilder自己
        sb.reverse();
        System.out.println(sb);

        //3.String toString() 将StringBuilder转成String
        String s = sb.toString();
        System.out.println(s.length());
    }
```

```java
练习: 给一个字符串,判断这个字符串是否是"回文内容"
     12321
     上海自来水来自海上
     山西运煤车煤运西山

     蝶恋花香花恋蝶
     鱼游水美水游鱼
```

```java
   @Test
    public void test3() {
        String str = "123321";
        StringBuilder sb = new StringBuilder(str);
        sb.reverse();
        String s = sb.toString();

        if (str.equals(s)){
            System.out.println("是回文内容");
        }else{
            System.out.println("不是回文内容");
        }
    }
```

> String,StringBuilder以及StringBuffer区别:
>
> 1.相同点:
>
> ​    三者都可以拼接字符串
>
> 2.不同点:
>
> ​    a.String每拼接一次,都会产生一个新的String对象,占用内存空间,效率低
>
> ​    b.StringBuilder:拼接的过程中不会随意产生新对象.节省内存空间,线程不安全,效率高
>
> ​    c.StringBuffer:拼接的过程中不会随意产生新对象,节省内存空间, 线程安全, 效率低
>
> 3.从拼接效率上来看: StringBuilder>StringBuffer>String

# 第六章.作业

```java
已知用户名和密码，请用程序实现模拟用户登录。总共给三次机会，登录成功与否，给出相应的提示
```

```java
public class Demo04String {
    public static void main(String[] args) {
        //定义两个字符串,表示已经注册的用户
        String username = "admin";
        String password = "1234";

        //创建Scanner对象
        Scanner sc = new Scanner(System.in);
        //循环3次录入用户名和密码
        for (int i = 0; i < 3; i++) {
            System.out.println("请输入用户名:");
            String name = sc.next();
            System.out.println("请输入密码:");
            String pwd = sc.next();
            if (username.equals(name) && password.equals(pwd)) {
                System.out.println("登录成功");
                break;
            } else {
                if (i == 2) {
                    System.out.println("账号冻结");
                } else {
                    System.out.println("用户名或密码错误");
                }
            }
        }
    }
}

```
