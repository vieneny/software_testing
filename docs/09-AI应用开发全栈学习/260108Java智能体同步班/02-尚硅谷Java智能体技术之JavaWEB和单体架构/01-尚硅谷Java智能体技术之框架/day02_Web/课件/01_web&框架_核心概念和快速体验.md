# 01_web&框架_核心概念和快速体验

## 1. Web 核心概念总结

### 1.1 Web 项目定义

Web 项目是**通过网络实现 “用户设备” 与 “远程服务端” 数据交互的应用**！

> 课程配图（未随笔记提交）

涵盖两类场景：

- 不需要装本地软件的：比如网页版淘宝、百度搜索（直接用浏览器打开）。
- 需要装客户端的：比如抖音 APP、微信小程序（装在手机上，但数据存在远程服务端）。

核心特质：数据存在 “云端服务端”，跨设备可同步（比如淘宝订单在手机 / 电脑上都能看）。

### 1.2 Web 核心骨架：C/S 模式

Web 项目的核心是 “客户端（用户侧）” 与 “服务端（远程侧）” 的分工协作：

1. **角色分工**

   - **客户端**：形式包括浏览器、手机 APP、小程序；**核心作用**是 “展示服务端内容 + 收集用户操作”（比如把商品页面给你看、把你选的商品发给服务端）。
   - **服务端**：是部署在机房的高性能电脑（24 小时开机）；**核心作用**是 “处理业务逻辑 + 操作数据库”（比如算订单总价、存订单信息）。

2. **交互流程（以 “淘宝查商品” 为例）**

   > 课程配图（未随笔记提交）

### 1.3 资源分类：静态 vs 动态

> 课程配图（未随笔记提交）

服务端给客户端返回的内容分为两类：

|   资源类型   | 包含内容                                      | 特点 & 案例                                               |
| :----------: | --------------------------------------------- | --------------------------------------------------------- |
|   静态资源   | HTML/CSS/JS、图片、视频                       | 内容固定（谁看都一样），比如淘宝首页的 logo、按钮样式     |
| **动态资源** | Spring / Spring MVC（替代过时的 Servlet/JSP） | 内容随用户变化（每人看到的不同），比如 “你的个人订单列表” |

### 1.4 架构模式：B/S 与 C/S

根据客户端是否需要安装，Web 项目分为两种架构：

- **C/S 模式（Client/Server）**：需装专用客户端软件，本地运行，连接服务器使用。（需要下载客户端，用户粘度高）
- **B/S 模式（Browser/Server）**：浏览器当客户端，不用装软件，网页访问即可用。（更方便快捷，用户粘度差！）

### 1.5 通信规则：HTTP 协议

客户端和服务端能 “听懂对方”，靠的是 HTTP 协议，它是 “规定请求 / 响应格式的通用规则”。

通信流程：客户端发 “HTTP 请求”（说明 “要什么资源 + 怎么要”）→ 服务端回 “HTTP 响应”（说明 “请求是否成功 + 返回内容”）。

> 课程配图（未随笔记提交）

### 1.6 运行容器：服务器软件

服务端代码（如 Spring Boot 程序）需要 “服务器软件” 承载运行！

它的核心作用是：**接收 HTTP 请求** → **解析请求** → **运行代码** → **返回响应**

常见软件：

- Tomcat：Java Web 开发最常用（后续课会用它跑咱们写的 Spring Boot 项目）。
- Nginx：主要部署静态资源、做反向代理（提升服务稳定性）。
- JBoss：企业级服务器（大型项目常用）。

### 1.7 Web 与框架学习路线

> 课程配图（未随笔记提交）：image-20251223102733935

**第一步：Spring Boot**

- **核心作用**：快速搭建 Java Web 项目的 “脚手架”，自动配置大部分框架（不用手动写大量配置）。
- **学习原因**：是当前企业级开发的主流框架，能让你 5 分钟内启动一个可运行的 Web 服务，大幅降低项目初始化成本。

**第二步：Spring MVC**

- **核心作用**：处理 Web 项目的 “请求 - 响应” 流程（比如接收前端请求、返回数据 / 页面）
- **学习原因**：所有 Web 项目都需要处理请求，Spring MVC 是 Spring 体系中 Web 层的标准实现，必须掌握其请求映射、参数接收等核心逻辑。

**第三步：MyBatis**

