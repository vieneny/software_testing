# day04._数组

```java
课前回顾:
  1.Scanner:键盘录入
    a.导包:import java.util.Scanner
    b.创建对象:Scanner 变量名 = new Scanner(System.in)
    c.调用方法:
      变量名.nextInt()录入整数
      变量名.next()录入字符串
  2.switch:
    a.格式:
      switch(变量名){
          case 目标值1:
              执行语句1;
              break;
          case 目标值2:
              执行语句2;
              break;
              ...
          default:
              执行语句n
              break;
      }
   b.执行流程:从上到下和case后面的目标值做匹配,匹配上哪个case就走哪个case对应的执行语句,break结束switch
             如果以上所有的case都没有匹配上,就走default对应的执行语句n
   c.没有break:会出现case的穿透性,从匹配上的case开始向下穿透执行,直到遇到break或者switch结束了为止

 3.if判断:
   a.格式:
     if(boolean表达式){
         执行语句
     }
   b.执行流程:先走if对应的boolean表达式,如果是true,就走if对应的执行语句,否则就不走
 4.if...else
   a.格式:
     if(boolean表达式){
         执行语句1
     }else{
         执行语句2
     }
   b.执行流程:
     先走if后面的boolean表达式判断,如果是true,就走if里面的执行语句1,否则就走else对应的执行语句2
 5.else...if
   a.格式:
     if(boolean表达式){
         执行语句1
     }else if(boolean表达式){
         执行语句2
     }...else{
         执行语句n
     }
   b.执行流程:
     从上到下挨个判断,哪个条件成立,就走哪个if对应的执行语句,如果以上所有的判断都不成立,就走else对应的执行语句n
 6.for循环:
   a.格式:
     for(初始化变量;比较;步进表达式){
         循环语句
     }
   b.执行流程:
     先初始化变量,比较,如果是true,就走循环语句,走步进表达式;再比较,如果还是true,继续循环,继续走步进表达式,再比较,直到比较为false,循环结束

 7.while循环:
   a.格式:
     初始化变量
     while(比较){
         循环语句
         步进表达式
     }
   b.执行流程:先初始化变量,比较,如果是true,就走循环语句,走步进表达式;再比较,如果还是true,继续循环,继续走步进表达式,再比较,直到比较为false,循环结束

 8.do...while
   a.格式:
     初始化变量
     do{
         循环语句
         步进表达式
     }while(比较);
   b.执行流程:
     先初始化变量,走循环语句,走步进表达式,比较,如果是true,继续循环,继续步进,再比较,直到比较为false,循环结束

 9.循环控制语句:
   break:结束循环
   continue:结束本次循环,进入下一次循环
 10.死循环:条件永远是true
 11.嵌套循环:
    先走外层循环,再走内层循环,内层循环就一直循环,直到内层循环结束,外层循环进入到下一次循环,直到外层循环都结束了整体结束
 12.Random随机数:
    a.导包:import java.util.Random
    b.创建对象:Random 变量名 = new Random()
    c.调用方法:
      变量名.nextInt(int bound) -> 在0-(bound-1)之间随机一个整数

今日重点:
  1.知道数组的作用
  2.知道数组的特点
  3.会定义数组,为数组存元素,取元素,遍历元素
```

# 第一章.数组的介绍以及定义

```java
1.概述:数组是一个容器,本身属于引用类型
2.作用:
  一次存多个数据
3.特点:
  a.定长(定义数组的时候长度为多少,后续不能更改)
  b.既能存储基本类型,也能存储引用类型的数据
4.定义:
  a.动态初始化:
    数据类型[] 数组名 = new 数据类型[数组长度] -> 常用
    数据类型 数组名[] = new 数据类型[数组长度] -> 常用

    等号左边的数据类型: 规定数组中元素的类型
    []:代表数组
    数组名:见名知意
    new:创建数组
    new后面的数据类型:要和等号左边的数据类型一致
    [数组长度]:给数组规定长度,最多能存多少个数据

  b.静态初始化:
    数据类型[] 数组名 = new 数据类型[]{元素1,元素2...} ->不常用
    数据类型 数组名[] = new 数据类型[]{元素1,元素2...} ->不常用
  c.简化静态初始化:
    数据类型[] 数组名 = {元素1,元素2...} -> 静态初始化中最常用的格式

```

