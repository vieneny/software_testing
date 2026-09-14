# 03 Web&框架：MVC 模式 & Spring 核心容器入门

## 1. 三层架构 & MVC 设计模式

### 1.1 现有代码问题 & 解决思路

先看我们当前`UserController`的新增用户方法，能直观看到 “代码堆砌、职责混乱” 的典型问题，也是新手最容易踩的坑：

```java
/**
 * 新增用户
 * 【硬编码登录校验：后续可通过拦截器统一处理，避免重复代码】
 * @param user 新增用户信息（请求体JSON）
 * @return 统一Result格式响应
 */
@PostMapping
public Result saveUser(
        HttpSession session, // 注入Session
        @Valid @RequestBody SysUser user,
        BindingResult bindingResult) {
    String username = (String) session.getAttribute("username");
    if (username == null || username.isEmpty()) {
        return Result.fail(501, "未登录,请先登录");
    }
    // 1. 参数校验逻辑
    if (bindingResult.hasErrors()) {
        String errorMsg = bindingResult.getFieldErrors().stream()
                .map(error -> error.getField() + "：" + error.getDefaultMessage())
                .collect(Collectors.joining("；"));
        return Result.fail(500, "参数校验失败：" + errorMsg);
    }
    // 2. 业务逻辑（直接调用工具类操作数据）
    SysUser savedUser = SysUserDataUtil.saveUser(user);
    System.out.println("新增后用户：" + savedUser);
    // 3. 响应结果
    return Result.success("新增用户成功！", savedUser);
}
```

这段代码的核心问题：

1. **职责混乱**：请求接收、参数校验、业务处理、数据操作（调用`SysUserDataUtil`）全堆在 Controller 里，一个方法干了多件事；
2. **维护成本高**：想修改 “参数校验规则” 或 “用户新增逻辑”，都要在同一个方法里翻找，代码越堆越乱；
3. **代码无法复用**：如果订单模块也要做 “用户状态校验”，只能复制粘贴代码，重复且易出错；
4. **扩展困难**：后续加 “登录校验”“权限控制”，只能往 Controller 里塞代码，最终变成难以维护的 “屎山代码”。

**结论**：这种写法仅适用于 demo 演示，企业级开发绝对不会这么写！解决方案是采用 **三层架构 + MVC 设计模式** 拆分代码，让每个模块只做自己的事，实现 “高内聚、低耦合”，从根本上解决代码混乱的问题。

### 1.2 MVC 设计模式 & 三层架构

#### 1.2.1 什么是 MVC 设计模式？

MVC（Model-View-Controller）是**针对 “前端交互 + 后端数据处理” 的表现层设计模式**，核心思想是把 “数据管理、界面展示、请求调度” 三个核心职责拆分开。

MVC 是跨语言通用的设计思想（Java、Python、C# 等都适用），核心聚焦 “前后端交互的表现层”，解决 “界面和数据耦合” 的问题。

> 课程配图（未随笔记提交）

**核心组件与职责（Web 场景下）**

| 组件                 | 核心职责                                                     |
| -------------------- | ------------------------------------------------------------ |
| Model（模型）        | 封装业务数据（如 SysUser 对象）、处理数据逻辑（如数据库 CRUD、参数校验） |
| View（视图）         | 展示数据、呈现用户界面（前端页面：Vue、Thymeleaf 模板、小程序界面） |
| Controller（控制器） | 接收用户请求（如 POST /user）、调度 Model 处理数据、控制 View 展示内容 |

**Web 场景下的数据流程**

浏览器发起请求 → Controller 接收请求 → 调用 Model 处理业务 / 操作数据 → Model 返回处理结果 → Controller 封装响应 → View 展示数据给用户

#### 1.2.2 什么是三层架构？

三层架构是**JavaWeb 项目特有的整体分层设计思想**，按 “职责范围” 把后端代码拆分为三个层级，覆盖从 “数据库操作” 到 “用户请求响应” 的全流程，核心目标是 “降低层间依赖、支撑复杂业务扩展”。

可以简单理解：MVC 是 “前端交互层的分工”，而三层架构是 “后端整体的分工”，二者结合能让代码结构更清晰、扩展更方便。

**核心层次与职责**

| 层次                  | 英文全称           | 核心职责                                                     | 依赖关系                     |
| --------------------- | ------------------ | ------------------------------------------------------------ | ---------------------------- |
| 表现层（Controller）  | Presentation Layer | 接收前端请求、返回响应结果（对应 MVC 中的 Controller），不处理核心业务逻辑 | 仅依赖业务逻辑层             |
| 业务逻辑层（Service） | Business Layer     | 处理核心业务规则（如用户新增前的唯一性校验、订单生成的库存扣减），承上启下 | 依赖数据访问层，被表现层调用 |
| 数据访问层（DAO）     | Data Access Layer  | 仅负责与数据源交互（数据库 / Redis 等），提供 CRUD 操作（如新增用户到数据库） | 不依赖上层，仅被业务层调用   |

**三层架构数据流程（Java 后端）**

前端请求 → 表现层（Controller）接收 → 调用业务逻辑层（Service）处理业务 → 业务层调用数据访问层（DAO）操作数据库 → DAO 返回数据给业务层 → 业务层处理后返回给表现层 → 表现层封装响应返回给前端

#### 1.2.3 MVC 与三层架构的核心区别

很多新手会混淆 MVC 和三层架构，核心区别如下（记住：**MVC 聚焦表现层，三层架构覆盖全后端**）：

| 对比维度        | MVC 设计模式                                                 | 三层架构                                         |
| --------------- | ------------------------------------------------------------ | ------------------------------------------------ |
| 概念定位        | 表现层的分工方法（聚焦 “交互 - 数据 - 展示”）                | Java 后端整体的分层策略（覆盖全业务流程）        |
| 核心范围        | 仅涉及 “前端请求 - 数据展示” 的表现层环节                    | 涵盖数据存储→业务处理→用户交互的后端全流程       |
| 组成形式        | 三元组（Model/View/Controller）                              | 三层（表现层 / 业务逻辑层 / 数据访问层）         |
| 适用场景        | Web / 移动端等带界面的应用开发                               | 企业级 JavaWeb 应用、微服务等后端系统            |
| 核心目标        | 解决视图与数据的耦合，便于界面迭代                           | 降低层间依赖，支撑复杂业务扩展、代码复用         |
| 与 JavaWeb 结合 | MVC 的 Controller 对应三层架构的表现层，Model 覆盖业务层 + DAO 层 | 三层架构是后端代码的整体骨架，MVC 是表现层的细分 |

**核心总结**

1. 无分层代码的核心问题：职责混乱、维护困难、无法复用，企业开发必须按 “三层架构 + MVC” 拆分；
2. MVC 是表现层设计模式，拆分 “请求调度（Controller）、数据处理（Model）、界面展示（View）”；
3. 三层架构是 Java 后端整体分层，拆分 “表现层（Controller）、业务层（Service）、DAO 层”；
4. 核心关系：MVC 的 Controller 对应三层架构的表现层，MVC 的 Model 覆盖三层架构的业务层 + DAO 层；
5. 最终目标：让每个模块只做一件事，实现 “高内聚、低耦合”，便于维护和扩展。

## 2. 案例 8：项目代码三层架构拆分

### 2.1 用户管理五套功能三层架构拆分

#### 2.1.1 数据访问层（DAO）

```java
import java.util.List;
/**
 * 数据访问层：仅负责用户数据的增删改查，不包含任何业务逻辑
 */
public interface UserDao {
    boolean deleteById(Long id);
    boolean updateById(Long id, SysUser sysUser);
    SysUser save(SysUser sysUser);
    SysUser getById(Long id);
    List<SysUser> list(String username, String phone, Integer status);
}
```

 UserDaoImpl 实现类

