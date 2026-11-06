# 面试复习大纲 & 优先级

> 排序逻辑:**consultancy internal(最近一场,最快)→ vendor/client Java backend → bank/fintech/general backend → 保留 L4 foundation**。
> 同一份基础覆盖前 3 类;L4 只在 P1/P2 里顺带打底,不专门为它加码。

**优先级图例**
- `P0` 立即必备(consultancy 第一轮 + 广泛复用)
- `P1` 面试前应覆盖(bank/client/backend 常深挖)
- `P2` 现在低优先(L4 storyline / 少数深挖题才用)

**知识点标签**:`【背】`能脱口而出 · `【码】`能现场手写 · `【懂】`能解释+画图+讲 trade-off

---

## 1. 优先级总表

| 领域 | 优先级 | consultancy 概率 | bank/backend 概率 | 简历相关 | 备注 |
|---|:--:|:--:|:--:|:--:|---|
| Resume deep dive | **P0** | 高 | 高 | ★★★ | 每个 bullet 都会被追问,先自审弱点 |
| Core Java | **P0** | 高 | 高 | ★★ | consultancy 最爱考,基础概念+陷阱 |
| Spring Boot | **P0** | 高 | 高 | ★★★ | IoC/事务/AOP/REST 是主场 |
| SQL / Transaction | **P0** | 高 | 高 | ★★ | 手写 SQL + ACID/隔离级别 |
| Messaging (SQS/idempotency) | **P0** | 中 | 高 | ★★★ | 简历有 event-driven,必被挖 |
| Coding(pattern-based) | **P0** | 高 | 高 | — | 1 道 medium 为主 |
| Basic LLD | **P0** | 中 | 高 | ★ | 停车场/vending 级别 |
| Mid System Design | **P1** | 低 | 高 | ★★★ | reconciliation/pipeline 可借简历 |
| AWS / Data pipeline | **P1** | 中 | 中 | ★★★ | Glue/ECS/Lambda/DynamoDB |
| JVM / Concurrency | **P1** | 中 | 中 | ★ | GC、线程池、CAS、volatile |
| Testing / Observability | **P1** | 中 | 中 | ★★ | 90% coverage 含义、RCA |
| Behavioral / consultancy fit | **P1** | 高 | 中 | ★ | 8 个 STAR + client-facing 问题 |
| Advanced DP / graph | **P2** | 低 | 低 | — | 跳过复杂 DP |
| Advanced distributed (raft/paxos 证明) | **P2** | 低 | 低 | — | 只需概念,不深挖 |
| Deep ML theory | **P2** | 低 | 低 | ★ | AI bullet 讲 workflow,不讲训练 |

---

## 2. Coding / LeetCode 策略

**规则(diagnostic-first,不从 01 顺刷)**
- 能在 10 分钟内一次写对的 easy → **直接跳过**
- 每个 pattern 先做 **1 道 diagnostic(medium)**;做错/超时/卡壳 → 再补 2–4 道同类
- 评分维度:correctness → complexity → edge case → 讲清思路(communication) → clean Java
- 目标是 readiness,不是刷题量

**Pattern 优先级**

| 优先级 | Patterns |
|:--:|---|
| **P0** | HashMap/Set · Two Pointers · Sliding Window · Stack · Binary Search · Linked List · Tree DFS/BFS · Graph BFS/DFS · Heap/PriorityQueue · Intervals · 基础 Backtracking |
| **P1** | Topological Sort · Union Find · Trie · Greedy · Prefix Sum · Monotonic Stack · 1D DP · 2D DP |
| **P2** | 复杂 DP · Bitmask DP · 高级最短路变体 · Segment Tree · 复杂数学 |

**每个 P0 pattern 的 diagnostic 锚题(先各做 1 道自测)**
- HashMap → Two Sum / Group Anagrams
- Two Pointers → 3Sum
- Sliding Window → Longest Substring Without Repeating
- Stack → Valid Parentheses / Daily Temperatures(带出 monotonic)
- Binary Search → Search in Rotated Sorted Array
- Linked List → Reverse Linked List / Merge Two Lists
- Tree → Level Order Traversal + Lowest Common Ancestor
- Graph → Number of Islands + Course Schedule(带出 topo)
- Heap → Kth Largest / Merge K Sorted Lists
- Intervals → Merge Intervals
- Backtracking → Subsets / Permutations

