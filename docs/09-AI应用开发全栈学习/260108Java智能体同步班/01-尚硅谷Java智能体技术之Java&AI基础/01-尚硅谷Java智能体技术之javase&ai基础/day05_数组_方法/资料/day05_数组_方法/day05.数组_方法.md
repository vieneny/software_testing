# day05.数组_方法

```java
课前回顾:
  1.数组的作用:一次存储多个数据
  2.数组的特点:
    a.定长
    b.既可以存储基本类型数据,还可以存储引用类型数据
  3.定义:
    a.动态初始化: 数据类型[] 数组名 = new 数据类型[长度]
    b.静态初始化: 数据类型[] 数组名 = {元素1,元素2...}
  4.获取数组长度: 数组名.length
  5.索引:元素在数组中存储的位置
    特点:
         a.从0开始,最大索引为数组长度-1
         b.唯一
  6.存元素:数组名[索引值] = 值
  7.取元素:数组名[索引值]
  8.遍历数组: 数组名.fori
  9.操作数组容易出现的问题:
    a.数组索引越界异常:ArrayIndexOutOfBoundsException -> 操作的索引超出了数组索引范围
    b.空指针异常:NullPointerException -> 引用类型为null,然后还操作它
今日重点:
  1.会手撕冒泡排序,二分查找
  2.会使用Arrays数组工具类
  3.会操作二维数组:定义,存,取,遍历
  4.方法的使用:
    无参无返回值方法以及调用
    有参无返回值方法以及调用
    无参有返回值方法以及调用
    有参有返回值方法以及调用
```

> 今天如果方法的定义和调用不熟练,那么其他所有的知识点都要给方法让路

# 第一章.数组常见算法

## 1.数组翻转

<img src="image/image-20260114090159722.png" alt="image-20260114090159722" style="zoom:80%;" />

```java
1.概述:数组中对称位置上的元素互换
```

```java
public class Demo01ArrayReverse {
    public static void main(String[] args) {
        int[] arr = {1,2,3,4,5};
        for (int min = 0,max = arr.length - 1; min < max; min++,max--){
            int temp = arr[min];
            arr[min] = arr[max];
            arr[max] = temp;
        }

        for (int i : arr) {
            System.out.print(i+" ");
        }
    }
}

```

## 2.冒泡排序

```java
1.概述:相邻两个元素比较大小,大的往后走,小的往前走->升序
```

<img src="image/image-20260114091930654.png" alt="image-20260114091930654" style="zoom:80%;" />

```java
public class Demo02Bubble {
    public static void main(String[] args) {
        int[] arr = {5,4,3,2,1};
        /*
           越界原因:当i到4的时候,4<arr.length,进循环了
                   进了循环直接判断arr[4]>arr[4+1] -> 此时操作了5索引
                   当前这个数组没有5索引,所以越界
           越界解决方案:i<arr.length-1
         */

        //第一圈 比较了4次
/*        for (int i = 0; i < arr.length-1-0; i++) {
            if (arr[i] > arr[i+1]){
                int temp = arr[i];
                arr[i] = arr[i+1];
                arr[i+1] = temp;
            }
        }*/

        //第二圈 比较了3次
/*        for (int i = 0; i < arr.length-1-1; i++) {
            if (arr[i] > arr[i+1]){
                int temp = arr[i];
                arr[i] = arr[i+1];
                arr[i+1] = temp;
            }
        }*/

        //第三圈 比较了2次
/*        for (int i = 0; i < arr.length-1-2; i++) {
            if (arr[i] > arr[i+1]){
                int temp = arr[i];
                arr[i] = arr[i+1];
                arr[i+1] = temp;
            }
        }*/

        //第四圈 比较了1次
  /*      for (int i = 0; i < arr.length-1-3; i++) {
            if (arr[i] > arr[i+1]){
                int temp = arr[i];
                arr[i] = arr[i+1];
                arr[i+1] = temp;
            }
        }*/

        /*
           外层循环控制圈数
           每层循环控制每圈比较的次数以及如何换位
         */
        for (int i = 0; i < arr.length-1; i++) {
            for (int j = 0; j < arr.length-1-i; j++) {
                if (arr[j] > arr[j+1]){
                    int temp = arr[j];
                    arr[j] = arr[j+1];
                    arr[j+1] = temp;
                }
            }
        }

        for (int i = 0; i < arr.length; i++) {
            System.out.print(arr[i]+" ");
        }
    }
}

```

