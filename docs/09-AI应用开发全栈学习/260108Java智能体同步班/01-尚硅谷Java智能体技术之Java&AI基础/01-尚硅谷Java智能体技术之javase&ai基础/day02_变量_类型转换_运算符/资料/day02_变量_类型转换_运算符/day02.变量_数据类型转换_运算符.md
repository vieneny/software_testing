#  day02.变量  数据类型转换   运算符

```java
课前回顾:
  1.字节:计算机存储数据的最小计量单位,用byte或B表示
    8bit(二进制) = 1B -> 以后都是1024倍
  2.java的用处:主要开发应用程序(主要是网站式的操作系统)
  3.常见的dos命令:
    cd 文件夹名  进入指定文件夹
    cd 文件夹名\文件夹名 进入多级文件夹
    cd.. 退到上一级
    cd\  退到根目录
    exit  退出dos命令窗口
    dir   查看文件夹下都有啥
    盘符名:  切换盘符
  4.java环境:
    jvm:运行java程序的假想计算机,用于编译代码,运行代码
    跨平台:一次编写到处运行
    jre:运行java代码的环境,包含了jvm以及核心类库
    jdk:java开发工具包

    jdk包含jre,jre包含jvm
  5.环境变量:在任意位置编写代码以及运行代码
    JAVA_HOME
  6.入门程序:
    a.编写:创建一个xxx.java文件
      public class 类名{
          public static void main(String[] args){
              System.out.println("输出的内容");
          }
      }
    b.编译:会生成xxx.class文件,jvm运行只认class文件
      javac java文件名.java
    c.运行:
      java class文件名 -> 不要带.class后缀


  7.注释:对代码的解释说明
    a.单行注释: //
    b.多行注释: /**/
    c.文档注释: /***/
  8.关键字:java提前定义好的,具有特殊含义的小写单词
  9.print和println区别:
    println:自带换行效果
    print:不带换行效果

今日重点:
   除了第六章,第七章,第八章,都是重点
```

> 隐藏指定没有用的文件或者文件夹
>
> > 课程配图（未随笔记提交）

# 第一章.常量

```java
1.概述:在代码的运行过程中,值不会随着不同的情况发生改变的数据,也叫"字面值"
2.分类:
  整数常量:所有的整数
  小数常量:所有带小数点的  2.5  2.0
  字符常量:''表示, 单引号中必须有且只能有一个内容
          'a'    '11'(不是字符,因为11是两个内容)
          ''(不是字符,因为单引号中啥也没有)
          ' '(是字符,因为一个空格在引号中也算一个内容)

  字符串常量:""表示  双引号中随便写
  布尔常量:true(真) false(假)  -> 主要用于判断
  空常量:null  代表的是数据不存在,不能直接使用,null都是作为引用数据类型初始化值使用
```

```java
public class Demo01ChangLiang {
    public static void main(String[] args) {
        //整数常量
        System.out.println(10);
        //小数常量
        System.out.println(10.5);
        //字符常量
        System.out.println('a');
        //布尔常量
        System.out.println(true);
        //字符串常量
        System.out.println("hello world");
        System.out.println("");
        //空常量->不能直接使用,只能代表引用类型的初始化值
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
           /除号前后都是整数,结果只取整数部分,小数点直接舍去
           /除号前后一旦有一个是小数,结果就是正常小数
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
1.概述:在代码的运行过程中,值会随着不同的情况随时发生改变的数据,叫做变量
       int price = 10,后续如果这个价格该了,我们可以直接用price去做运算
2.定义格式:
  a. 数据类型 变量名 = 值 -> 一定要先看等号右边的,然后将等号右边的值赋值给等号左边的变量,即使等号右边有运算,咱们都得先算出结果,再将这个结果赋值给等号左边的变量
  b. 数据类型 变量名1 = 值1,变量名2 = 值2... -> 定义多个相同类型的变量

3.java中的数据类型 -> 背下来
  基本类型:4类8种
      a.整型:byte short int long
      b.浮点型:float double
      c.字符型:char
      d.布尔型:boolean

  引用类型:类 数组  接口  枚举 注解  Record类

4.注意:
  a.String属于类的一种,所以就属于引用类型了 -> 字符串的类型为String-> String 变量名 = ""
  b.整数默认类型为int;小数默认类型为double
5.按照取值范围来看,基本类型从小到大排列
  byte,short,char -> int -> long -> float -> double
```

