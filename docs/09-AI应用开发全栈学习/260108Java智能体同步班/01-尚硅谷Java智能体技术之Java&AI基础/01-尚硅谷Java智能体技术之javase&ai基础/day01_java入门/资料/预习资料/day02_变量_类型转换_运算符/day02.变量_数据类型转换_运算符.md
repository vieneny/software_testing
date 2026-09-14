#  day02.变量  数据类型转换   运算符

```java
课前回顾:
  1.字节:计算机存储数据的最小计量单位,用byte或者B表示
     8bit = 1B
     以后都是1024了
  2.常用dos命令:
    切换盘符  盘符名:
    查看      dir
    进入指定目录  cd 文件夹名   或者  cd 文件夹名\文件夹名
    退到上一级   cd..
    退到根目录   cd\
    清屏        cls
    退出黑窗口   exit
    创建文件夹  mkdir 文件夹名   或者  mkdir 文件夹名\文件夹名
    删除文件夹  rd 文件夹名 -> 文件夹必须是空的而且不走回收站
    删除文件    del *.后缀名
  3.java所需要的环境:
    a.jvm:java虚拟机,是运行java程序的假想计算机
    b.跨平台:java程序可以在不同的操作系统上运行
    c.jre:java运行环境,包含了核心类库
    d.jdk:java开发工具包,包含了jre
  4.环境变量:在任意位置使用javac 和 java 命令
    JAVA_HOME
  5.入门程序:
    a.编写:创建一个.java文件
      public class 类名{
          public static void main(String[] args){
              System.out.println("helloworld");
          }
      }

    b.编译:会生成一个xxx.class文件(字节码文件),jvm运行java程序只认class文件
      javac java文件名.java
    c.运行:
      java class文件名

  6.注释:对代码进行的解释说明
    a.单行注释://
    b.多行注释:
      /**/
    c.文档注释:
      /**内容*/
  7.println和print的区别:
    a.相同点:都是输出语句
    b.不同点:
       println自带换行效果
       print不带换行效果

今日重点:
   除了第三章,第六章,第七章,第八章,都是重点
```

# 第一章.常量

```java
1.概述:在代码的运行过程中值不会发生改变的数据,我们叫做"字面值"
2.分类:
  整数常量: 所有整数
  小数常量: 所有带小数点的  2.5  2.0
  字符常量: 带单引号的'',单引号中的内容必须有且只能有一个内容
           '1'
           'a'
           '11' -> 不算,11在引号算两个内容
           '' -> 不算,单引号中必须有且只能有一个内容
           '中'
           ' ' -> 单引号中有一个空格,算字符,因为一个空格就是一个内容
           '    ' -> 四个空格不算字符
           '	' -> 一个tab键就算一个字符
  字符串常量:带双引号的"",双引号中内容随意
           ""

  布尔常量:true false
  空常量:null 代表数据不存在,不能直接使用
```

```java
public class Demo01ChangLiang {
    public static void main(String[] args) {
        //整数常量
        System.out.println(10);
        //小数常量
        System.out.println(10.1);
        //字符常量
        System.out.println('a');
        //字符串常量
        System.out.println("abc");
        //布尔常量
        System.out.println(true);
        System.out.println(false);
        //空常量
        //System.out.println(null);
    }
}
```

```java
public class Demo02ChangLiang {
    public static void main(String[] args) {
        System.out.println(10+3);
        System.out.println(10-3);
        System.out.println(10*3);
        /*
           /前后如果都是整数,结果肯定会取整数部分
           /前后如果有一个是带小数点的,结果就是正常的小数
         */
        System.out.println(10/3);//3
        System.out.println(10.0/3);//3.3333333333333335
    }
}

```

# 第二章.变量

> 配眼镜:潘家园 -> 北京眼镜城 ->3楼

| 数据类型     | 关键字         | 内存占用 | 取值范围                                                 |
| :----------- | :------------- | :------- | :------------------------------------------------------- |
| 字节型       | byte           | 1个字节  | -128 至 127  定义byte变量时超出范围,废了                 |
| 短整型       | short          | 2个字节  | -32768 至 32767                                          |
| 整型         | int（默认）    | 4个字节  | -2^31^ 至 2^31^-1  正负21个亿<br>-2147483648——2147483647 |
| 长整型       | long           | 8个字节  | -2^63^ 至 2^63^-1   19位数字                             |
| 单精度浮点数 | float          | 4个字节  | 1.4013E-45 至 3.4028E+38                                 |
| 双精度浮点数 | double（默认） | 8个字节  | 4.9E-324 至 1.7977E+308                                  |
| 字符型       | char           | 2个字节  | 0 至 2^16^-1                                             |
| 布尔类型     | boolean        | 1个字节  | true，false(可以做判断条件使用)                          |