```java
import java.util.List;

/**
 * DAO实现类：仅调用SysUserDataUtil工具类完成数据操作
 */
public class UserDaoImpl implements UserDao {
    /**
     * 【DAO逻辑】调用工具类删除用户
     */
    @Override
    public boolean deleteById(Long id) {
        return SysUserDataUtil.deleteUserById(id);
    }
    /**
     * 【DAO逻辑】调用工具类更新用户
     */
    @Override
    public boolean updateById(Long id, SysUser sysUser) {
        return SysUserDataUtil.updateUserById(id, sysUser);
    }
    /**
     * 【DAO逻辑】调用工具类新增用户
     */
    @Override
    public SysUser save(SysUser sysUser) {
        return SysUserDataUtil.saveUser(sysUser);
    }
    /**
     * 【DAO逻辑】调用工具类查询单个用户
     */
    @Override
    public SysUser getById(Long id) {
        return SysUserDataUtil.getUserById(id);
    }
    /**
     * 【DAO逻辑】调用工具类条件查询用户列表
     */
    @Override
    public List<SysUser> list(String username, String phone, Integer status) {
        return SysUserDataUtil.listUsers(username, phone, status);
    }
}
```

#### 2.1.2 业务逻辑层（Service）

UserService 接口

```java
import java.util.List;

/**
 * 业务逻辑层：封装用户相关核心业务规则
 */
public interface UserService {
    boolean removeUserById(Long id);
    boolean updateUserById(Long id, SysUser sysUser);
    SysUser saveUser(SysUser sysUser);
    SysUser getUserById(Long id);
    List<SysUser> getUserList(String username, String phone, Integer status);
}
```

UserServiceImpl 实现类

```java
import java.util.List;

/**
 * Service实现类：具体实现用户业务逻辑，手动创建DAO实例
 */
public class UserServiceImpl implements UserService {

    // 手动new DAO实例
    private UserDao userDao = new UserDaoImpl();

    /**
     * 【业务逻辑】根据ID删除用户
     */
    @Override
    public boolean removeUserById(Long id) {
        return userDao.deleteById(id);
    }

    /**
     * 【业务逻辑】根据ID更新用户
     * 核心规则：先查用户是否存在，再更新
     */
    @Override
    public boolean updateUserById(Long id, SysUser sysUser) {
        if (userDao.getById(id) == null) {
            return false;
        }
        return userDao.updateById(id, sysUser);
    }

    /**
     * 【业务逻辑】新增用户
     */
    @Override
    public SysUser saveUser(SysUser sysUser) {
        return userDao.save(sysUser);
    }

    /**
     * 【业务逻辑】根据ID查询用户
     */
    @Override
    public SysUser getUserById(Long id) {
        return userDao.getById(id);
    }

    /**
     * 【业务逻辑】条件查询用户列表
     */
    @Override
    public List<SysUser> getUserList(String username, String phone, Integer status) {
        return userDao.list(username, phone, status);
    }
}
```

#### 2.1.3 表现层（Controller）

```java
/**
 * 表现层：仅接收请求、参数校验、调用Service、返回响应
 * 保留@RestController等Web注解，手动创建Service实例
 */
@RequestMapping("/user")
@RestController
public class UserController {

    // 手动new Service实例
    private UserService userService = new UserServiceImpl();

    /**
     * 根据ID删除用户
     * 【Controller仅做：接收请求→调用Service→返回响应】
     */
    @DeleteMapping("{id}")
    public Result removeUser(HttpSession session, @PathVariable Long id) {
        boolean deleted = userService.removeUserById(id);
        if (deleted) {
            return Result.success("删除ID为" + id + "的用户成功！");
        } else {
            return Result.fail("删除失败：ID为" + id + "的用户不存在！");
        }
    }

    /**
     * 根据ID更新用户
     * 【Controller仅做：参数校验→调用Service→返回响应】
     */
    @PutMapping("{id}")
    public Result updateUser(
            HttpSession session,
            @PathVariable Long id,
            @Valid @RequestBody SysUser sysUser,
            BindingResult bindingResult){

        // 仅做参数格式校验（无业务逻辑）
        if (bindingResult.hasErrors()) {
            String errorMsg = bindingResult.getFieldErrors().stream()
                    .map(error -> error.getField() + "：" + error.getDefaultMessage())
                    .collect(Collectors.joining("；"));
            return Result.fail(500, "参数校验失败：" + errorMsg);
        }
        Boolean updatedUser = userService.updateUserById(id, sysUser);
        if (updatedUser){
            return Result.success("更新ID为" + id + "的用户成功！");
        }
        return Result.fail("更新失败：ID为" + id + "的用户不存在！");
    }

    /**
     * 新增用户
     * 【Controller仅做：参数校验→调用Service→返回响应】
     */
    @PostMapping
    public Result saveUser(
            HttpSession session,
            @Valid @RequestBody SysUser user,
            BindingResult bindingResult
    ) {
        // 仅做参数格式校验（无业务逻辑）
        if (bindingResult.hasErrors()) {
            String errorMsg = bindingResult.getFieldErrors().stream()
                    .map(error -> error.getField() + "：" + error.getDefaultMessage())
                    .collect(Collectors.joining("；"));
            return Result.fail(500, "参数校验失败：" + errorMsg);
        }

        SysUser savedUser = userService.saveUser(user);
        return Result.success("新增用户成功！", savedUser);
    }

    /**
     * 根据ID查询用户详情
     * 【Controller仅做：接收请求→调用Service→返回响应】
     */
    @GetMapping("{id}")
    public Result findById(HttpSession session, @PathVariable Long id) {
        SysUser sysUser = userService.getUserById(id);
        System.out.println("查询到的用户：" + sysUser);
        if (sysUser == null) {
            return Result.fail("查询失败：ID为" + id + "的用户不存在！");
        }
        return Result.success("查询成功！", sysUser);
    }

    /**
     * 条件查询用户列表
     * 【Controller仅做：接收请求→调用Service→返回响应】
     */
    @GetMapping("/list")
    public Result getUserList(
            HttpSession session,
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String phone,
            @RequestParam(required = false) Integer status) {

        List<SysUser> sysUserList = userService.getUserList(username, phone, status);

        return Result.success("查询成功！共找到" + sysUserList.size() + "条数据", sysUserList);
    }
}
```

### 2.2 用户登录两套功能三层架构拆分

#### 2.2.1 扩展 DAO 层

扩展 UserDao 接口（新增登录方法）

```java
/**
 * 数据访问层：新增登录校验方法，仅调用工具类
 */
public interface UserDao {
    // 新增：登录校验（仅调用工具类，无业务逻辑）
    boolean login(String username, String password);
}
```

扩展 UserDaoImpl 实现类（实现登录方法，调用工具类）

```java
/**
 * DAO实现类：新增登录方法，仅转发调用SysUserDataUtil
 */
public class UserDaoImpl implements UserDao {

    // 新增：登录校验（仅调用工具类，无任何业务逻辑）
    @Override
    public boolean login(String username, String password) {
        return SysUserDataUtil.login(username, password);
    }
}
```

第扩展 Service 层（复用原有 UserService，新增登录业务方法）

#### 2.2.2 扩展 UserService 接口（新增登录方法）

```java
/**
 * 业务逻辑层：新增登录业务方法
 */
public interface UserService {
    // 新增：登录业务校验（可扩展登录规则，如账号是否禁用）
    boolean login(String username, String password);
}
```

扩展 UserServiceImpl 实现类（实现登录业务逻辑）

```java
/**
 * Service实现类：新增登录业务逻辑，复用已有DAO实例
 */
public class UserServiceImpl implements UserService {

    // 新增：登录业务逻辑（可扩展规则，如校验账号状态、登录次数限制等）
    @Override
    public boolean login(String username, String password) {
        // 业务逻辑1：调用DAO校验账号密码（基础校验）
        boolean validateResult = userDao.login(username, password);
        if (!validateResult) {
            return false;
        }
        // 业务逻辑2：（可扩展）校验账号是否禁用（示例）
        // 先查询用户信息，判断状态
        // SysUser user = userDao.getByUsername(username); // 可新增DAO方法
        // if (user != null && 0 == user.getStatus()) {
        //     return false; // 账号禁用，登录失败
        // }

        return true;
    }
}
```

