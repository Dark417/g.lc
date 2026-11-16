# 03db.01aurora.04serverless-v2 Serverless v2 Capacity

> Serverless v2 resizes an instance in place between a min and max Aurora Capacity Unit (ACU); the cost is a cache that shrinks with it.

## Index

- [1. Capacity Unit](#1-capacity-unit)
- [2. Mechanism](#2-mechanism)
- [3. Costs](#3-costs)
- [4. Deciding Variable](#4-deciding-variable)
- [Related](#related)

## 1. Capacity Unit

- **ACU**: about 2 gibibytes (GiB) of memory plus matching Central Processing Unit (CPU) and network
- Instance scales in fine steps (0.5 ACU) between a configured min and max
  - Terraform here: 0.5–8 ACU ([`modules/03db_01aurora/main.tf`](../../terraform/modules/03db_01aurora/main.tf))
  - Amazon Web Services (AWS) ceiling per instance: 256 ACU (user guide, 2024; check current)
  - Newer engine versions allow min 0 with auto-pause (AWS announcement, Nov 2024)

## 2. Mechanism

- Scales the instance in place
- No failover, no reconnect

## 3. Costs

- Buffer cache shrinks with capacity
  - Result: cold reads after scale-down
- Scale-up takes time
  - A sudden spike from a very low floor hits a small cache
- `max_connections` is derived from max capacity, not current capacity
  - Pool sizing uses that number; see [06pools-rds-proxy](01aurora.06pools-rds-proxy.md)

## 4. Deciding Variable

- For `min_capacity`: how cold a cache you tolerate at the first request after idle

**Catch**

- The repo has no code for this concept; it is pure infrastructure (Terraform)

## Related

- [00index](01aurora.00index.md)
- [01architecture](01aurora.01architecture.md)