```java
public class Demo01Array {
    public static void main(String[] args) {
        //动态初始化
        int[] arr1 = new int[3];
        String[] arr2 = new String[3];

        //静态初始化
        int[] arr3 = {1,2,3,4,5};
        String[] arr4 = {"努尔哈赤","皇太极","顺治","康熙","雍正","乾隆","嘉庆","道光","咸丰","同治","光绪","宣统"};
    }
}
```

> 将8种基本数据类型的数组定义一遍 -> 动态 初始化 以及 静态初始化

# 第二章.操作数组

## 1.获取数组的长度

```java
1.格式:
  数组名.length
2.注意:
  数组中的length,不是一个方法,而是数组中的一个属性
```

```java
public class Demo02Array {
    public static void main(String[] args) {
        int[] arr = {2,21,23,341,4,4,3,3,5,65,67,7,7};
        System.out.println(arr.length);
    }
}
```

## 2.索引

```java
1.概述:元素在数组中的位置(编号,下标)
2.特点:
  a.从0开始的,最大索引是 数组的长度-1(数组名.length-1)
  b.索引是唯一的
3.注意:
  我们操作元素,都是根据索引来操作的 -> 存,取
```

> 课程配图（未随笔记提交）

## 3.存储元素

```java
1.格式:
  数组名[索引值] = 元素 -> 将元素存储到数组的指定索引位置上
```

```java
public class Demo03Array {
    public static void main(String[] args) {
        int[] arr = new int[3];
        //存元素
        arr[0] = 100;
        arr[1] = 200;
        arr[2] = 300;
        //arr[3] = 400;
        System.out.println(arr[0]);
        System.out.println(arr[1]);
        System.out.println(arr[2]);
    }
}
```

## 4.获取元素

```java
 1.格式:
   数组名[索引值]
 2.注意:
   a.数组不能直接输出数组名,因为直接输出数组名会输出数组在内存中的地址值
 3.地址值:
   引用类型数据在内存中保存的唯一编号,我们可以通过这个唯一编号,在内存中找到这个数据
```

```java
public class Demo04Array {
    public static void main(String[] args) {
        int[] arr = new int[3];
        arr[0] = 100;
        arr[1] = 200;
        arr[2] = 300;
        System.out.println(arr);//[I@776ec8df
        System.out.println(arr[0]);
        System.out.println(arr[1]);
        System.out.println(arr[2]);
    }
}

```

> 课程配图（未随笔记提交）

> arr1[0] = arr2[1] -> 将arr2这个数组的1索引上的元素取出来放到arr1这个数组的0索引上

## 5.遍历数组

```java
1.概述:挨个将数组中的元素获取出来
2.快捷键:
  数组名.fori
```

```java
public class Demo05Array {
    public static void main(String[] args) {
        int[] arr = {1,2,3,4,5};
        for (int i = 0; i < arr.length; i++) {
            System.out.println(arr[i]);
        }
    }
}
```

## 6.操作数组时容易出现的问题

### 6.1.数组索引越界异常_ArrayIndexOutOfBoundsException

```java
1.出现的原因:操作的索引超出了数组的索引范围
```

```java
public class Demo06Array {
    public static void main(String[] args) {
        int[] arr = new int[3];
        arr[0] = 100;
        arr[1] = 200;
        arr[2] = 300;
        System.out.println(arr[0]);
        System.out.println(arr[1]);
        System.out.println(arr[2]);
        //System.out.println(arr[3]);
        //System.out.println(arr[-1]);
    }
}
```

> 课程配图（未随笔记提交）

### 6.2.空指针异常_NullPointerException

```java
1.出现的原因:如果一个引用类型为null,再操作这个引用类型数据,就会出现空指针异常
```

