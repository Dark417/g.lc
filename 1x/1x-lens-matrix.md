# 1x Lens Matrix — Which Lens Applies To Which Component

- What this is: every component in [1x-plan.md](1x-plan.md) crossed with the lenses from its Part A
- Use it two ways
  - Studying a component: read its row; answer every ● aloud, then the ○
  - Studying a theme (say, idempotency): read [By lens](#by-lens) for where it matters most
- Marks: ● = lead lens, must answer · ○ = applies, answer in pass 2 · blank = n/a, skip
- Four lenses apply to every row, so they have no column
  - L1 Problem, L2 Mechanism, L19 Siblings and choice, L20 My experience
- The marks are my judgment of what interviews probe, not a standard; tell me a cell is wrong and I'll fix it
- 2026-11-15 · 74 components × 17 lenses (L21 State added)

## Index
- [Lens legend](#lens-legend)
- [Matrix](#matrix)

  - [I. Language and code](#i-language-and-code)
  - [II. Spring stack](#ii-spring-stack)
  - [III. Architecture and APIs](#iii-architecture-and-apis)
  - [IV. Network, security, edge](#iv-network-security-edge)
  - [V. Data](#v-data)
  - [VI. Async and distributed](#vi-async-and-distributed)
  - [VII. Cloud and delivery](#vii-cloud-and-delivery)
- [By lens](#by-lens)
- [Lens families](#lens-families)
- [Components with the most lead lenses](#components-with-the-most-lead-lenses)

---

## Lens legend

| Lens | Column | Question in one line |
|---|---|---|
| L3 Guarantees | Guar | What does it promise, and under which conditions? |
| L4 Knobs | Knob | Which 2–3 settings matter, and what does each trade? |
| L5 Pitfalls | Pit | How is it misused; what silently doesn't work? |
| L6 Capacity limits | Cap | What does one instance / partition handle; which limit is hit first? |
| L7 Latency | Lat | What does one operation cost; p50 vs p99? |
| L8 10× test and skew | 10× | At 10× load, or one hot key: what breaks first, and what do you scale? |
| L9 Cost | Cost | What is billed, and what makes it expensive? |
| L10 Concurrency | Conc | Two requests at once on the same data: what protects it? |
| L11 Idempotency and retries | Idem | The same request twice: still correct? What is the key? |
| L12 Consistency model | Cons | Can a reader see stale data? |
| L13 Failure modes | Fail | What fails, what does the user see, how is it detected? |
| L14 Recovery and redundancy | Rec | Replication, failover, backup; what is lost in a crash? |
| L15 Backpressure | Back | Input exceeds capacity: queue, drop, throttle, shed? |
| L16 Observability | Obs | Which metrics show health; which alarm fires first? |
| L17 Security | Sec | Who can call it; data protection; the common misconfiguration? |
| L18 Evolution | Evol | How do you change it safely? |
| L21 State: stateful vs stateless | State | Stateful or stateless? Where does state live, and what happens to it on restart, scale-out, failover? |

## Matrix

### I. Language and code

| Component | Topic | L3 Guar | L4 Knob | L5 Pit | L6 Cap | L7 Lat | L8 10× | L9 Cost | L10 Conc | L11 Idem | L12 Cons | L13 Fail | L14 Rec | L15 Back | L16 Obs | L17 Sec | L18 Evol | L21 State |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| OOP and object contract | B1.1–B1.2 | ○ |   | ● |   |   |   |   |   |   |   |   |   |   |   |   | ○ |   |
| Collections, HashMap | B1.3 | ● | ○ | ● | ○ | ● | ○ |   | ● |   |   | ○ |   |   |   |   |   |   |
| Generics, reflection, proxies | B1.4–B1.5 | ○ |   | ● |   | ○ |   |   |   |   |   |   |   |   |   |   |   |   |
| Exceptions | B1.6 | ○ |   | ● |   |   |   |   |   |   |   | ○ |   |   |   |   |   |   |
| Threads, locks, `volatile` | B1.7 | ● | ○ | ● | ○ | ○ | ○ |   | ● |   | ○ | ● |   |   | ○ | ○ |   | ○ |
| Thread pools, executors | B1.7 | ○ | ● | ● | ● | ○ | ● |   | ● |   |   | ● |   | ● | ● |   |   | ○ |
| `CompletableFuture`, async | B1.7 | ○ | ○ | ● | ○ | ○ | ○ |   | ● |   |   | ● |   | ○ | ○ |   |   | ○ |
| JVM memory, GC | B1.8 | ○ | ● | ● | ● | ● | ● | ○ | ○ |   |   | ● |   |   | ● |   |   |   |
| Streams, lambdas | B1.9 | ○ |   | ● |   | ○ |   |   | ○ |   |   |   |   |   |   |   |   |   |
| SOLID, design patterns | B2 |   |   | ● |   |   |   |   | ○ |   |   |   |   |   |   |   | ● |   |

### II. Spring stack

| Component | Topic | L3 Guar | L4 Knob | L5 Pit | L6 Cap | L7 Lat | L8 10× | L9 Cost | L10 Conc | L11 Idem | L12 Cons | L13 Fail | L14 Rec | L15 Back | L16 Obs | L17 Sec | L18 Evol | L21 State |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| IoC, DI, bean lifecycle | B3.1–B3.2 | ○ | ○ | ● |   |   |   |   | ● |   |   | ○ |   |   |   |   | ○ | ● |
| AOP, proxies | B3.3 | ○ |   | ● |   | ○ |   |   |   |   |   | ○ |   |   |   |   |   |   |
| `@Transactional` | B3.4 | ● | ● | ● |   | ○ | ○ |   | ● | ○ | ● | ● | ○ |   | ○ |   |   | ○ |
| Spring Boot config, Actuator | B3.5 |   | ● | ● |   |   |   |   |   |   |   | ○ |   |   | ● | ○ | ○ |   |
| JDBC, HikariCP pool | B4.1 | ○ | ● | ● | ● | ○ | ● |   | ● |   |   | ● | ○ | ● | ● | ○ |   | ○ |
| JPA, Hibernate, Spring Data | B4.2–B4.6 | ○ | ● | ● | ○ | ● | ● |   | ● | ○ | ○ | ○ |   |   | ○ |   | ● | ● |
| Schema migration (Flyway) | B4.7 | ○ |   | ● |   |   | ○ |   | ○ |   |   | ● | ● |   |   |   | ● |   |
| Spring MVC, Tomcat threads | B5 |   | ● | ○ | ● | ○ | ● |   | ● | ○ |   | ● |   | ● | ● | ○ | ○ | ● |
| Spring Security | B6 | ● | ○ | ● |   | ○ |   |   | ○ |   |   | ○ |   |   | ○ | ● | ○ | ● |

### III. Architecture and APIs

| Component | Topic | L3 Guar | L4 Knob | L5 Pit | L6 Cap | L7 Lat | L8 10× | L9 Cost | L10 Conc | L11 Idem | L12 Cons | L13 Fail | L14 Rec | L15 Back | L16 Obs | L17 Sec | L18 Evol | L21 State |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| DDD, ports and adapters | B7 | ○ |   | ● |   |   |   |   | ○ |   | ○ |   |   |   |   |   | ● | ○ |
| Microservice boundaries | B8.1 |   |   | ● |   | ● | ● | ○ |   | ○ | ● | ● | ○ | ○ | ● | ○ | ● | ● |
| Calling many services (fan-out) | B8.2 | ○ | ● | ● | ○ | ● | ● |   | ○ | ● |   | ● | ○ | ● | ● | ○ | ○ | ○ |
| Saga, outbox (multi-service txn) | B8.3 | ● | ○ | ● |   | ○ | ○ |   | ● | ● | ● | ● | ● | ○ | ● |   | ○ | ● |
| Retries, circuit breaker, timeouts | B8.4 | ○ | ● | ● |   | ○ | ● |   |   | ● |   | ● | ● | ● | ● |   |   | ○ |
| REST API | B9.1 | ● |   | ● | ○ | ○ | ○ |   | ● | ● | ○ | ● |   | ○ | ○ | ● | ● | ● |
| WebSocket, SSE, long polling | B9.2 | ○ | ○ | ● | ● | ○ | ● | ○ |   | ○ | ○ | ● | ● | ● | ○ | ○ |   | ● |
| Webhooks | B9.2 | ○ | ○ | ● |   |   | ○ |   |   | ● |   | ● | ● | ○ | ○ | ● | ○ | ○ |
| GraphQL | B9.3 | ○ | ○ | ● | ○ | ● | ● | ○ |   | ○ |   | ○ |   | ● | ○ | ● | ● | ○ |
| gRPC | B9.4 | ○ | ● | ○ | ○ | ● | ○ |   |   | ○ |   | ● |   | ● | ○ | ○ | ● | ○ |

### IV. Network, security, edge

| Component | Topic | L3 Guar | L4 Knob | L5 Pit | L6 Cap | L7 Lat | L8 10× | L9 Cost | L10 Conc | L11 Idem | L12 Cons | L13 Fail | L14 Rec | L15 Back | L16 Obs | L17 Sec | L18 Evol | L21 State |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| TCP | B10.1 | ● | ○ | ○ | ○ | ● | ○ |   |   |   |   | ● | ○ | ● |   |   |   | ● |
| HTTP/1.1, 2, 3 | B10.2 | ○ | ○ | ○ | ○ | ● | ○ |   | ○ | ○ |   | ○ |   | ○ |   | ○ | ○ | ○ |
| TLS, mTLS, certificates | B10.3 | ● | ○ | ● |   | ● | ○ |   |   |   |   | ● | ○ |   | ○ | ● | ● | ○ |
| DNS | B10.4 | ○ | ● | ● |   | ○ | ○ |   |   |   | ● | ● | ● |   | ○ | ○ | ○ | ○ |
| OAuth 2.0, OIDC | B11.2 | ● | ○ | ● |   | ○ | ○ |   |   |   | ○ | ○ |   |   | ○ | ● | ○ | ● |
| JWT | B11.3 | ● | ○ | ● |   | ○ | ○ |   |   |   | ● | ○ |   |   |   | ● | ● | ● |
| KMS, encryption, secrets | B11.4 | ● | ○ | ● | ○ | ○ | ○ | ● |   |   |   | ● | ○ | ○ | ○ | ● | ● |   |
| Load balancer | B12.1 | ○ | ● | ● | ● | ○ | ● | ○ |   |   |   | ● | ● | ○ | ● | ○ | ○ | ● |
| API gateway | B12.2 | ○ | ● | ● | ● | ○ | ● | ● |   | ○ | ○ | ● | ○ | ● | ● | ● | ● | ○ |
| CDN | B12.3 | ○ | ● | ● | ○ | ● | ● | ● |   |   | ● | ○ | ● | ○ | ○ | ● | ○ | ○ |
| Rate limiter | B12.4 | ● | ● | ● | ○ | ○ | ● |   | ● |   | ○ | ● | ○ | ● | ○ | ○ |   | ● |

### V. Data

| Component | Topic | L3 Guar | L4 Knob | L5 Pit | L6 Cap | L7 Lat | L8 10× | L9 Cost | L10 Conc | L11 Idem | L12 Cons | L13 Fail | L14 Rec | L15 Back | L16 Obs | L17 Sec | L18 Evol | L21 State |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| ACID, isolation, locking | B13.1–B13.3 | ● | ● | ● |   | ○ | ○ |   | ● | ○ | ● | ● | ● |   | ○ |   |   |   |
| Indexes | B13.4 | ○ | ○ | ● | ○ | ● | ● | ○ | ○ |   |   | ○ |   |   | ○ |   | ● |   |
| SQL queries | B13.5 | ○ |   | ● |   | ● | ● |   |   |   |   |   |   |   |   |   |   |   |
| Replication | B13.6 | ● | ● | ● | ○ | ○ | ● | ○ |   |   | ● | ● | ● |   | ● |   | ○ | ● |
| Sharding, partitioning | B13.7 | ○ | ● | ● | ● | ○ | ● | ○ | ○ |   | ○ | ● | ○ |   | ● |   | ● | ○ |
| Data modeling, keys, IDs | B14 | ● |   | ● | ○ | ○ | ● |   | ○ | ○ | ○ |   |   |   |   | ○ | ● |   |
| Postgres | B15.1 | ● | ● | ● | ● | ● | ● | ○ | ● | ○ | ● | ● | ● | ○ | ● | ● | ● | ○ |
| Aurora Postgres | B15.3 | ● | ● | ● | ● | ● | ● | ● | ● | ○ | ● | ● | ● | ○ | ● | ● | ● | ○ |
| MySQL (InnoDB) | B15.4 | ● | ● | ● | ● | ● | ● | ○ | ● | ○ | ● | ● | ● | ○ | ● | ● | ● | ○ |
| Caching patterns, TTL | B16.1–B16.2 | ○ | ● | ● | ○ | ● | ● | ○ | ● |   | ● | ● | ○ | ○ | ● |   | ○ | ● |
| Redis | B16.3 | ● | ● | ● | ● | ● | ● | ● | ● | ○ | ● | ● | ● | ○ | ● | ● | ○ | ● |
| DynamoDB | B17.2 | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ○ |
| MongoDB | B17.3 | ● | ● | ● | ● | ○ | ● | ○ | ● | ○ | ● | ● | ● | ○ | ● | ● | ● | ○ |
| Elasticsearch / OpenSearch | B17.4 | ○ | ● | ● | ● | ● | ● | ● | ○ | ○ | ● | ● | ● | ● | ● | ○ | ● |   |
| Cassandra | B17.5 | ● | ● | ● | ● | ○ | ● | ○ | ○ | ○ | ● | ● | ● | ○ | ● | ○ | ● |   |
| S3 | B21.5 | ● | ○ | ● | ● | ● | ○ | ● | ● | ● | ● | ○ | ● | ○ | ○ | ● | ● | ○ |

### VI. Async and distributed

| Component | Topic | L3 Guar | L4 Knob | L5 Pit | L6 Cap | L7 Lat | L8 10× | L9 Cost | L10 Conc | L11 Idem | L12 Cons | L13 Fail | L14 Rec | L15 Back | L16 Obs | L17 Sec | L18 Evol | L21 State |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Kafka | B19.3 | ● | ● | ● | ● | ● | ● | ○ | ● | ● | ○ | ● | ● | ● | ● | ○ | ● | ● |
| SQS | B19.4 | ● | ● | ● | ● | ○ | ○ | ○ | ● | ● |   | ● | ● | ● | ● | ○ | ○ | ○ |
| SNS | B19.4 | ○ | ○ | ○ | ○ | ○ | ○ | ○ |   | ● |   | ● | ● | ○ | ○ | ○ | ○ |   |
| Kinesis, Firehose | B19.6 | ● | ● | ● | ● | ○ | ● | ● | ○ | ● |   | ● | ● | ● | ● | ○ | ○ | ○ |
| EventBridge, Step Functions | B21.4 | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ● |   | ● | ● | ○ | ● | ○ | ○ | ● |
| Stream processing (Flink) | B19.6 | ● | ● | ● | ○ | ● | ● | ○ | ○ | ● | ○ | ● | ● | ● | ● |   | ● | ● |
| Idempotency keys | B20.1 | ● | ● | ● | ○ |   | ○ |   | ● | ● | ○ | ● | ○ |   | ○ |   |   | ● |
| 2PC | B20.2 | ● |   | ● |   | ● | ○ |   | ● | ○ | ● | ● | ● |   |   |   |   |   |
| Consensus (Raft, etcd) | B20.3 | ● | ○ | ○ | ○ | ● | ○ |   | ● |   | ● | ● | ● |   | ○ |   | ○ | ● |
| Distributed locks, leases | B20.4 | ● | ● | ● |   | ○ | ○ |   | ● | ○ | ● | ● | ● |   | ○ |   |   | ● |

### VII. Cloud and delivery

| Component | Topic | L3 Guar | L4 Knob | L5 Pit | L6 Cap | L7 Lat | L8 10× | L9 Cost | L10 Conc | L11 Idem | L12 Cons | L13 Fail | L14 Rec | L15 Back | L16 Obs | L17 Sec | L18 Evol | L21 State |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Lambda | B21.1 | ○ | ● | ● | ● | ● | ● | ● | ● | ● |   | ● | ○ | ● | ● | ● | ○ | ● |
| ECS / Fargate, EC2 | B21.1 |   | ● | ○ | ● | ○ | ● | ● |   |   |   | ● | ● | ○ | ● | ○ | ● | ● |
| IAM | B21.2 | ● |   | ● | ○ |   |   |   |   |   | ○ | ○ |   |   | ○ | ● | ○ |   |
| VPC networking | B21.3 | ○ | ○ | ● | ○ | ○ | ○ | ● |   |   |   | ● | ● |   | ○ | ● | ○ |   |
| Docker | B22.1 |   | ○ | ● |   | ○ |   |   |   |   |   | ○ |   |   |   | ○ | ● | ● |
| Kubernetes | B22.2 | ○ | ● | ● | ● | ○ | ● | ○ |   |   | ○ | ● | ● | ○ | ● | ○ | ● | ● |
| CI/CD pipeline | B22.3 |   | ○ | ○ |   |   |   |   |   | ○ |   | ● | ● |   | ○ | ○ | ● |   |
| Terraform | B22.4 | ○ | ○ | ● |   |   |   |   | ● | ● | ○ | ● | ○ |   |   | ○ | ● | ● |

## By lens

- For each lens: the components where it is a lead lens (●)

- **L3 Guarantees** (32)
  - Collections, HashMap; Threads, locks, `volatile`; `@Transactional`; Spring Security; Saga, outbox (multi-service txn); REST API; TCP; TLS, mTLS, certificates; OAuth 2.0, OIDC; JWT; KMS, encryption, secrets; Rate limiter; ACID, isolation, locking; Replication; Data modeling, keys, IDs; Postgres; Aurora Postgres; MySQL (InnoDB); Redis; DynamoDB; MongoDB; Cassandra; S3; Kafka; SQS; Kinesis, Firehose; Stream processing (Flink); Idempotency keys; 2PC; Consensus (Raft, etcd); Distributed locks, leases; IAM
- **L4 Knobs** (36)
  - Thread pools, executors; JVM memory, GC; `@Transactional`; Spring Boot config, Actuator; JDBC, HikariCP pool; JPA, Hibernate, Spring Data; Spring MVC, Tomcat threads; Calling many services (fan-out); Retries, circuit breaker, timeouts; gRPC; DNS; Load balancer; API gateway; CDN; Rate limiter; ACID, isolation, locking; Replication; Sharding, partitioning; Postgres; Aurora Postgres; MySQL (InnoDB); Caching patterns, TTL; Redis; DynamoDB; MongoDB; Elasticsearch / OpenSearch; Cassandra; Kafka; SQS; Kinesis, Firehose; Stream processing (Flink); Idempotency keys; Distributed locks, leases; Lambda; ECS / Fargate, EC2; Kubernetes
- **L5 Pitfalls** (65)
  - OOP and object contract; Collections, HashMap; Generics, reflection, proxies; Exceptions; Threads, locks, `volatile`; Thread pools, executors; `CompletableFuture`, async; JVM memory, GC; Streams, lambdas; SOLID, design patterns; IoC, DI, bean lifecycle; AOP, proxies; `@Transactional`; Spring Boot config, Actuator; JDBC, HikariCP pool; JPA, Hibernate, Spring Data; Schema migration (Flyway); Spring Security; DDD, ports and adapters; Microservice boundaries; Calling many services (fan-out); Saga, outbox (multi-service txn); Retries, circuit breaker, timeouts; REST API; WebSocket, SSE, long polling; Webhooks; GraphQL; TLS, mTLS, certificates; DNS; OAuth 2.0, OIDC; JWT; KMS, encryption, secrets; Load balancer; API gateway; CDN; Rate limiter; ACID, isolation, locking; Indexes; SQL queries; Replication; Sharding, partitioning; Data modeling, keys, IDs; Postgres; Aurora Postgres; MySQL (InnoDB); Caching patterns, TTL; Redis; DynamoDB; MongoDB; Elasticsearch / OpenSearch; Cassandra; S3; Kafka; SQS; Kinesis, Firehose; Stream processing (Flink); Idempotency keys; 2PC; Distributed locks, leases; Lambda; IAM; VPC networking; Docker; Kubernetes; Terraform
- **L6 Capacity limits** (23)
  - Thread pools, executors; JVM memory, GC; JDBC, HikariCP pool; Spring MVC, Tomcat threads; WebSocket, SSE, long polling; Load balancer; API gateway; Sharding, partitioning; Postgres; Aurora Postgres; MySQL (InnoDB); Redis; DynamoDB; MongoDB; Elasticsearch / OpenSearch; Cassandra; S3; Kafka; SQS; Kinesis, Firehose; Lambda; ECS / Fargate, EC2; Kubernetes
- **L7 Latency** (26)
  - Collections, HashMap; JVM memory, GC; JPA, Hibernate, Spring Data; Microservice boundaries; Calling many services (fan-out); GraphQL; gRPC; TCP; HTTP/1.1, 2, 3; TLS, mTLS, certificates; CDN; Indexes; SQL queries; Postgres; Aurora Postgres; MySQL (InnoDB); Caching patterns, TTL; Redis; DynamoDB; Elasticsearch / OpenSearch; S3; Kafka; Stream processing (Flink); 2PC; Consensus (Raft, etcd); Lambda
- **L8 10× test and skew** (34)
  - Thread pools, executors; JVM memory, GC; JDBC, HikariCP pool; JPA, Hibernate, Spring Data; Spring MVC, Tomcat threads; Microservice boundaries; Calling many services (fan-out); Retries, circuit breaker, timeouts; WebSocket, SSE, long polling; GraphQL; Load balancer; API gateway; CDN; Rate limiter; Indexes; SQL queries; Replication; Sharding, partitioning; Data modeling, keys, IDs; Postgres; Aurora Postgres; MySQL (InnoDB); Caching patterns, TTL; Redis; DynamoDB; MongoDB; Elasticsearch / OpenSearch; Cassandra; Kafka; Kinesis, Firehose; Stream processing (Flink); Lambda; ECS / Fargate, EC2; Kubernetes
- **L9 Cost** (12)
  - KMS, encryption, secrets; API gateway; CDN; Aurora Postgres; Redis; DynamoDB; Elasticsearch / OpenSearch; S3; Kinesis, Firehose; Lambda; ECS / Fargate, EC2; VPC networking
- **L10 Concurrency** (29)
  - Collections, HashMap; Threads, locks, `volatile`; Thread pools, executors; `CompletableFuture`, async; IoC, DI, bean lifecycle; `@Transactional`; JDBC, HikariCP pool; JPA, Hibernate, Spring Data; Spring MVC, Tomcat threads; Saga, outbox (multi-service txn); REST API; Rate limiter; ACID, isolation, locking; Postgres; Aurora Postgres; MySQL (InnoDB); Caching patterns, TTL; Redis; DynamoDB; MongoDB; S3; Kafka; SQS; Idempotency keys; 2PC; Consensus (Raft, etcd); Distributed locks, leases; Lambda; Terraform
- **L11 Idempotency and retries** (16)
  - Calling many services (fan-out); Saga, outbox (multi-service txn); Retries, circuit breaker, timeouts; REST API; Webhooks; DynamoDB; S3; Kafka; SQS; SNS; Kinesis, Firehose; EventBridge, Step Functions; Stream processing (Flink); Idempotency keys; Lambda; Terraform
- **L12 Consistency model** (21)
  - `@Transactional`; Microservice boundaries; Saga, outbox (multi-service txn); DNS; JWT; CDN; ACID, isolation, locking; Replication; Postgres; Aurora Postgres; MySQL (InnoDB); Caching patterns, TTL; Redis; DynamoDB; MongoDB; Elasticsearch / OpenSearch; Cassandra; S3; 2PC; Consensus (Raft, etcd); Distributed locks, leases
- **L13 Failure modes** (51)
  - Threads, locks, `volatile`; Thread pools, executors; `CompletableFuture`, async; JVM memory, GC; `@Transactional`; JDBC, HikariCP pool; Schema migration (Flyway); Spring MVC, Tomcat threads; Microservice boundaries; Calling many services (fan-out); Saga, outbox (multi-service txn); Retries, circuit breaker, timeouts; REST API; WebSocket, SSE, long polling; Webhooks; gRPC; TCP; TLS, mTLS, certificates; DNS; KMS, encryption, secrets; Load balancer; API gateway; Rate limiter; ACID, isolation, locking; Replication; Sharding, partitioning; Postgres; Aurora Postgres; MySQL (InnoDB); Caching patterns, TTL; Redis; DynamoDB; MongoDB; Elasticsearch / OpenSearch; Cassandra; Kafka; SQS; SNS; Kinesis, Firehose; EventBridge, Step Functions; Stream processing (Flink); Idempotency keys; 2PC; Consensus (Raft, etcd); Distributed locks, leases; Lambda; ECS / Fargate, EC2; VPC networking; Kubernetes; CI/CD pipeline; Terraform
- **L14 Recovery and redundancy** (32)
  - Schema migration (Flyway); Saga, outbox (multi-service txn); Retries, circuit breaker, timeouts; WebSocket, SSE, long polling; Webhooks; DNS; Load balancer; CDN; ACID, isolation, locking; Replication; Postgres; Aurora Postgres; MySQL (InnoDB); Redis; DynamoDB; MongoDB; Elasticsearch / OpenSearch; Cassandra; S3; Kafka; SQS; SNS; Kinesis, Firehose; EventBridge, Step Functions; Stream processing (Flink); 2PC; Consensus (Raft, etcd); Distributed locks, leases; ECS / Fargate, EC2; VPC networking; Kubernetes; CI/CD pipeline
- **L15 Backpressure** (18)
  - Thread pools, executors; JDBC, HikariCP pool; Spring MVC, Tomcat threads; Calling many services (fan-out); Retries, circuit breaker, timeouts; WebSocket, SSE, long polling; GraphQL; gRPC; TCP; API gateway; Rate limiter; DynamoDB; Elasticsearch / OpenSearch; Kafka; SQS; Kinesis, Firehose; Stream processing (Flink); Lambda
- **L16 Observability** (30)
  - Thread pools, executors; JVM memory, GC; Spring Boot config, Actuator; JDBC, HikariCP pool; Spring MVC, Tomcat threads; Microservice boundaries; Calling many services (fan-out); Saga, outbox (multi-service txn); Retries, circuit breaker, timeouts; Load balancer; API gateway; Replication; Sharding, partitioning; Postgres; Aurora Postgres; MySQL (InnoDB); Caching patterns, TTL; Redis; DynamoDB; MongoDB; Elasticsearch / OpenSearch; Cassandra; Kafka; SQS; Kinesis, Firehose; EventBridge, Step Functions; Stream processing (Flink); Lambda; ECS / Fargate, EC2; Kubernetes
- **L17 Security** (20)
  - Spring Security; REST API; Webhooks; GraphQL; TLS, mTLS, certificates; OAuth 2.0, OIDC; JWT; KMS, encryption, secrets; API gateway; CDN; Postgres; Aurora Postgres; MySQL (InnoDB); Redis; DynamoDB; MongoDB; S3; Lambda; IAM; VPC networking
- **L18 Evolution** (30)
  - SOLID, design patterns; JPA, Hibernate, Spring Data; Schema migration (Flyway); DDD, ports and adapters; Microservice boundaries; REST API; GraphQL; gRPC; TLS, mTLS, certificates; JWT; KMS, encryption, secrets; API gateway; Indexes; Sharding, partitioning; Data modeling, keys, IDs; Postgres; Aurora Postgres; MySQL (InnoDB); DynamoDB; MongoDB; Elasticsearch / OpenSearch; Cassandra; S3; Kafka; Stream processing (Flink); ECS / Fargate, EC2; Docker; Kubernetes; CI/CD pipeline; Terraform
- **L21 State: stateful vs stateless** (27)
  - IoC, DI, bean lifecycle; JPA, Hibernate, Spring Data; Spring MVC, Tomcat threads; Spring Security; Microservice boundaries; Saga, outbox (multi-service txn); REST API; WebSocket, SSE, long polling; TCP; OAuth 2.0, OIDC; JWT; Load balancer; Rate limiter; Replication; Caching patterns, TTL; Redis; Kafka; EventBridge, Step Functions; Stream processing (Flink); Idempotency keys; Consensus (Raft, etcd); Distributed locks, leases; Lambda; ECS / Fargate, EC2; Docker; Kubernetes; Terraform

## Lens families

- Plain idea: some lenses travel together; study them as one theme across components

| Family | Lenses | Where it bites hardest |
|---|---|---|
| Shared state | L10 Concurrency, L12 Consistency, L3 Guarantees | Threads and locks, `@Transactional`, isolation levels, Redis, DynamoDB conditional writes, distributed locks |
| Retry safety | L11 Idempotency, L13 Failure, L14 Recovery | REST POST, service fan-out, saga, Kafka, SQS, Lambda, webhooks |
| Load | L6 Capacity, L8 10× test, L15 Backpressure | Thread pools, connection pools, Tomcat, Kafka, Kinesis, DynamoDB, load balancer, rate limiter |
| Memory and latency | L6 Capacity, L7 Latency, L4 Knobs | JVM and GC, HashMap, Redis, caches, indexes |
| Staleness | L12 Consistency, L4 Knobs (TTL) | Caching and TTL, CDN, DNS, read replicas, JWT, GSI |
| State | L21 State, L12 Consistency, L14 Recovery | Sessions vs JWT, sticky load balancing, WebSocket servers, Redis, Kafka offsets, Lambda, containers, Terraform state |
| Operate | L16 Observability, L17 Security, L18 Evolution, L9 Cost | Managed services: Aurora, DynamoDB, S3, Lambda, API gateway |

## Components with the most lead lenses

- These rows are the densest; they repay study first

| Component | Lead lenses (of 16) |
|---|---|
| DynamoDB | 16 |
| Aurora Postgres | 14 |
| Redis | 14 |
| Kafka | 14 |
| Postgres | 13 |
| MySQL (InnoDB) | 13 |
| Lambda | 13 |
| MongoDB | 12 |
| Elasticsearch / OpenSearch | 12 |
| Stream processing (Flink) | 12 |
| S3 | 11 |
| Kinesis, Firehose | 11 |
