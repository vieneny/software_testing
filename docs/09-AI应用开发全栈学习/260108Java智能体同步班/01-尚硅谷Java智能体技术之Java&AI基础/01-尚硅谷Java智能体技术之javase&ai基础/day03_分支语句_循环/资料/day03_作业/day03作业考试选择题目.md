```
1.下列语句序列执行后，x 的值是()
int a=3, b=4, x=5;
if(a<b){
     x=x+1;
}
```



|      | `A: 5 ` |
| ---- | ------- |
|      | `B: 3`  |
|      | `C: 4`  |
|      | `D: 6`  |



```
2.下列语句序列执行后，ch的值是( )。
int a = 10;
int b = 20;
char ch = 'A';
if(a < b) {
    ch='C';
}
```



|      | `A: ‘A’` |
| ---- | -------- |
|      | `B: ‘B’` |
|      | `C: ‘C’` |
|      | `D: 'D'` |



```
3.下列语句序列执行后，b 的值是()。
int a=2, b=4;
if( a < b){
     a *= 2;
}
```



|      | `A: 5 ` |
| ---- | ------- |
|      | `B: 4`  |
|      | `C: 8`  |
|      | `D: 10` |





```
4.以下一段代码执行完毕后y的值是（）。 
int x = 11; 
int y = 0; 
if(x>5){
    y = x + 5; 
} else {
    y = x – 5; 
}  
```



|      | `A: 16` |
| ---- | ------- |
|      | `B: 6`  |
|      | `C: 11` |
|      | `D: 0`  |



```
5.下列语句序列执行后，m 的值是()。
int a=10, b=3, m=5;
if( a==b ) {
    m+=a;
}else{
    m*=a;
}
```



|      | `A: 15 ` |
| ---- | -------- |
|      | `B: 50`  |
|      | `C: 55 ` |
|      | `D: 5`   |



6.下列语句序列执行后，i 的值是(  ) 

```java
int i=8, j=16;   
if( i > j ){
    i--; 
} else{
  	j--; 
}  
```



|      | `A: 15` |
| ---- | ------- |
|      | `B: 16` |
|      | `C: 7`  |
|      | `D: 8`  |



7.考虑下列嵌套的if语句，说法正确的是( )

```java
if(条件1){
    if(条件2){    
        语句体1; 
    } else {
        语句体2; 
    } 
} 
```



|      | `A: 只有当条件1为false及条件2为false时语句体2才能执行` |
| ---- | ------------------------------------------------------ |
|      | `B: 无论条件2是什么，只要条件1=false,语句体2就能执行`  |
|      | `C: 语句体2无论在什么情况下，都不能执行`               |
|      | `D: 只有当条件1为true及条件2为false时语句体2才能执行`  |



8.下面的代码执行完后 x 的值是（ ）

```java
public static void main(String[] args) {
    int i = 10,j = 25,x = 30;
    switch(j-i) {
        case 15:
            x++;
        case 16:
            x+=2;
        case 17:
            x+=3;
        default:
            --x;
    }
}
```



|      | `A: 35` |
| ---- | ------- |
|      | `B: 36` |
|      | `C: 34` |
|      | `D: 16` |



9.【多选题】下列程序段的输出结果是（  ）

```java
public class test {
     public static void main(String[] args) {
        int x = 1, a = 0, b = 0;
        switch (x) {
            case 0:
                b++;
            case 1:
                a++;
            case 2:
                a++;
                b++;
        }
         System.out.println("a=" + a);
         System.out.println("b=" + b);
     }
}
```



|      | `A: a=2` |
| ---- | -------- |
|      | `B: b=1` |
|      | `C: a=1` |
|      | `D: b=2` |



10.分析下面代码，说法正确的有（  ）

```java
int x = 2;
switch(x){
    case 1:
         System.out.println(1);
     case 2:
    case 3:
         System.out.println(3);
     case 4:
         System.out.println(4);
 }
```