> 完整 35–50 题精选表(含 consultancy 高频 10 / bank 高频 10 / Java-specific 5 / SQL 5)放到**下轮**给,先用锚题把 pattern 过一遍定位薄弱区。

---

## 3. System Design / LLD 题库(你这个 level)

> SWE II / 4 YOE / consultancy·bank:LLD 出现概率 > 大型 distributed SD。不用一上来 Google L5 难度。

### 3.1 LLD(按概率)
| 题 | 概率 | 说明 |
|---|:--:|---|
| Parking Lot | 高 | 你遇过,巩固 strategy/state 模式即可 |
| Vending Machine / ATM | 高 | State pattern 主场 |
| Elevator | 中 | 调度策略 |
| Movie/Ticket Booking | 中 | 并发订座 = 乐观锁/幂等 |
| Notification Service(对象模型) | 中 | 简历相关,可复用 |
| Payment Processor(对象模型) | 中 | bank 常考 |
| Library / Inventory | 中 | 基础建模 |

**每题固定覆盖**:requirements → 核心 class/interface → 关系 → 用到的 design pattern → 扩展性 → 并发 → 可测性 → 常见错误。

### 3.2 Mid-level System Design(按概率,★=能借你简历经验,高杠杆)
| 题 | 概率 | 简历杠杆 |
|---|:--:|:--:|
| Transaction Reconciliation System | 高 | ★★★(你的 AI reconciliation + pipeline) |
| Data Ingestion Pipeline | 高 | ★★★(30k/day Glue ETL) |
| Notification System | 高 | ★ |
| Audit Logging System | 中 | ★★(enrichment audit log) |
| Rate Limiter | 中 | — |
| URL Shortener | 中 | — |
| Payment Service | 中 | ★ |
| Document Management System | 中 | ★★(document broker) |
| Order Management / Inventory | 中 | ★ |
| Donation Platform | 中 | 你遇过,idempotency/webhook/ledger 是考点 |

**框架(每题固定套路)**:功能需求 → 非功能需求 → 规模估算 → API → 数据模型 → 高层架构 → 主流程 → DB 选型 → cache → MQ → **idempotency** → 失败处理 → security → observability → scaling → trade-offs。

---

## 4. Core Java 知识树

**4.1 语言基础** `P0`
- primitive vs wrapper / autoboxing 陷阱 `【懂】`
- String immutability + string pool `【背】`
- pass-by-value(对象传引用副本)`【背】`
- `final/finally/finalize` 区别 `【背】`
- abstract class vs interface `【背】` · overloading vs overriding `【背】`
- composition over inheritance `【懂】` · immutable object 设计 `【码】`
- `record` / `enum` / `annotation` 基本用途 `【懂】`

**4.2 对象契约** `P0`
- `equals()` / `hashCode()` 契约 `【背】【码】` ← 高频
- Comparable vs Comparator `【码】`
- shallow vs deep copy `【懂】`

**4.3 集合** `P0`
- ArrayList vs LinkedList `【背】`
- **HashMap 内部**:数组+链表/红黑树、hash、collision、resize、load factor、Java8 treeify `【懂】` ← 必考
- ConcurrentHashMap vs HashMap vs Collections.synchronizedMap `【懂】`
- TreeMap / LinkedHashMap / PriorityQueue 何时用 `【背】`
- fail-fast vs fail-safe `【懂】`

**4.4 异常** `P0`
- checked vs unchecked `【背】` · try-with-resources `【码】`
- REST 里的异常处理(接 Spring `@ControllerAdvice`)`【懂】`

**4.5 泛型** `P1`
- bounded type · wildcard · **PECS** · type erasure `【懂】`

**4.6 Java 8+** `P0`
- Lambda / functional interface `【码】`
- Stream:map/flatMap/filter/reduce/collect `【码】` ← 现场可能让写
- Optional 正确用法 `【背】`
- CompletableFuture 基本编排 `【懂】`
- parallel stream 的坑 `【懂】`