## 1.变量的介绍以及使用

```java
1.概述:在代码的运行过程中会随着不同的情况其值随之发生改变的数据
      int age = 18
          age = 19
2.定义格式:
  a.数据类型 变量名 = 值   -> 先看等号右边的,将等号右边的值赋值给等号左边的变量,哪怕等号右边是运算,我们都得先算出来一个结果,然后将这个结果赋值给等号左边的变量

  b.数据类型 变量名;
    变量名 = 值;

  c.定义多个相同类型的变量:
    数据类型 变量名1 = 值,变量名2 = 值,变量名3 = 值

3.java中的数据类型分为2大类:
  基本类型:4类8种
      整型: byte short int long
      浮点型:float double
      字符型:char
      布尔型:boolean
  引用类型:
      类  数组  接口  枚举  注解  Record

4.注意:
  a.整数变量默认类型为int;小数变量默认类型为double
  b.String属于类的一种,是引用数据类型,但是定义格式和基本类型一样
    String 变量名 = ""
```

```java
public class Demo01Var {
    public static void main(String[] args) {
        //byte
        byte num1 = 10;
        num1 = 20;
        System.out.println(num1);
        //short
        short num2 = 10;
        num2 = 20;
        System.out.println(num2);
        //int 整数默认类型
        int num3 = 10;
        System.out.println(num3);
        //long-> long型的变量习惯上添加L
        long num4 = 10L;
        System.out.println(num4);
        //float-> float型的变量习惯上添加F
        float num5 = 10.1F;
        System.out.println(num5);
        //double
        double num6 = 10.1;
        System.out.println(num6);
        //char
        char num7 = 'a';
        System.out.println(num7);
        //boolean
        boolean num8 = true;
        boolean num9 = false;
        /*
           将num9的值赋值给num8
         */
        num8 = num9;
        System.out.println(num8);

        System.out.println("===========================");
        String num10 = "abc";
        System.out.println(num10);
    }
}

```

```java
public class Demo02Var {
    public static void main(String[] args) {
        int a = 10;
        int b = 3;
        System.out.println(a+b);
        int sum = a + b;
        System.out.println(sum);
        //int c = a + b;
        //System.out.println(c);

        int sub = a-b;
        System.out.println(sub);

        int mul = a*b;
        System.out.println(mul);

        int div = a/b;
        System.out.println(div);

        double mod = 10.0/3;
        System.out.println("mod = " + mod);
    }
}

```

```java
public class Demo03Var {
    public static void main(String[] args) {
        /*
           \ 是转义字符
           1.将普通的字符转义成具有特殊含义的字符
           2.将具有特殊含义的字符转义成普通字符

           n:普通字符 -> \n:换行

         */
        System.out.println("哈哈哈哈\n嘿嘿嘿嘿");

        /*
          t:普通字符
          \t:制表符,相当于tab键
         */
        System.out.println("哈哈哈哈\t嘿嘿嘿嘿");

        /*
           表示一个路径
           F:\idea\io
         */
        String path = "F:\\idea\\io";
        System.out.println(path);
    }
}
```

## 2.变量使用时的注意事项

```java
1.变量不初始化(第一次赋值)不能直接使用
2.在同一个作用域(一对大括号就是一个作用域)中不能连续定义多个重名的变量
3.不同的作用域之间不要随意互相访问
  a.在小作用域中能使用大作用域中的变量
  b.在大作用域中不能直接使用小作用域中的变量
```

```java
public class Demo04Var {
    public static void main(String[] args) {
        int i;
        i = 10;
        System.out.println(i);

        //double i = 20;
        {
            System.out.println(i);
            int j = 200;
        }

        //System.out.println(j);
    }
}

```

## 3.练习

```java
定义一个人类,用变量表示 姓名 性别 年龄 身高 体重
```

```java
public class Demo05Var {
    public static void main(String[] args) {
        //姓名 String
        String name = "涛哥";
        //性别 char
        char gender = '男';
        //年龄 int
        int age = 18;
        //身高 double
        double height = 1.88;
        //体重 double
        double weight = 80.5;

        //System.out.println(name);
        //System.out.println(gender);
        //System.out.println(age);
        //System.out.println(height);
        //System.out.println(weight);
        System.out.println(name+","+gender+","+age+","+height+","+weight);
    }
}

```