```java
public class Demo01Var {
    public static void main(String[] args) {
        //byte
        byte num1 = 10;
        System.out.println(num1);
        // short
        short num2 = 10;
        System.out.println(num2);
        //int
        int num3 = 10;
        num3 = 200;
        System.out.println(num3);
        //long 给long赋值的话,值建议后面加L
        long num4 = 10L;
        System.out.println(num4);
        //float 给float赋值,值建议后面加F
        float num5 = 10.5F;
        System.out.println(num5);
        //double
        double num6 = 10.5;
        System.out.println(num6);
        //char
        char num7 = 'a';
        System.out.println(num7);
        //boolean
        boolean num8 = true;
        boolean num9 = false;
        /*
           num9是false
           num8 = num9代表的是将num9的值赋值给变量num8,num8就会由true变成false
         */
        num8 = num9;
        System.out.println(num8);

        System.out.println("==================");

        //定义一个字符串类型的变量
        String s = "金莲和大郎的故事";
        System.out.println(s);

    }
}

```

```java
public class Demo02Var {
    public static void main(String[] args) {
        int a = 10;
        int b = 3;
        System.out.println(a + b);// 13
        int sub = a - b;
        System.out.println(sub);//  7
        int mul = a * b;
        System.out.println(mul);//  30
        /*
           除号前后如果都是整数,结果只取整数部分 ,小数点直接舍去
           除号前后一旦有一个是小数,结果就是正常小数
         */
        int div = a / b;
        System.out.println(div);//  3
    }
}

```

```java
public class Demo03Var {
    public static void main(String[] args) {
       /*
          \:在java中代表的是转义字符
          1.可以将具有特殊含义的字符转成普通字符
          2.将普通字符转义成具有特殊含义的字符
        */

        /*
          n:普通字符
          \n:换行
         */
        System.out.println("hello\nworld");

        /*
          t:普通字符
          \t:制表符  tab
         */
        System.out.println("hello\tworld");

        /*
           用字符串表示一个路径
           \:转义字符
           我们需要将具有特殊含义的\变成普通的\字符
         */
        String path = "F:\\jdk\\bin";
        System.out.println(path);
    }
}
```

```java
public class Demo04Var {
    public static void main(String[] args) {
        var i = 10.5;
        System.out.println(i);
    }
}

```

## 2.变量使用时的注意事项

```java
1.在同一个作用域中(一个大括号就是一个作用域),不能定义重名的变量
2.在不同的作用域中,尽量不要随意互相访问变量
  a.在小作用域中可以直接访问大作用域中的变量
  b.在大作用域中不能直接访问小作用域中的变量
3.变量不初始化(第一次赋值)不能直接使用
```

```java
public class Demo05Var {
    public static void main(String[] args) {
        int i = 10;
        //int i = 20;//重新定义
        i = 20;//重新赋值
        System.out.println(i);

        {
           int j = 100;
           System.out.println(j);
           System.out.println(i);
        }
        //System.out.println(j);


        int x;
        //由于x没有被初始化,所以不能直接使用
        //System.out.println(x);
    }
}

```

## 3.练习

```java
定义一个人类,用变量表示 姓名 性别 年龄 身高 体重
```

```java
public class Demo06Person {
    public static void main(String[] args) {
        //姓名 String
        String name = "和珅";
        //性别 char
        char gender = '男';
        //年龄 int
        int age = 18;
        //身高 double
        double height = 1.78;
        //体重 double
        double weight = 80.5;
        System.out.println(name);
        System.out.println(gender);
        System.out.println(age);
        System.out.println(height);
        System.out.println(weight);
    }
}
```

# 第三章.标识符

```java
1.概述:给类,变量,方法取的名字
2.注意:
  硬性规定:
    a.标识符不能是关键字
    b.标识符中可以包含字母,数字,_和$,但是不能以数字开头
  软性建议:
    a.给类取名字,遵循大驼峰式命名规范(每个单词首字母大写)
    b.给方法,变量取名字遵循小驼峰式命名规范(从第二个单词开始首字母大写)
```

# 第四章.数据类型转换

```java
1.什么时候发生数据类型转换:等号左右两边类型不一致
2.怎么转换:
  a.自动类型转换
  b.强制类型转换(强转)
```

> 按照取值范围大小排序:
>
>   byte short char -> int -> long -> float -> double

## 1.自动类型转换->小转大

```java
1.自动类型转换发生时机:
  a.取值范围大的类型 变量名 = 取值范围小的类型 -> 小转大
  b.取值范围大的类型和取值范围小的类型做运算 -> 小转大
```

```java
public class Demo01DataType {
    public static void main(String[] args) {
        /*
           100默认类型int
           num1类型为long
           将100赋值给long型的num1,相当于将取值范围小的类型赋值给取值范围大的类型
           发生了自动类型转换
         */
        long num1 = 100;
        System.out.println(num1);

        int a = 10;
        double b = 2.5;

        /*
            double = int+double
            double = double+double
         */
        double sum = a+b;
        System.out.println(sum);
    }
}

```

