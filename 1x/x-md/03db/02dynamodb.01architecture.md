# 03db.02dynamodb.01architecture Why DynamoDB And How It Is Built

> Why DynamoDB was created, its common uses, and the request path through partitions and replicas.

## Index

- [1. Why It Was Created](#1-why-it-was-created)
  - [1.1 The Pain Before It](#11-the-pain-before-it)
  - [1.2 Prior Art](#12-prior-art)
  - [1.3 DynamoDB 2012](#13-dynamodb-2012)
  - [1.4 Common Use Cases](#14-common-use-cases)
- [2. Picture](#2-picture)
- [3. Write And Read Paths](#3-write-and-read-paths)
- [4. Client Wiring In Code](#4-client-wiring-in-code)
- [Related](#related)

## 1. Why It Was Created

DynamoDB exists because most high-traffic retail access was key-based, and relational databases paid for features nobody used.

### 1.1 The Pain Before It

- Amazon retail hit relational-database scaling limits in the 2004 holiday season
  - Source: Werner Vogels, "A Decade of Dynamo", 2017
- Most of that traffic was key-based (same source)
  - Get cart by id
  - Put cart

⇒ Joins and ad-hoc Structured Query Language (SQL) were paid for but rarely used.

### 1.2 Prior Art

- **Dynamo** (2007): leaderless, eventual, operated by each team
  - Result: powerful, but every team ran its own cluster
- **SimpleDB**: managed
  - Small table limits
  - Unpredictable latency

### 1.3 DynamoDB 2012

- Managed service
- Predictable latency
- Scale by adding partitions
- Leader-based replication per partition (Multi-Paxos)
  - Not Dynamo's leaderless design
  - Source: USENIX Annual Technical Conference (ATC) 2022 paper (see [References](02dynamodb.00index.md#references))

### 1.4 Common Use Cases

- Carts, sessions, user profiles, orders by customer
- Idempotency keys, distributed locks, leases
- Counters, feature flags, device state, game state
- Metadata index in front of Simple Storage Service (S3)

## 2. Picture

A request router hashes the partition key to a partition; each partition has one leader and two replicas in other Availability Zones (AZs).

```text
client ──► request router ──► partition map: hash(PK) → partition
                                   │
            ┌──────────────────────┼──────────────────────┐
            ▼                      ▼                      ▼
   ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
   │  partition 1   │     │  partition 2   │     │  partition 3   │
   │ leader  (AZ a) │     │ leader  (AZ b) │     │ leader  (AZ c) │
   │ replica (AZ b) │     │ replica (AZ c) │     │ replica (AZ a) │
   │ replica (AZ c) │     │ replica (AZ a) │     │ replica (AZ b) │
   └────────────────┘     └────────────────┘     └────────────────┘

inside a partition:  PK = CUSTOMER#c1
                       SK = ORDER#2026-01-02T10:00:00.000Z#o1
                       SK = ORDER#2026-01-05T09:30:00.000Z#o2   ← sorted by SK
                       SK = PROFILE
```

Notice that all items of one customer sit in one partition, sorted by Sort Key (SK): that is the "item collection".

## 3. Write And Read Paths

Writes always go through the partition leader; reads go to the leader or any replica depending on consistency.

**Write path**

→ Router hashes Partition Key (PK) and finds the partition leader  
→ Leader evaluates the condition expression against the current item  
→ Leader appends to its log and replicates to the two peers  
→ Write is acknowledged once a quorum (2 of 3) has it durable

**Read path**

- Strong read → served by the leader
- Eventual read → any replica
  - May miss the last write
  - Usually by well under a second (order of magnitude)
- Details: [03reads-consistency](02dynamodb.03reads-consistency.md)

## 4. Client Wiring In Code

The app holds one long-lived client; there are no connection pools, failover, or vacuum to run.

- Clients are thread-safe and hold a Hypertext Transfer Protocol (HTTP) connection pool
  - One per app, never one per request
- Building a client makes no network call
  - The first request resolves credentials and the endpoint

**Java**

```java
// config/_03db_02dynamodb/DynamoDbConfig.java
// Sync client: DynamoDB calls are short (single-digit ms), so blocking threads are fine here.
@Bean(destroyMethod = "close")
public DynamoDbClient dynamoDbClient(Region region, AwsCredentialsProvider credentialsProvider,
        @Value("${x.dynamodb.endpoint-override:}") String endpointOverride) {
    DynamoDbClientBuilder builder = DynamoDbClient.builder()
            .region(region)
            .credentialsProvider(credentialsProvider)
            .overrideConfiguration(ClientOverrideConfiguration.builder()
                    .apiCallAttemptTimeout(Duration.ofSeconds(2)) // bounds one HTTP try
                    .apiCallTimeout(Duration.ofSeconds(10))       // bounds all SDK retries together
                    .build());
    if (!endpointOverride.isBlank()) {
        builder.endpointOverride(URI.create(endpointOverride)); // DynamoDB Local on laptops
    }
    return builder.build();
}

// Enhanced Client: beans <-> AttributeValue maps; VersionedRecordExtension + AtomicCounterExtension on by default.
@Bean
public DynamoDbEnhancedClient dynamoDbEnhancedClient(DynamoDbClient dynamoDbClient) {
    return DynamoDbEnhancedClient.builder().dynamoDbClient(dynamoDbClient).build();
}
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
class DynamoDbShowcase:
    """Methods ending in _resource use the Table API, the others the low-level client."""

    # Lazy: created on first call; boto3 clients are thread-safe, resources are not (one per thread).
    @property
    def client(self) -> Any:
        return aws.client("dynamodb")

    @property
    def table(self) -> Any:
        return aws.resource("dynamodb").Table(self.orders_table)
```

**Catch**

- Numbers come back as `Decimal` from both boto3 Application Programming Interfaces (APIs)
  - Floats are rejected on write; use `int` or `Decimal`
- `status` is a reserved word in expressions
  - Always use `#name` placeholders with the client API
- The Software Development Kit (SDK) retries throttling and 5xx; app retries only for conditional work ([11capacity-modes](02dynamodb.11capacity-modes.md))

## Related

- [00index](02dynamodb.00index.md)
- [02partitions-hot-keys](02dynamodb.02partitions-hot-keys.md)
- [03reads-consistency](02dynamodb.03reads-consistency.md)
