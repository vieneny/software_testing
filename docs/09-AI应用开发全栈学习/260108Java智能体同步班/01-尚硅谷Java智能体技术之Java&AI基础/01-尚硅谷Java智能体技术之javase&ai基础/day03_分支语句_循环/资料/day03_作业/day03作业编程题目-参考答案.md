### day03作业编程题

### 题目1:

```java
需求:
    让用户依次录入三个整数，求出三个数中的最大值，并打印到控制台。【使用if】

实现步骤:
1.创建Scanner对象
2.调用三次nextInt()  a  b  c
3.定义一个第三方变量temp
  if(a>b){
    temp = a;
  }else{
    temp = b;
  }

  int max = 0;
  if(temp>c){
      max = temp;
  }else{
      max = c;
  }

```

**您的代码**

```java
/*
    需求:
        让用户依次录入三个整数，求出三个数中的最大值，并打印到控制台。【使用if】

    实现步骤:
        1.创建键盘录入Scanner类的对象
        2.获取键盘录入的三个整数数字,保存到三个int变量a,b,c中
        3.定义int变量temp,保存a和b的最大值
        4.使用if语句第二种格式计算a和b的最大值,保存到temp中
        5.定义int变量max,保存temp和c的最大值
        6.使用if语句第二种格式计算temp和c的最大值,保存到max中
        7.打印max的值
 */
public class Test01_01 {
    public static void main(String[] args) {
        //1.创建键盘录入Scanner类的对象
        Scanner sc = new Scanner(System.in);

        //2.获取键盘录入的三个整数数字,保存到三个int变量a,b,c中
        System.out.println("请输入第一个整数数字:");
        int a = sc.nextInt();

        System.out.println("请输入第二个整数数字:");
        int b = sc.nextInt();

        System.out.println("请输入第三个整数数字:");
        int c = sc.nextInt();

        //3.定义int变量temp,保存a和b的最大值
        int temp;

        //4.使用if语句第二种格式计算a和b的最大值,保存到temp中
        if (a > b) {
            temp = a;
        } else {
            temp = b;
        }
        //5.定义int变量max,保存temp和c的最大值
        int max;

        //6.使用if语句第二种格式计算temp和c的最大值,保存到max中
        if (temp > c) {
            max = temp;
        } else {
            max = c;
        }
        //7.打印max的值
        System.out.println("最大值: "+max);
    }
}

```



### 题目2:

```java
需求:
    1.根据程序员的工龄(整数)给程序员涨工资(整数),程序员的工龄和基本工资通过键盘录入
    2.涨工资的条件如下：
        [10-15)     +20000
        [5-10)      +10000
        [3~5)       +5000
        [1~3)       +3000
     3.运行程序:
         请输入作为程序员的你的工作的工龄:10
         请输入作为程序员的你的基本工资为:60000
         程序运行后打印格式
             "您目前工作了10年，基本工资为 60000元, 应涨工资 20000元,涨后工资 80000元"

实现步骤:
    1.创建Scanner对象
    2.调用nextInt()  age  salary
    3.判断,符合某个条件,涨薪多少
```

**您的代码**