**4.7 并发** `P1`(bank 会深挖)
- race condition / atomicity / visibility / ordering `【懂】`
- `synchronized` vs `volatile` `【背】` ← 高频
- Lock/ReentrantLock · AtomicInteger · CAS · ABA `【懂】`
- deadlock 四条件 + 怎么避免 `【背】`
- ExecutorService / 线程池参数(core/max/queue/reject)`【懂】【码】`
- producer-consumer(BlockingQueue)`【码】`
- virtual threads 一句话认知 `【懂】`

**4.8 JVM** `P1`
- stack vs heap vs metaspace `【背】`
- class loading + 双亲委派 `【懂】`
- GC basics / minor vs full GC `【懂】`
- strong/soft/weak/phantom reference `【背】`
- memory leak 场景 · OOM vs StackOverflow `【懂】`
- thread dump / heap dump 会看 `【懂】`

---

## 5. Spring / Spring Boot 知识树

**5.1 IoC / DI** `P0`
- IoC & DI 概念 · constructor vs field injection(为什么推构造器)`【背】`
- bean 生命周期 / scope / 组件扫描 `【懂】`
- `@Component/@Service/@Repository/@Controller` · `@Configuration/@Bean` · `@Qualifier/@Primary` `【背】`

**5.2 Spring Boot** `P0`
- auto-configuration 原理 · starter · embedded server `【懂】`
- profiles · actuator · `@ConditionalOn*` `【懂】`

**5.3 AOP / Proxy** `P1`
- pointcut/advice/join point `【懂】`
- JDK dynamic proxy vs CGLIB `【背】`
- **self-invocation 问题**(同类内调用 `@Transactional` 为何失效)`【懂】` ← 高频陷阱

**5.4 Transaction** `P0`(bank 主场)
- `@Transactional` 代理机制 `【懂】`
- propagation:REQUIRED / REQUIRES_NEW / NESTED(重点这三)`【背】`
- isolation 四级 + 对应读现象 `【背】`
- rollback 规则:默认只回滚 RuntimeException `【背】` ← 高频
- 事务为什么"没生效"(self-invocation / private / 非 public / 异常被吞)`【懂】`
- 乐观锁 vs 悲观锁 `【懂】`
- **DB + MQ 一致性**(outbox / 至少一次 + 幂等)`【懂】` ← 接你简历

**5.5 Spring MVC / REST** `P0`
- DispatcherServlet 请求生命周期 `【懂】`
- Controller/Service/Repository 分层 · DTO · validation `【码】`
- `@ControllerAdvice` 全局异常 `【码】`
- HTTP 方法 · idempotency · status code · pagination · API versioning `【背】`
- authN vs authZ · JWT 基础 · filter vs interceptor `【懂】`

**5.6 JPA / Hibernate** `P1`
- entity lifecycle · persistence context · dirty checking `【懂】`
- lazy vs eager · **N+1 问题 + join fetch** `【懂】` ← 接你 GraphQL resolver
- 乐观锁 `@Version` `【懂】`

**5.7 Testing** `P1`
- JUnit + Mockito · mock vs spy `【码】`
- unit vs integration · `@SpringBootTest` · MockMvc · Testcontainers `【懂】`
- **90% coverage 到底意味着什么 + 局限** `【懂】` ← 你简历写了,必问

---

## 6. Messaging Systems `P0`(你的 event-driven 简历核心)

**6.1 核心概念**:queue vs topic · consumer group · offset · visibility timeout · ordering · backpressure `【懂】`

**6.2 Delivery semantics**(重点)
- at-most / at-least / exactly-once,为什么 exactly-once 难 `【背】`
- **idempotent consumer / dedup / idempotency key** `【懂】` ← 接"防止同一 instrument 重复写入"
- transactional outbox / inbox `【懂】`
- retry + exponential backoff · poison message · **DLQ + redrive** `【懂】`