# 第三章.标识符

```java
1.概述:给类,方法,变量取的名字
2.规范:
  硬性规定:
    a.名字中可以包含"英文字母","数字","_","$"
    b.不能以数字开头
    c.名字不能是关键字
  软性建议:
    a.给类取名,要遵循"大驼峰式"(每个单词的首字母大写)
    b.给方法和变量取名,要遵循"小驼峰式"(从第二个单词开始首字母大写)
```

# 第四章.数据类型转换

```java
1.什么时候会发生数据类型转换
  当等号左右两边类型不一致的时候或者两个不同类型的数据做运算

2.分类:
  a.自动类型转换
  b.强制类型转换 -> 强转
```

> 按照取值范围大小从小到大排列:
>
>    byte,short,char -> int -> long -> float -> double

## 1.自动类型转换->小转大

```java
1.什么时候发生:
  a.将取值范围小的数据类型赋值给取值范围大的变量,小转大
  b.取值范围小的数据和取值范围大的数据做运算,小转大
```

```java
public class Demo01DataType {
    public static void main(String[] args) {
        /*
            100默认类型为int,num1是long型
            相当于将取值范围小的类型赋值给了取值范围大的变量->发生了自动类型转
         */
        //long num1 = 100;
        long num1 = 100L;
        System.out.println(num1);

        int num2 = 20;
        /*
           num2是int型
           2.5默认类型为double
           double sum = int+double -> 发生了自动类型转换
           double  = double + double
         */
        double sum = num2+2.5;
        System.out.println("sum = " + sum);
    }
}

```

## 2.强制类型转换

```java
1.什么时候需要强转:
  取值范围小的类型 变量名 = 取值范围大的数据类型 -> 需要强转

2.怎么强转:
  取值范围小的类型 变量名 = (取值范围小的类型)取值范围大的数据类型
```

```java
public class Demo02DataType {
    public static void main(String[] args) {
        /*
           2.5默认类型double型
           下面的代码相当于将取值范围大的类型赋值给取值范围小的类型,需要强转
         */
         //int num1 = 2.5;
         int num1 = (int)2.5;

         /*
           2.5默认类型为double型
           相当于将取值范围大的类型赋值给了取值范围小的变量,需要强转
          */
         float num2 = (float) 2.5;
         float num3 = 2.5F;
    }
}
```

## 3.强转的注意事项

```java
1.将来开发不要故意写成强转的形式,除非没有办法,否则会出现精度损失和数据溢出现象
2.byte和short的变量如果等号右边是一个字面值且没有超出取值范围,jvm会自动强转
  但是byte和short接收的值如果有变量参与,结果重新赋值给byte或者short变量,byte和short会提升为int型,需要我们手动强转
3.char类型的数据一旦参与运算,char类型的数据会自动提升为int型数据,这个字符对应的int整数会自动取ASCII码中查找,如果ASCII码表中没有此字符,会自动去unicode码表(万国码)中查询字符对应的int值
```

```java
public class Demo03DataType {
    public static void main(String[] args) {
        //精度损失
        int num1 = (int) 2.9;
        System.out.println(num1);

        /*
           数据溢出
           int型转成二进制应该是32为二进制
           100亿转成二进制:0010 0101 0100 0000 1011 1110 0100 0000 0000

           此时多出来4位,我们就把前4位干掉,剩下的二进制转成十进制就是最后的结果
         */
        int num2 = (int)10000000000L;
        System.out.println(num2);

        System.out.println("======================");

        byte b = 100;
        System.out.println(b);

        /*
          byte = byte+int
          byte = int+int
         */
        byte b1 = (byte)(b+1);
        System.out.println(b1);

        System.out.println("======================");

        char data = 'a';
        System.out.println(data+0);
        System.out.println('A'+0);

        System.out.println("=====================");

        char data2 = '中';
        System.out.println(data2+0);
    }
}

```

> 课程配图（未随笔记提交）

> 温馨小提示:
>
> ​    将来如果算钱的时候,千万不要直接用float和double算,因为float和double直接参与运算也会出现精度损失现象
>
> ​    解决:将来会学BigDecimal,它会解决float或者double直接参与运算而出现的精度损失问题

# 第五章.运算符

