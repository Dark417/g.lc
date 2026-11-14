# 03db.02dynamodb.11capacity-modes Capacity Modes And Retries

> On-demand vs provisioned capacity, what each absorbs, and where Software Development Kit (SDK) vs app-level retries belong.

## Index

- [1. On-Demand](#1-on-demand)
- [2. Provisioned](#2-provisioned)
- [3. Comparison And Default](#3-comparison-and-default)
- [4. Retries](#4-retries)
- [Related](#related)

## 1. On-Demand

On-demand (`PAY_PER_REQUEST`, used in `x-orders`) charges per request with no capacity planning.

- Pay per request
- Absorbs up to double the previous traffic peak instantly
  - Source: Developer Guide, "On-demand capacity mode"
- Spikes beyond that can throttle until DynamoDB adds partitions
  - Order of magnitude: tens of minutes
- Per-partition limits still apply
  - Result: on-demand does not fix a hot key ([02partitions-hot-keys](02dynamodb.02partitions-hot-keys.md))
- Pre-warm: raise warm throughput before a known event (or switch to provisioned at peak)

## 2. Provisioned

Provisioned sets Read Capacity Unit (RCU)/Write Capacity Unit (WCU) per table and per Global Secondary Index (GSI), optionally with auto scaling.

- Auto scaling reacts in minutes
  - Result: sharp spikes throttle
- Cheaper per request for steady, high, predictable load
  - Order of magnitude; check the pricing page

## 3. Comparison And Default

| Mode | Billing | Spike behavior | Best fit |
|---|---|---|---|
| On-demand | Per request | 2x previous peak instantly | Spiky or unknown load, no ops team |
| Provisioned | Per RCU/WCU-hour | Auto scaling lags minutes | Steady, high, predictable load |

Pick: on-demand, unless traffic is steady enough to keep provisioned utilization high.

## 4. Retries

Throttling and 5xx are retried by the SDK; the app retries only work that is safe to repeat.

- SDK retries throttling and 5xx with backoff
  - Adaptive mode in Python, standard in Java
- App-level retries only for idempotent or conditional writes
- Java client timeouts
  - Attempt timeout (2 s) bounds one Hypertext Transfer Protocol (HTTP) try
  - Call timeout (10 s) bounds all SDK retries together

**Java**

```java
// config/_03db_02dynamodb/DynamoDbConfig.java
.overrideConfiguration(ClientOverrideConfiguration.builder()
        .apiCallAttemptTimeout(Duration.ofSeconds(2))
        .apiCallTimeout(Duration.ofSeconds(10))
        .build())
```

```java
// infra/_03db_02dynamodb/DynamoDbShowcase.java
// App-level retry only around the transaction, and only for transient cancellation reasons.
retry.call(() -> client.transactWriteItems(req), DynamoDbShowcase::isRetryableTransactionFailure);
```

**Python**

```python
# app/infra/_03db_02dynamodb.py
# App-level retry only around the transaction, and only for transient cancellation reasons.
call_with_retry(call, is_retryable_transaction_error)
```

**Catch**

- `ADD` updates are not idempotent ⇒ never retry them blindly at app level
- Backoff for batch leftovers is app-level too ([08batch-ops](02dynamodb.08batch-ops.md#2-unprocessed-retry-loop))

## Related

- [00index](02dynamodb.00index.md)
- [02partitions-hot-keys](02dynamodb.02partitions-hot-keys.md)
- [98tradeoffs](02dynamodb.98tradeoffs.md)
