# 03db.04mongodb.13sharding Sharding

> Shard when one replica set cannot hold the data or the write rate; the shard key decides everything.

## Index

- [1. How It Works](#1-how-it-works)
- [2. Choosing A Shard Key](#2-choosing-a-shard-key)
- [Related](#related)

## 1. How It Works

A sharded cluster splits a collection into chunks by shard key and spreads them over replica sets.

- `mongos` routes each query; config servers hold the chunk map
- Query with the shard key ⇒ targeted to one shard; without it ⇒ scatter-gather to all
- The balancer moves chunks to even out data, not traffic

```text
app -> mongos -> config servers (chunk map)
          |
   +------+------+
   v      v      v
 shard1 shard2 shard3   each a replica set
```

The shard key routes every query, so most queries should include it.

## 2. Choosing A Shard Key

A good key has high cardinality, even frequency, and matches the common query.

- Monotonic key (timestamp, ObjectId) ⇒ every insert hits the last chunk = hot shard
- Hashed key ⇒ even writes, but range queries scatter
- Compound `{customerId: 1, createdAt: 1}` ⇒ targeted per-customer reads, spread writes
- Since 5.0 you can reshard; it copies the whole collection, so plan it like a migration

```java
// infra/_03db_04mongodb/MongoAdmin.java
// Shard orders on {customerId: 1, _id: 1}: tenant-targeted queries (customerId is in every hot query),
// and the _id suffix lets a whale customer's range split instead of forming a jumbo chunk.
// Run via mongos, once; resharding later (5.0+) rewrites the whole collection.
public Document shardOrdersCollection() {
    return client.getDatabase("admin").runCommand(new Document("shardCollection",
            db.getName() + "." + OrderDocuments.ORDERS)
            .append("key", new Document("customerId", 1).append("_id", 1)));
}
```

```python
# app/infra/_03db_04mongodb.py
def shard_orders_collection(self) -> Doc:
    """{customerId: 1, _id: 1}: tenant-targeted routing; the _id suffix keeps a whale splittable."""
    return get_client().admin.command(
        "shardCollection", f"{self.db.name}.{ORDERS}", key={"customerId": 1, "_id": 1}
    )
```

## Related

- [Index](04mongodb.00index.md)
- [Replica sets](04mongodb.10replica-sets-oplog.md)
- [Tradeoffs](04mongodb.98tradeoffs.md)