## 2.强制类型转换

```java
1.强制类型转换发生时机:
  a.取值范围小的类型 变量名 = 取值范围大的类型-> 报错,需要强转
  b.怎么强转:
    取值范围小的类型 变量名 = (取值范围小的类型)取值范围大的类型
```

```java
public class Demo02DataType {
    public static void main(String[] args) {
        /*
           2.5默认类型double
           a类型为int
           将2.5赋值给int型的a,相当于将取值范围大的类型赋值给取值范围小的类型
           需要强转
         */
        //int a = 2.5;
        int a = (int)2.5;
        System.out.println(a);
    }
}

```

## 3.强转的注意事项

```java
1.不要故意写成强转形式,除非没有办法,否则容易出现精度损失和数据溢出现象
2.byte和short如果等号右边是字面值,不超范围,不需要我们自己手动强转,jvm帮我们自动强转了
  byte和short的变量如果等号右边有变量参与运算,byte和short会自动提升为int型,如果最终结果重新赋值给byte或者short的变量,需要我们自己手动强转

3.char类型如果做运算,会自动提升为int,会去ASCII码表中找这个字符对应的int值,如果ASCII码表中没有,去自动去unicode码表(万国码)中查找字符对应的int值
```

```java
public class Demo02DataType {
    public static void main(String[] args) {
        /*
           2.5默认类型double
           a类型为int
           将2.5赋值给int型的a,相当于将取值范围大的类型赋值给取值范围小的类型
           需要强转
         */
        //int a = 2.5;
        int a = (int)2.5;
        System.out.println(a);

        System.out.println("==================");

        /*
           int占内存4个字节,1一个字节是8个二进制位,所以4个字节就是32位二进制
           100亿换算成二进制36位二进制,干掉前4位二进制,最后算回十进制就是
           最终结果
         */
        int num2 = (int)10000000000L;
        System.out.println(num2);//1410065408

        System.out.println("==================");

        byte b = 10;
        System.out.println(b);

        byte result = (byte)(b+1);
        System.out.println(result);

        System.out.println("==================");

        char c = 'a';
        System.out.println(c+0);//97

        System.out.println('中'+0);//20013
    }
}

```

> > 课程配图（未随笔记提交）
>
> double 和float 的变量在开发中不要直接做运算,因为都会出现精度损失问题

# 第五章.运算符

## 1.算数运算符

| 符号 | 说明     |
| ---- | -------- |
| +    | 加法     |
| -    | 减法     |
| *    | 乘法     |
| /    | 除法     |
| %    | 模(取余) |

```java
public class Demo01SuanShu {
    public static void main(String[] args) {
        int a = 10;
        int b = 3;
        int sum = a + b;
        System.out.println(sum);
        int sub = a - b;
        System.out.println(sub);
        int mul = a * b;
        System.out.println(mul);
        int div = a / b;
        System.out.println(div);
        int mod = a % b;
        System.out.println(mod);
    }
}
```

```java
+
  1.加法
  2.字符串拼接:任意类型遇到字符串都会变成字符串,此时就不是运算了,会直接往后拼接内容
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

        System.out.println("a和b相加等于:"+(a+b));

        int result = a+b;
        System.out.println("result = " + result);//变量名.soutv

    }
}
```

## 2.自增自减运算符(也算算数运算符的一种)

```java
1.格式:
  变量++
  ++变量
  变量--
  --变量
2.作用:
  让一个变量的值+1或者-1

3.注意:
  单独使用:++ --单独为一句代码,没有和其他的代码混合使用
         符号在前还是在后,都是先运算
  混合使用:++ --和其他语句混合使用了
         a.符号在前:先运算,再使用运算后的值
         b.符号在后:先试用原值,再运算

```

```java
public class Demo03SuanShu {
    public static void main(String[] args) {
        int i = 10;
        //单独使用
        //i ++;
        ++i;
        System.out.println(i);
        System.out.println("=====================");

        int j = 10;
        //混合使用
        //int result = ++j;
        int result = j++;
        System.out.println(result);//10
        System.out.println(j);//11

        System.out.println("=====================");
        int c = 100;
        c = c++;
        System.out.println(c);
        System.out.println(c);
    }
}

```

> 课程配图（未随笔记提交）

> 以后开发只使用单独使用的方式

## 3.赋值运算符