- **核心作用**：连接数据库的 “持久层框架”，通过 XML / 注解写 SQL，实现 Java 代码与数据库的交互。
- **学习原因**：项目必然需要操作数据库（存数据、查数据），MyBatis 是 Java 生态中最流行的持久层框架之一，灵活且易维护。

**第四步：MyBatis-Plus**

- **核心作用**：MyBatis 的增强工具，提供 “CRUD 通用方法”（不用手写简单 SQL）、分页、条件查询等功能。
- **学习原因**：能大幅减少重复代码（比如新增用户不用写 insert 语句），提升开发效率，是企业中 MyBatis 的 “标配增强工具”。

**第五步：Spring 高级**

- **核心作用**：深入 Spring 的底层原理（如 IOC/AOP、事务管理），解决复杂业务场景问题。
- **学习原因**：入门 Spring 后，要解决 “事务失效”“Bean 冲突” 等进阶问题，必须理解 Spring 的底层机制，是从 “会用” 到 “用好” 的关键。

**第六步：Spring Boot 高级**

- **核心作用**：掌握 Spring Boot 的高级特性（如自定义 Starter、分布式配置、性能优化），应对大型项目需求。
- **学习原因**：企业级项目需要高可用、易扩展，Spring Boot 高级特性是搭建大型微服务、复杂系统的必备技能

## 2. Spring 核心框架与关系梳理

### 2.1 Spring 简介

官网地址：https://spring.io/

> From configuration to security, web apps to big data—whatever the infrastructure needs of your application may be, there is a Spring Project to help you build it. Start small and use just what you need—Spring is modular by design.
>
> 从配置到安全，从 Web 应用到大数据 —— 无论你的应用有何种基础设施需求，都能找到对应的 Spring 项目助力开发。从小处着手，仅选用所需功能即可，Spring 在设计上具备模块化特性。
>
> 现在的 Spring 已经是一套技术栈的全家桶，包含各个技术方向的子框架！不过他的核心是 Spring Framework!

项目列表：https://spring.io/projects

> 课程配图（未随笔记提交）

通俗解释 Spring 就好比 Java 程序员的 “万能工具箱”+“智能管家”：

1. **智能管家**：以前写 Java 得自己创建、管理对象（比如数据库连接），Spring 包揽这些杂活 —— 你只需说「我要啥」，它就备好，帮你从繁琐的对象管理里解放出来。
2. **万能工具箱**：做网站、连数据库、搞安全验证等需求，Spring 都有现成的模块化工具，想用啥拿啥，不用从头造轮子，Web 开发好帮手。

简言之，Spring 帮你省掉重复麻烦的工作，专心写业务核心逻辑（比如电商下单、支付）。

### 2.2 Spring Framework 简介

若把 Spring 家族比作「大家族企业」，Spring Framework 就是「总部大楼 + 核心制度」—— 所有子项目（Spring Boot、Spring Security 等）都依赖它运转：

> 课程配图（未随笔记提交）

总结 Spring Framework：

- 是「地基骨架」：所有 Spring 家族项目的基础，比如 Spring Boot 也是基于它 IoC/DI 进行扩展。
- 是「规则制定者」：定好统一玩法，让各子项目能无缝配合，更好融合家族和第三方框架。
- 是「基础服务站」：提供对象管理、事务处理、AOP 编程等底层能力，子项目直接复用。

简言之，Spring Framework 是 Spring 家族的「根」，核心是帮我们创建、维护和管理对象。

### 2.3 Spring Boot 简介

Spring Boot 是基于 Spring Framework 的「快速开发工具」，核心是简化 Spring 开发：

- **建应用快**：一键创建可独立运行的 Spring 应用，不用手动导包、写大量配置。
- **部署简单**：内置 Tomcat 等服务器，直接用 `java -jar` 就能启动。
- **整合方便**：用「场景启动器」（如 web、数据库）引入功能，版本和依赖自动适配。
- **配置省心**：按「约定大于配置」来，大部分功能默认配好，改配置只需几行代码，还自带监控、健康检查。

总结：Spring Boot 让 Spring 开发「少折腾、快上手，之前配置文件太繁琐了」，零配置，直接专注写业务代码。

*注意：后面称呼 Spring 都指 Spring Framework 框架！*

### 2.4 框架关系总结

> 课程配图（未随笔记提交）：未命名绘图.drawio-1765169505883.png)

这是 Spring 技术栈的「分层支撑结构」（从下到上是「基础→核心→工具→应用」的依赖关系）：

* **最底层：Java 底层技术**

  是整个体系的「地基」—— 所有 Spring 技术都基于 Java（基础语法） 开发，无 Java 则后续技术无法运行。