```java
public class Demo07Array {
    public static void main(String[] args) {
        int[] arr = new int[3];
        System.out.println(arr.length);//3
        arr = null;
        System.out.println(arr.length);//空指针异常 NullPointerException
    }
}
```

> 课程配图（未随笔记提交）

> 以上两个问题,不需要练习,只需要知道以上两个问题出现的原因即可
>

## 7.静态初始化和动态初始化区别

```java
1.动态初始化:定义的时候只指定了元素类型以及长度,但是还没有存具体的值(但是有默认值)
           整数默认值 0
           小数默认值 0.0
           字符默认值 '\u0000' (空白字符,转成int值也是0)
           布尔默认值 false
           引用类型默认值 null

           当我们只只知道元素类型以及存储的元素个数,但是不知道后续具体存啥,我们就可以用动态初始化定义数组

2.静态初始化:定义的时候直接存了具体的值,我们可以根据存的数据个数来确定数组长度
           当我们定义的时候知道存啥,就可以使用静态初始化了
```

# 第三章.数组练习

## 1.练习

```java
获取数组最大值
步骤:
  1.定义数组,随意存点数据
  2.定义一个变量max,用于接收两个元素之间的较大值
  3.遍历数组,将每一个元素获取出来
  4.判断,如果max小于遍历出来的元素,证明遍历出来的元素大,就将大的给max
  5.输出max
```

```java
public class Demo01GetMax {
    public static void main(String[] args) {
        //1.定义数组,随意存点数据
        int[] arr = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100};
        //2.定义一个变量max,用于接收两个元素之间的较大值
        int max = arr[0];
        //3.遍历数组,将每一个元素获取出来
        for (int i = 1; i < arr.length; i++) {
        //4.判断,如果max小于遍历出来的元素,证明遍历出来的元素大,就将大的给max
            if (max<arr[i]){
                max = arr[i];
            }
        }
        //5.输出max
        System.out.println(max);
    }
}
```

> 课程配图（未随笔记提交）

## 2.练习

```java
随机产生10个[0,100]之间整数，统计既是3又是5，但不是7的倍数的个数
步骤:
  1.创建长度为10的数组以及Random对象以及统计的count变量
  2.产生10个随机数放到数组中
  3.遍历数组,在遍历的过程中判断,符合条件的count++
  4.输出count
```

```java
public class Demo02Count {
    public static void main(String[] args) {
        //1.创建长度为10的数组以及Random对象以及统计的count变量
        int[] arr = new int[10];
        Random rd = new Random();
        int count = 0;
        //2.产生10个随机数放到数组中
        for (int i = 0; i < arr.length; i++) {
            arr[i] = rd.nextInt(101);
        }
        //3.遍历数组,在遍历的过程中判断,符合条件的count++
        for (int i = 0; i < arr.length; i++) {
            if (arr[i]%3==0 && arr[i]%5==0 && arr[i]%7!=0){
                count++;
            }
        }
        //4.输出count层
        System.out.println(count);
    }
}
```

## 3.练习

```java
用一个数组存储本组学员的姓名，从键盘输入，并遍历显示
```

```java
自己写
```

## 4.练习

```java
需求:
  1.定义一个数组 int[] arr = {1,2,3,4}
  2.遍历数组,输出元素按照[1,2,3,4]
```

```java
public class Demo03Print {
    public static void main(String[] args) {
        int[] arr = {1, 2, 3, 4};
        System.out.print("[");
        for (int i = 0; i < arr.length; i++) {
            if (i == arr.length - 1) {
                System.out.print(arr[i] + "]");
            } else {
                System.out.print(arr[i] + ",");
            }
        }
    }
}
```