```java
1.基本赋值运算符
  = -> 先看等号右边的
2.复合赋值运算符
  +=
  -=
  *=
  /=
  %=

3.注意:
  复合赋值运算符会需要强转的话会自动强转
```

```java
public class Demo04FuZhi {
    public static void main(String[] args) {
        int i = 10;
        i += 3;//i = i+3
        System.out.println(i);
        System.out.println("==============");

        byte b = 10;
        b+=1;//b = b+1
        System.out.println(b);
    }
}

```

## 4.关系运算符(比较运算符)

```java
1.作用:主要是用于比较的,做判断条件
2.结果:boolean类型的结果
```

| 符号 | 说明                                                         |
| ---- | ------------------------------------------------------------ |
| ==   | 判断符号两边的结果是否相等,如果相等为true,否则为false        |
| >    | 判断符号前的是否大于符号后的,如果大于为true,否则为false      |
| <    | 判断符号前的是否小于符号后的,如果小于为true,否则为false      |
| >=   | 判断符号前的是否大于或者等于符号后的,如果大于或者等于为true,否则为false |
| <=   | 判断符号前的是否小于或者等于符号后的,如果小于或者等于为true,否则为false |
| !=   | 判断符号两边的结果是否不相等,如果不相等为true,否则为false    |

```java
public class Demo05Compare {
    public static void main(String[] args) {
        int i = 10;
        int j = 20;
        int k = 10;
        boolean result01 = i == j;
        System.out.println(result01);

        System.out.println(i > j);// false
        System.out.println(i < j);// true
        System.out.println(i >= k);// true
        System.out.println(i <= k);// true
        System.out.println(i != k);// false
    }
}

```

## 5.逻辑运算符

```java
1.作用:连接多个判断条件  score = 60  score>=0 && score<=100
2.结果:boolean型结果
```

| 符号 | 说明                                                         |
| ---- | ------------------------------------------------------------ |
| &&   | 与,并且  有假则假符号前后有一个是false,结果就是false;符号前后都是true,结果才是true |
| \|\| | 或  有真则真,符号前后有一个为true,结果就是true               |
| !    | 非,取反                                                      |
| ^    | 异或:  符号前后结果一样为false,不一样为true<br>true^true  -> false<br>true^false -> true |

```java
public class Demo06LuoJi {
    public static void main(String[] args) {
        int i = 10;
        int j = 20;
        int k = 10;
        boolean result = (i > j) && (i == k);
        System.out.println(result);// false

        boolean result02 = (i > j) || (i == k);
        System.out.println(result02);// true

        boolean result03 = !(i > j);
        System.out.println(result03);
    }
}
```

> ```java
> &:有假则假,如果符号前面为false,还会继续判断符号后面的
> &&:有假则假,如果符号前面为false.符号后面就不判断了 -> 短路效果
>
> |:有真则真,如果符号前面为true,还会继续判断符号后面的
> ||:有真则真,如果符号前面为true,符号后面就不判断了 -> 短路效果
> ```
>
> ```java
> public class Demo07LuoJi {
>     public static void main(String[] args) {
>         int a = 10;
>         int b = 20;
>         //boolean result = ++a > 100 & ++b > 100;
>         boolean result = ++a > 100 && ++b > 100;
>         System.out.println(result);
>         System.out.println(a);
>         System.out.println(b);
>     }
> }
>
> ```
>
> ```java
>  score = 60  score>=0 && score<=100
> ```

## 6.三元运算符

```java
1.格式:
  boolean表达式?表达式1:表达式2
2.执行流程:
  先走boolean表达式判断,如果是true,就走?后面的表达式1,否则就走:后面的表达式2
```

```java
public class Demo06SanYuan {
    public static void main(String[] args) {
        int score = 59;
        String result = score>=60?"及格":"不及格";
        System.out.println(result);
    }
}
```

```java
需求:有两个和尚,分别身高为150  , 170 获取两个和尚的最高身高
```

```java
public class Demo09SanYuan {
    public static void main(String[] args) {
        int heShang1 = 150;
        int heShang2 = 170;
        int result = heShang1 > heShang2 ? heShang1 : heShang2;
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
        int heShang1 = 150;
        int heShang2 = 210;
        int heShang3 = 170;
        int temp = heShang1 > heShang2 ? heShang1 : heShang2;
        int max = temp > heShang3 ? temp : heShang3;
        System.out.println(max);
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
从右边开始将二进制分开(3位为一组),如果左边剩下的不够3位,前面补0
```

> 课程配图（未随笔记提交）：1621755513297

## 3.4 二进制转成十六进制

```java
从右边开始将二进制分为4个为一组,如果左边剩下的不够4位,前面补0
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
