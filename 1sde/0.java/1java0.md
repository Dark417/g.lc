# Java 快速背诵模板(中英结合)

> 用法:每条 = `English term` → 一句话标准答案 → ⚠️陷阱 / follow-up。
> 🔥 = 高频必背  ⚠️ = 易错点  【码】= 能现场手写

---

## 1. 语言基础 Language Fundamentals

- 🔥 **pass-by-value**:Java 只有值传递。传对象时传的是**引用的副本**,方法内改对象内容会生效,但重新赋值引用不影响外部。
- 🔥 **String immutable**:`String` 是 `final class` + 内部 `char[]` 不可变。好处:线程安全、可缓存 hash、可放 **string pool(常量池)**。
  - ⚠️ `"a"+"b"` 编译期直接优化成 `"ab"`;`new String("a")` 在堆上新建对象,不进池。
  - `StringBuilder`(非线程安全,快)vs `StringBuffer`(`synchronized`,线程安全)。
- 🔥 **final / finally / finalize**
  - `final`:变量=常量、方法=不可 override、类=不可继承。
  - `finally`:一定执行(除非 `System.exit()` / JVM 崩)。
  - `finalize`:GC 前回调,**已废弃**,别用。
- 🔥 **overload vs override**:overload=**编译期**、同名不同参;override=**运行时**、签名相同、子类重写(多态)。
- 🔥 **abstract class vs interface**
  - interface:可**多实现**、常量、`default`/`static` 方法(Java8)、无状态。
  - abstract class:单继承、可有**成员状态**和构造器。
  - 选择:能力/契约用 interface,共享代码+状态用 abstract。
- **primitive vs wrapper**:`int` vs `Integer`。⚠️ **Integer 缓存 -128~127**,`==` 比较超范围会 false,比值用 `.equals()`。
- **immutable object 设计**【码】:`final class` + 全 `final` 字段 + 无 setter + 构造器深拷贝可变字段 + getter 返回副本。
- **record**(Java16):不可变数据载体,自动生成 `equals/hashCode/toString`。
- **static**:类级别,随类加载;不能访问非静态成员;`static` 块在类初始化时执行一次。

---

## 2. 对象契约 Object Contracts

- 🔥【码】**equals() / hashCode() 契约**
  - 重写 `equals` **必须**重写 `hashCode`。
  - `equal` 的对象 → `hashCode` **必相等**;`hashCode` 相等 → 不一定 `equal`(哈希冲突)。
  - 默认 `equals` 比引用(`==`),默认 `hashCode` 是对象地址。
  - ⚠️ 不重写就放进 HashMap/HashSet → 逻辑相等的对象被当成两个。
- **Comparable vs Comparator**:`Comparable.compareTo`(自身自然序,一个)vs `Comparator.compare`(外部定义,可多个,`Comparator.comparing(...)`)。
- **shallow vs deep copy**:浅拷贝共享内部引用对象;深拷贝递归复制。`clone()` 默认浅拷贝。

---

## 3. 集合 Collections

- **ArrayList vs LinkedList**:ArrayList=动态数组,随机访问 O(1)、中间插删 O(n);LinkedList=双向链表,插删 O(1)(拿到节点)、随机访问 O(n)。实战几乎都用 ArrayList。
- 🔥 **HashMap 内部结构**(必考)
  - 结构:**数组 + 链表 + 红黑树**(Java8)。
  - 默认容量 **16**,load factor **0.75**,超阈值 **resize 扩容 2 倍**。
  - **链表长度 ≥ 8 且数组长度 ≥ 64** → 转红黑树;< 6 退化回链表。
  - key 通过 `hashCode()` 定位桶 + `equals()` 判等。
  - ⚠️ Java7 头插法多线程 resize 会成环死循环 → **Java8 改尾插**;但 HashMap 仍**非线程安全**。
- 🔥 **ConcurrentHashMap**
  - Java8:**CAS + synchronized 锁桶头节点**(放弃 Java7 的 Segment 分段锁)。
  - ⚠️ **不允许 null key/value**(HashMap 允许)。
- **TreeMap**:红黑树,有序,O(log n);**LinkedHashMap**:保插入/访问顺序(可做 LRU);**PriorityQueue**:堆,取最值 O(log n)。
- **fail-fast vs fail-safe**:fail-fast=遍历时结构改变抛 `ConcurrentModificationException`(ArrayList/HashMap);fail-safe=遍历副本不抛(CopyOnWriteArrayList/ConcurrentHashMap)。

---

## 4. 异常 Exception

- 🔥 **checked vs unchecked**
  - checked:编译期强制处理(`IOException`、`SQLException`)。
  - unchecked:`RuntimeException` 及子类(`NPE`、`IllegalArgument`),不强制。
  - ⚠️ 接 Spring:**默认只对 RuntimeException 回滚事务**。
- 【码】**try-with-resources**:实现 `AutoCloseable` 自动关流,逆序关闭。
- REST 里:`@ControllerAdvice` + `@ExceptionHandler` 全局兜底,转标准错误响应。

---

## 5. 泛型 Generics

- **type erasure(类型擦除)**:编译后泛型被擦成 `Object`/边界,运行时无泛型信息。⚠️ 不能 `new T[]`、不能 `instanceof List<String>`。
- 🔥 **PECS**:`Producer extends, Consumer super`。取数据用 `? extends T`,存数据用 `? super T`。
- **bounded type**:`<T extends Comparable<T>>`。

---

## 6. Java 8+ 函数式