#### 2.2.3 修改 LoginController

```java
/**
 * 登录表现层：仅处理请求、参数校验、调用Service、操作Session、返回响应
 * 复用已有UserService，手动new实例（无IOC注解）
 */
@RestController
@RequestMapping("auth")
public class LoginController {

    // 手动new Service实例（复用原有UserService，无需新增Service）
    private UserService userService = new UserServiceImpl();

    /**
     * 登录接口
     * /auth/login  post方式 请求体传递参数 username password
     * 验证成功以后，将账号存储在session!
     * 返回 {code:200,message:"登录成功",data:null}
     */
    @PostMapping("login")
    public Result login(HttpSession session, @Valid @RequestBody SysUserLoginDto user, BindingResult bindingResult) {
        // 1. 表现层职责：仅做参数格式校验（无业务逻辑）
        if (bindingResult.hasErrors()) {
            return Result.fail(500, "账号和密码不符合规则,登录失败！");
        }
        // 2. 调用Service完成登录业务校验（不直接调用工具类/DAO）
        boolean logined = userService.login(user.getUsername(), user.getPassword());
        if (!logined) {
            return Result.fail("账号或者密码错误！");
        }
        // 3. 表现层职责：操作Session（属于请求响应层面，无需走Service）
        session.setAttribute("username", user.getUsername());
        return Result.success("登录成功！");
    }

    /**
     * 退出登录接口
     * /auth/logout  get方式  没有参数
     * 清空session数据，返回成功响应
     * 返回 {code:200,message:"退出登录成功",data:null}
     */
    @GetMapping("logout")
    public Result logout(HttpSession session) {
        // 表现层职责：操作Session（无需走Service/DAO）
        session.removeAttribute("username");
        session.invalidate();
        return Result.success("退出登录成功！");
    }
}
```

## 3. Spring 核心容器入门（IoC/DI）

### 3.1 @Controller 是什么？有什么作用？

#### 3.1.1 先戳痛点：手动 new 对象 “自己操持所有家务”

```java
@RestController
@RequestMapping("/auth")
public class LoginController {

    // 手动new Service实例
    private UserService userService = new UserServiceImpl();

}
```

使用`UserController`时，我们得手动`new UserService`创建对象，如果这样的对象非常多怎么办？而且多个Controller都要用，每次都得new个新的吗？

这时候，**Spring 核心容器**就来了 —— 它就是你的 “专属对象管家”，专门帮你搞定这些麻烦事！

#### 3.1.2 Spring 核心容器：你的 “全能对象管家”

##### 3.1.2.1 什么是 Spring 核心容器？

你可以把 Spring 核心容器想象成**家里的全能管家**，核心职责特别清晰：管理对象生命周期

> 课程配图（未随笔记提交）

简单说，核心容器就是 Spring 的 “对象管理中心”，把对象的 “生老病死” 全接管，你彻底不用手动`new`对象、管依赖，解放双手！

**提醒：**把对象交给 Spring 核心容器管理，不只是 “更方便”，而是**必须这么做**！因为只有让 Spring 接管对象，你才能享受 AOP、事务管理等 Spring 核心功能 —— 不交给它管，Spring 的强大能力根本用不了。

##### 3.1.2.2 容器核心概念理解

**① 基础概念：对象 vs 组件**

- 对象：普通的 Java 对象（比如手动`new`的`UserServiceImpl`），没人管、自己生自己灭；
- 组件：被 Spring 核心容器接管的 “特殊对象”—— 相当于给普通对象上了 Spring 的 “户籍”，全程由管家统一管理。

**② 组件管理 IoC/DI**

* **IoC（Inverse of Control，控制反转）**

  一种软件工程设计思想，核心是将对象的创建权、生命周期管理权从开发者的业务代码中剥离，转移到 Spring 核心容器统一管控，实现对象控制权从 “开发者” 到 “容器” 的反转。

* **DI（Dependency Injection，依赖注入）**

  IoC 思想的核心实现方式，指 Spring 容器在创建目标对象（如 UserController）时，自动识别该对象依赖的其他对象（如 UserService），并将容器中已实例化的依赖对象注入到目标对象的指定属性 / 方法中，无需开发者手动赋值。

**③ 总结**

1. Spring 核心容器的核心作用是**接管对象的创建、存储、生命周期管理**，替代手动`new`；
2. 组件是被 Spring 容器管理的对象，普通对象需 “纳入容器” 才能成为组件；
3. 交给容器管理是使用 Spring 核心功能的前提，而非单纯的 “便捷选择”。

##### 3.1.2.3 核心容器接口与实现

核心接口（顶层抽象）

| 接口               | 核心定位                                                     | 关键特性                                        |
| ------------------ | ------------------------------------------------------------ | ----------------------------------------------- |
| BeanFactory        | Spring 容器的最基础核心接口，定义了 Bean 管理的最小规范（获取 Bean、判断 Bean 存在等） | 懒加载（获取 Bean 时才实例化）                  |
| ApplicationContext | BeanFactory 的子接口，扩展了容器能力（国际化、事件发布、资源加载等） | 立即加载（容器启动即实例化所有 Bean），主流选择 |

常用实现类

| 实现类                                             | 适用场景                                             |
| -------------------------------------------------- | ---------------------------------------------------- |
| ClassPathXmlApplicationContext                     | 基于类路径下的 XML 配置文件创建容器（传统 XML 开发） |
| AnnotationConfigApplicationContext                 | 基于注解配置类创建容器（纯注解开发）                 |
| AnnotationConfigServletWebServerApplicationContext | Spring Boot Web 项目核心容器（适配 Web 环境 + 注解） |

在 Spring Boot 环境下，已经无需我们手动创建核心容器，Spring Boot 已经帮我们完成创建了，以上了解即可！

#### 3.1.3 怎么才能将对象交给 Spring 核心容器管理呢？

`@Controller`（包括我们写接口常用的`@RestController`），本质就是给 Controller 类办 “托管登记”—— 跟管家说：“这个控制器我不管了，归你管！”，其他层也是同样的思路，只不过使用不同的注解！

核心意思就一句话：**告诉 Spring 核心容器（管家）：这个控制器类麻烦你帮我创建对象、好好存着，我要用的时候直接跟你要，不用我自己手动`new`了！**

关键特性：

1. 办了 “托管登记”（加了注解）的控制器，管家会主动找上门（Spring 自动扫描），创建好对象后存进 “专属仓库”（核心容器）；
2. 控制器的本职工作（处理前端请求）一点没少，只是 “创建” 的活交给管家了；
3. `@RestController`是 “豪华版登记”：不仅让管家管对象，还自带 “快递服务”—— 把处理结果直接打包成 JSON，送给前端（不用额外加其他注解，前后端分离场景直接用）。

### 3.2 三层架构组件类管理（标记）注解

#### 3.2.1 组件管理注解

Spring 核心容器（IoC 容器）是 Spring 的 “心脏”，本质就是一个**统一管理所有组件对象的仓库**：

- 核心流程：我们用「组件注解（@Controller）」标记类 → Spring 自动扫描这些类 → 核心容器帮我们创建对象（实例化）；
- 核心价值：实现**控制反转（IoC）**，对象的创建权从 “程序员手动 new” 转移到 “Spring 容器自动创建”，彻底解耦，并且交给核心容器管理的组件才能享受 Spring 其他高级功能！

`@Controller`只是组件注解的一种，Spring 为三层架构量身设计了**专属组件注解**，它们的核心作用一致：“告诉 Spring：这个类要交给容器管理”，只是语义上对应不同层级：