## 3.二分查找

```java
1.中心思想:每次都计算数组的中间索引,然后和中间索引做==比较-> 说白了每次干掉一半
2.前提:数组元素是有序的 -> 默认是升序
```

<img src="image/image-20260114104553032.png" alt="image-20260114104553032" style="zoom:80%;" />

```java
public class Demo03BinarySearch {
    public static void main(String[] args) {
        int[] arr = {1,2,3,4,5,6,7,8,9,10};
        //定义三个变量,分别代表最小索引,最大索引,以及中间索引
        int min = 0;
        int max = arr.length - 1;
        int mid = 0;
        int key = 10;
        while (min <= max) {
            mid = (min + max) / 2;
            if (key>arr[mid]){
                min = mid + 1;
            }else if (key<arr[mid]){
                max = mid - 1;
            }else{
                System.out.println("找到了,索引是:"+mid);
                break;
            }
        }
    }
}
```

# 第二章.数组工具类

## 1.数组工具类

### 1.1.System类

```java
1.概述:系统相关类
2.方法调用:
  类名直接调方法
```

| 方法                                                         | 说明                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| static void arraycopy(Object src, int srcPos, Object dest, int destPos, int length) | src:源数组,复制哪个数组中的元素<br>srcPos:从源数组的哪个索引开始复制<br>dest:目标数组,将元素复制到哪个数组中去<br>destPos:从目标数组的哪个索引开始粘贴<br>length:复制多少个元素 |

```java
public class Demo04System {
    public static void main(String[] args) {
        int[] arr = {1,2,3,4,5,6,7,8};
        int[] arr2 = new int[10];
        System.arraycopy(arr,0,arr2,0,arr.length);
        for (int element : arr2) {
            System.out.print(element+" ");
        }
    }
}

```

### 1.2.Arrays类

```java
1.概述:数组工具类
2.使用:
  类名直接调用方法
```

| 方法                                | 说明                         |
| ----------------------------------- | ---------------------------- |
| String toString(数组)               | 按照[元素1,元素2...]格式打印 |
| void sort(数组)                     | 数组升序排序                 |
| int binarySearch(数组,要查找的元素) | 二分查找,返回元素对应的索引  |
| int[] copyOf(数组,新数组长度)       | 数组扩容,返回新数组          |

```java
public class Demo05Arrays {
    public static void main(String[] args) {
        int[] arr = {1,2,3,4,5,6,7,8};
        //String toString(数组) 按照[元素1,元素2...]格式打印
        System.out.println(Arrays.toString(arr));

        //void sort(数组)数组升序排序
        int[] arr2 = {5,4,3,2,1};
        Arrays.sort(arr2);
        System.out.println(Arrays.toString(arr2));

        //int binarySearch(数组,要查找的元素)二分查找,返回元素对应的索引
        int index = Arrays.binarySearch(arr, 3);
        System.out.println(index);

        //int[] copyOf(数组,新数组长度)数组扩容,返回新数组
        int[] newArr = Arrays.copyOf(arr2, 10);
        arr2 = newArr;
        System.out.println(Arrays.toString(newArr));
        System.out.println(Arrays.toString(arr2));
    }
}
```

## 2.Hutool工具

```java
1.概述:就是一个纯工具,属于第三方的工具
2.使用:需要导入第三方提供给咱们的jar包
```

官网：https://www.hutool.cn/

<img src="image/image-20251021112459290.png" alt="image-20251021112459290" style="zoom:80%;" />



### 2.1.引入jar