* **第二层：Spring Framework（基础核心）**

  是 Spring 家族的「核心骨架」——Spring Boot 等子项目都依赖它的 IoC、AOP 等核心能力。

* **第三层：Spring Boot（快速开发工具）**

  把 Spring Framework 的能力包装成便捷工具，简化配置、快速整合上层框架。

* **最上层：Spring 家族框架 + 第三方框架 + 自定义工具**

  实际开发用的具体框架（如 Spring Security、MyBatis）和自定义工具，靠 Spring Boot 简化整合，基于整个分层运行。

总结：Spring 技术栈的依赖逻辑是 “Java 打底 → Spring Framework 做核心 → Spring Boot 当简化工具 → 支撑我们用各种框架 / 工具做开发” 的关系，越下层越基础，上层得靠下层才能运行。

❓ **问题 / 思考：为啥直接基于 Spring Boot 讲解框架技术？**

因为 Spring Boot 是当前企业开发的**主流 “入口框架”**：它把 Spring、Spring MVC 等核心技术做了 “自动配置”，能跳过复杂的手动配置步骤，让你快速从 “写代码实现功能” 入手，降低框架学习的门槛；同时，企业实际项目几乎都是用 Spring Boot 搭建的，直接基于它学习更贴合真实开发场景。

## 3. Spring Boot Web 快速体验

在实际开发中，我们几乎都会基于 Spring Boot 环境进行开发 —— 因为 Spring Boot 是对 Spring Framework 的进一步简化与封装，因此我们直接在 Spring Boot 环境下学习 Spring Framework、Spring MVC 和 MyBatis 即可。

### 3.1 案例需求说明

通过一个极简的 Web 小案例，完整体验基于 Spring Boot 的 Java Web 项目「创建 → 编写 → 启动 → 访问」全流程。

> 课程配图（未随笔记提交）

**具体需求**

1. 基于 Spring Boot 搭建一个 Web 项目；
2. 编写动态资源接口，当浏览器（客户端）访问地址 `http://localhost:8080/hello` 时；
3. 后台返回字符串 "hello javaweb!"，并在浏览器页面上显示该内容。

### 3.2 案例实现步骤

#### 3.2.1 创建 Spring Boot Web 项目

我们基于 IDEA 的 Spring Boot 工程创建向导来搭建项目，步骤如下：

**步骤 1：初始化 Boot 工程**

> 课程配图（未随笔记提交）

⚠️ **注意**：通过向导创建 Spring Boot 工程需联网！若创建速度慢，可将 Server URL 改为阿里云镜像地址：`https://start.aliyun.com`

**步骤 2：选择 Spring Boot 版本与场景启动器（依赖）**

> 课程配图（未随笔记提交）

💡 提示：向导生成的项目会包含部分暂时无用的文件，可直接删除以简化项目结构：

> 课程配图（未随笔记提交）

**步骤 3：项目 POM 依赖解读**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <!-- 继承 Spring Boot 官方父 POM，统一管理依赖版本和基础配置 -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <!-- Spring Boot 版本（后续统一使用 3.0.5 稳定版，非最新版最优） -->
        <version>3.0.5</version>
        <relativePath/> <!-- 跳过本地查找，直接读取官方父POM -->
    </parent>

    <!-- 项目唯一标识（GAV） -->
    <groupId>com.atguigu.java</groupId>
    <artifactId>module01_javaweb_hello</artifactId>
    <version>0.0.1-SNAPSHOT</version>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <!-- Web 开发场景启动器：一键引入 Web 开发所需所有依赖（依赖传递） -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- Lombok：简化实体类代码（如省略 get/set 方法） -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- 测试场景启动器：仅在测试环境生效 -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

**步骤 4：Boot 工程结构说明**