| 注解                            | 作用（标记的组件）               | 对应三层架构层级     |
| ------------------------------- | -------------------------------- | -------------------- |
| `@Controller`/`@RestController` | 标记 MVC 控制器，处理前端请求    | 表现层（Controller） |
| `@Service`                      | 标记业务逻辑组件，封装业务规则   | 业务层（Service）    |
| `@Repository`                   | 标记数据访问组件，处理数据交互   | 数据层（DAO）        |
| `@Component`                    | 通用组件注解（以上注解的父注解） | 非三层通用组件       |

#### 3.2.2 包扫描机制

需要明确的是：`@Component`系列注解本身不负责创建对象，它只是给类 “贴标签”—— 告诉 Spring “这个类要被你管理”。所有实际操作（创建对象、注入依赖）都是 Spring 框架的 Java 代码完成的，注解只是 “指令标记”。

举个通俗例子：

元旦布置教室时，班长在墙上贴标记：蓝色区域贴 “元旦快乐”、红色区域贴拉花、黄色区域贴气球。墙上的 “标记” 就相当于代码里的注解，而同学们按标记完成布置的过程，就是 Spring 框架按注解执行的具体操作。

> 课程配图（未随笔记提交）

想要找到这些 “标记”，Spring 就必须通过 “包扫描” 的方式，确定哪些包下的类上贴了注解、需要被管理。

**1. Spring Boot 默认扫描范围**

Spring Boot 会默认扫描以下范围的类：

- 主启动类所在的包及子包。

**2. 自定义扫描范围：@ComponentScan 注解**

如果默认扫描范围满足不了需求（比如组件不在主启动类包下），可通过`@ComponentScan`手动指定扫描路径：

```java
// 多路径扫描
@ComponentScan(value = {"com.atguigu.spring.user","com.atguigu.spring.order"})
```

⚠️ 核心注意事项：

1. 一旦手动指定`@ComponentScan`，Spring Boot 的默认扫描范围会**立即失效**；
2. `@ComponentScan`必须标记在**主启动类**或**配置类**上才生效；
3. 多路径扫描时，需用数组格式（`{包1, 包2}`）指定多个扫描路径。

总结

1. 组件注解的核心作用是 “标记类交给 Spring 管理”，不同注解仅对应三层架构的语义区分；
2. 注解本身不执行逻辑，Spring 需通过 “包扫描” 找到标记的类，再完成对象创建；

#### 3.2.3 组件管理案例实践

案例目标：

1. 用`@Component/@Repository/@Service/@RestController`四种注解将组件纳入 Spring 核心容器；
2. 业务层（Service）、数据层（DAO）设计接口 + 实现类，贴合实际开发规范；
3. 启动类中获取 Spring 核心容器，演示多种获取组件的方法；
4. 无需外部接口调用，启动类内直接验证组件管理效果。

代码结构：

```cmd
com.atguigu.iocdemo
  ├── IocDemoApplication.java  // 主启动类（核心：获取容器+演示获取组件）
  ├── component                // 通用组件包
  │   └── DateUtil.java        // 标记@Component（无接口）
  ├── dao                      // 数据层包
  │   ├── UserDao.java         // DAO 接口
  │   └── UserDaoImpl.java     // 标记@Repository（实现类）
  ├── service                  // 业务层包
  │   ├── UserService.java     // Service 接口
  │   └── UserServiceImpl.java // 标记@Service（实现类）
  └── controller               // 表现层包
      └── UserController.java  // 标记@Controller或@RestController（无接口）
```

核心代码：

1. 通用组件（@Component）：日期工具类（无接口）

   ```java
   /**
    * 通用工具类：标记@Component，纳入 Spring 容器管理
    * 非三层架构组件，使用通用注解
    */
   @Component // 核心：告诉Spring该类交给容器管理
   public class DateUtil {
       // 示例方法：获取当前时间字符串
       public String getNowTime() {
           return java.time.LocalDateTime.now().toString();
       }
   }
   ```

2. 数据层（@Repository）：DAO 接口 + 实现类

   DAO 接口

   ```java
   /**
    * 数据层接口：定义数据操作规范
    */
   public interface UserDao {
       // 模拟：根据ID删除用户
       boolean deleteById(Long id);
   }
   ```

   DAO 实现类

   ```java
   /**
    * DAO实现类：标记@Repository，纳入 Spring 容器管理
    * 对应数据层，语义化标识“数据访问组件”
    */
   @Repository // 核心：告诉Spring该类交给容器管理
   public class UserDaoImpl implements UserDao {
       @Override
       public boolean deleteById(Long id) {
           System.out.println("DAO层：执行删除操作，用户ID=" + id);
           return true; // 模拟删除成功
       }
   }
   ```

3. 业务层（@Service）：Service 接口 + 实现类

   Service 接口

   ```java
   /**
    * 业务层接口：定义业务操作规范
    */
   public interface UserService {
       // 模拟：删除用户（封装DAO操作）
       boolean removeUser(Long id);
   }
   ```

   Service 实现类（标记 @Service）

   ```java
   /**
    * Service实现类：标记@Service，纳入 Spring 容器管理
    * 对应业务层，语义化标识“业务逻辑组件”
    */
   @Service // 核心：告诉Spring该类交给容器管理
   public class UserServiceImpl implements UserService {

       // 依赖注入：从容器中获取 UserDao 组件（无需手动 new）
       @Autowired
       private UserDao userDao; // 按接口类型注入，容器自动匹配实现类

       @Override
       public boolean removeUser(Long id) {
           System.out.println("Service层：处理删除用户业务逻辑");
           return userDao.deleteById(id);
       }
   }
   ```

4. 表现层（@RestController）：测试控制器（无接口）

   ```java
   /**
    * 表现层组件：标记@RestController，纳入 Spring 容器管理
    * 对应Controller层，语义化标识“请求处理组件”
    */
   @RestController // 核心：告诉Spring该类交给容器管理
   public class UserController {

       // 依赖注入：从容器中获取 UserService 组件
       @Autowired
       private UserService userService;

       // 仅用于验证注入，无需对外暴露接口
       public void testRemoveUser(Long id) {
           userService.removeUser(id);
       }
   }
   ```

 5. 主启动类（核心：获取容器 + 演示获取组件）

    ```java
    /**
     * 主启动类：
     * 1. 启动 Spring Boot 应用，自动扫描组件并创建核心容器；
     * 2. 获取容器，演示多种获取组件的方法；
     * 3. 验证组件是否成功纳入容器并可调用。
     */
    @SpringBootApplication // 自带@ComponentScan，默认扫描当前包及子包
    public class IocDemoApplication {

        public static void main(String[] args) {
            // 核心步骤1：启动应用，获取 Spring 核心容器（ApplicationContext）
            ApplicationContext context = SpringApplication.run(IocDemoApplication.class, args);
            System.out.println("=== Spring 核心容器创建成功 ===");

            // 核心步骤2：演示多种从容器中获取组件的方法
            System.out.println("\n=== 方式1：按【类型】获取组件（最常用）===");
            // ① 获取通用组件（DateUtil）
            DateUtil dateUtil = context.getBean(DateUtil.class);
            System.out.println("DateUtil组件调用：当前时间=" + dateUtil.getNowTime());

            // ② 获取DAO组件（按接口类型）
            UserDao userDao = context.getBean(UserDao.class);
            userDao.deleteById(1L);

            // ③ 获取Service组件（按接口类型）
            UserService userService = context.getBean(UserService.class);
            userService.removeUser(2L);

            // ④ 获取Controller组件（按类型）
            UserController userController = context.getBean(UserController.class);
            userController.testRemoveUser(3L);

            System.out.println("\n=== 方式2：按【名称】获取组件 ===");
            // Spring默认组件名称：类名首字母小写（如UserDaoImpl → userDaoImpl）
            UserDaoImpl userDaoImpl = (UserDaoImpl) context.getBean("userDaoImpl");
            userDaoImpl.deleteById(4L);

            UserServiceImpl userServiceImpl = (UserServiceImpl) context.getBean("userServiceImpl");
            userServiceImpl.removeUser(5L);

            System.out.println("\n=== 方式3：按【类型+名称】获取组件（解决同接口多实现类冲突）===");
            // 当一个接口有多个实现类时，指定名称避免冲突
            UserDao userDao2 = context.getBean("userDaoImpl", UserDao.class);
            userDao2.deleteById(6L);

            // 核心步骤3：验证容器中是否存在指定组件（辅助排查）
            System.out.println("\n=== 验证组件是否存在 ===");
            boolean hasDateUtil = context.containsBean("dateUtil");
            boolean hasUserService = context.containsBean("userServiceImpl");
            System.out.println("容器中是否有DateUtil组件：" + hasDateUtil);
            System.out.println("容器中是否有UserService组件：" + hasUserService);
        }
    }
    ```