```java
1.概述:jar包其实就一个压缩包,可以解压,里面包含的是第三方提供给咱们的工具类(class文件)
2.怎么手动导jar包:
  a.在模块下右键-> new -> directory -> 取名lib或者libs
  b.将jar包复制到lib包下
  c.对着lib包右键->add as library-> level选项中选择module,此时name选项会变成空的,不要管 -> ok
```

<img src="image/image-20260114115232583.png" alt="image-20260114115232583" style="zoom:80%;" />

### 2.2.ArrayUtil工具类

| 方法                           | 说明                              |
| ------------------------------ | --------------------------------- |
| int max(数组)                  | 返回数组最大值                    |
| int indexOf(数组,要查找的数据) | 顺序查找,指定的数据在数组中的位置 |
| reverse()                      | 数组翻转                          |

```java
public class Demo06Hutool {
    public static void main(String[] args) {
        int[] arr = {1,2,3,4,5,6,7,8};
        //int max(数组)返回数组最大值
        System.out.println(ArrayUtil.max(arr));

        //int indexOf(数组,要查找的数据)顺序查找,指定的数据在数组中的位置
        System.out.println(ArrayUtil.indexOf(arr, 3));

        //reverse()数组翻转
        ArrayUtil.reverse(arr);
        //这个toString不是Arrays中的,而是Hutool工具的ArrayUtil中的
        System.out.println(ArrayUtil.toString(arr));
    }
}
```

# 第三章.二维数组

## 2.1二维数组的定义格式

```java
1.概述:数组中嵌套多个一维数组
2.定义:
  a.动态初始化:
    数据类型[][] 数组名 = new 数据类型[m][n]
    数据类型 数组名[][]  = new 数据类型[m][n]
    数据类型[] 数组名[] = new 数据类型[m][n]

    m:代表的是二维数组长度;n代表的是每一个一维数组长度

  b.静态初始化
    数据类型[][] 数组名 = new 数据类型[][]{{元素1,元素2...},{元素1,元素2...},{元素1,元素2...}...}
    数据类型 数组名[][] = new 数据类型[][]{{元素1,元素2...},{元素1,元素2...},{元素1,元素2...}...}
    数据类型[] 数组名[] = new 数据类型[][]{{元素1,元素2...},{元素1,元素2...},{元素1,元素2...}...}

  c.简化静态初始化:
    数据类型[][] 数组名 = {{元素1,元素2...},{元素1,元素2...},{元素1,元素2...}...}
```

```java
public class Demo01TwoArray {
    public static void main(String[] args) {
        //动态初始化
        int[][] arr1 = new int[3][3];

        //如果没有指定一维数组长度,相当于一维数组没有被创建
        int[][] arr2 = new int[3][];
        //静态初始化
        int[][] arr3 = {{1,2,3},{4,5,6},{7,8,9}};
        String[][] arr4 = {{"唐僧","孙悟空","猪八戒"},{"刘备","关羽"},{"金莲","涛哥"}};
    }
}
```

<img src="image/image-20260114141750990.png" alt="image-20260114141750990" style="zoom:80%;" />

## 2.2获取二维数组长度

```java
1.格式:
  数组名.length
```

```java

public class Demo02TwoArray {
    public static void main(String[] args) {
        //动态初始化
        int[][] arr1 = new int[3][3];
        //获取二维数组长度
        System.out.println(arr1.length);
        System.out.println("================");
        //获取二维数组中每一个一维数组长度
        for (int i = 0; i < arr1.length; i++) {
            System.out.println(arr1[i].length);
        }
    }
}

```

## 2.3获取二维数组中的元素

```java
1.格式:
  数组名[i][j]

  i:代表的是一维数组在二维数组中的索引位置
  j:代表的是元素在一维数组中的索引位置
```

```java
public class Demo03TwoArray {
    public static void main(String[] args) {
        String[][] arr1 = {{"唐僧","孙悟空","猪八戒"},{"刘备","关羽"},{"金莲","涛哥"}};
        System.out.println(arr1[0][0]);
        System.out.println(arr1[1][1]);
        System.out.println(arr1[2][1]);
    }
}
```