## 1.算数运算符

| 符号 | 说明                                                         |
| ---- | ------------------------------------------------------------ |
| +    | 加法                                                         |
| -    | 减法                                                         |
| *    | 乘法                                                         |
| /    | 除法<br>如果符号前后都是整数,结果只取整数部分<br>如果符号前后有一个是小数,结果就是正常带小数点的 |
| %    | 取模(取余数)                                                 |

```java
public class Demo01SuanShu {
    public static void main(String[] args) {
        int a = 10;
        int b = 3;
        int sum = a+b;
        System.out.println("sum = " + sum);
        int sub = a-b;
        System.out.println("sub = " + sub);
        int mul = a*b;
        System.out.println("mul = " + mul);
        int div = a/b;
        System.out.println("div = " + div);
        int mod = a%b;
        System.out.println("mod = " + mod);
    }
}

```

```java
+:
  1.加法运算
  2.字符串拼接符号 -> 任意数据遇到字符串都会变成字符串,直接往后拼接
```

```java
public class Demo02SuanShu {
    public static void main(String[] args) {
        int a = 10;
        int b = 3;
        System.out.println(a+b+"");//13
        System.out.println(""+a+b);//103
        System.out.println(a+""+b);//103
        System.out.println(""+(a+b));//13

        System.out.println("a与b之和为:"+(a+b));
    }
}
```

## 2.自增自减运算符(也算算数运算符的一种)

```java
1.格式:
  变量名++  -> 后自加
  ++变量名  -> 前自加
  变量名--  -> 后自减
  --变量名  -> 前自减

2.使用:
  a.单独使用:自增自减单独成为一句,没有和其他的语句相关联
    符号在前在后都是先运算
  b.混合使用:自增自减和其他语句混合使用了(比如:赋值语句,打印语句)
    符号在前:先运算,再使用运算后的值
    符号在后:先使用原值,用完之后自身加减
```

```java
public class Demo03SuanShu {
    public static void main(String[] args) {
        int i = 10;
        //i++;
        //单独使用
        ++i;
        System.out.println(i);
        System.out.println("===================");

        int j = 10;
        //混合使用
        //int result = ++j;
        int result = j++;
        System.out.println("result = " + result);
        System.out.println(j);

        System.out.println("====================");

        int c = 100;
        c = c++;
        System.out.println("c = " + c);
    }
}

```

> 课程配图（未随笔记提交）

> 以后都是单独使用

## 3.赋值运算符

```java
基本赋值运算符:
  =  :  先看等号右边的,如果有运算,也得先算出结果,将结果赋值给等号左边的变量
复合赋值运算符:
  +=:
   int i = 10;
   i+=2;//i = i+2
  -=
  *=
  /=
  %=

注意:
  针对于复合赋值运算符,使用byte和short的时候,jvm会自动转型
```

```java
public class Demo04FuZhi {
    public static void main(String[] args) {
        int i = 10;
        i+=2;//i = i+2
        System.out.println(i);

        i*=2;//i = i*2
        System.out.println(i);
        System.out.println("================");

        byte b = 10;
        //b = b+2;
        b+=2;
        System.out.println(b);
    }
}

```

## 4.关系运算符(比较运算符)

```java
1.作用:用于比较,判断
2.结果:boolean型结果
```

| 符号 | 说明                                                         |
| ---- | ------------------------------------------------------------ |
| ==   | 判断符号前后的数据是否相等,如果相等返回true;否则返回false    |
| >    | 判断符号前的数据是否大于符号后的数据,如果大于返回true;否则返回false |
| <    | 判断符号前的数据是否小于符号后的数据,如果小于返回true;否则返回false |
| >=   | 判断符号前的数据是否大于或者等于符号后的数据,如果大于或者等于返回true,否则返回false |
| <=   | 判断符号前的数据是否小于或者等于符号后的数据,如果小于或者等于返回true,否则返回false |
| !=   | 判断符号前后数据是否不相等,如果不相等返回true;否则返回false  |

```java
public class Demo05Compare {
    public static void main(String[] args) {
        int i = 10;
        int j = 20;
        int k = 10;
        System.out.println(i == j);//false
        boolean result01 = i>j;
        System.out.println("result01 = " + result01);//false
        boolean result02 = i<j;
        System.out.println("result02 = " + result02);//true
        boolean result03 = i>=k;
        System.out.println("result03 = " + result03);//true
        boolean result04 = i<=k;
        System.out.println("result04 = " + result04);//true
        boolean result05 = i!=k;
        System.out.println("result05 = " + result05);//false
    }
}

```