- **lambda / functional interface**:单抽象方法接口(`Function/Consumer/Supplier/Predicate`),`@FunctionalInterface`。
- 🔥【码】**Stream**:
  - 中间操作(**lazy**):`map / filter / flatMap / sorted`。
  - 终止操作:`collect / reduce / forEach / count`。
  - `flatMap` = 展平嵌套流。
  - ⚠️ **parallel stream** 用公共 `ForkJoinPool`,注意共享可变状态 + 顺序,IO 密集别用。
- **Optional**:防 NPE。用 `orElse / orElseGet / map / ifPresent`,⚠️ **别直接 `.get()`**。
- **CompletableFuture**:异步编排。`thenApply`(转换)/`thenCompose`(串联另一个 future)/`thenCombine`(合并)/`allOf`。

---

## 7. 并发 Concurrency 🔥(bank 深挖区)

- 🔥 **三大问题**:atomicity(原子性)、visibility(可见性)、ordering(有序性/重排)。
- 🔥 **volatile vs synchronized**
  - `volatile`:保证**可见性 + 禁止指令重排**,**不保证原子性**。实现=内存屏障。
  - `synchronized`:三者都保证,可重入,JVM 层锁升级(偏向→轻量→重量)。
- 🔥 **CAS(Compare-And-Swap)**:乐观锁,`AtomicInteger` 底层。⚠️ **ABA 问题** → `AtomicStampedReference`(加版本号)。
- 🔥 **deadlock 四条件**:互斥、持有并等待、不可抢占、循环等待。破坏任一即可(常用:按固定顺序加锁)。
  - livelock=一直重试不前进;starvation=低优先级拿不到资源。
- 🔥【码】**线程池 ThreadPoolExecutor 7 参数**
  - `corePoolSize / maximumPoolSize / keepAliveTime / workQueue / threadFactory / handler`。
  - **执行流程**:core 满 → 入队 → 队列满且 < max → 开新线程 → 超 max → **拒绝**。
  - **4 种拒绝策略**:`AbortPolicy`(默认抛异常)/`CallerRunsPolicy`(调用线程执行)/`DiscardPolicy`(丢弃)/`DiscardOldestPolicy`(丢最老)。
  - ⚠️ 别用 `Executors.newFixedThreadPool`(无界队列 OOM),手动 `new ThreadPoolExecutor`。
- 【码】**producer-consumer**:`BlockingQueue`(`put`/`take` 自动阻塞)。
- **ReentrantLock vs synchronized**:Lock 可**中断、超时、公平锁、多条件 Condition**;synchronized 更简单自动释放。
- **virtual threads**(Java21):轻量级线程,适合高并发 IO 阻塞任务,一句话认知即可。

---

## 8. JVM 🔥

- 🔥 **运行时数据区**
  - **heap**(共享,对象实例,GC 主战场)。
  - **metaspace/方法区**(类信息,Java8 起用**本地内存**,取代永久代 PermGen)。
  - **JVM stack**(线程私有,栈帧=局部变量+操作数栈)。
  - **PC 寄存器 / native method stack**。
- 🔥 **class loading 流程**:加载 → 验证 → 准备 → 解析 → 初始化。
- 🔥 **双亲委派(parent delegation)**:Bootstrap → Platform/Ext → App → 自定义。**向上委托,向上找不到才向下加载**。作用:避免重复加载 + 核心类安全(防篡改)。
- 🔥 **GC 分代**:young(Eden + 2×Survivor)+ old。
  - **Minor GC**=回收 young(频繁快);**Full GC**=整堆(慢,要避免)。
  - 对象:Eden 分配 → 存活进 Survivor → 熬过多次进 old。
  - 算法:标记-清除(碎片)/复制(young)/标记-整理(old)。
  - **GC Roots**:栈局部变量、静态变量、常量、JNI 引用(可达性分析)。
  - 收集器:**G1**(Java9+ 默认)、ZGC(低延迟)、CMS(已废弃)。
- 🔥 **4 种引用**:strong(不回收)/ soft(内存不足才回收,做缓存)/ weak(下次 GC 回收,`ThreadLocal`/`WeakHashMap`)/ phantom(回收通知)。
- ⚠️ **OOM vs StackOverflowError**:OOM=堆/元空间满;SOE=递归太深栈溢出。
- **memory leak 场景**:静态集合持有对象、未关资源、`ThreadLocal` 不 remove、监听器未注销。
- 工具:`jstack`(thread dump 查死锁)、`jmap`(heap dump 查内存)、`jstat`(看 GC)。

---

## 背诵优先级(时间不够就按这个背)

1. **必背 🔥**:pass-by-value、String immutable、equals/hashCode 契约、HashMap 内部、ConcurrentHashMap、volatile vs synchronized、线程池流程 + 拒绝策略、GC 分代 + Full GC、双亲委派、4 种引用、事务回滚(见 Spring 篇)。
2. **能现场码【码】**:equals/hashCode、Stream、线程池创建、producer-consumer、immutable 对象。
3. **能画/讲**:HashMap resize、class loading、GC 流程、线程池执行链路。

---

## References

1. **JavaGuide**(github.com/Snailclimb/JavaGuide)— 中文 Java 面试知识树,和这份模板逐条对得上,深挖首选。
2. **Oracle Java Documentation / JLS** — 技术事实以官方为准(String pool、pass-by-value、generics erasure)。
3. **Baeldung**(baeldung.com)— Spring/Java 每个概念配可运行代码,查 CompletableFuture、ThreadPoolExecutor 用。
4. **《Java Concurrency in Practice》** — 并发深挖(volatile/CAS/线程池语义)。
