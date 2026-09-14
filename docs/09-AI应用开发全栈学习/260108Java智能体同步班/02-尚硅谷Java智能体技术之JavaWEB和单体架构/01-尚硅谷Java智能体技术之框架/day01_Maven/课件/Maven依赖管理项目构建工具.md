# Maven 依赖管理 & 项目构建工具（Maven）

[TOC]

## 1、Maven 简介

### 1.1 Maven 介绍

> [Maven 官方文档](https://maven.apache.org/what-is-maven.html)
>
> version: 3.9.11
> release date: 2025-07-12
> required java version: Java 8

`Maven` 是一款为 Java 项目提供「构建」与「依赖管理」的工具（软件）。使用 Maven 可以自动化完成编译、测试、打包、发布等流程，从而提升开发效率与交付质量。

总结：Maven 就是一个软件。掌握 Maven 的安装、配置与两大核心能力（项目构建、依赖管理）就是本课程的主要目标。

**场景 1：依赖管理**
项目需要第三方库（依赖），如 Druid 连接池、MySQL 数据库驱动、Jackson 等。只要把依赖坐标写进 Maven 工程的配置文件，Maven 就会自动下载并引入依赖；同时也会自动下载「依赖所依赖的依赖」，确保依赖链完整、版本可控、冲突更少。

**场景 2：项目构建**
项目开发完成后，需要打包成 `.war` 并部署到服务器运行。使用 Maven 只需一条构建命令（如 `mvn package`）即可完成构建与打包，节省大量时间。

### 1.2 Maven 主要作用理解

1. **依赖管理**
   Maven 可以管理项目依赖（jar），包括自动下载所需依赖库、自动下载传递依赖、依赖版本管理等。开发者只需要在 `pom.xml` 中写配置（XML）即可维护项目依赖。
2. **构建管理**
   项目构建是指将源代码、配置文件、资源文件等转化为可运行或可部署的应用程序/库的过程。Maven 通过标准化的构建生命周期，统一管理编译、测试、打包、部署等流程；同时依靠插件机制支持扩展与定制。触发构建通常只需要简单的命令操作。

> 课程配图（未随笔记提交）

### 1.3 Maven 软件工作原理模型图

> 课程配图（未随笔记提交）：课堂配图

## 2、Maven 项目定位属性和结构强化

### 2.1 梳理 Maven 工程 GAVP 属性

GAVP 是 Maven 给项目的「唯一身份标识」（类似人的“姓 + 名”），核心目的是：**让项目在 Maven 仓库中可被精准找到，方便后期项目间相互引用依赖。**

> 课程配图（未随笔记提交）

其中 GroupId、ArtifactId、Version（GAV）是必填项，Packaging（P）是可选项且有默认值。

| 属性       | 核心作用                      | 是否必填       |
| ---------- | ----------------------------- | -------------- |
| GroupId    | 标识“归属”（公司 / 业务）     | 是             |
| ArtifactId | 标识“具体项目 / 模块”         | 是             |
| Version    | 标识“迭代版本”                | 是             |
| Packaging  | 标识“打包类型”【pom,jar,war】 | 否（默认 jar） |

记住：GAV 组合起来是项目的唯一标识，P 决定项目类型与打包结果。

**GAV 规则明细：**

1. GroupId
   作用：标识项目的归属（公司 / 团队 + 业务线）
   格式：`com.公司/BU.业务线.[子业务线]`（最多 4 级，子业务线可选）
   例子：`com.alibaba.sourcing`（阿里 + 采购业务）、`com.taobao.tddl`（淘宝 + 分库分表业务）
2. ArtifactId
   作用：标识同一“公司”下的具体项目/模块
   格式：`产品线名-模块名`（语义唯一，建议先查仓库避免重复）
   例子：`tc-client`（tc 产品线 - 客户端模块）、`bookstore-api`（书店产品线 - 接口模块）
3. Version（项目“版本号”）
   作用：区分项目的不同迭代版本
   格式：`主版本号.次版本号.修订号`（三段式）
   核心规则：
   - 主版本号：不兼容的 API 修改（比如 1.0.0 → 2.0.0）
   - 次版本号：兼容的功能新增（比如 1.0.0 → 1.1.0）
   - 修订号：仅修复 bug / 优化（不改 API，比如 1.0.0 → 1.0.1）
4. Packaging（项目“打包类型”）
   作用：指定项目打包后的文件格式，IDEA 会据此识别项目类型
   可选值（常用）：
   - `jar`：默认值，普通 Java 工程 → 打包为 `.jar` 文件
   - `war`：Java Web 工程 → 打包为 `.war` 文件（部署到 Tomcat 等服务器）
   - `pom`：父工程（用于继承）→ 不生成打包文件

### 2.2 Maven 工程项目结构说明

Maven 提供标准化的项目结构，便于管理依赖、构建、测试、发布等任务。以下是 Maven jar 程序的文件结构示例与说明：

```xml
|-- pom.xml                               # Maven 项目管理文件
|-- src
    |-- main                              # 项目主要代码
    |   |-- java                          # Java 源代码目录
    |   |   `-- com/example/myapp         # 开发者代码主目录
    |   |       |-- controller            # 存放 Controller 层代码的目录 【控制层】
    |   |       |-- service               # 存放 Service 层代码的目录    【业务层】
    |   |       |-- dao                   # 存放 DAO 层代码的目录        【持久层】
    |   |       `-- model                 # 存放数据模型的目录
    |   |-- resources                     # 资源目录：配置文件、静态资源等
    |   |   |-- log4j.properties          # 日志配置文件
    |   |   |-- spring-mybatis.xml        # Spring MyBatis 配置文件
    `-- test                              # 项目测试代码
        |-- java                          # 单元测试目录
        `-- resources                     # 测试资源目录
```

- `pom.xml`：Maven 项目管理文件，用于描述项目依赖与构建配置等信息
- `src/main/java`：项目 Java 源代码（标准 MVC 架构代码）
- `src/main/resources`：资源目录（配置文件、静态资源等）
- `src/test/java`：测试代码目录
- `src/test/resources`：测试资源目录（测试配置等）

## 3、Maven 依赖管理

### 3.1 依赖管理概念

Maven 依赖管理是 Maven 最重要的功能之一。它能够帮助开发人员自动解决软件包依赖问题，使得开发人员能轻松将其他模块或第三方框架集成到自己的项目中，避免版本冲突与依赖缺失。

通过定义 POM 文件，Maven 能自动解析项目的依赖关系，并通过 Maven **仓库自动**下载与管理依赖，从而避免手动下载、手动拷贝、版本难控等问题。

> 课程配图（未随笔记提交）：依赖管理

Maven 的依赖管理能力使得依赖使用更加智能和方便，简化开发过程，并提升软件质量与可维护性。

### 3.2 依赖管理进阶

#### 3.2.1 依赖管理作用域说明

```xml
<!--
   通过编写依赖 jar 包的 GAV 必要属性，引入第三方依赖
   scope 属性是可选的，用于指定依赖生效范围
   依赖信息查询方式：
      1. Maven 仓库信息官网：https://mvnrepository.com/
      2. MavenSearch 插件搜索
-->
<dependencies>
    <dependency>
        <groupId>log4j</groupId>
        <artifactId>log4j</artifactId>
        <version>1.2.17</version>
        <!--
            生效范围：
            - compile ：main 目录、test 目录、运行、打包 [默认]
            - provided：main 目录、test 目录            Servlet
            - runtime ：运行、打包                      MySQL驱动
            - test    ：test 目录                      JUnit
        -->
        <scope>runtime</scope>
    </dependency>
</dependencies>
```

#### 3.2.2 依赖版本统一提取和维护

```xml
<!-- 统一管理版本号、编码、JDK 等参数 -->
<properties>
    <!-- 1. 自定义变量：管理第三方依赖版本（命名自定义，方便统一修改） -->
    <junit.version>4.11</junit.version>

    <!-- 2. Maven 固定参数：配置编码格式（避免中文乱码） -->
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>

    <!-- 3. 自定义变量：指定 JDK 版本（常用 1.8，可按需调整） -->
    <maven.compiler.source>1.8</maven.compiler.source>
    <maven.compiler.target>1.8</maven.compiler.target>
</properties>

<dependencies>
    <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <!-- 引用 properties 声明版本 -->
        <version>${junit.version}</version>
    </dependency>
</dependencies>
```

### 3.3 依赖下载失败错误解决流程

使用 Maven 构建项目时可能出现依赖下载错误，常见原因如下：

1. **网络故障 / 仓库服务器异常**：无法连接 Maven 仓库导致下载失败

   ```
   org.projectlombok:lombok-utils:pom:1.18.11 failed to transfer from https://repo.maven.apache.org/maven2 during a previous attempt. This failure was cached in the local repository and resolution is not reattempted until the update interval of central has elapsed or updates are forced. Original error: Could not transfer artifact org.projectlombok:lombok-utils:pom:1.18.11 from/to central (https://repo.maven.apache.org/maven2):【 Remote host terminated the handshake】
   ```
   标注部分意思：**远程服务器没建立好连接就断开了**

2. **依赖版本号 / 配置错误**：依赖坐标不正确或版本不存在

   ```
   Could [ not find ] artifact org.projectlombok:lombok-utils:pom:1.18.19 in central (https://repo.maven.apache.org/maven2)
   ```

3. **本地仓库缓存损坏 / 占位文件未清理**：下载中断导致 `.lastUpdated` 等缓存影响刷新

> 课程配图（未随笔记提交）

​	解决方案：

1. 检查网络连接与 Maven 仓库服务器状态
2. 确认依赖版本与 `pom.xml` 配置正确
3. 清除本地 Maven 仓库缓存（`lastUpdated` 文件）：只要存在该缓存文件，即使刷新也不会重新下载。根据依赖的 GAV 逐级定位到对应目录，删除其中相关文件后再刷新即可

> 课程配图（未随笔记提交）

### 3.4 Maven 依赖传递特性

假如有 Maven 项目 A，项目 A 依赖 B，项目 B 依赖 C。那么我们可以说 **A 依赖 C**。也就是说，依赖关系为：A → B → C。执行项目 A 时，会自动把 B、C 都下载并引入到 A 项目中，这就是依赖的传递性。

**传递原则**
在 A 依赖 B、B 依赖 C 的前提下，C 是否能传递到 A，取决于 B 依赖 C 时使用的依赖范围（scope）：

- B 依赖 C 使用 `compile`：可以传递
- B 依赖 C 使用 `test` 或 `provided`：不能传递

**作用**

- 简化依赖导入过程
- 确保依赖链路完整、版本更可控

**依赖传递终止**

- 非 `compile` 范围依赖不参与传递
- 依赖冲突（传递的依赖已经存在）会导致传递终止

**案例 1：导入 Jackson 依赖**

分析：Jackson 需要三个依赖。

> 课程配图（未随笔记提交）

依赖传递关系：`jackson-databind` 会依赖另外两个依赖。

> 课程配图（未随笔记提交）：课堂配图

最佳导入方式：直接导入 `jackson-databind`，依赖会自动传递。

```xml
<!-- https://mvnrepository.com/artifact/com.fasterxml.jackson.core/jackson-databind -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.15.0</version>
</dependency>
```

### 3.5 Maven 依赖冲突特性

当直接引用或者间接引用出现了相同的 jar 包时，一个项目会出现重复 jar 包，这就算作冲突。依赖冲突会带来重复依赖，并且会终止依赖传递。

> 课程配图（未随笔记提交）

Maven 具备自动解决依赖冲突的能力，会按规则选择其中一个版本，同时也提供了手动方式（一般不推荐频繁使用）。

**解决依赖冲突（如何选择重复依赖）方式：**

1. 自动选择原则
   - 最短路径优先原则（第一原则）
     ```
     A → B → C → X(version 0.0.1)
     A → F → X(version 0.0.2)
     ```
     则 A 最终依赖于 `X(version 0.0.2)`。
   - 依赖路径长度相同时，“先声明优先”（第二原则）
     ```
     A → B → X(version 0.0.1)
     A → F → X(version 0.0.2)
     ```
     则 A 最终依赖于 `X(version 0.0.1)`。

2. 手动排除

   ```xml
   <dependency>
     <groupId>com.atguigu.maven</groupId>
     <artifactId>pro01-maven-java</artifactId>
     <version>1.0-SNAPSHOT</version>
     <scope>compile</scope>
     <exclusions>
       <exclusion>
         <groupId>commons-logging</groupId>
         <artifactId>commons-logging</artifactId>
       </exclusion>
     </exclusions>
   </dependency>
   ```

## 4、进行 Maven 工程构建

### 4.1 构建概念和构建过程

项目构建是指将源代码、依赖库和资源文件等转换成可执行或可部署应用程序的过程。通常包含编译源代码、链接依赖库、打包与部署等步骤。

项目构建是软件开发过程中至关重要的一部分，它能提升开发效率，使开发人员更专注于业务开发与维护，而不必关注构建细节。

同时，项目构建还能将多位开发人员的代码汇合到一起，并支持自动化构建与部署，降低出错风险。

常见构建工具包括 `Maven`、`Gradle`、`Ant` 等。

> 课程配图（未随笔记提交）：课堂配图

### 4.2 命令方式项目构建

| 命令        | 描述                                         |
| ----------- | -------------------------------------------- |
| mvn compile | 编译项目，生成 `target` 文件                 |
| mvn package | 项目打包，在 `target` 中生成 `war/jar` 文件  |
| mvn clean   | 清理编译或打包后的项目文件，删除 `target`    |
| mvn install | 打包后上传到 Maven 本地仓库（本地部署）      |
| mvn deploy  | 打包后上传到 Maven 私服仓库（私服部署）      |
| mvn site    | 生成站点（报告）                             |
| mvn test    | 执行测试源码（测试）                         |

命令触发练习：需在pom.xml所在目录执行命令

```bash
# 清理
mvn clean

# 清理，并重新打包
mvn clean package

# 执行测试代码
mvn test
```

### 4.3 可视化方式项目构建

> 课程配图（未随笔记提交）

### 4.4 构建插件、命令、生命周期命令之间关系

- **构建生命周期**
  会出现这样的现象：执行 `package` 命令时，也会自动执行 `compile`。

  ```xml
  [INFO] --------------------------------[ jar ]---------------------------------
  [INFO]
  [INFO] --- maven-resources-plugin:2.6:resources (default-resources) @ mybatis-base-curd ---
  [INFO] --- maven-compiler-plugin:3.1:compile (default-compile) @ mybatis-base-curd ---
  [INFO] --- maven-resources-plugin:2.6:testResources (default-testResources) @ mybatis-base-curd ---
  [INFO] --- maven-compiler-plugin:3.1:testCompile (default-testCompile) @ mybatis-base-curd ---
  [INFO] --- maven-surefire-plugin:2.12.4:test (default-test) @ mybatis-base-curd ---
  [INFO] --- maven-jar-plugin:2.4:jar (default-jar) @ mybatis-base-curd ---
  [INFO] Building jar: D:\javaprojects\backend-engineering\part03-mybatis\mybatis-base-curd\target\mybatis-base-curd-1.0-SNAPSHOT.jar
  [INFO] ------------------------------------------------------------------------
  [INFO] BUILD SUCCESS
  [INFO] ------------------------------------------------------------------------
  [INFO] Total time:  5.013 s
  [INFO] Finished at: 2025-06-05T10:03:47+08:00
  [INFO] ------------------------------------------------------------------------
  ```

  这种行为就是因为构建生命周期产生的。构建生命周期可以理解成是一组固定构建命令的有序集合：触发后面的命令，会自动触发前面的命令。

  **构建周期作用：简化构建过程**

  例如：项目打包只需要执行 `mvn clean package` 即可。

  主要三个构建生命周期：
  - **清理周期**：对项目编译生成文件进行清理，删除target

    包含命令：`clean`

  - **默认周期**：定义了真正构建时所需执行的所有步骤，是最核心的周期

    包含命令：`compile` - `test` - `package` - `install` / `deploy`

  - **报告周期**

  - 包含命令：`site`

  打包：`mvn clean package`

  本地仓库：`mvn clean install`

- **插件、命令、周期三者关系（了解）**

  周期 → 包含若干命令 → 对应若干插件

  使用周期命令构建，可以简化构建过程；最终真正执行构建，干活的是插件。

### 4.5 构建相关的pom配置说明

在 Maven 中，默认情况下 无需额外配置 即可完成基本构建流程（Maven 自带缺省配置）。当然，我们也可以在 pom.xml 中通过 `<build>` 标签进行定制，来修改默认的构建行为与产物，例如：

- 指定构建产物（war/jar）的文件名（不使用默认命名）
- 控制打包时包含/排除的文件类型或路径
- 插件版本过低时，升级到更高版本的构建插件
#### 4.5.1 指定打包命名

默认打包名称通常为： artifactId-version.打包方式 。 如果要自定义最终产物名称，可以配置 finalName ：

```
<!-- 自定义打包名称 -->
<build>
  <finalName>定义打包名称</finalName>
</build>
```
#### 4.5.2 指定需要打包的资源文件（resources）

默认情况下，符合 Maven 标准工程结构的资源文件会被编译/打包到 classes 目录下。需要注意的是：

- 在 src/main/java 下添加的 .java 会被编译并输出到 classes
- 但在 src/main/java 下添加的 .xml 等文件， 默认不会被打包
如果希望额外把某些静态资源打包进 classes 根目录，可以通过 <resources> 指定需要打包的目录，并使用 <includes> / <excludes> 控制包含与排除规则：

```xml
<!-- 打包指定静态资源 -->
<build>
  <resources>
    <resource>
      <!-- 指定要打包资源的文件夹，并配置包含规则
      -->
      <directory>src/main/resources</directory>
      <includes>
        <include>**/*.xml</include>
        <include>**/*.properties</include>
      </includes>
    </resource>

    <resource>
      <directory>src/main/resources</directory>
      <excludes>
        <exclude>spring/*</exclude>
      </excludes>
      <includes>
        <include>*.xml</include>
        <!--<include>*/*.properties</include>-->
      </includes>
    </resource>
  </resources>
</build>
```
#### 4.5.3 配置构建插件（plugins）

在 Maven 中，“依赖”和“插件”是两个不同的概念：

- 依赖（dependency） ：项目运行或编译所需要的第三方库/模块，Maven 通过依赖机制自动管理依赖关系 通常写在 `<dependencies>` 中
- 插件（plugin） ：用于扩展 Maven 构建过程的工具，例如编译、测试、打包、发布等 通常写在` <build><plugins> `中
常见插件用途包括：调整构建插件版本、配置 JDK 编译版本、使用 Tomcat 插件、MyBatis 逆向工程插件等。

例如，遇到 “JDK 17 与低版本 war 插件不兼容” 时，可以在 build/plugins 中提升插件版本：

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-war-plugin</artifactId>
      <version>3.2.2</version>
    </plugin>
  </plugins>
</build>
```

## 5、Maven 工程继承和聚合关系

### 5.1 Maven 工程继承关系

1. **继承概念**

   Maven 继承是指在 Maven 项目中，让一个项目从另一个项目中继承配置信息的机制。继承可以让多个项目共享同一份**配置信息**，简化管理与维护工作。

   > 课程配图（未随笔记提交）

2. **继承作用**
   - 统一版本：大型项目拆多个模块后，父工程集中管理依赖版本，所有子模块直接复用，避免各模块版本不一致导致冲突
   - 复用经验：把调试好的依赖组合声明在父工程，子模块直接继承，避免重复声明

   简单说：父工程当“依赖管家”，子模块省心又规范。

3. **继承语法**
   - 父工程
     ```xml
     <groupId>com.atguigu.maven</groupId>
     <artifactId>pro03-maven-parent</artifactId>
     <version>1.0-SNAPSHOT</version>
     <!-- 当前工程作为父工程，它要去管理子工程，所以打包方式必须是 pom -->
     <packaging>pom</packaging>
     ```
   - 子工程
     ```xml
     <!-- 使用 parent 标签指定当前工程的父工程 -->
     <parent>
       <!-- 父工程的坐标 -->
       <groupId>com.atguigu.maven</groupId>
       <artifactId>pro03-maven-parent</artifactId>
       <version>1.0-SNAPSHOT</version>
     </parent>

     <!-- 子工程的坐标 -->
     <!-- 如果子工程坐标中的 groupId 和 version 与父工程一致，那么可以省略 -->
     <!-- <groupId>com.atguigu.maven</groupId> -->
     <artifactId>pro04-maven-module</artifactId>
     <!-- <version>1.0-SNAPSHOT</version> -->
     ```

4. **父工程依赖统一管理**
   - 父工程声明版本
     ```xml
     <!-- 使用 dependencyManagement 标签配置对依赖的管理 -->
     <!-- 被管理的依赖并没有真正被引入到工程 -->
     <dependencyManagement>
       <dependencies>
         <dependency>
           <groupId>org.springframework</groupId>
           <artifactId>spring-core</artifactId>
           <version>6.0.6</version>
         </dependency>
         <dependency>
           <groupId>org.springframework</groupId>
           <artifactId>spring-beans</artifactId>
           <version>6.0.6</version>
         </dependency>
         <dependency>
           <groupId>org.springframework</groupId>
           <artifactId>spring-context</artifactId>
           <version>6.0.6</version>
         </dependency>
         <dependency>
           <groupId>org.springframework</groupId>
           <artifactId>spring-expression</artifactId>
           <version>6.0.6</version>
         </dependency>
         <dependency>
           <groupId>org.springframework</groupId>
           <artifactId>spring-aop</artifactId>
           <version>6.0.6</version>
         </dependency>
       </dependencies>
     </dependencyManagement>
     ```
   - 子工程引用版本
     ```xml
     <!-- 子工程引用父工程中的依赖信息时，可以把版本号去掉 -->
     <!-- 去掉版本号表示子工程依赖版本由父工程决定 -->
     <!-- 具体来说由父工程的 dependencyManagement 决定 -->
     <dependencies>
       <dependency>
         <groupId>org.springframework</groupId>
         <artifactId>spring-core</artifactId>
       </dependency>
       <dependency>
         <groupId>org.springframework</groupId>
         <artifactId>spring-beans</artifactId>
       </dependency>
       <dependency>
         <groupId>org.springframework</groupId>
         <artifactId>spring-context</artifactId>
       </dependency>
       <dependency>
         <groupId>org.springframework</groupId>
         <artifactId>spring-expression</artifactId>
       </dependency>
       <dependency>
         <groupId>org.springframework</groupId>
         <artifactId>spring-aop</artifactId>
       </dependency>
     </dependencies>
     ```

### 5.2 Maven 工程聚合关系

1. **聚合概念**

   Maven 聚合是指将多个项目组织到一个父级项目中，以便一起构建和管理的机制。聚合可以帮助我们更好地管理一组相关的子项目，同时简化它们的构建与部署过程。

2. **聚合作用**

   1. 管理多个子项目：通过聚合将多个子项目组织在一起，方便管理与维护
   2. 构建和发布一组相关项目：一个命令构建和发布多个相关项目，简化部署与维护
   3. 优化构建**顺序**：对多个项目进行顺序控制，避免依赖混乱导致构建失败
4. 统一管理依赖项：父项目统一管理公共依赖与插件，避免重复定义

3. **聚合语法**

   父项目中包含的子项目列表：

   ```xml
   <project>

     <groupId>com.example</groupId>
     <artifactId>parent-project</artifactId>
     <version>1.0.0</version>

     <packaging>pom</packaging>

     <modules>
       <module>child-project1</module>
       <module>child-project2</module>
     </modules>

   </project>
   ```

4. **聚合演示**
   通过触发父工程构建命令，引发所有子模块构建（产生反应堆）：

   > 课程配图（未随笔记提交）

## 6、Maven 仓库之间的关系和优先级

### 6.1 仓库类型介绍

Maven 仓库主要分为三类：本地仓库（Local Repository）、中央仓库（Central Repository）、远程仓库（Remote Repository）。

1. **本地仓库**

   Maven 在本地系统上创建的目录，用于存储构建所需的依赖与插件。每个用户都有一个本地仓库，位于用户主目录下的 `.m2` 文件夹。当 Maven 需要某个依赖时，会先查本地仓库：若存在则直接使用，否则向远程仓库请求下载。

2. **中央仓库**

   Maven 官方维护的仓库，包含大量开源构件，是默认访问的仓库。当本地仓库不存在所需依赖时，Maven 会从中央仓库下载并缓存到本地。也可以配置使用其他公共或私有的中央仓库。

3. **远程仓库**

   通常由管理员或团队维护，用于共享内部构件或作为第三方依赖的备选源。Maven 会检查远程仓库中是否存在所需依赖：存在则下载并缓存到本地。远程仓库可以是私有的或公共的，也可能作为镜像仓库使用。

仓库优先级：**本地仓库 > 远程仓库 > 中央仓库**。也就是说，只要本地仓库中已存在所需依赖，Maven 会直接使用本地依赖，不再访问远程/中央仓库。

总之，Maven 仓库机制为依赖与插件管理提供了核心支持，使项目构建与部署更加便捷高效。理解并掌握仓库机制对于 Maven 使用至关重要。

### 6.2 仓库关系和流程图解

> 课程配图（未随笔记提交）

## 7、Maven 实战案例：分布式 Maven 工程架构

### 7.1 项目需求和结构分析

> 课程配图（未随笔记提交）

需求案例：搭建一个电商平台项目。该平台包括用户服务、订单服务、通用工具模块等。本案例不写业务代码，重点在于：**实现分布式项目创建与依赖管理**。

项目架构：

1. 用户服务：负责处理用户相关逻辑，例如用户信息管理、用户注册、登录等
2. 订单服务：负责处理订单相关逻辑，例如订单创建、订单支付、退货、订单查看等
3. 通用模块：存放各服务通用工具类，其他服务依赖此模块

服务依赖：

1. 用户服务（1.0.1）
   ```json
   - spring-context 6.0.6
   - spring-core 6.0.6
   - spring-beans 6.0.6
   - jackson-databind / jackson-core / jackson-annotations 2.15.0
   ```
2. 订单服务（1.0.1）
   ```json
   - shiro-core 1.10.1
   - spring-context 6.0.6
   - spring-core 6.0.6
   - spring-beans 6.0.6
   ```
3. 通用模块（1.0.1）
   ```json
   - commons-io 2.11.0
   ```

### 7.2 项目搭建与依赖管理

#### 7.2.1 父模块搭建（micro-shop）

1. 创建父工程

   > 课程配图（未随笔记提交）

2. `pom.xml` 配置

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <project xmlns="http://maven.apache.org/POM/4.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
       <modelVersion>4.0.0</modelVersion>

       <groupId>com.atguigu</groupId>
       <artifactId>micro-shop</artifactId>
       <version>1.0.1</version>
       <!-- 父工程不打包，所以选择 pom 值 -->
       <packaging>pom</packaging>

       <properties>
           <spring.version>6.0.6</spring.version>
           <jackson.version>2.15.0</jackson.version>
           <shiro.version>1.10.1</shiro.version>
           <commons.version>2.11.0</commons.version>
           <maven.compiler.source>17</maven.compiler.source>
           <maven.compiler.target>17</maven.compiler.target>
           <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
       </properties>

       <!-- 依赖管理 -->
       <dependencyManagement>
           <dependencies>
               <!-- spring-context 会依赖传递 core / beans -->
               <dependency>
                   <groupId>org.springframework</groupId>
                   <artifactId>spring-context</artifactId>
                   <version>${spring.version}</version>
               </dependency>

               <!-- jackson-databind 会依赖传递 core / annotations -->
               <dependency>
                   <groupId>com.fasterxml.jackson.core</groupId>
                   <artifactId>jackson-databind</artifactId>
                   <version>${jackson.version}</version>
               </dependency>

               <!-- shiro-core -->
               <dependency>
                   <groupId>org.apache.shiro</groupId>
                   <artifactId>shiro-core</artifactId>
                   <version>${shiro.version}</version>
               </dependency>

               <!-- commons-io -->
               <dependency>
                   <groupId>commons-io</groupId>
                   <artifactId>commons-io</artifactId>
                   <version>${commons.version}</version>
               </dependency>
           </dependencies>
       </dependencyManagement>

       <dependencies>
           <!-- 父工程添加依赖，会自动传递给所有子工程，不推荐 -->
       </dependencies>

       <!-- 统一更新子工程打包插件 -->
       <build>
           <!-- JDK17 和 war 包版本插件不匹配 -->
           <plugins>
               <plugin>
                   <groupId>org.apache.maven.plugins</groupId>
                   <artifactId>maven-war-plugin</artifactId>
                   <version>3.2.2</version>
               </plugin>
           </plugins>
       </build>
   </project>
   ```

#### 7.2.2 通用模块（common-service）

1. 创建通用模块

   > 课程配图（未随笔记提交）

   > 课程配图（未随笔记提交）

2. `pom.xml` 配置

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <project xmlns="http://maven.apache.org/POM/4.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
       <modelVersion>4.0.0</modelVersion>
       <parent>
           <groupId>com.atguigu</groupId>
           <artifactId>micro-shop</artifactId>
           <version>1.0.1</version>
       </parent>
       <artifactId>common-service</artifactId>
       <!-- 打包方式默认就是 jar -->
       <packaging>jar</packaging>

       <properties>
           <maven.compiler.source>17</maven.compiler.source>
           <maven.compiler.target>17</maven.compiler.target>
           <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
       </properties>

       <dependencies>
           <!-- 声明 commons-io，继承父工程版本 -->
           <dependency>
               <groupId>commons-io</groupId>
               <artifactId>commons-io</artifactId>
           </dependency>
       </dependencies>
   </project>
   ```

#### 7.2.3 用户模块（user-service）

1. 创建模块

   > 课程配图（未随笔记提交）

   > 课程配图（未随笔记提交）

2. `pom.xml` 配置

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <project xmlns="http://maven.apache.org/POM/4.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
     <modelVersion>4.0.0</modelVersion>
     <parent>
       <groupId>com.atguigu</groupId>
       <artifactId>micro-shop</artifactId>
       <version>1.0.1</version>
     </parent>
     <artifactId>user-service</artifactId>
     <packaging>war</packaging>

     <properties>
       <maven.compiler.source>17</maven.compiler.source>
       <maven.compiler.target>17</maven.compiler.target>
       <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
     </properties>

     <dependencies>
       <!-- 添加 spring-context 自动传递 core / beans -->
       <dependency>
         <groupId>org.springframework</groupId>
         <artifactId>spring-context</artifactId>
       </dependency>

       <!-- 添加 jackson-databind 自动传递 core / annotations -->
       <dependency>
         <groupId>com.fasterxml.jackson.core</groupId>
         <artifactId>jackson-databind</artifactId>
       </dependency>
     </dependencies>
   </project>
   ```

#### 7.2.4 订单模块（order-service）

1. 创建模块

   > 课程配图（未随笔记提交）

   > 课程配图（未随笔记提交）

2. `pom.xml`

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <project xmlns="http://maven.apache.org/POM/4.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
       <modelVersion>4.0.0</modelVersion>
       <parent>
           <groupId>com.atguigu</groupId>
           <artifactId>micro-shop</artifactId>
           <version>1.0.1</version>
       </parent>

       <artifactId>order-service</artifactId>
       <packaging>war</packaging>

       <properties>
           <maven.compiler.source>17</maven.compiler.source>
           <maven.compiler.target>17</maven.compiler.target>
           <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
       </properties>

       <dependencies>
           <!-- 继承父工程依赖版本 -->
           <dependency>
               <groupId>org.springframework</groupId>
               <artifactId>spring-context</artifactId>
           </dependency>

           <!-- 继承父工程依赖版本 -->
           <dependency>
               <groupId>org.apache.shiro</groupId>
               <artifactId>shiro-core</artifactId>
           </dependency>
       </dependencies>
   </project>
   ```