## 5.逻辑运算符

```java
1.作用:连接多个boolean表达式
2.结果:boolean结果
```

| 符号        | 说明                                                         |
| ----------- | ------------------------------------------------------------ |
| &&(与,并且) | 有假则假,符号前后有一个为false,结果就是false                 |
| \|\|(或者)  | 有真则真,符号前后有一个为true,结果就是true                   |
| !(非,取反)  | 不是真就是假;不是假就是真                                    |
| ^(异或)     | 符号前后结果一样为false;不一样为true<br>true^true     结果为false<br>false^false   结果为false<br>true^false    结果为true<br>false^true    结果为true |

```java
public class Demo06LuoJi {
    public static void main(String[] args) {
        int i = 10;
        int j = 20;
        int k = 10;
        boolean result01 = (i>j)&&(i==k);
        System.out.println("result01 = " + result01);//false
        boolean result02 = (i>j)||(i==k);
        System.out.println("result02 = " + result02);//true
        boolean result03 = !(i>j);
        System.out.println("result03 = " + result03);//true
        boolean result04 = (i>j)^(i==k); // false^true
        System.out.println("result04 = " + result04);//true
    }
}

```

> ```java
> 单与:& -> 有假则假,如果符号前面为false,符号后面的还会判断
> 双与:&&(短路效果) -> 有假则假,如好前面为false,符号后面不看了
> 单或:| -> 有真则真,如果符号前面为true,符号后面的还会判断
> 双或:||(短路效果) -> 有真则真,如果符号前面为true,符号后面不看了
> ```
>
> ```java
> public class Demo07LuoJi {
>     public static void main(String[] args) {
>         int i = 10;
>         int j = 20;
>         //boolean result = (++i>100) && (++j>100);
>         boolean result = (++i>100) & (++j>100);
>         System.out.println("result = " + result);//false
>         System.out.println(i);
>         System.out.println(j);
>     }
> }
> ```
>
> ```java
> 问题: 定义一个变量x,判断是否在50到100之间
>       50<=x<=100 -> 不行 -> 数学写法
>       x>=50&&x<=100 -> java写法
> ```

## 6.三元运算符

```java
1.格式:
  boolean表达式?表达式1:表达式2

2.执行流程:
  先走boolean表达式判断,如果是true执行?后面的表达式1,否则执行:后面的表达式2
```

```java
public class Demo08SanYuan {
    public static void main(String[] args) {
        int score = 59;
        String result = score>=60?"及格":"不及格";
        System.out.println("result = " + result);
    }
}

```

```java
需求:有两个和尚,分别身高为150  , 170 获取两个和尚的最高身高
```

```java
public class Demo09SanYuan {
    public static void main(String[] args) {
      /*
       需求:有两个和尚,分别身高为150  , 170 获取两个和尚的最高身高
       */
        int h1 = 150;
        int h2 = 170;
        int result = h1>h2?h1:h2;
        System.out.println(result);
    }
}
```

```java
需求:有三个和尚,分别身高为150 210 170 获取三个和尚的最高身高
```

```java
public class Demo10SanYuan {
    public static void main(String[] args) {
      /*
       需求:有三个和尚,分别身高为150 210 170 获取三个和尚的最高身高
       */
        int h1 = 150;
        int h2 = 210;
        int h3 = 170;
        int temp = h1>h2?h1:h2;
        int result = temp>h3?temp:h3;
        System.out.println("result = " + result);
    }
}

```

# 第六章.进制的转换(了解)

| 十进制 | 二进制 | 八进制 | 十六进制 |
| ------ | ------ | ------ | -------- |
| 0      | 0      | 0      | 0        |
| 1      | 1      | 1      | 1        |
| 2      | 10     | 2      | 2        |
| 3      | 11     | 3      | 3        |
| 4      | 100    | 4      | 4        |
| 5      | 101    | 5      | 5        |
| 6      | 110    | 6      | 6        |
| 7      | 111    | 7      | 7        |
| 8      | 1000   | 10     | 8        |
| 9      | 1001   | 11     | 9        |
| 10     | 1010   | 12     | a或A     |
| 11     | 1011   | 13     | b或B     |
| 12     | 1100   | 14     | c或C     |
| 13     | 1101   | 15     | d或D     |
| 14     | 1110   | 16     | e或E     |
| 15     | 1111   | 17     | f或F     |
| 16     | 10000  | 20     | 10       |