<img src="image/image-20260114142540127.png" alt="image-20260114142540127" style="zoom:80%;" />

## 2.4二维数组中存储元素

```java
1.格式:
  数组名[i][j] = 值

  i:代表的是一维数组在二维数组中的索引位置
  j:代表的是元素在一维数组中的索引位置
```

```java
public class Demo04TwoArray {
    public static void main(String[] args) {
        int[][] arr1 = new int[3][3];
        arr1[0][0] = 100;
        arr1[0][1] = 200;
        arr1[0][2] = 300;

        arr1[1][0] = 1000;
        arr1[1][1] = 2000;
        arr1[1][2] = 3000;

        arr1[2][0] = 10000;
        arr1[2][1] = 20000;
        arr1[2][2] = 30000;
        System.out.println(arr1[0][0]);
        System.out.println(arr1[0][1]);
        System.out.println(arr1[0][2]);
        System.out.println(arr1[1][0]);
        System.out.println(arr1[1][1]);
        System.out.println(arr1[1][2]);
        System.out.println(arr1[2][0]);
        System.out.println(arr1[2][1]);
        System.out.println(arr1[2][2]);

    }
}
```

## 2.5.二维数组的遍历

```java
1.嵌套循环:先遍历二维数组,将每一个一维数组获取出来,然后再遍历每一个一维数组
```

```java
public class Demo05TwoArray {
    public static void main(String[] args) {
        int[][] arr1 = new int[3][3];
        arr1[0][0] = 100;
        arr1[0][1] = 200;
        arr1[0][2] = 300;

        arr1[1][0] = 1000;
        arr1[1][1] = 2000;
        arr1[1][2] = 3000;

        arr1[2][0] = 10000;
        arr1[2][1] = 20000;
        arr1[2][2] = 30000;

        //先遍历二维数组,将每一个一维数组获取出来
        for (int i = 0; i < arr1.length; i++) {
            //再遍历每一个一维数组
            for (int j = 0; j < arr1[i].length; j++) {
                System.out.println(arr1[i][j]);
            }
        }
    }
}

```

# 第四章.方法的使用

```java
1.问题描述:我们不能将所有功能的代码都放到一个main方法中,这样不好维护
2.解决:一个功能就应该对应一个方法,将来在网页上或者在程序里面单独点一个按钮,就应该单独执行一个方法

3.方法:拥有功能性代码的代码块 -> 方法就是功能

4.方法的通用定义格式:
  修饰符 返回值类型 方法名(参数){
      方法体
      return 结果
  }

  无参无返回值方法
  有参无返回值方法
  无参有返回值方法
  有参有返回值方法
```

<img src="image/image-20260114144701351.png" alt="image-20260114144701351" style="zoom:80%;" />

## 1.无参无返回值方法定义和调用

```java
1.格式:
  public static void 方法名(){
      方法体
  }

2.注意:
  void 代表的是无返回值,写了[void]就不要写[return 结果]

3.调用:
  在其他方法中直接调用: 方法名()
```

```java
定义一个方法,实现两个整数相加
```

```java
public class Demo01Method {
    public static void main(String[] args) {
        //直接调用
        add();
        //sub();
    }
    public static void add(){
        int a = 10;
        int b = 20;
        int sum = a+b;
        System.out.println(sum);
    }

    public static void sub(){
        int a = 10;
        int b = 20;
        int sub = a-b;
        System.out.println(sub);
    }
}

```

<img src="image/image-20260114152021657.png" alt="image-20260114152021657" style="zoom:80%;" />

> <img src="image/image-20260114152214779.png" alt="image-20260114152214779" style="zoom:80%;" />

> 注意事项:
>
> 1.方法不调用不执行 ->main方法是jvm调用的
>
> 2.方法不能互相嵌套
>
> 3.方法的执行顺序只和调用顺序有关系

## 2.方法定义各部分解释