#### 3.2.4 Spring 核心容器获取组件方法

| 获取方式          | 语法示例                              | 适用场景                       | 注意事项                    |
| ----------------- | ------------------------------------- | ------------------------------ | --------------------------- |
| 按类型获取        | `context.getBean(类名.class)`         | 接口只有一个实现类（最常用）   | 同类型有多个组件会报错      |
| 按名称获取        | `context.getBean("组件名称")`         | 需精准指定组件名               | 返回 Object，需强制类型转换 |
| 按类型 + 名称获取 | `context.getBean("名称", 类名.class)` | 同接口有多个实现类（解决冲突） | 兼顾类型安全和名称精准      |

**组件默认名称规则**：类名首字母小写（如`UserDaoImpl` → `userDaoImpl`），也可手动指定（如`@Service("myUserService")`）。

#### 3.2.5 常见问题排查

- 组件获取失败（NoSuchBeanDefinitionException）：

  ① 组件未加注解；② 组件不在扫描包范围内；③ 组件名称 / 类型写错；

- 同类型多实现类冲突（NoUniqueBeanDefinitionException）：

  使用 “类型 + 名称” 方式获取，或给组件手动指定唯一名称（如)

  ```java
   UserDao userDao2 = context.getBean("userDaoImpl", UserDao.class);
  ```

### 3.3 Spring组件属性注入注解

#### 3.3.1 @Autowired&@Resource注解

我们已经通过`@Controller`/`@Service`等注解把类标记为组件、交给 Spring 容器管理，接下来的核心问题是：如何让这些组件之间建立关联（比如 Controller 调用 Service）？

如果还像以前一样手动`new`，就失去了 Spring 容器解耦的意义 —— 而**依赖注入（DI）** 就是答案：让 Spring 容器自动把需要的组件 “送” 到目标对象中，替代手动`new`，实现组件间的解耦关联。

`@Autowired`和`@Resource`是 Spring 中实现依赖注入的两大核心注解，都能从容器中获取组件并注入到目标对象，但底层匹配规则、使用位置、使用场景有明确区别（DI 是 IoC 的具体实现形式）。

##### ① 核心基础：注解使用位置

两个注解的使用位置完全一致，优先推荐「成员变量」位置（最简洁），其次是「set 方法」「构造方法」：

| 使用位置         | 特点                                      | 示例代码片段                                                 |
| ---------------- | ----------------------------------------- | ------------------------------------------------------------ |
| 成员变量（推荐） | 无需写 set 方法，代码最简洁               | `@Autowired private UserService userService;`                |
| set 方法         | 可在 set 方法中添加额外逻辑（如参数校验） | `@Autowired public void setUserService(UserService userService) { ... }` |
| 构造方法         | 适合强制依赖（Spring4.3 + 可省略注解）    | `@Autowired public UserController(UserService userService) { ... }` |

> 注意：日常开发中 90% 以上场景用「成员变量位置」即可，简洁高效；仅需额外处理依赖时，才用 set 方法 / 构造方法。

##### ② 核心区别

| 特性         | @Autowired                                | @Resource                                    |
| ------------ | ----------------------------------------- | -------------------------------------------- |
| 所属框架     | Spring 框架原生注解                       | JDK 原生注解（遵循 JSR-250 规范）            |
| 匹配规则     | 默认按「类型」匹配（byType）              | 默认按「名称」匹配（byName），可手动指定类型 |
| 依赖是否必须 | 默认必须（无匹配组件时直接抛异常）        | 默认必须（无匹配组件时直接抛异常）           |
| 可选配置     | `@Autowired(required = false)` 设为非必须 | `@Resource(required = false)` 设为非必须     |
| 多实现类处理 | 需配合`@Qualifier`注解指定组件名称        | 直接通过`name`属性指定组件名称（更简洁）     |

##### ③ 实战案例（完整可运行，贴合真实开发场景）

场景准备：定义基础接口和多实现类

```java
// 1. 定义UserDao接口（数据层）
public interface UserDao {
    boolean deleteById(Long id);
}

// 2. 实现类1：默认组件名称（userDaoImpl）
@Repository // 未指定name，默认组件名=类名首字母小写：userDaoImpl
public class UserDaoImpl implements UserDao {
    @Override
    public boolean deleteById(Long id) {
        System.out.println("DAO层V1：删除用户，ID=" + id);
        return true;
    }
}

// 3. 实现类2：自定义组件名称（userDaoImplV2）
@Repository("userDaoImplV2") // 手动指定组件名称
public class UserDaoImplV2 implements UserDao {
    @Override
    public boolean deleteById(Long id) {
        System.out.println("DAO层V2：删除用户（升级版），ID=" + id);
        return true;
    }
}

// 4. 定义 UserService 接口（业务层）
public interface UserService {
    boolean removeUser(Long id);
}
```

**案例 1：@Autowired 使用（单实现类 + 多实现类）**

```java
@Service
public class UserServiceImpl implements UserService {
    // ========== 场景1：单实现类（默认按类型匹配） ==========
    // @Autowired // 容器中只有UserDaoImpl时，直接按类型注入
    // private UserDao userDao;

    // ========== 场景2：多实现类（配合@Qualifier指定名称） ==========
    @Autowired(required = false) // 设为非必须，无匹配时不抛异常
    @Qualifier("userDaoImplV2")  // 明确注入名称为userDaoImplV2的组件
    private UserDao userDao;

    @Override
    public boolean removeUser(Long id) {
        System.out.println("Service层：校验删除权限，准备执行删除");
        return userDao.deleteById(id); // 调用注入的DAO组件
    }
}
```

**案例 2：@Resource 使用（按名称匹配 + 多实现类）**

```java
@Service
public class UserServiceImpl implements UserService {
    // ========== 场景1：默认按名称匹配（变量名=组件名） ==========
    // @Resource // 变量名userDaoImpl匹配组件名，注入UserDaoImpl
    // private UserDao userDaoImpl;

    // ========== 场景2：手动指定名称（多实现类推荐） ==========
    @Resource(name = "userDaoImplV2", required = false)
    private UserDao userDao; // 变量名可任意，只需name属性匹配组件名

    @Override
    public boolean removeUser(Long id) {
        System.out.println("Service层：校验删除权限，准备执行删除");
        return userDao.deleteById(id);
    }
}
```

**案例 3：Controller 中注入 Service（真实业务场景）**

```java
@RestController
@RequestMapping("/user")
public class UserController {
    // 成员变量位置注入（开发中最常用）
    @Autowired
    private UserService userService;

    // 测试接口：调用Service删除用户
    @DeleteMapping("/{id}")
    public Result removeUser(@PathVariable Long id) {
        boolean success = userService.removeUser(id);
        return success ? Result.success("删除成功") : Result.fail("删除失败");
    }
}
```

测试结果（调用接口 /user/100）

```plaintext
Service层：校验删除权限，准备执行删除
DAO层V2：删除用户（升级版），ID=100
```