```java
/*
    需求:
        1.根据程序员的工龄(整数)给程序员涨工资(整数),程序员的工龄和基本工资通过键盘录入
        2.涨工资的条件如下：
            [10-15)     +20000
            [5-10)      +10000
            [3~5)       +5000
            [1~3)       +3000

         3.运行程序:
             请输入作为程序员的你的工作的工龄:10
             请输入作为程序员的你的基本工资为:60000
             程序运行后打印格式
                "您目前工作了10年，基本工资为 60000元, 应涨工资 20000元,涨后工资 80000元"

    实现步骤:
        1.创建键盘录入Scanner类的对象
        2.获取键盘录入的代表工龄的整数数字,保存到int变量years中
        3.获取键盘录入的代表基本工资的整数数字,保存到int变量salary中
        4.定义int变量upSalary,记录应涨钱数
        5.使用if语句的第三种格式,根据工龄所在的区间,给变量upSalary进行赋值
        6.按照格式打印结果
 */
public class Test02 {
    public static void main(String[] args) {
        //1.创建键盘录入Scanner类的对象
        Scanner sc = new Scanner(System.in);

        //2.获取键盘录入的代表工龄的整数数字,保存到int变量years中
        System.out.println("请输入作为程序员的你的工作的工龄:");
        int years = sc.nextInt();

        //3.获取键盘录入的代表基本工资的整数数字,保存到int变量salary中
        System.out.println("请输入作为程序员的你的基本工资为:");
        int salary = sc.nextInt();

        //4.定义int变量upSalary,记录应涨钱数
        int upSalary /*= 0*/;

        //5.使用if语句的第三种格式,根据工龄所在的区间,给变量upSalary进行赋值
        if (years >= 10 && years < 15) {
            upSalary = 20000;
        } else if (years >= 5 && years < 10) {
            upSalary = 10000;
        } else if (years >= 3 && years < 5) {
            upSalary = 5000;
        } else if (years >= 1 && years < 3) {
            upSalary = 3000;
        } else {//隐藏条件: years<1 || years>=15
            upSalary = 0;
        }

        //6.按照格式打印结果
        System.out.println("您目前工作了" + years + "年，基本工资为 "
                + salary + "元, 应涨工资 " + upSalary + "元,涨后工资 "+(salary+upSalary)+"元");
    }
}

```



### 题目4:

```java
需求:
    打印出1到100之间的既是3的倍数又是5倍数的数字以及这些数字的和
实现步骤:
    判断条件(i%3==0 && i%5==0)
```

##### 答案:

```java
/*
    需求:
        打印出1到100之间的既是3的倍数又是5倍数的数字以及这些数字的和

        总的条件: 既是3的倍数又是5倍数
        条件1是3的倍数: 数字%3==0
        条件2是5倍数: 数字%5==0
        以上条件1和条件2是&&的关系

    实现步骤:
        1.定义int变量sum,初始值0,用来累加求和
        2.使用for循环获取1到100之间的数字,循环变量int类型num
        2.1 如果num中的数字既是3的倍数又是5倍数,说明是满足条件的数字,打印该数字
        2.2 把num中的数字累加到求和变量sum中
        3.for循环结束后,打印输出sum的值
 */
public class Test01 {
    public static void main(String[] args) {
        //1.定义int变量sum,初始值0,用来累加求和
        int sum = 0;

        //2.使用for循环获取1到100之间的数字,循环变量int类型num
        for (int num = 1; num <= 100; num++) {
            //2.1 如果num中的数字既是3的倍数又是5倍数,说明是满足条件的数字,打印该数字
            if ((num % 3 == 0) && (num % 5 == 0)) {
                System.out.println(num);
                //2.2 把num中的数字累加到求和变量sum中
                sum += num;
            }

        }
        //3.for循环结束后,打印输出sum的值
        System.out.println("以上满足条件的数字之和: "+sum);
    }
}

```



### 题目5:

```java
需求:
    从键盘上录入一个大于100的三位数,打印出100到该数字之间满足如下要求的数字,数字的个数,以及数字的和:
        1.数字的个位数不为7;
        2.数字的十位数不为5;
        3.数字的百位数不为3;
实现步骤:
  int n = Scanner.nextInt();
  for(int i = 100; i<n;i++){

  }
```

##### 答案:

```java
/*
    需求:
        从键盘上录入一个大于100的三位数,打印出100到该数字之间满足如下要求的数字,数字的个数,以及数字的和:
            1.数字的个位数不为7;
            2.数字的十位数不为5;
            3.数字的百位数不为3;

        分析条件:
            条件1个位数不为7: 数字%10 != 7
            条件2十位数不为5: 数字/10%10 != 5
            条件3百位数不为3: 数字/100%10 != 3

            以上三个条件是&&的关系


    实现步骤:
        1.创建键盘录入Scanner类的对象
        2.获取键盘录入的大于100的整数数字,保存到int变量maxNum中
        3.定义int变量sum,初始值0,用来累加求和
        4.定义int变量count,初始值0,用来统计个数
        5.使用for循环获取从100到maxNum之间的三位数字,保存到int变量num中
        5.1 计算num中数字的个位,十位,百位,分别保存到int变量ge,shi,bai中
        5.2 判断如果满足 个位数不为7 并且  十位数不为5 并且 百位数不为3 说明是符合条件的数字
        5.3 打印num中的数字
        5.4 把num中的数字累加到求和变量sum中
        5.5 计数器count的值增加1
        6.for循环结束后,打印结果数据
 */
public class Test02 {
    public static void main(String[] args) {
        //1.创建键盘录入Scanner类的对象
        Scanner sc = new Scanner(System.in);

        //2.获取键盘录入的大于100的整数数字,保存到int变量maxNum中
        System.out.println("请输入一个大于100的整数数字: ");
        int maxNum = sc.nextInt();

        //3.定义int变量sum,初始值0,用来累加求和
        int sum = 0;

        //4.定义int变量count,初始值0,用来统计个数
        int count = 0;

        //5.使用for循环获取从100到maxNum之间的三位数字,保存到int变量num中
        for (int num = 100; num <= maxNum; num++) {
            //5.1 计算num中数字的个位,十位,百位,分别保存到int变量ge,shi,bai中
            int ge = num % 10;//个位
            int shi = num / 10 % 10;//十位
            int bai = num / 100 % 10;//百位

            //5.2 判断如果满足 个位数不为7 并且  十位数不为5 并且 百位数不为3 说明是符合条件的数字
            if ((ge != 7) && (shi != 5) && (bai != 3)) {
                //5.3 打印num中的数字
                System.out.println(num);

                //5.4 把num中的数字累加到求和变量sum中
                sum += num;

                //5.5 计数器count的值增加1
                count++;
            }

        }
        //6.for循环结束后,打印结果数据
        System.out.println("以上满足条件的数字之和: "+sum);
        System.out.println("以上满足条件的数字个数: "+count);
    }
}

```



### 题目6:

```java
需求:
    1.打印所有四位数中 个位 + 千位 == 百位 + 十位 的数字
    2.最后要打印符合条件的数字的总数量
       3.打印格式如下:
        1010
        1021
        1032
        1043
        ....
        以上满足条件的四位数总共有 615 个
实现步骤:

```

##### 答案:

```java
/*
    需求:
        1.打印所有四位数中 个位 + 千位 == 百位 + 十位 的数字
        2.最后要打印符合条件的数字的总数量
        3.打印格式如下:
            1010
            1021
            1032
            1043
            ....
            以上满足条件的四位数总共有 615 个

    实现步骤:
        1.定义int变量count,初始值0,用来统计个数
        2.使用for循环获取所有的四位数字,循环变量int类型num
        2.1 计算num中数字的个位,十位,百位,千位,分别保存到int变量ge,shi,bai,qian中
        2.2 判断如果 个位 + 十位 的和 等于 百位 + 千位的和,说明是满足条件的数字
        2.3 打印num中的数字
        2.4 计数器增加1
        3.for循环结束后,打印count的值
 */
public class Test03 {
    public static void main(String[] args) {
        //1.定义int变量count,初始值0,用来统计个数
        int count = 0;

        //2.使用for循环获取所有的四位数字,循环变量int类型num
        for (int num = 1000; num <= 9999; num++) {
            //2.1 计算num中数字的个位,十位,百位,千位,分别保存到int变量ge,shi,bai,qian中
            int ge = num % 10;//个位
            int shi = num / 10 % 10;//十位
            int bai = num / 100 % 10;//百位
            int qian = num / 1000 % 10;//千位

            //2.2 判断如果 个位 + 十位 的和 等于 百位 + 千位的和,说明是满足条件的数字
            if ((ge + shi) == (bai + qian)) {
                //2.3 打印num中的数字
                System.out.println(num);

                //2.4 计数器增加1
                count++;
            }

        }
        //3.for循环结束后,打印count的值
        System.out.println("以上满足条件的数字总共有: "+count+"个!!!!!!!!!!!!!!!!!!!!");
    }
}

```