```java
1.方法的通用定义格式:
  修饰符 返回值类型 方法名(参数){
      方法体
      return 结果
  }

2.各部分解释:
  修饰符:固定public static
  返回值类型:代表的是return 结果中这个"结果"的数据类型
  方法名:小驼峰,见名知意
  参数:进入到方法内部的数据 -> 数据类型 变量名 -> 如果有多个参数:数据类型 变量名,数据类型 变量名...
  方法体:实现此方法(功能)的具体代码
  return 结果:代表的是将结果返回,不要和void共存
```

## 3.有参数无返回值的方法定义和执行流程

```java
1.格式:
  public static void 方法名(参数){
      方法体
  }

2.调用:直接调用
  方法名(具体的值)
```

```java
定义一个方法,实现两个整数相加
```

```java
public class Demo02Method {
    public static void main(String[] args) {
        //调用
        add(10,20);
    }
    public static void add(int a,int b){
        int sum = a+b;
        System.out.println(sum);
    }
}
```

<img src="image/image-20260114154025178.png" alt="image-20260114154025178" style="zoom:80%;" />

## 4.无参数有返回值定义以及执行流程

```java
1.格式:
  public static 返回值类型 方法名(){
      方法体
      return 结果
  }

2.调用:  哪里调用方法,该方法的返回值就返回给哪里
  a.打印调用:sout(方法名())
  b.赋值调用:数据类型 变量名 = 方法名()
```

```java
定义一个方法,实现两个整数相加,将结果返回
```

```java
public class Demo03Method {
    public static void main(String[] args) {
        //打印调用
        //System.out.println(add());
        //赋值调用
        int result = add();
        System.out.println(result);
    }
    public static int add(){
        int a = 10;
        int b = 20;
        int sum = a+b;
        return sum;
    }
}
```

<img src="image/image-20260114155527184.png" alt="image-20260114155527184" style="zoom:80%;" />

## 5.有参数有返回值定义以及执行流程

```java
1.格式:
  public static 返回值类型 方法名(参数){
      方法体
      return 结果
  }

2.调用:
  打印调用:sout(方法名(具体的值))
  赋值调用:数据类型 变量名 = 方法名(具体的值)
```

```java
定义一个方法,实现两个整数相加,将结果返回
```

```java
public class Demo04Method {
    public static void main(String[] args) {
        //赋值调用
        int result = add(10,20);
        System.out.println(result);
    }
    public static int add(int a,int b){
        int sum = a+b;
        return sum;
    }
}
```

<img src="image/image-20260114161927792.png" alt="image-20260114161927792" style="zoom:80%;" />

## 6.形参和实参的区别

```java
1.形式参数(形参):[在定义方法的时候],形式上定义了1个或者多个参数,此时还没有具体的值
2.实际参数(实参):[在调用方法的时候],给形参传递的具体的值
```

> 作为初学者:
>
> 1.先定义,再调用
>
> 2.没有返回值的-> 直接调用
>
> 3.有返回值的 -> 赋值调用

## 7.参数和返回值的使用时机

```java
将来开发方法一般都是带参带返回值的
====================================
1.参数的使用时机:当想将方法A中的数据传递到方法B中做操作,方法B在定义的时候就需要带参数,等着接收方法A中的数据
2.返回值的使用时机:方法A调用方法B之后,需要方法B的结果,然后拿到方法B的结果在A中做其他操作,此时方法B就需要将自己的结果返回出去
```

```java
public class Demo05Method {
    public static void main(String[] args) {
        int a = 10;
        int b = 20;
        //method(a,b);//相当于将a代表的10以及b代表的20传给了method方法
        int result = method(a,b);
        if (result > 10){
            System.out.println("结果大于10");
        }else{
            System.out.println("结果不大于10");
        }
    }
/*    public static void method(int a,int b){
        int sum = a+b;
        System.out.println(sum);
    }*/

    public static int method(int a,int b){
        int sum = a+b;
        return sum;
    }
}
```

> <img src="image/image-20260114165407906.png" alt="image-20260114165407906" style="zoom:80%;" />
