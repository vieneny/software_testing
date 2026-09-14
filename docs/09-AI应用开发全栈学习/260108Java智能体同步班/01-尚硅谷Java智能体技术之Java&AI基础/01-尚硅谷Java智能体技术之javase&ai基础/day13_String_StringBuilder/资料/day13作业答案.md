# Day13作业答案

## 选择题

### 题目1(单选):

​	下面是关于String类 API 当中与判断相关的方法，如果用于忽略大小写验证码的判断，最佳的方法是（B）

#### 选项 :

A：

```
public boolean equals(Object anObject){  ... }
```

B：

```
public boolean equalsIgnoreCase(String anotherString){ ... }
```

C：

```
public boolean endsWith(String suffix){ ... }
```

D：

```
public boolean startsWith(String prefix){ ... }
```

------

### 题目2(单选):

​	下列代码的运行结果是（ C ）

```java
public static void main(String[] args) {
    String s1 = "abc";
    String s2 = "abc";
    String s3 = "ABC";
    String s4 = "a";
    String s5 = s4 + "bc";
    System.out.println(s1.equals(s2));
    System.out.println(s1.equalsIgnoreCase(s3));
    System.out.println(s2.equals(s5));
    System.out.println(s3.equalsIgnoreCase(s5));
}
```

#### 选项 :

​	A:  true false true true

      B:  true true false true

​	C:  true true true true

​	D:  true true true false



------

### 题目3(单选):

​	以下哪个选项可以获取字符串对象的长度（ B）

#### 选项 :

A：

```
public int length
```

B：

```
public int length(){ ... }
```

C：

```
public int size(){ ... }
```

D：

```
public char charAt(int index){ ... }
```



------

### 题目4(多选):

​	下列关于String和StringBuilder的区别(BC )

#### 选项 :

​	A:  String是可变的字符序列

      B:  String是不可变的字符序列

​	C:  StringBuilder是可变的字符序列

​	D:  StringBuilder是不可变的字符序列

------

​	D:  0



------

## 代码题

### 题目9:

​	键盘录入一个字符串，统计该字符串中大写字母字符，小写字母字符，数字字符出现的次数(不考虑其他字符)

### 训练提示

1.  定义统计变量
2. 遍历字符串,筛选出指定的字符, 让对应记录的变量累加

### 操作步骤

1. 键盘录入一个字符串，用 Scanner 实现

2. 要统计三种类型的字符个数，需定义三个统计变量，初始值都为0

3. 遍历字符串，得到每一个字符

4. 判断该字符属于哪种类型，然后对应类型的统计变量+1   

   ​	假如ch是一个字符，我要判断它属于大写字母，小写字母，还是数字，直接判断该字符是否在对应的范围即可   

   ​	大写字母：ch>='A' && ch<='Z'   

   ​	小写字母： ch>='a' && ch<='z'   

   ​	数字： ch>='0' && ch<='9' 5:

5. 输出三种类型的字符个数



### 参考代码

```java


import java.util.Scanner;

/*
    需求：
        键盘录入一个字符串，统计该字符串中大写字母字符，小写字母字符，数字字符出现的次数(不考虑其他字符)

    思路：
        1:键盘录入一个字符串，用 Scanner 实现
        2:要统计三种类型的字符个数，需定义三个统计变量，初始值都为0
        3:遍历字符串，得到每一个字符
        4:判断该字符属于哪种类型，然后对应类型的统计变量+1
            假如ch是一个字符，我要判断它属于大写字母，小写字母，还是数字，直接判断该字符是否在对应的范围即可
            大写字母：ch>='A' && ch<='Z'
            小写字母： ch>='a' && ch<='z'
            数字： ch>='0' && ch<='9'
        5:输出三种类型的字符个数
 */
public class StringTest03 {
    public static void main(String[] args) {
        //键盘录入一个字符串，用 Scanner 实现
        Scanner sc = new Scanner(System.in);

        System.out.println("请输入一个字符串：");
        String line = sc.nextLine();

        //要统计三种类型的字符个数，需定义三个统计变量，初始值都为0
        int bigCount = 0;
        int smallCount = 0;
        int numberCount = 0;

        //遍历字符串，得到每一个字符
        for(int i=0; i<line.length(); i++) {
            char ch = line.charAt(i);

            //判断该字符属于哪种类型，然后对应类型的统计变量+1
            if(ch>='A' && ch<='Z') {
                bigCount++;
            } else if(ch>='a' && ch<='z') {
                smallCount++;
            } else if(ch>='0' && ch<='9') {
                numberCount++;
            }
        }

        //输出三种类型的字符个数
        System.out.println("大写字母：" + bigCount + "个");
        System.out.println("小写字母：" + smallCount + "个");
        System.out.println("数字：" + numberCount + "个");

    }
}
```



------

### 题目10:

​	请定义一个方法用于判断一个字符串是否是对称的字符串，并在主方法中测试方法。例如："abcba"、"上海自来水来自海上"均为对称字符串。

### 训练提示

1、判断是否对称，方法的返回值是什么类型boolean.参数列表需要接收一个S

2、怎样判断对称呢？如果可以将字符串反转，反转后发现跟原来的字符串完全一样，不就可以判断出来了吗，那么哪个类有字符串的反转功能呢？

### 操作步骤

1、定义方法，返回值类型为boolean，参数列表为String类型的一个参数。

2、将字符串转换为StringBuilder类型，调用StringBuilder的reverse()方法将字符串反转。

3、将反转后的字符串再转回String类型，并与原字符串比较，如果相等，返回true，否则返回false

4、在主方法中，定义一个字符串，调用方法测试结果。

### 参考代码

```java
public class Test05 {
    public static void main(String[] args) {
        String str = "上海自来水来自海上";
        System.out.println(isSym(str));
    }

    public static boolean isSym(String str) {
        // 为了程序的健壮，如果传递的是空值，返回false
        if (str == null) {
            return false;
        }
        // 转换为StringBuilder
        StringBuilder sb = new StringBuilder(str);
        // 反转，再转成String
        String reStr = sb.reverse().toString();
        // 比较与原字符串是否相等
        // 相等返回true，不相等返回false，正好与equals的返回值一致，直接返回即可。
        return reStr.equals(str);
    }
}
```