##### ④ 核心总结

1. 依赖注入注解的核心使用位置：**成员变量（优先）**、set 方法、构造方法，其中成员变量写法最简洁；
2. 选型原则：单实现类用`@Autowired`（简洁），多实现类用`@Resource(name = "xxx")`（无需额外注解）；
3. 关键细节：`@Autowired`按类型匹配，多实现类需配合`@Qualifier`；`@Resource`默认按名称匹配，可直接指定 name；
4. 非必须依赖：通过`required = false`配置，避免无匹配组件时抛异常（适用于可选依赖）。

#### 3.3.2 注解读取配置参数

Spring Boot 项目默认采用**统一配置中心思想**，将所有配置集中在 `application.properties`（或 `application.yml`）文件中管理，这是框架的默认配置文件，启动时会自动加载，无需额外配置。

##### 3.3.2.1  @Value 注解读取默认配置（application.properties/yml）

`@Value` 是 Spring 读取单个配置项的基础注解，可直接读取 `application.properties/yml` 中的参数，支持默认值、系统变量等语法，是读取默认配置的首选方式。

| 语法格式                  | 说明                               | 示例                         |
| ------------------------- | ---------------------------------- | ---------------------------- |
| `@Value("${key}")`        | 读取默认配置文件中指定 key 的值    | `@Value("${app.name}")`      |
| `@Value("${key:默认值}")` | 读取失败（key 不存在）时使用默认值 | `@Value("${app.port:8080}")` |

**步骤 1：编写默认配置文件（application.properties）**

```properties
# 应用基础配置
app.name=SpringIocDemo
app.version=1.0.0
app.port=8888
# 数据库模拟配置
db.username=root
db.password=123456
```

**步骤 2：在组件中使用 @Value 读取配置**

```java
@Component // 纳入 Spring 容器管理，才能使用@Value
public class ConfigReaderUtil {
    // 读取基础配置（无默认值，key不存在会抛异常）
    @Value("${app.name}")
    private String appName;

    // 读取配置+默认值（key不存在时用默认值dev）
    @Value("${app.env:dev}")
    private String appEnv;

    // 读取数据库配置
    @Value("${db.username}")
    private String dbUsername;
    @Value("${db.password}")
    private String dbPassword;

    // 测试方法：打印读取结果
    public void printConfig() {
        System.out.println("=== 读取默认配置文件结果 ===");
        System.out.println("应用名称：" + appName);
        System.out.println("运行环境：" + appEnv);
        System.out.println("数据库账号：" + dbUsername);
        System.out.println("数据库密码：" + dbPassword);
    }
}
```

**步骤 3：启动类验证读取结果**

```java
// 在 Spring Boot 主启动类 main 方法中添加
public static void main(String[] args) {
    ConfigurableApplicationContext context = SpringApplication.run(IocDemoApplication.class, args);
    // 获取配置读取组件
    ConfigReaderUtil configReader = context.getBean(ConfigReaderUtil.class);
    // 打印配置
    configReader.printConfig();
}
```

**运行结果**：

```plaintext
=== 读取默认配置文件结果 ===
应用名称：SpringIocDemo
运行环境：dev
数据库账号：root
数据库密码：123456
```

##### 3.3.2.2  @Value 注解读取外部自定义配置文件（非默认配置）

`@Value` 仅能读取已加载的配置文件，若要读取**非默认的外部 properties 文件**（如单独的数据库配置、业务配置），需先通过 `@PropertySource` 加载文件，再用 `@Value` 读取参数，实现配置拆分和解耦。

| 注解                      | 作用                           | 示例                                                |
| ------------------------- | ------------------------------ | --------------------------------------------------- |
| `@PropertySource`         | 加载自定义外部 properties 文件 | `@PropertySource("classpath:config/db.properties")` |
| `@Value("${key}")`        | 读取外部文件中指定 key 的值    | `@Value("${db.mysql.username}")`                    |
| `@Value("${key:默认值}")` | 读取失败时使用默认值           | `@Value("${db.mysql.port:3306}")`                   |

**核心说明**：

- `@PropertySource`：标注在组件类上，指定外部配置文件路径（支持 `classpath:` 项目资源路径、`file:` 本地磁盘绝对路径）；
- 多文件加载：通过 `@PropertySource(value = {"文件1", "文件2"})` 加载多个外部文件；
- 中文兼容：配置文件含中文时，需指定编码 `encoding = "UTF-8"`。

**步骤 1：创建外部自定义配置文件**

在项目 `resources` 目录下新建 `config` 文件夹，创建 `db.properties`（单独存放数据库配置）：

```properties
# 外部数据库配置文件（resources/config/db.properties）
db.mysql.username=root_outer
db.mysql.password=outer_123456
db.mysql.url=jdbc:mysql://localhost:3306/outer_db
db.mysql.driver=com.mysql.cj.jdbc.Driver
db.mysql.port=3306
```

**步骤 2：加载外部文件并读取配置**

```java
/**
 * 读取外部自定义properties文件（非默认配置）
 */
@Component // 必须纳入容器，注解才生效
// 加载外部文件，指定UTF-8编码避免中文乱码
@PropertySource(encoding = "UTF-8", value = "classpath:config/db.properties")
public class OuterConfigReader {

    // 读取外部文件中的配置项
    @Value("${db.mysql.username}")
    private String dbUsername;

    @Value("${db.mysql.password}")
    private String dbPassword;

    @Value("${db.mysql.url}")
    private String dbUrl;

    // 读取不存在的key，使用默认值
    @Value("${db.mysql.max-connections:10}")
    private Integer dbMaxConnections;

    // 测试方法：打印外部配置
    public void printOuterConfig() {
        System.out.println("=== 读取外部自定义配置文件结果 ===");
        System.out.println("外部数据库账号：" + dbUsername);
        System.out.println("外部数据库密码：" + dbPassword);
        System.out.println("外部数据库URL：" + dbUrl);
        System.out.println("数据库最大连接数：" + dbMaxConnections);
    }
}
```

**步骤 3：启动类验证读取结果**

```java
public static void main(String[] args) {
    ConfigurableApplicationContext context = SpringApplication.run(IocDemoApplication.class, args);
    // 获取外部配置读取组件
    OuterConfigReader outerConfigReader = context.getBean(OuterConfigReader.class);
    // 打印外部配置
    outerConfigReader.printOuterConfig();
}
```

**运行结果**：

```plaintext
=== 读取外部自定义配置文件结果 ===
外部数据库账号：root_outer
外部数据库密码：outer_123456
外部数据库URL：jdbc:mysql://localhost:3306/outer_db
数据库最大连接数：10
```

**关键注意事项**：

1. 路径规则：

   - `classpath:`：从项目 `resources` 目录读取（推荐，适配打包部署）；
   - `file:`：从本地磁盘绝对路径读取（如 `file:D:/config/db.properties`），适用于配置文件外置场景；

2. **编码问题**：外部文件含中文时，必须指定 `encoding = "UTF-8"`，否则会乱码；

3. **优先级**：外部文件与默认 `application.properties` 有重复 key 时，默认文件配置会覆盖外部文件；

4. 多文件加载： **后加载的文件会覆盖先前文件的同名属性**

   ```java
   @PropertySource(encoding = "UTF-8", value = {
       "classpath:config/db.properties",
       "classpath:config/business.properties"
   })
   ```

##### 3.3.2.3  @ConfigurationProperties批量读取

`@Value`适合读取单个配置，但如果要读取一组相关配置（比如数据库的账号、密码、URL），用`@Value`要写多个注解，代码冗余。

`@ConfigurationProperties`是 Spring Boot 专门用来**批量读取一组配置**的注解：只需要指定一个 “配置前缀”，就能把前缀相同的所有配置，一次性绑定到一个实体类的属性上，比`@Value`更简洁、易维护。