|      | `A: 没有输出任何结果`                                       |
| ---- | ----------------------------------------------------------- |
|      | `B: 输出结果为 3 和 4`                                      |
|      | `C: 输出结果为 1、3 和 4`                                   |
|      | `D: 如果在”case 3：“输出语句后加上 break，程序输出结果为 3` |

11.下列程序的运行结果是 ？

```java
public static void main(String [] args){
    int i = 1;
    while(i <= 10){
        i++;
        System.out.println("HelloWorld");
    }
}
```



|      | `A: 输出1次HelloWorld`  |
| ---- | ----------------------- |
|      | `B: 输出2次HelloWorld`  |
|      | `C: 输出9次HelloWorld`  |
|      | `D: 输出10次HelloWorld` |



12.下列程序的运行结果是 ？

```java
public static void main(String [] args){
    int i = 1;
    while(i <= 10){
        i++;
        if(i % 2 == 0) {
           System.out.println("HelloWorld");
        }
    }
}
```



|      | `A: 输出1次HelloWorld` |
| ---- | ---------------------- |
|      | `B: 输出2次HelloWorld` |
|      | `C: 输出4次HelloWorld` |
|      | `D: 输出5次HelloWorld` |



13.下列程序的运行结果是 ？

```java
public static void main(String [] args){
    int sum = 0;
    int i = 1;
    while(i <= 5){
        sum += i;
        i++;
    }
    System.out.println(sum);
}
```



|      | `A: 1`  |
| ---- | ------- |
|      | `B: 5`  |
|      | `C: 10` |
|      | `D: 15` |



14.下列程序的运行结果是 ？

```java
public static void main(String [] args){
    int sum = 0;
    int i = 1;
    while(i <= 5){
        if(i % 2 == 1) {
            sum += i;
        }
        i++;
    }
    System.out.println(sum);
}
```



|      | `A: 1` |
| ---- | ------ |
|      | `B: 3` |
|      | `C: 6` |
|      | `D: 9` |



15.下列程序运行结果是 ？

```java
public static void main(String[] args) {
    int i = 1;
    do {
        System.out.println("HelloWorld");
        i++;
    } while(i < 0);
}
```



|      | `A: 没有任何输出`       |
| ---- | ----------------------- |
|      | `B: 输出1次HelloWorld`  |
|      | `C: 输出5次HelloWorld`  |
|      | `D: 输出10次HelloWorld` |



16.下列程序会输出几次HelloWorld

```java
public static void main(String[] args) {
    for(int i = 1; i <= 10; i++) {
        System.out.println("HelloWorld");
    }
}
```



|      | `A: 1`  |
| ---- | ------- |
|      | `B: 2`  |
|      | `C: 10` |
|      | `D: 11` |



17.下列程序的输出结果是

```java
public static void main(String[] args) {
    int sum = 0;
    for (int i = 1; i <= 5; i++) {
        sum += i;
    }
    System.out.println(sum);
}
```



|      | `A: 1`  |
| ---- | ------- |
|      | `B: 5`  |
|      | `C: 10` |
|      | `D: 15` |



18.下列程序的运行的结果是

```java
public static void main(String[] args) {
    int num = 10;
    for (int i = 0; i < 3; i++) {
        num--;
    }
    System.out.print(num);
}
```



|      | `A: 1`  |
| ---- | ------- |
|      | `B: 3`  |
|      | `C: 7`  |
|      | `D: 10` |



19.下面程序的运行结果是

```java
public static void main(String[] args) {
    int sum = 0;
    for(int i = 1;i <= 5;i++) {
        if (i % 2 == 0) {
            sum += i;
        }
    }
    System.out.println(sum);
}
```



|      | `A: 0`  |
| ---- | ------- |
|      | `B: 2`  |
|      | `C: 6`  |
|      | `D: 15` |



20.下面程序的运行结果是

```java
public static void main(String[] args) {
    int count = 0;
    for (int i = 1; i <= 10; i++) {
        if(i % 3 == 0) {
            count++;
        }
    }
    System.out.println(count);
}
```



|      | `A: 1`  |
| ---- | ------- |
|      | `B: 3`  |
|      | `C: 6`  |
|      | `D: 10` |