## 3.1 十进制转成二进制

```java
辗转相除法-> 循环除以2,取余数
```

> 课程配图（未随笔记提交）：image-20211218165309579

## 3.2 二进制转成十进制

```java
8421规则
```

> 课程配图（未随笔记提交）：image-20211218165556758

## 3.3 二进制转成八进制

```java
将二进制分开(3位为一组)
```

> 课程配图（未随笔记提交）：1621755513297

## 3.4 二进制转成十六进制

```java
二进制分为4个为一组
```

> 课程配图（未随笔记提交）：1627036847498

# 第七章.位运算符(了解)

> 课程配图（未随笔记提交）：1621755993815

```java
1代表true   0代表false

我们要知道计算机在存储数据的时候都是存储的数据的补码,而计算的也是数据的补码

1.正数二进制最高位为0;负数二进制最高位是1
2.正数的原码(这个数的二进制表示形式),反码,补码一致
  如:5的原码,反码,补码为:
     0000 0000 0000 0000 0000 0000 0000 0101->二进制最高位是0,因为是正数
3.负数的话原码,反码,补码就不一样了
  反码是原码的基础上最高位不变,其他的0和1互变
  补码是在反码的基础上+1

  如:-9
     原码:1000 0000 0000 0000 0000 0000 0000 1001
     反码:1111 1111 1111 1111 1111 1111 1111 0110
     补码:1111 1111 1111 1111 1111 1111 1111 0111
```

#### （1）左移：<<

​	**运算规则**：左移几位就相当于乘以2的几次方

​	**注意：**当左移的位数n超过该数据类型的总位数时，相当于左移（n-总位数）位

```java
2<<2   等于8
相当于:2*(2的2次方)
```

> 课程配图（未随笔记提交）：1621689774890

```java
-2<<2   等于-8

相当于:-2*(2的2次方)
```

> 课程配图（未随笔记提交）：1621689784804

#### （2）右移：>>

快速运算：类似于除以2的n次，如果不能整除，**向下取整**

```java
9>>2  等于 2

相当于:9除以(2的2次方)

```

> 课程配图（未随笔记提交）：1621689793253

```java
-9>>2  等于-3

相当于:-9除以(2的2次方)
```

> 课程配图（未随笔记提交）：1621689801211

#### （3）无符号右移：>>>

运算规则：往右移动后，左边空出来的位直接补0，不管最高位是0还是1空出来的都拿0补

正数：和右移一样

```java
9>>>2  等于 2

相当于:9除以(2的2次方)
```

负数：右边移出去几位，左边补几个0，结果变为正数

```java
-9>>>2

结果为:1073741821
```

> 笔试题:8>>>32位->相当于没有移动还是8
>
> ​             8>>>34位->相当于移动2位

#### （4）按位与：&

小技巧:将0看成为false  将1看成true

运算规则：对应位都是1才为1,相当于符号左右两边都为true,结果才为true

​		1 & 1 结果为1  相当于  true&true

​		1 & 0 结果为0

​		0 & 1 结果为0

​		0 & 0 结果为0

```java
比如:  5&3   结果为1

```

> 课程配图（未随笔记提交）：1621689811573

#### （5）按位或：|

运算规则：对应位只要有1即为1,相当于符号前后只要有一个为true,结果就是true

​		1 | 1 结果为1

​		1 | 0 结果为1

​		0 | 1 结果为1

​		0 | 0 结果为0

```
比如: 5|3  结果为:7
```

> 课程配图（未随笔记提交）：1621689820632

#### （6）按位异或：^

​	运算规则：对应位一样的为0,不一样的为1

​		1 ^ 1 结果为0 false

​		1 ^ 0 结果为1  true

​		0 ^ 1 结果为1   true

​		0 ^ 0 结果为0  false

```java
比如: 5^3   结果为6
```

> 课程配图（未随笔记提交）：1621689829688

#### （7）按位取反

运算规则：~0就是1

​			       ~1就是0

```java
~10     ->  结果为-11
```

> 课程配图（未随笔记提交）：1621689837355

# 第八章.运算符的优先级(了解)

> 课程配图（未随笔记提交）：1621689848780

```java
提示说明：
（1）表达式不要太复杂
（2）先算的使用(),记住,如果想让那个表达式先运行,就加小括号就可以了
i<(n*m)
```