| 注解                       | 作用                                   | 示例                                      |
| -------------------------- | -------------------------------------- | ----------------------------------------- |
| `@ConfigurationProperties` | 标记类为批量配置类，指定配置前缀       | `@ConfigurationProperties(prefix = "db")` |
| `@Component`               | 把配置类交给 Spring 容器管理（必须加） | 配合上面的注解使用                        |

关键规则：

1. 配置类的属性名要和配置文件中 “前缀后” 的字段名一致（比如前缀是`db`，配置`db.username`对应类里的`username`）；
2. 配置类必须写`setter`方法（Spring 靠 setter 给属性赋值）。

**代码实战：**

**步骤 1：添加配置文件（application.properties）**

沿用和`@Value`案例一致的配置，保持统一：

```properties
# 应用基础配置
app.name=SpringIocDemo
app.version=1.0.0
app.port=8888
# 数据库模拟配置
db.username=root
db.password=123456
```

**步骤 2：创建批量配置绑定类**

新建配置类，批量绑定`app`和`db`前缀的配置（分开绑定更清晰）：

（1）数据库配置类（绑定 db 前缀）

```java
/**
 * 批量绑定db前缀的配置
 * @Component：交给 Spring 容器管理
 * @ConfigurationProperties：指定配置前缀为db
 */
@Data
@Component
@ConfigurationProperties(prefix = "db")
public class DbConfig {
    // 属性名和配置文件中“db.xxx”的xxx一致
    private String username;
    private String password;

    // 必须写setter方法（Spring赋值用）
}
```

**步骤3：应用配置类（绑定 app 前缀）**

```java
/**
 * 批量绑定app前缀的配置
 */
@Data
@Component
@ConfigurationProperties(prefix = "app")
public class AppConfig {
    // 属性名和配置文件中“app.xxx”的xxx一致
    private String name;
    private String version;
    private Integer port;

    // 必须写setter方法（Spring赋值用）
}
```

**步骤 4：启动类中验证批量读取结果**

```java
@SpringBootApplication
public class IocDemoApplication {
    public static void main(String[] args) {
        // 启动 Spring 容器
        ApplicationContext context = SpringApplication.run(IocDemoApplication.class, args);
        System.out.println("=== 批量读取配置参数结果 ===");

        // 1. 获取数据库配置类，打印值
        DbConfig dbConfig = context.getBean(DbConfig.class);
        System.out.println("=== 数据库配置 ===");
        System.out.println("账号：" + dbConfig.getUsername());
        System.out.println("密码：" + dbConfig.getPassword());

        // 2. 获取应用配置类，打印值
        AppConfig appConfig = context.getBean(AppConfig.class);
        System.out.println("\n=== 应用配置 ===");
        System.out.println("应用名称：" + appConfig.getName());
        System.out.println("应用版本：" + appConfig.getVersion());
        System.out.println("服务端口：" + appConfig.getPort());
    }
}
```

**步骤 5：运行结果（控制台输出）**

```plaintext
=== 批量读取配置参数结果 ===
=== 数据库配置 ===
账号：root
密码：123456

=== 应用配置 ===
应用名称：SpringIocDemo
应用版本：1.0.0
服务端口：8888
```

**核心总结（@Value vs @ConfigurationProperties）**

| 特性       | @Value                     | @ConfigurationProperties     |
| ---------- | -------------------------- | ---------------------------- |
| 读取方式   | 单个读取（写多个注解）     | 批量读取（一个前缀搞定）     |
| 代码整洁度 | 配置多则冗余               | 配置越多越简洁               |
| 适用场景   | 少量零散配置（如单个端口） | 一组相关配置（如数据库配置） |

## 4. 案例 9：组件管理三层架构实践

将原有 “手动 new 实例” 的三层架构，替换为**Spring 组件注解管理 + 依赖注入**：

- DAO 层：`UserDaoImpl` 加 `@Repository` 纳入容器；
- Service 层：`UserServiceImpl` 加 `@Service` 纳入容器，通过 `@Autowired` 注入 `UserDao`；
- Controller 层：保留 `@RestController`，通过 `@Autowired` 注入 `UserService`；
- 完全移除手动 `new UserDaoImpl()`/`new UserServiceImpl()`，由 Spring 容器统一管理对象创建和依赖注入。

### 4.1 用户管理五套功能（IoC/DI 注解版）

#### 4.1.1 数据访问层（DAO）

UserDao 接口（无改动）

```java
import java.util.List;

/**
 * 数据访问层：仅负责用户数据的增删改查，不包含任何业务逻辑
 */
public interface UserDao {
    boolean deleteById(Long id);
    boolean updateById(Long id, SysUser sysUser);
    SysUser save(SysUser sysUser);
    SysUser getById(Long id);
    List<SysUser> list(String username, String phone, Integer status);
}
```

UserDaoImpl 实现类（加 @Repository，纳入容器）

```java
/**
 * DAO实现类：加@Repository注解，交给 Spring 容器管理
 * 仅调用SysUserDataUtil工具类完成数据操作
 */
@Repository // 核心：标记为DAO组件，纳入 Spring 容器
public class UserDaoImpl implements UserDao {
    /**
     * 【DAO逻辑】调用工具类删除用户
     */
    @Override
    public boolean deleteById(Long id) {
        return SysUserDataUtil.deleteUserById(id);
    }
    /**
     * 【DAO逻辑】调用工具类更新用户
     */
    @Override
    public boolean updateById(Long id, SysUser sysUser) {
        return SysUserDataUtil.updateUserById(id, sysUser);
    }
    /**
     * 【DAO逻辑】调用工具类新增用户
     */
    @Override
    public SysUser save(SysUser sysUser) {
        return SysUserDataUtil.saveUser(sysUser);
    }
    /**
     * 【DAO逻辑】调用工具类查询单个用户
     */
    @Override
    public SysUser getById(Long id) {
        return SysUserDataUtil.getUserById(id);
    }
    /**
     * 【DAO逻辑】调用工具类条件查询用户列表
     */
    @Override
    public List<SysUser> list(String username, String phone, Integer status) {
        return SysUserDataUtil.listUsers(username, phone, status);
    }
}
```

#### 4.1.2 业务逻辑层（Service）

UserService 接口（无改动）

```java
import java.util.List;

/**
 * 业务逻辑层：封装用户相关核心业务规则
 */
public interface UserService {
    boolean removeUserById(Long id);
    boolean updateUserById(Long id, SysUser sysUser);
    SysUser saveUser(SysUser sysUser);
    SysUser getUserById(Long id);
    List<SysUser> getUserList(String username, String phone, Integer status);
}
```

UserServiceImpl 实现类（加 @Service + @Autowired 注入 DAO）

```java
/**
 * Service实现类：加@Service注解纳入容器，通过@Autowired注入DAO（移除手动new）
 * 具体实现用户业务逻辑
 */
@Service // 核心：标记为Service组件，纳入 Spring 容器
public class UserServiceImpl implements UserService {

    // 核心改造：移除手动new，通过@Autowired从容器注入UserDao（按类型匹配UserDaoImpl）
    @Autowired
    private UserDao userDao;

    /**
     * 【业务逻辑】根据ID删除用户
     */
    @Override
    public boolean removeUserById(Long id) {
        return userDao.deleteById(id);
    }

    /**
     * 【业务逻辑】根据ID更新用户
     * 核心规则：先查用户是否存在，再更新
     */
    @Override
    public boolean updateUserById(Long id, SysUser sysUser) {
        if (userDao.getById(id) == null) {
            return false;
        }
        return userDao.updateById(id, sysUser);
    }

    /**
     * 【业务逻辑】新增用户
     */
    @Override
    public SysUser saveUser(SysUser sysUser) {
        return userDao.save(sysUser);
    }

    /**
     * 【业务逻辑】根据ID查询用户
     */
    @Override
    public SysUser getUserById(Long id) {
        return userDao.getById(id);
    }

    /**
     * 【业务逻辑】条件查询用户列表
     */
    @Override
    public List<SysUser> getUserList(String username, String phone, Integer status) {
        return userDao.list(username, phone, status);
    }
}
```