> 利用字符串拼接的方式拼成[1,2,3,4]
>
> ```java
> public class Demo03Print {
>     public static void main(String[] args) {
>         int[] arr = {1, 2, 3, 4};
>         /*System.out.print("[");
>         for (int i = 0; i < arr.length; i++) {
>             if (i == arr.length - 1) {
>                 System.out.print(arr[i] + "]");
>             } else {
>                 System.out.print(arr[i] + ",");
>             }
>         }*/
>         //定义一个String
>         String str = "[";
>         for (int i = 0; i < arr.length; i++) {
>             if (i==arr.length-1){
>                 str += arr[i] + "]";
>             }else{
>                 str += arr[i] + ",";
>             }
>         }
>         System.out.println(str);
>     }
> }
>
> ```
>
> > 课程配图（未随笔记提交）

## 5.练习

```java
键盘录入一个整数,找出整数在数组中存储的索引位置
```

```java
public class Demo04Search {
    public static void main(String[] args) {
        int[] arr = {11,22,33,44,55,66};
        Scanner sc = new Scanner(System.in);
        int data = sc.nextInt();
        //遍历数组,用data和每一个遍历出来的元素进行比较
        for (int i = 0; i < arr.length; i++) {
            if (data==arr[i]){
                System.out.println(i);
            }
        }
    }
}

```

```java
问题升级:如果找不到输出-1
```

```java
public class Demo04Search {
    public static void main(String[] args) {
        int[] arr = {11,22,33,44,55,66};
        Scanner sc = new Scanner(System.in);
        int data = sc.nextInt();

        //定义一个标记,表示数组中是否有这个数据
        int flag = 0;

        //遍历数组,用data和每一个遍历出来的元素进行比较
        for (int i = 0; i < arr.length; i++) {
            if (data==arr[i]){
                System.out.println(i);
                flag++;
            }
        }

        /*
           循环之后,如果flag还是0,证明在循环的过程中if语句就没有执行过
           if没有执行过,证明数组中没有我们想要找的元素
         */
        if (flag==0){
            System.out.println(-1);
        }
    }
}
```

# 第四章.内存的说明

```java
1.概述:内存指的是运行内存,在java的世界中,将内存严格划分出了5块
2.分类:
  堆(Heap):保存的是引用类型的数据,而且我们每new一次就都在堆内存中开辟一个空间,堆内存会自动为这个空间分配一个地址值
           保存在堆内存中的数据都是有默认值的
           整数 0
           小数 0.0
           字符 '\u0000'
           布尔 false
           引用 null

  栈(Stack):运行方法,方法的运行都会进栈运行

  方法区(Method Area):所有代码真正运行前的"预备区",保存了类的信息以及类中成员的信息

  本地方法栈(Native Method Stack):运行本地方法的(带native关键字的方法)
                                本地方法是由C语言编写,C语言没有对我们开源,所以我们看不到本地方法的方法体
                                本地方法是对java语言无法实现的功能进行功能上的扩充
  寄存器(PC Register):和CPU有关
```

> 课程配图（未随笔记提交）



## 1.一个数组内存图

> 课程配图（未随笔记提交）

## 2.两个数组内存图

```java
创建两个数组的时候产生了不同的空间,修改一个空间中的数据不会影响另外一个空间的数据
```

> 课程配图（未随笔记提交）

## 3.两个数组指向同一片内存空间

```java
arr2不是重新创建出来的,而是arr直接赋值过去的,那么此时会将arr的地址值给arr2,那么arr和arr2的地址值是一样的,所以arr和arr2指向了同一片空间,操作同一个数组,所以修改arr2的元素会影响到arr这个数组
```

> 课程配图（未随笔记提交）

# 第五章.数组复杂操作_数组扩容

```java
1.定义一个数组,存储1,2,3,将其扩容到长度为5
```

```java
public class Demo04Array {
    public static void main(String[] args) {
        int[] arr1 = {1,2,3};
        int[] arr2 = new int[5];

        //将arr1中的元素放到arr2中
        for (int i = 0; i < arr1.length; i++) {
            arr2[i] = arr1[i];
        }

        //将arr2的地址值给arr1
        arr1 = arr2;

        for (int i = 0; i < arr1.length; i++) {
            System.out.println(arr1[i]);
        }
    }
}
```

> 课程配图（未随笔记提交）