**6.3 AWS SQS**(你实际用的)
- Standard vs FIFO(何时选哪个)`【背】`
- at-least-once + best-effort ordering `【背】`
- message group id / dedup id · long polling · partial batch failure `【懂】`

**6.4 Kafka**(讲对比,不用深挖)
- partition/offset/consumer group/rebalance · ordering 只在 partition 内 · idempotent producer `【懂】`

**简历必答题**(下轮给 sample answer):
SQS 为何 trigger Glue?Glue 失败怎么 retry?重复消费怎么办?怎么避免同一 instrument 重复写入?FIFO vs Standard?poison message?DLQ replay?DB 写成功但 ack 失败 / ack 成功但 DB 写失败?schema evolution?30k/day 要不要高吞吐?怎么扩到 30M/day?

---

## 7. Database / SQL

**7.1 SQL** `P0` `【码】`
- JOIN / GROUP BY / HAVING / subquery / CTE
- **window function:ROW_NUMBER / RANK**(高频)
- index / composite index / covering index / query plan
- normalization vs denormalization

**7.2 Transaction** `P0`
- ACID · 隔离级别 vs 读现象(dirty/non-repeatable/phantom)`【背】`
- lost update · deadlock · 乐观 vs 悲观 · MVCC `【懂】`

**7.3 你的存储选型(必问:为什么三个存储)** `P0`
- Aurora PostgreSQL(事务/关系)vs DynamoDB(KV/规模)vs OpenSearch(全文检索)分工与一致性 `【懂】` ★
- DynamoDB:partition/sort key · hot partition · GSI/LSI · 强 vs 最终一致 · conditional write(幂等)`【懂】`
- MongoDB:embedding vs referencing · replica set · 权限文档建模(接 document broker)`【懂】`
- OpenSearch:inverted index · DB 与 search index 的一致性/indexing lag `【懂】`

---

## 8. 简历深挖热点(先自审弱点,下轮逐条给强答案)

| Bullet | 最可能被挖 | 现在的弱点/风险 |
|---|---|---|
| Data pipeline | idempotency / dedup / retry / DLQ / schema evolution / 三存储分工 | 需想清"schema 校验失败的记录去哪"(quarantine/DLQ/drop-log) |
| Java 微服务 | GraphQL N+1 / resolver 架构 / manual correction 一致性 / 90% coverage | coverage 是否含 integration/API 测试要能答 |
| Document broker | 权限解析 RBAC vs ABAC / partner service 挂了怎么办 / 一致性 | permission-resolution redesign 细节要能画 |
| Production reliability | 80%/90% 数字怎么算 / 一个真实 RCA 案例 / alert 阈值 | 准备 1 个具体 RCA 故事 |
| AI governance | 什么是 governance / rule validation 怎么跑 / 你个人做了啥 / prod 还是 internal | 分清"我做的 infra/delivery"边界 |
| AI agent | router 是什么 / loop 何时停 / parallel tool call / tool error / 幻觉控制 / evaluation | 讲 workflow,不吹模型能力 |

---

## 9. Behavioral `P1`

**8 个 STAR 故事**(各配 result + 风险措辞 vs 强措辞):ownership · production incident · conflict · 模糊需求 · failure · 紧 deadline · 跨团队依赖 · 技术 trade-off。

**consultancy 专属**:Why consulting?client 舒适度?换项目适应?快速学新 stack?怎么报 blocker?relocation?多久能入职?多 stakeholder 怎么处理?

---

## 10. 下一轮(带 @Search 深挖)

按你说的,下轮开始逐块深挖,搜 2025–2026 US 市场面试模式,并交付:
1. 每个 P0 topic 的 **sample answer + common follow-up + 常见错误答法**
2. 完整 **35–50 题精选 coding 表**(含 consultancy/bank/Java/SQL 分类)
3. **48h / 7天 / 30天** 三套 schedule
4. 简历每个 bullet 的 **"追问 → 强答案结构"** 逐条稿

**建议下轮开工顺序**:Resume deep dive → Messaging/idempotency → Spring 事务 → Core Java 陷阱 → SQL/存储选型 → LLD/SD。(consultancy 最快命中的先做)