#### 4.1.3 表现层（Controller）

```java
/**
 * 表现层：加@RestController（已保留），通过@Autowired注入Service（移除手动new）
 * 仅接收请求、参数校验、调用Service、返回响应
 */
@RequestMapping("user")
@RestController // 标记为Controller组件，纳入 Spring 容器
public class UserController {

    // 核心改造：移除手动new，通过@Autowired从容器注入UserService
    @Autowired
    private UserService userService;

    /**
     * 根据ID删除用户
     * 【Controller仅做：接收请求→调用Service→返回响应】
     */
    @DeleteMapping("{id}")
    public Result removeUser(HttpSession session, @PathVariable Long id) {
        boolean deleted = userService.removeUserById(id);
        if (deleted) {
            return Result.success("删除ID为" + id + "的用户成功！");
        } else {
            return Result.fail("删除失败：ID为" + id + "的用户不存在！");
        }
    }

    /**
     * 根据ID更新用户
     * 【Controller仅做：参数校验→调用Service→返回响应】
     */
    @PutMapping("{id}")
    public Result updateUser(
            HttpSession session,
            @PathVariable Long id,
            @Valid @RequestBody SysUser sysUser,
            BindingResult bindingResult){

        // 仅做参数格式校验（无业务逻辑）
        if (bindingResult.hasErrors()) {
            String errorMsg = bindingResult.getFieldErrors().stream()
                    .map(error -> error.getField() + "：" + error.getDefaultMessage())
                    .collect(Collectors.joining("；"));
            return Result.fail(500, "参数校验失败：" + errorMsg);
        }
        Boolean updatedUser = userService.updateUserById(id, sysUser);
        if (updatedUser){
            return Result.success("更新ID为" + id + "的用户成功！");
        }
        return Result.fail("更新失败：ID为" + id + "的用户不存在！");
    }

    /**
     * 新增用户
     * 【Controller仅做：参数校验→调用Service→返回响应】
     */
    @PostMapping
    public Result saveUser(
            HttpSession session,
            @Valid @RequestBody SysUser user,
            BindingResult bindingResult
    ) {
        // 仅做参数格式校验（无业务逻辑）
        if (bindingResult.hasErrors()) {
            String errorMsg = bindingResult.getFieldErrors().stream()
                    .map(error -> error.getField() + "：" + error.getDefaultMessage())
                    .collect(Collectors.joining("；"));
            return Result.fail(500, "参数校验失败：" + errorMsg);
        }

        SysUser savedUser = userService.saveUser(user);
        return Result.success("新增用户成功！", savedUser);
    }

    /**
     * 根据ID查询用户详情
     * 【Controller仅做：接收请求→调用Service→返回响应】
     */
    @GetMapping("{id}")
    public Result findById(HttpSession session, @PathVariable Long id) {
        SysUser sysUser = userService.getUserById(id);
        System.out.println("查询到的用户：" + sysUser);
        if (sysUser == null) {
            return Result.fail("查询失败：ID为" + id + "的用户不存在！");
        }
        return Result.success("查询成功！", sysUser);
    }

    /**
     * 条件查询用户列表
     * 【Controller仅做：接收请求→调用Service→返回响应】
     */
    @GetMapping("/list")
    public Result getUserList(
            HttpSession session,
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String phone,
            @RequestParam(required = false) Integer status) {
        List<SysUser> sysUserList = userService.getUserList(username, phone, status);
        return Result.success("查询成功！共找到" + sysUserList.size() + "条数据", sysUserList);
    }
}
```

### 4.2 用户登录两套功能（IoC/DI 注解版）

#### 4.2.1 扩展 DAO 层（加 @Repository，无其他改动）

扩展 UserDao 接口

```java
import java.util.List;

/**
 * 数据访问层：新增登录校验方法，仅调用工具类
 */
public interface UserDao {

    // 新增：登录校验（仅调用工具类，无业务逻辑）
    boolean login(String username, String password);
}
```

扩展 UserDaoImpl 实现类

```java
import org.springframework.stereotype.Repository;
import java.util.List;

/**
 * DAO实现类：加@Repository纳入容器，新增登录方法（仅转发调用SysUserDataUtil）
 */
@Repository // 核心：标记为DAO组件，纳入 Spring 容器
public class UserDaoImpl implements UserDao {

    // 新增：登录校验（仅调用工具类，无任何业务逻辑）
    @Override
    public boolean login(String username, String password) {
        return SysUserDataUtil.login(username, password);
    }
}
```

#### 4.2.2 扩展 Service 层（加 @Service + @Autowired 注入 DAO）

扩展 UserService 接口

```java
import java.util.List;

/**
 * 业务逻辑层：新增登录业务方法
 */
public interface UserService {

    // 新增：登录业务校验（可扩展登录规则，如账号是否禁用）
    boolean login(String username, String password);
}
```

扩展 UserServiceImpl 实现类

```java
/**
 * Service实现类：加@Service纳入容器，通过@Autowired注入DAO（移除手动new）
 * 新增登录业务逻辑，复用已有DAO实例
 */
@Service // 核心：标记为Service组件，纳入 Spring 容器
public class UserServiceImpl implements UserService {

    // 核心改造：移除手动new，通过@Autowired从容器注入UserDao
    @Autowired
    private UserDao userDao;

    // 新增：登录业务逻辑（可扩展规则，如校验账号状态、登录次数限制等）
    @Override
    public boolean login(String username, String password) {
        // 业务逻辑1：调用DAO校验账号密码（基础校验）
        boolean validateResult = userDao.login(username, password);
        if (!validateResult) {
            return false;
        }
        // 业务逻辑2：（可扩展）校验账号是否禁用（示例）
        // SysUser user = userDao.getByUsername(username); // 可新增DAO方法
        // if (user != null && 0 == user.getStatus()) {
        //     return false; // 账号禁用，登录失败
        // }

        return true;
    }
}
```

#### 4.2.3 修改 LoginController（@Autowired 注入 Service）

```java
/**
 * 登录表现层：加@RestController（已保留），通过@Autowired注入Service（移除手动new）
 * 仅处理请求、参数校验、调用Service、操作Session、返回响应
 */
@RestController
@RequestMapping("auth")
public class LoginController {

    // 核心改造：移除手动new，通过@Autowired从容器注入UserService
    @Autowired
    private UserService userService;

    /**
     * 登录接口
     * /auth/login  post方式 请求体传递参数 username password
     * 验证成功以后，将账号存储在session!
     * 返回 {code:200,message:"登录成功",data:null}
     */
    @PostMapping("login")
    public Result login(HttpSession session, @Valid @RequestBody SysUserLoginDto user, BindingResult bindingResult) {
        // 1. 表现层职责：仅做参数格式校验（无业务逻辑）
        if (bindingResult.hasErrors()) {
            return Result.fail(500, "账号和密码不符合规则,登录失败！");
        }
        // 2. 调用Service完成登录业务校验（不直接调用工具类/DAO）
        boolean logined = userService.login(user.getUsername(), user.getPassword());
        if (!logined) {
            return Result.fail("账号或者密码错误！");
        }
        // 3. 表现层职责：操作Session（属于请求响应层面，无需走Service）
        session.setAttribute("username", user.getUsername());
        return Result.success("登录成功！");
    }

    /**
     * 退出登录接口
     * /auth/logout  get方式  没有参数
     * 清空session数据，返回成功响应
     * 返回 {code:200,message:"退出登录成功",data:null}
     */
    @GetMapping("logout")
    public Result logout(HttpSession session) {
        // 表现层职责：操作Session（无需走Service/DAO）
        session.removeAttribute("username");
        session.invalidate();
        return Result.success("退出登录成功！");
    }
}
```