```
module01/javaweb_hello
├── src
│   ├── main
│   │   ├── java
│   │   │   └── com.atguigu.java.module01_javaweb_hello # 项目主包（Spring Boot自动扫描的根包）
│   │   │       ├── controller  # 控制器包（处理 Web 请求的类放在这里）
│   │   │       │   └── HelloController  # 具体的 Web 控制器类（定义接口、处理请求）
│   │   │       └── Module01JavawebHelloApplication  # Spring Boot 主启动类（运行它）
│   │   └── resources  # 非代码类的资源文件目录
│   │       ├── static  # 静态资源目录（存 HTML、CSS、图片等，浏览器可直接访问）
│   │       ├── templates  # 模板文件目录（存 Thymeleaf 等模板引擎的页面文件，用于渲染动态页面）
│   │       └── application.properties  # Spring Boot 核心配置文件（配端口、数据库等参数）
│   └── test
│       └── java
│           └── com.atguigu.java.module01_javaweb_hello  # 测试代码根包
│               └── Module01JavawebHelloApplicationTests  # 项目测试类（测试应用功能是否正常）
├── target  # Maven 构建输出目录（存编译后的 class 文件、打包的 JAR 包等）
└── pom.xml  # Maven 配置文件（管理项目依赖、构建插件等）
```

#### 3.2.2 编写动态资源

💡 关键要求：`HelloController` 类必须放在**主启动类所在包或其子包**下（否则 Spring 无法扫描到）。

```java
package com.atguigu.java.module01_javaweb_hello.controller;
/**
 * @RestController：标记当前类为「动态资源类」，Spring 会自动创建该类的实例并管理
 * 作用等价于 @Controller + @ResponseBody（返回字符串而非页面）
 */
@RestController
public class HelloController {

    /**
     * @RequestMapping("hello")：映射请求路径，浏览器访问/hello时执行该方法
     */
    @RequestMapping("hello")
    public String hello() {
        System.out.println("HelloController.hello 方法被调用");
        // 返回字符串给客户端（浏览器）
        return "hello javaweb!";
    }
}
```

#### 3.2.3 启动 Web 项目

直接点击主启动类的 `main` 方法运行即可：

> 课程配图（未随笔记提交）

#### 3.2.4 客户端浏览器访问

在浏览器地址栏输入：`http://localhost:8080/hello`，即可看到返回结果：

> 课程配图（未随笔记提交）

### 3.3 核心知识点总结

#### 3.3.1 为什么要继承 `spring-boot-starter-parent`？

继承该父 POM 的核心价值是**简化配置、规避坑点**，具体体现在 3 点：

1. **版本统一管理**：父 POM 预设了所有 Spring Boot 依赖的兼容版本，引入依赖时无需手动写版本号，避免版本冲突。
2. **插件简化配置**：内置 Spring Boot 常用 Maven 插件（如打包插件）的适配版本，无需重复配置。
3. **基础配置预设**：默认配置 UTF-8 编码、适配的 Java 版本等，省去基础配置工作。

简单说：父 POM 是 Spring Boot 官方的 “配置模板”，让你聚焦业务而非基础配置。

#### 3.3.2 为什么依赖叫 “场景启动器”？有什么好处？

Spring Boot 的 “场景启动器（Starter）” 是**一站式依赖解决方案**，核心好处是 “一键引入场景所需所有资源”：

- 官方场景启动器命名规则：`spring-boot-starter-*`（如 `spring-boot-starter-web`）。
- 第三方场景启动器命名规则：`*-spring-boot-starter`（如 `mybatis-spring-boot-starter`）。

导入对应场景启动器后，Spring Boot 会自动引入该场景的所有依赖、完成默认配置（如导入 `web` 启动器后，自动引入 Tomcat、Spring MVC 等依赖并配置），实现 “场景一导入，万物皆就绪”。

⚠️ 注意：场景启动器仅在 Spring Boot 工程中生效。
Spring Boot 官方支持的所有场景可参考：https://docs.spring.io/spring-boot/docs/current/reference/html/using.html#using.build-systems.starters

#### 3.3.3 为什么点击启动类就能运行整个项目？

核心就两个关键点：

1. **`main` 方法是程序入口**：Java 程序的启动入口就是 `main` 方法，点击启动类本质是执行这个方法；
2. **注解 + `run` 方法完成初始化**：
   - `@SpringBootApplication`：让 Spring 自动扫描并加载项目中的功能类（如 Controller）。
   - `SpringApplication.run(...)`：启动 Spring 核心容器，同时自动启动内置 Tomcat 服务器，加载所有配置和组件。

两者结合，只需运行启动类，就能完成 “组件加载 + 服务器启动”，整个项目即可运行。

### 3.4 本章小结

1. Spring Boot 项目创建核心是选对场景启动器（如 `web`），继承父 POM 可大幅简化配置。
2. 控制器类需放在主启动类的包 / 子包下，`@RestController` + `@RequestMapping` 可快速定义接口。
3. 启动类的 `main` 方法 + `@SpringBootApplication` 是项目运行的核心，可自动完成容器和服务器启动。