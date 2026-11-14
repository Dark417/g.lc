# MongoDB Operations — mongosh, Python, Java/Spring Boot

> Version anchor: MongoDB server **8.0**, `mongosh` 2.x, **PyMongo 4.x**, **Java Driver 5.x**
> (`mongodb-driver-sync`), **Spring Boot 3.x / Spring Data MongoDB 4.x**. Companion to
> [1.mongodb.md](1.mongodb.md), which covers internals; this file is the "how do I actually type
> it" layer. Organised **by language**: §1 shared concepts and operator tables, then one full
> operations walkthrough each for §2 mongosh, §3 Python, §4 Java driver, §5 Spring Boot, then
> §6 shared reference (modeling, errors, testing, interview quick-fire).

---

## 1. Shared Concepts (read once, apply everywhere)

### 1.1 API Mental Model

```
                 mongosh                PyMongo                 Java driver           Spring Data MongoDB
                 ───────                ───────                 ───────────           ───────────────────
Connection       mongosh <uri>          MongoClient(uri)        MongoClients.create   spring.data.mongodb.uri
Database         db / use x             client["x"]             client.getDatabase    MongoTemplate (one db)
Collection       db.coll                db["coll"]              db.getCollection      @Document(collection=)
Filter           { a: 1 }               {"a": 1}                Filters.eq("a", 1)    Query(Criteria.where("a").is(1))
Update           { $set: {...} }        {"$set": {...}}         Updates.set(...)      Update().set(...)
Result           cursor / doc           Cursor / dict           FindIterable/Document  List<T> / T (mapped POJO)
```

- **Filter, update, projection and pipeline stages are all just BSON documents.** Anything that
  works in mongosh works verbatim as a Python `dict`, a Java `Document`, or a Spring
  `BasicQuery`. Typed builders (`Filters`, `Updates`, `Criteria`) add compile-time field names,
  nothing more.
- **`find` is lazy; `findOne` is eager.** A cursor runs on first iteration, fetches in batches
  (first batch 101 docs, later batches ≤ 16 MB), and the server cursor dies after 10 min idle.
- **Every write returns a result** with `matchedCount / modifiedCount / upsertedId / insertedId(s) /
  deletedCount`. `matched 1, modified 0` = document existed, update was a no-op.
- **`_id`** is always returned unless projected out (`{_id: 0}`) and immutable (code 66).

### 1.2 Connection String

```
mongodb+srv://user:pass@cluster0.abc.mongodb.net/mydb?retryWrites=true&w=majority&appName=svc
│            │         │                            │     └─ options (also settable in code)
│            │         │                            └─ default auth/target database
│            │         └─ SRV record → resolved to the seed list of hosts
│            └─ credentials (URL-encode @ : / ? # in passwords)
└─ +srv = DNS seedlist discovery; plain mongodb:// takes host:port[,host:port]
```

Options that matter: `maxPoolSize` (default **100**/host), `minPoolSize`, `connectTimeoutMS`
(10 s), `socketTimeoutMS`, `serverSelectionTimeoutMS` (**30 s** — what times out when there is no
primary), `readPreference`, `readConcernLevel`, `w`, `journal`, `retryWrites` (default true),
`retryReads`, `compressors=zstd,snappy`, `directConnection=true` (talk to one node only).

### 1.3 Query Operator Cheat Sheet

| Operator                                    | Meaning                                              |
| ------------------------------------------- | ---------------------------------------------------- |
| `$eq $ne $gt $gte $lt $lte $in $nin`        | comparison                                           |
| `$and $or $nor $not`                        | logical                                              |
| `$exists $type`                             | field presence / BSON type                           |
| `$regex` (+ `$options`)                     | regex; only anchored `^abc` prefixes use an index    |
| `$expr`                                     | aggregation expression in a filter (compare fields)  |
| `$all $size $elemMatch`                     | arrays; `$elemMatch` = conditions on the same element|
| `"a.b"` dot path                            | embedded field / array element field                 |
| `$text $geoWithin $near`                    | text / geo (need matching index)                     |
| `$jsonSchema`                               | validation-style match                               |

### 1.4 Update Operator Cheat Sheet

| Operator                              | Effect                                                                  |
| ------------------------------------- | ----------------------------------------------------------------------- |
| `$set` / `$unset`                     | set / remove fields                                                     |
| `$inc` / `$mul`                       | atomic add / multiply (`$inc` creates the field if absent)              |
| `$min` / `$max`                       | set only if new value is lower / higher                                 |
| `$rename`                             | rename field                                                            |
| `$setOnInsert`                        | apply only when the upsert inserts                                      |
| `$currentDate`                        | `{ f: true }` → Date; `{ f: { $type: "timestamp" } }`                   |
| `$push` / `$addToSet`                 | append / append-if-absent; modifiers `$each $slice $sort $position`     |
| `$pull` / `$pullAll` / `$pop`         | remove matching / remove listed / remove first (-1) or last (1)         |
| `arr.$`                               | first array element matched by the **query**                            |
| `arr.$[]`                             | every element                                                           |
| `arr.$[el]` + `arrayFilters`          | elements matching a named filter                                        |
| `[ {$set: ...}, ... ]` pipeline update| since 4.2 — expressions referencing other fields                        |

### 1.5 Aggregation Stage Cheat Sheet

| Stage                                            | Use                                                                          |
| ------------------------------------------------ | ---------------------------------------------------------------------------- |
| `$match`                                         | filter — put **first** so it can use an index                                |
| `$project` / `$addFields` (`$set`) / `$unset`    | reshape                                                                      |
| `$group`                                         | `_id` + accumulators `$sum $avg $min $max $first $last $push $addToSet $count`|
| `$sort` / `$limit` / `$skip`                     | `$sort`+`$limit` adjacent → memory-bounded top-k                             |
| `$unwind`                                        | one doc per array element; `preserveNullAndEmptyArrays`                      |
| `$lookup`                                        | left outer join; `let`/`pipeline` form for correlated subqueries             |
| `$facet`                                         | several sub-pipelines on one input (results + count + facets)                |
| `$bucket` / `$bucketAuto`                        | histogram                                                                    |
| `$setWindowFields`                               | 5.0+ running totals, rank, lag/lead                                          |
| `$graphLookup`                                   | recursive traversal                                                          |
| `$replaceRoot` / `$replaceWith`                  | promote a sub-document                                                       |
| `$count`                                         | terminal count                                                               |
| `$out` / `$merge`                                | materialise (`$merge` upserts, `$out` replaces)                              |
| `$unionWith` / `$sample` / `$densify` / `$fill`  | UNION ALL / random / time-series gap fill                                    |
| `$search` / `$vectorSearch`                      | Atlas only                                                                   |

Each stage has a **100 MB** limit; `allowDiskUse: true` spills (server default true since 6.0,
still pass it explicitly). Output docs ≤ 16 MB.

### 1.6 Index Types

| Type                    | Create option                                          | Notes                                              |
| ----------------------- | ------------------------------------------------------ | -------------------------------------------------- |
| single / compound       | `{ a: 1, b: -1 }`                                      | ESR order: Equality, Sort, Range                   |
| unique                  | `unique: true`                                         | 11000 on violation                                 |
| partial                 | `partialFilterExpression: {...}`                       | preferred over sparse                              |
| TTL                     | `expireAfterSeconds: n` on a Date field                | background thread once/min, primary only           |
| text                    | `{ f: "text" }`, `weights`                             | one per collection                                 |
| 2dsphere                | `{ loc: "2dsphere" }`                                  | GeoJSON                                            |
| wildcard                | `{ "meta.$**": 1 }`                                    | unknown/dynamic keys                               |
| hashed                  | `{ k: "hashed" }`                                      | shard keys                                         |
| collation               | `collation: { locale: "en", strength: 2 }`             | case-insensitive; query must use same collation    |
| hidden                  | `hidden: true`                                         | test dropping without dropping                     |

Index builds since 4.2 are non-blocking by default (`background` flag ignored).

### 1.7 Pagination Rule

`skip(N)` is O(N) per page. Use keyset pagination on `(sortKey, _id)` with a matching compound
index — the shape is shown in each language section.

### 1.8 Transactions Rule

Since 4.0 (RS) / 4.2 (sharded). Need a session, a replica set (single-node OK for dev),
**60 s** default lifetime. **Every operation inside must carry the session** or it silently runs
outside. Keep them short; retry on `TransientTransactionError` (code 112 `WriteConflict`).

---

## 2. mongosh (native shell)

### 2.1 Connect & Navigate

```javascript
mongosh "mongodb://localhost:27017/mydb"
mongosh "mongodb+srv://cluster0.abc.mongodb.net/mydb" --username user   // prompts for password
mongosh --eval 'db.users.countDocuments()' "mongodb://localhost/mydb"   // non-interactive
mongosh --file script.js

use mydb                        // switch db (created lazily on first write)
db ; show dbs ; show collections
db.getSiblingDB("other").users.findOne()
db.getMongo().setReadPref("secondaryPreferred")
```

### 2.2 Insert

```javascript
db.users.insertOne({ name: "Ana", email: "ana@x.io", age: 31, tags: ["a", "b"], createdAt: new Date() })
// { acknowledged: true, insertedId: ObjectId("...") }

db.users.insertMany([{ name: "Bo" }, { name: "Cy" }, { name: "Di" }], { ordered: false })
// ordered:false keeps going past a failing doc; ordered:true (default) stops but EARLIER docs persist
```

### 2.3 Find

```javascript
db.users.findOne({ email: "ana@x.io" })
db.users.find({ age: { $gte: 30 }, status: "active" })
  .projection({ name: 1, email: 1, _id: 0 })
  .sort({ age: -1, _id: 1 })                     // tiebreaker for stable ordering
  .skip(20).limit(10)

db.users.find({ "address.city": "Austin" })
db.users.find({ tags: "a" })                                  // array contains
db.users.find({ tags: { $all: ["a", "b"] } })
db.users.find({ age: { $in: [30, 31] }, name: /^an/i })
db.users.find({ $or: [{ age: { $lt: 18 } }, { age: { $gt: 65 } }] })
db.users.find({ phone: { $exists: false } })
db.users.find({ $expr: { $gt: ["$spent", "$budget"] } })
db.users.find({ items: { $elemMatch: { qty: { $gt: 5 }, price: { $lt: 10 } } } })

db.users.countDocuments({ status: "active" })   // accurate
db.users.estimatedDocumentCount()               // metadata, O(1)
db.users.distinct("status", { age: { $gt: 20 } })
db.users.find(q).maxTimeMS(2000)

// keyset pagination (index { userId: 1, createdAt: -1, _id: -1 })
db.orders.find({ userId: u,
  $or: [ { createdAt: { $lt: lastCreatedAt } },
         { createdAt: lastCreatedAt, _id: { $lt: lastId } } ] })
  .sort({ createdAt: -1, _id: -1 }).limit(20)
```

### 2.4 Update

```javascript
db.users.updateOne({ _id: id }, { $set: { status: "active" }, $inc: { logins: 1 },
                                 $currentDate: { updatedAt: true } })
// { acknowledged, matchedCount: 1, modifiedCount: 1, upsertedId: null }

db.users.updateMany({ status: "trial", createdAt: { $lt: cutoff } }, { $set: { status: "expired" } })

// upsert
db.counters.updateOne({ _id: "orderSeq" },
  { $inc: { seq: 1 }, $setOnInsert: { createdAt: new Date() } }, { upsert: true })

// arrays
db.users.updateOne({ _id: id }, { $push: { tags: { $each: ["x", "y"], $slice: -50 } } })
db.users.updateOne({ _id: id }, { $addToSet: { tags: "z" } })
db.users.updateOne({ _id: id }, { $pull: { tags: { $in: ["x"] } } })
db.orders.updateOne({ _id: id, "items.sku": "A1" }, { $inc: { "items.$.qty": 1 } })   // positional needs array in filter
db.orders.updateOne({ _id: id }, { $set: { "items.$[i].shipped": true } },
                    { arrayFilters: [{ "i.qty": { $gt: 0 } }] })

// pipeline update — compute from other fields
db.orders.updateMany({}, [{ $set: { total: { $multiply: ["$qty", "$price"] } } }])

// replace whole doc (keeps _id)
db.users.replaceOne({ _id: id }, { name: "Ana", email: "ana@x.io" })

// atomic read-modify-write
db.counters.findOneAndUpdate({ _id: "orderSeq" }, { $inc: { seq: 1 } },
                             { upsert: true, returnNewDocument: true })
db.jobs.findOneAndUpdate({ status: "queued" }, { $set: { status: "running", worker: me } },
                         { sort: { priority: -1, _id: 1 }, returnDocument: "after" })   // job claim

// optimistic lock by hand
db.accounts.updateOne({ _id: id, version: 7 }, { $set: { balance: 90 }, $inc: { version: 1 } })
// matchedCount 0 ⇒ someone else won; re-read and retry
```

### 2.5 Delete

```javascript
db.users.deleteOne({ _id: id })                 // { deletedCount: 1 }
db.users.deleteMany({ status: "expired" })
db.jobs.findOneAndDelete({ status: "done" }, { sort: { finishedAt: 1 } })
db.users.drop()                                 // O(1), also drops indexes
db.dropDatabase()
// soft delete
db.users.updateOne({ _id: id }, { $set: { deletedAt: new Date() } })
```

### 2.6 Indexes & explain

```javascript
db.users.createIndex({ email: 1 }, { unique: true, name: "uq_email" })
db.orders.createIndex({ userId: 1, createdAt: -1 })
db.users.createIndex({ email: 1 }, { unique: true, partialFilterExpression: { deletedAt: { $exists: false } } })
db.sessions.createIndex({ lastSeen: 1 }, { expireAfterSeconds: 3600 })
db.articles.createIndex({ title: "text", body: "text" }, { weights: { title: 10 } })
db.places.createIndex({ loc: "2dsphere" })
db.events.createIndex({ "meta.$**": 1 })
db.users.createIndex({ email: 1 }, { collation: { locale: "en", strength: 2 } })
db.big.createIndex({ k: 1 }, { hidden: true })

db.users.getIndexes()
db.users.dropIndex("uq_email") ; db.users.dropIndexes()
db.users.totalIndexSize()
db.users.aggregate([{ $indexStats: {} }])       // accesses.ops == 0 → unused

db.orders.find({ userId: u, status: "paid" }).sort({ createdAt: -1 }).explain("executionStats")
// winningPlan.stage: IXSCAN good / COLLSCAN bad; SORT stage = in-memory sort
// totalKeysExamined : totalDocsExamined : nReturned  → ideal ≈ 1:1:1; PROJECTION_COVERED = covered
db.orders.find(q).hint({ userId: 1, createdAt: -1 })
db.orders.find(q).hint({ $natural: 1 })          // force collscan
```

### 2.7 Aggregation

```javascript
// revenue per customer, top 10, with customer name
db.orders.aggregate([
  { $match: { status: "paid", createdAt: { $gte: ISODate("2026-01-01") } } },
  { $unwind: "$items" },
  { $group: { _id: "$customerId",
              revenue: { $sum: { $multiply: ["$items.qty", "$items.price"] } },
              orders:  { $addToSet: "$_id" } } },
  { $addFields: { orderCount: { $size: "$orders" } } },
  { $sort: { revenue: -1 } }, { $limit: 10 },
  { $lookup: { from: "customers", localField: "_id", foreignField: "_id", as: "customer" } },
  { $unwind: { path: "$customer", preserveNullAndEmptyArrays: true } },
  { $project: { _id: 0, customerId: "$_id", name: "$customer.name", revenue: 1, orderCount: 1 } }
], { allowDiskUse: true })

// correlated $lookup
{ $lookup: { from: "orders", let: { cid: "$_id" },
    pipeline: [ { $match: { $expr: { $and: [ { $eq: ["$customerId", "$$cid"] }, { $eq: ["$status", "paid"] } ] } } },
                { $sort: { createdAt: -1 } }, { $limit: 3 } ],
    as: "recentOrders" } }

// $facet search page
db.products.aggregate([
  { $match: { category: "shoes" } },
  { $facet: { results: [ { $sort: { price: 1 } }, { $skip: 0 }, { $limit: 20 } ],
              total:   [ { $count: "n" } ],
              byBrand: [ { $group: { _id: "$brand", n: { $sum: 1 } } } ] } }
])

// window function
{ $setWindowFields: { partitionBy: "$customerId", sortBy: { createdAt: 1 },
    output: { runningTotal: { $sum: "$total", window: { documents: ["unbounded", "current"] } } } } }

// materialise
{ $merge: { into: "customer_revenue", on: "_id", whenMatched: "replace", whenNotMatched: "insert" } }
```

### 2.8 Transactions

```javascript
const session = db.getMongo().startSession()
session.startTransaction({ readConcern: { level: "snapshot" }, writeConcern: { w: "majority" } })
try {
  const accts = session.getDatabase("bank").accounts       // ops via the session-bound db
  accts.updateOne({ _id: "A", balance: { $gte: 100 } }, { $inc: { balance: -100 } })
  accts.updateOne({ _id: "B" }, { $inc: { balance: 100 } })
  session.commitTransaction()
} catch (e) { session.abortTransaction(); throw e } finally { session.endSession() }
```

### 2.9 Bulk Write

```javascript
db.users.bulkWrite([
  { insertOne:  { document: { name: "E" } } },
  { updateOne:  { filter: { _id: 1 }, update: { $set: { a: 1 } }, upsert: true } },
  { updateMany: { filter: { status: "x" }, update: { $set: { status: "y" } } } },
  { replaceOne: { filter: { _id: 2 }, replacement: { name: "F" } } },
  { deleteOne:  { filter: { _id: 3 } } },
], { ordered: false })
// { insertedCount, matchedCount, modifiedCount, deletedCount, upsertedCount, upsertedIds }
```

### 2.10 Change Streams

```javascript
const cs = db.orders.watch(
  [{ $match: { operationType: { $in: ["insert", "update"] }, "fullDocument.status": "paid" } }],
  { fullDocument: "updateLookup" })
while (cs.hasNext()) { const ev = cs.next(); printjson(ev) /* persist ev._id as resume token */ }
db.orders.watch(pipeline, { resumeAfter: savedToken })       // or { startAtOperationTime: ts }
```

### 2.11 Consistency Knobs

```javascript
db.orders.insertOne(doc, { writeConcern: { w: "majority", j: true, wtimeout: 5000 } })
db.orders.find(q).readConcern("majority")
db.orders.find(q).readPref("secondaryPreferred", [{ region: "us-east" }])
// causal session
const s = db.getMongo().startSession({ causalConsistency: true })
```

### 2.12 Schema Validation, Collections, Admin

```javascript
db.createCollection("users", { validator: { $jsonSchema: {
    bsonType: "object", required: ["email", "createdAt"],
    properties: { email: { bsonType: "string", pattern: "^.+@.+$" }, age: { bsonType: "int", minimum: 0 } } } },
  validationLevel: "moderate", validationAction: "error" })
db.runCommand({ collMod: "users", validator: {...} })

db.createCollection("logs", { capped: true, size: 1e9, max: 1e6 })
db.createCollection("metrics", { timeseries: { timeField: "ts", metaField: "meta", granularity: "minutes" },
                                 expireAfterSeconds: 86400 * 30 })
db.users.renameCollection("people")
db.users.stats() ; db.stats()
db.currentOp({ active: true, secs_running: { $gt: 5 } }) ; db.killOp(opid)
db.serverStatus().connections ; db.serverStatus().wiredTiger.cache
rs.status() ; rs.conf() ; rs.printSecondaryReplicationInfo()
sh.status() ; sh.shardCollection("mydb.orders", { customerId: "hashed" })
db.setProfilingLevel(1, { slowms: 100 }) ; db.system.profile.find().sort({ ts: -1 }).limit(5)
db.createUser({ user: "svc", pwd: passwordPrompt(), roles: [{ role: "readWrite", db: "mydb" }] })
```

---

## 3. Python (PyMongo)

### 3.1 Connect

```python
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.server_api import ServerApi

client = MongoClient(
    "mongodb+srv://user:pass@cluster0.abc.mongodb.net/?retryWrites=true&w=majority",
    server_api=ServerApi("1"),          # Stable API
    maxPoolSize=50, serverSelectionTimeoutMS=5000, appname="orders-svc",
)
db = client["mydb"]
users = db["users"]
client.admin.command("ping")
```

- **One `MongoClient` per process** — thread-safe, owns the pool. Per-request clients are the #1
  PyMongo perf bug.
- **Not fork-safe**: with gunicorn/uWSGI pre-fork create it *after* fork (worker-init hook).
- Async: `motor.motor_asyncio.AsyncIOMotorClient`, or PyMongo 4.9+ `pymongo.AsyncMongoClient`;
  same method names with `await`.
- Dates: always timezone-aware `datetime` (`tz_aware=True` on the client to get them back aware).

### 3.2 Insert

```python
res = users.insert_one({"name": "Ana", "email": "ana@x.io", "age": 31, "tags": ["a", "b"],
                        "created_at": datetime.now(timezone.utc)})
res.inserted_id                      # ObjectId — your dict is ALSO mutated to include "_id"

res = users.insert_many([{"name": "Bo"}, {"name": "Cy"}], ordered=False)
res.inserted_ids                     # list[ObjectId]
```

### 3.3 Find

```python
users.find_one({"email": "ana@x.io"})                              # dict | None
cursor = (users.find({"age": {"$gte": 30}, "status": "active"},
                     {"name": 1, "email": 1, "_id": 0})            # projection = 2nd positional
               .sort([("age", DESCENDING), ("_id", ASCENDING)])   # list of tuples, not dict
               .skip(20).limit(10)
               .max_time_ms(2000))
docs = list(cursor)

users.find({"address.city": "Austin"})
users.find({"tags": {"$all": ["a", "b"]}})
users.find({"name": {"$regex": "^an", "$options": "i"}})           # or re.compile(...)
users.find({"$or": [{"age": {"$lt": 18}}, {"age": {"$gt": 65}}]})
users.find({"items": {"$elemMatch": {"qty": {"$gt": 5}, "price": {"$lt": 10}}}})
users.count_documents({"status": "active"})
users.estimated_document_count()
users.distinct("status", {"age": {"$gt": 20}})

# large scans
for doc in users.find(q, batch_size=1000): ...
with users.find(q, no_cursor_timeout=True) as cur:   # MUST close → context manager
    ...

# keyset pagination
q = {"userId": u, "$or": [{"createdAt": {"$lt": last_ts}},
                          {"createdAt": last_ts, "_id": {"$lt": last_id}}]}
orders.find(q).sort([("createdAt", -1), ("_id", -1)]).limit(20)
```

### 3.4 Update

```python
from pymongo import ReturnDocument

r = users.update_one({"_id": id}, {"$set": {"status": "active"}, "$inc": {"logins": 1},
                                   "$currentDate": {"updated_at": True}})
r.matched_count, r.modified_count, r.upserted_id

users.update_many({"status": "trial"}, {"$set": {"status": "expired"}})
counters.update_one({"_id": "orderSeq"}, {"$inc": {"seq": 1}, "$setOnInsert": {"created_at": now}}, upsert=True)

users.update_one({"_id": id}, {"$push": {"tags": {"$each": ["x", "y"], "$slice": -50}}})
users.update_one({"_id": id}, {"$addToSet": {"tags": "z"}})
users.update_one({"_id": id}, {"$pull": {"tags": {"$in": ["x"]}}})
orders.update_one({"_id": id, "items.sku": "A1"}, {"$inc": {"items.$.qty": 1}})
orders.update_one({"_id": id}, {"$set": {"items.$[i].shipped": True}},
                  array_filters=[{"i.qty": {"$gt": 0}}])
orders.update_many({}, [{"$set": {"total": {"$multiply": ["$qty", "$price"]}}}])   # pipeline update
users.replace_one({"_id": id}, {"name": "Ana", "email": "ana@x.io"})

doc = counters.find_one_and_update({"_id": "orderSeq"}, {"$inc": {"seq": 1}},
                                   upsert=True, return_document=ReturnDocument.AFTER)
job = jobs.find_one_and_update({"status": "queued"},
                               {"$set": {"status": "running", "worker": me}},
                               sort=[("priority", -1), ("_id", 1)],
                               return_document=ReturnDocument.AFTER)      # None if nothing queued

# optimistic lock
r = accounts.update_one({"_id": id, "version": v}, {"$set": {"balance": nb}, "$inc": {"version": 1}})
if r.matched_count == 0: raise ConcurrentModification()
```

### 3.5 Delete

```python
users.delete_one({"_id": id}).deleted_count
users.delete_many({"status": "expired"})
jobs.find_one_and_delete({"status": "done"}, sort=[("finishedAt", 1)])
users.drop()
client.drop_database("mydb")
```

### 3.6 Indexes & explain

```python
from pymongo import IndexModel, TEXT
users.create_index([("email", ASCENDING)], unique=True, name="uq_email")
orders.create_index([("userId", ASCENDING), ("createdAt", DESCENDING)])
users.create_index("email", unique=True, partialFilterExpression={"deletedAt": {"$exists": False}})
sessions.create_index("lastSeen", expireAfterSeconds=3600)
articles.create_index([("title", TEXT), ("body", TEXT)], weights={"title": 10})
places.create_index([("loc", "2dsphere")])
users.create_index("email", collation={"locale": "en", "strength": 2})
users.create_indexes([IndexModel([("a", 1)]), IndexModel([("b", 1), ("c", -1)], name="b_c")])

users.index_information()
users.drop_index("uq_email")
list(users.aggregate([{"$indexStats": {}}]))

orders.find(q).sort(s).explain()
db.command("explain", {"find": "orders", "filter": q, "sort": s}, verbosity="executionStats")
orders.find(q).hint([("userId", 1), ("createdAt", -1)])
```

### 3.7 Aggregation

```python
pipeline = [
    {"$match": {"status": "paid", "createdAt": {"$gte": datetime(2026, 1, 1, tzinfo=timezone.utc)}}},
    {"$unwind": "$items"},
    {"$group": {"_id": "$customerId",
                "revenue": {"$sum": {"$multiply": ["$items.qty", "$items.price"]}},
                "orders": {"$addToSet": "$_id"}}},
    {"$addFields": {"orderCount": {"$size": "$orders"}}},
    {"$sort": {"revenue": -1}}, {"$limit": 10},
    {"$lookup": {"from": "customers", "localField": "_id", "foreignField": "_id", "as": "customer"}},
    {"$unwind": {"path": "$customer", "preserveNullAndEmptyArrays": True}},
    {"$project": {"_id": 0, "customerId": "$_id", "name": "$customer.name", "revenue": 1, "orderCount": 1}},
]
rows = list(orders.aggregate(pipeline, allowDiskUse=True))

# $facet / $setWindowFields / $merge — identical dicts to the mongosh forms in §2.7
```

Pipelines are lists of dicts: keep them as module constants or builder functions, and test against
a real `mongod` (Testcontainers) — `mongomock` does not faithfully run aggregation.

### 3.8 Transactions

```python
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from pymongo import ReadPreference

def transfer(session):
    accts = session.client.bank.accounts
    r = accts.update_one({"_id": "A", "balance": {"$gte": 100}}, {"$inc": {"balance": -100}}, session=session)
    if r.matched_count == 0:
        raise ValueError("insufficient funds")            # non-Mongo exception → abort, no retry
    accts.update_one({"_id": "B"}, {"$inc": {"balance": 100}}, session=session)

with client.start_session() as s:
    s.with_transaction(transfer,                          # retries TransientTransactionError /
                       read_concern=ReadConcern("snapshot"),   # UnknownTransactionCommitResult
                       write_concern=WriteConcern("majority"),
                       read_preference=ReadPreference.PRIMARY)

# manual form
with client.start_session() as s:
    with s.start_transaction():
        coll.insert_one(doc, session=s)      # forgetting session= silently escapes the txn
```

### 3.9 Bulk Write

```python
from pymongo import InsertOne, UpdateOne, UpdateMany, ReplaceOne, DeleteOne
from pymongo.errors import BulkWriteError
ops = [InsertOne({"name": "E"}),
       UpdateOne({"_id": 1}, {"$set": {"a": 1}}, upsert=True),
       UpdateMany({"status": "x"}, {"$set": {"status": "y"}}),
       ReplaceOne({"_id": 2}, {"name": "F"}),
       DeleteOne({"_id": 3})]
try:
    r = users.bulk_write(ops, ordered=False)
    r.bulk_api_result
except BulkWriteError as e:
    e.details["writeErrors"]         # per-op index + code; successful ops are NOT rolled back
```

### 3.10 Change Streams

```python
pipeline = [{"$match": {"operationType": {"$in": ["insert", "update"]}}}]
with orders.watch(pipeline, full_document="updateLookup", resume_after=load_token()) as stream:
    for ev in stream:                       # blocks
        handle(ev)
        save_token(stream.resume_token)     # persist AFTER handling → at-least-once
```

### 3.11 Consistency Knobs

```python
coll = db.get_collection("orders",
        write_concern=WriteConcern(w="majority", wtimeout=5000, j=True),
        read_concern=ReadConcern("majority"),
        read_preference=ReadPreference.SECONDARY_PREFERRED)
coll = orders.with_options(read_preference=ReadPreference.NEAREST)   # per-call variant

with client.start_session(causal_consistency=True) as s:             # read your own writes on a secondary
    orders.insert_one(doc, session=s)
    orders.with_options(read_preference=ReadPreference.SECONDARY).find_one({"_id": doc["_id"]}, session=s)
```

### 3.12 Schema Validation, Collections, Admin

```python
db.create_collection("users", validator={"$jsonSchema": {...}}, validationLevel="moderate")
db.command("collMod", "users", validator={...})
db.create_collection("metrics", timeseries={"timeField": "ts", "metaField": "meta"}, expireAfterSeconds=86400*30)
db.create_collection("logs", capped=True, size=10**9)
users.rename("people")
db.command("collStats", "users") ; db.command("dbStats")
db.command("currentOp", active=True) ; db.command("killOp", op=opid)
client.admin.command("replSetGetStatus")
db.command("profile", 1, slowms=100)
```

### 3.13 Errors

```python
from pymongo.errors import (DuplicateKeyError, WriteError, BulkWriteError, OperationFailure,
                            ServerSelectionTimeoutError, AutoReconnect, NetworkTimeout,
                            ExecutionTimeout, CursorNotFound, NotPrimaryError)
try:
    users.insert_one(doc)
except DuplicateKeyError as e:
    e.details["keyValue"]                 # which unique key collided
except OperationFailure as e:
    e.code, e.details, e.has_error_label("TransientTransactionError")
```

---

## 4. Java (MongoDB Java Driver)

### 4.1 Connect

```java
// org.mongodb:mongodb-driver-sync:5.x   (reactive: mongodb-driver-reactivestreams)
import com.mongodb.*;
import com.mongodb.client.*;
import com.mongodb.client.model.*;
import com.mongodb.client.result.*;
import org.bson.Document;
import static com.mongodb.client.model.Filters.*;
import static com.mongodb.client.model.Updates.*;
import static com.mongodb.client.model.Projections.*;
import static com.mongodb.client.model.Sorts.*;
import static com.mongodb.client.model.Indexes.*;
import static com.mongodb.client.model.Aggregates.*;
import static com.mongodb.client.model.Accumulators.*;

MongoClientSettings settings = MongoClientSettings.builder()
    .applyConnectionString(new ConnectionString("mongodb+srv://user:pass@cluster0.abc.mongodb.net/"))
    .serverApi(ServerApi.builder().version(ServerApiVersion.V1).build())
    .applyToConnectionPoolSettings(b -> b.maxSize(50).maxWaitTime(5, TimeUnit.SECONDS))
    .applyToClusterSettings(b -> b.serverSelectionTimeout(5, TimeUnit.SECONDS))
    .retryWrites(true)
    .build();

MongoClient client = MongoClients.create(settings);             // singleton, thread-safe
MongoDatabase db = client.getDatabase("mydb");
MongoCollection<Document> users = db.getCollection("users");
db.runCommand(new Document("ping", 1));

// POJO mapping without Spring
CodecRegistry pojo = fromRegistries(MongoClientSettings.getDefaultCodecRegistry(),
        fromProviders(PojoCodecProvider.builder().automatic(true).build()));
MongoCollection<User> typed = db.withCodecRegistry(pojo).getCollection("users", User.class);
```

### 4.2 Insert

```java
InsertOneResult r = users.insertOne(new Document("name", "Ana").append("email", "ana@x.io")
        .append("age", 31).append("tags", List.of("a", "b")).append("createdAt", Instant.now()));
ObjectId id = r.getInsertedId().asObjectId().getValue();

InsertManyResult m = users.insertMany(List.of(new Document("name", "Bo"), new Document("name", "Cy")),
        new InsertManyOptions().ordered(false));
m.getInsertedIds();
```

### 4.3 Find

```java
Document one = users.find(eq("email", "ana@x.io")).first();          // null if none
List<Document> page = users.find(and(gte("age", 30), eq("status", "active")))
        .projection(fields(include("name", "email"), excludeId()))
        .sort(orderBy(descending("age"), ascending("_id")))
        .skip(20).limit(10)
        .maxTime(2, TimeUnit.SECONDS)
        .into(new ArrayList<>());

users.find(eq("address.city", "Austin"));
users.find(all("tags", "a", "b"));
users.find(regex("name", "^an", "i"));
users.find(or(lt("age", 18), gt("age", 65)));
users.find(exists("phone", false));
users.find(expr(new Document("$gt", List.of("$spent", "$budget"))));
users.find(elemMatch("items", and(gt("qty", 5), lt("price", 10))));
users.countDocuments(eq("status", "active"));
users.estimatedDocumentCount();
users.distinct("status", gt("age", 20), String.class).into(new ArrayList<>());

// raw BSON — identical semantics
users.find(Document.parse("{ age: { $gte: 30 }, status: 'active' }"));

// always close cursors you may not exhaust
try (MongoCursor<Document> c = users.find(f).batchSize(1000).iterator()) { while (c.hasNext()) {...} }

// keyset pagination
orders.find(and(eq("userId", u), or(lt("createdAt", lastTs), and(eq("createdAt", lastTs), lt("_id", lastId)))))
      .sort(orderBy(descending("createdAt"), descending("_id"))).limit(20);
```

### 4.4 Update

```java
UpdateResult r = users.updateOne(eq("_id", id),
        combine(set("status", "active"), inc("logins", 1), currentDate("updatedAt")));
r.getMatchedCount(); r.getModifiedCount(); r.getUpsertedId();

users.updateMany(eq("status", "trial"), set("status", "expired"));
counters.updateOne(eq("_id", "orderSeq"), combine(inc("seq", 1), setOnInsert("createdAt", Instant.now())),
                   new UpdateOptions().upsert(true));

users.updateOne(eq("_id", id), pushEach("tags", List.of("x", "y"), new PushOptions().slice(-50)));
users.updateOne(eq("_id", id), addToSet("tags", "z"));
users.updateOne(eq("_id", id), pull("tags", "x"));
orders.updateOne(and(eq("_id", id), eq("items.sku", "A1")), inc("items.$.qty", 1));
orders.updateOne(eq("_id", id), set("items.$[i].shipped", true),
                 new UpdateOptions().arrayFilters(List.of(gt("i.qty", 0))));
orders.updateMany(new Document(), List.of(new Document("$set",
        new Document("total", new Document("$multiply", List.of("$qty", "$price"))))));   // pipeline update
users.replaceOne(eq("_id", id), new Document("name", "Ana").append("email", "ana@x.io"));

Document after = counters.findOneAndUpdate(eq("_id", "orderSeq"), inc("seq", 1),
        new FindOneAndUpdateOptions().upsert(true).returnDocument(ReturnDocument.AFTER));
Document job = jobs.findOneAndUpdate(eq("status", "queued"),
        combine(set("status", "running"), set("worker", me)),
        new FindOneAndUpdateOptions().sort(orderBy(descending("priority"), ascending("_id")))
                                     .returnDocument(ReturnDocument.AFTER));

// optimistic lock
if (accounts.updateOne(and(eq("_id", id), eq("version", v)),
        combine(set("balance", nb), inc("version", 1))).getMatchedCount() == 0) throw new ConcurrentModificationException();
```

### 4.5 Delete

```java
DeleteResult d = users.deleteOne(eq("_id", id));  d.getDeletedCount();
users.deleteMany(eq("status", "expired"));
jobs.findOneAndDelete(eq("status", "done"), new FindOneAndDeleteOptions().sort(ascending("finishedAt")));
users.drop();  db.drop();
```

### 4.6 Indexes & explain

```java
users.createIndex(ascending("email"), new IndexOptions().unique(true).name("uq_email"));
orders.createIndex(compoundIndex(ascending("userId"), descending("createdAt")));
users.createIndex(ascending("email"), new IndexOptions().unique(true).partialFilterExpression(exists("deletedAt", false)));
sessions.createIndex(ascending("lastSeen"), new IndexOptions().expireAfter(1L, TimeUnit.HOURS));
articles.createIndex(compoundIndex(text("title"), text("body")), new IndexOptions().weights(new Document("title", 10)));
places.createIndex(geo2dsphere("loc"));
users.createIndex(ascending("email"), new IndexOptions().collation(Collation.builder().locale("en").collationStrength(CollationStrength.SECONDARY).build()));
users.createIndexes(List.of(new IndexModel(ascending("a")), new IndexModel(compoundIndex(ascending("b"), descending("c")))));

users.listIndexes().forEach(d -> System.out.println(d.toJson()));
users.dropIndex("uq_email");
users.aggregate(List.of(new Document("$indexStats", new Document())));

Document plan = orders.find(f).sort(s).explain(ExplainVerbosity.EXECUTION_STATS);
orders.find(f).hint(compoundIndex(ascending("userId"), descending("createdAt")));
```

### 4.7 Aggregation

```java
List<Document> rows = orders.aggregate(List.of(
    match(and(eq("status", "paid"), gte("createdAt", since))),
    unwind("$items"),
    group("$customerId",
          sum("revenue", new Document("$multiply", List.of("$items.qty", "$items.price"))),
          addToSet("orders", "$_id")),
    addFields(new Field<>("orderCount", new Document("$size", "$orders"))),
    sort(descending("revenue")),
    limit(10),
    lookup("customers", "_id", "_id", "customer"),
    unwind("$customer", new UnwindOptions().preserveNullAndEmptyArrays(true)),
    project(fields(excludeId(), computed("customerId", "$_id"), computed("name", "$customer.name"),
                   include("revenue", "orderCount")))
)).allowDiskUse(true).into(new ArrayList<>());

// correlated lookup / facet / window — mix builders and Document.parse freely
lookup("orders", List.of(new Variable<>("cid", "$_id")),
       List.of(match(expr(new Document("$eq", List.of("$customerId", "$$cid")))), sort(descending("createdAt")), limit(3)),
       "recentOrders");
facet(new Facet("results", sort(ascending("price")), limit(20)), new Facet("total", count("n")));
Document.parse("{ $setWindowFields: { partitionBy: '$customerId', sortBy: { createdAt: 1 }, output: { runningTotal: { $sum: '$total', window: { documents: ['unbounded','current'] } } } } }");
merge("customer_revenue", new MergeOptions().whenMatched(MergeOptions.WhenMatched.REPLACE));
```

### 4.8 Transactions

```java
try (ClientSession session = client.startSession()) {
    session.withTransaction(() -> {                                  // retries transient errors
        MongoCollection<Document> accts = client.getDatabase("bank").getCollection("accounts");
        UpdateResult r = accts.updateOne(session, and(eq("_id", "A"), gte("balance", 100)), inc("balance", -100));
        if (r.getMatchedCount() == 0) throw new IllegalStateException("insufficient funds");
        accts.updateOne(session, eq("_id", "B"), inc("balance", 100));   // session is ALWAYS the 1st arg
        return null;
    }, TransactionOptions.builder().readConcern(ReadConcern.SNAPSHOT).writeConcern(WriteConcern.MAJORITY).build());
}
// manual: session.startTransaction(); ... session.commitTransaction() / abortTransaction()
```

### 4.9 Bulk Write

```java
BulkWriteResult r = users.bulkWrite(List.of(
    new InsertOneModel<>(new Document("name", "E")),
    new UpdateOneModel<>(eq("_id", 1), set("a", 1), new UpdateOptions().upsert(true)),
    new UpdateManyModel<>(eq("status", "x"), set("status", "y")),
    new ReplaceOneModel<>(eq("_id", 2), new Document("name", "F")),
    new DeleteOneModel<>(eq("_id", 3))
), new BulkWriteOptions().ordered(false));
// catch MongoBulkWriteException → getWriteErrors(), getWriteResult()
```

### 4.10 Change Streams

```java
ChangeStreamIterable<Document> cs = orders.watch(List.of(match(in("operationType", "insert", "update"))))
        .fullDocument(FullDocument.UPDATE_LOOKUP).resumeAfter(savedToken);
try (MongoCursor<ChangeStreamDocument<Document>> it = cs.iterator()) {
    while (it.hasNext()) {
        ChangeStreamDocument<Document> ev = it.next();
        handle(ev.getFullDocument());
        save(ev.getResumeToken());
    }
}
```

### 4.11 Consistency Knobs

```java
MongoCollection<Document> c = orders
    .withWriteConcern(WriteConcern.MAJORITY.withWTimeout(5, TimeUnit.SECONDS).withJournal(true))
    .withReadConcern(ReadConcern.MAJORITY)
    .withReadPreference(ReadPreference.secondaryPreferred(new TagSet(new Tag("region", "us-east"))));
ClientSession s = client.startSession(ClientSessionOptions.builder().causallyConsistent(true).build());
```

### 4.12 Schema Validation, Collections, Admin

```java
db.createCollection("users", new CreateCollectionOptions().validationOptions(
        new ValidationOptions().validator(Document.parse("{ $jsonSchema: {...} }"))
                               .validationLevel(ValidationLevel.MODERATE).validationAction(ValidationAction.ERROR)));
db.runCommand(new Document("collMod", "users").append("validator", ...));
db.createCollection("metrics", new CreateCollectionOptions()
        .timeSeriesOptions(new TimeSeriesOptions("ts").metaField("meta")).expireAfter(30, TimeUnit.DAYS));
db.createCollection("logs", new CreateCollectionOptions().capped(true).sizeInBytes(1_000_000_000L));
users.renameCollection(new MongoNamespace("mydb", "people"));
db.runCommand(new Document("collStats", "users"));
db.runCommand(new Document("currentOp", 1).append("active", true));
client.getDatabase("admin").runCommand(new Document("replSetGetStatus", 1));
```

### 4.13 Errors

```java
try { users.insertOne(doc); }
catch (MongoWriteException e) {
    if (e.getError().getCategory() == ErrorCategory.DUPLICATE_KEY) { ... }     // 11000
}
catch (MongoCommandException e)          { e.getErrorCode(); e.hasErrorLabel("TransientTransactionError"); }
catch (MongoExecutionTimeoutException e) { /* maxTime exceeded, code 50 */ }
catch (MongoTimeoutException e)          { /* no server selectable */ }
catch (MongoSocketException e)           { /* network */ }
catch (MongoBulkWriteException e)        { e.getWriteErrors(); }
```

---

## 5. Spring Boot (Spring Data MongoDB)

### 5.1 Setup & Mapping

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-data-mongodb</artifactId>       <!-- or -reactive -->
</dependency>
```

```yaml
spring:
  data:
    mongodb:
      uri: mongodb+srv://user:pass@cluster0.abc.mongodb.net/mydb?retryWrites=true&w=majority
      auto-index-creation: false     # default; create indexes explicitly (§5.6)
```

```java
@Configuration
class MongoConfig {
    @Bean MongoClientSettingsBuilderCustomizer pool() {                        // tune beyond the URI
        return b -> b.applyToConnectionPoolSettings(p -> p.maxSize(50).maxWaitTime(5, SECONDS));
    }
    @Bean MongoTransactionManager transactionManager(MongoDatabaseFactory f) { // NOT auto-configured
        return new MongoTransactionManager(f);
    }
    // drop the _class discriminator field if you don't want it in documents
    @Bean MappingMongoConverter converter(MongoDatabaseFactory f, MongoMappingContext ctx) {
        var c = new MappingMongoConverter(new DefaultDbRefResolver(f), ctx);
        c.setTypeMapper(new DefaultMongoTypeMapper(null));
        return c;
    }
}
```

```java
@Document(collection = "users")
public class User {
    @Id private String id;                       // String ↔ ObjectId auto-converted
    @Indexed(unique = true) private String email;
    private String name;
    private int age;
    @Field("created_at") private Instant createdAt;
    private List<String> tags;
    private Address address;                     // embedded, no annotation needed
    private String teamId;                       // store the id; avoid @DBRef (N+1, proxies)
    @DocumentReference(lazy = true) private Team team;   // sane alternative if you want mapping help
    @Version private Long version;               // optimistic locking
    @Transient private String computed;
}
```

Two access styles, both auto-configured:

```java
public interface UserRepository extends MongoRepository<User, String> {        // (a) repository
    Optional<User> findByEmail(String email);
    List<User> findByAgeGreaterThanAndStatus(int age, String status);
    List<User> findTop5ByStatusOrderByAgeDesc(String status);
    Page<User> findByStatus(String status, Pageable pageable);
    Slice<User> findByStatusAndAgeGreaterThan(String status, int age, Pageable p);   // no count query
    boolean existsByEmail(String email);
    long deleteByStatus(String status);
    @Query("{ 'tags': { $in: ?0 } }") List<User> findByAnyTag(List<String> tags);
    @Query(value = "{ 'status': ?0 }", fields = "{ 'email': 1, 'name': 1 }") List<User> emailsByStatus(String s);
    @Query(value = "{ 'status': ?0 }", sort = "{ 'age': -1 }") List<User> byStatusOldestFirst(String s);
    @Aggregation(pipeline = { "{ $match: { status: ?0 } }", "{ $group: { _id: null, n: { $sum: 1 } } }" })
    Long countByStatusAgg(String status);
}
// derived-query keywords: And Or Between LessThan GreaterThanEqual IsNull NotNull Like StartingWith
// Containing In NotIn Exists True False Regex Near OrderBy First/Top<N> Distinct IgnoreCase

@Autowired MongoTemplate template;                                              // (b) template
```

### 5.2 Insert

```java
repo.insert(user);                   // pure insert — DuplicateKeyException if id exists
repo.save(user);                     // id null → insert; id set → REPLACE whole doc (upsert)
repo.saveAll(list);                  // N round trips unless all new
template.insert(user);
template.insertAll(list);            // bulk insert grouped by collection
```

`save` for a partial change is a lost-update machine: it writes back *every* field of the POJO,
clobbering concurrent changes and any fields the class doesn't know. Use `insert` to insert and
`updateFirst` + `$set` to update.

### 5.3 Find

```java
// repository
Page<User> p = repo.findByStatus("active", PageRequest.of(2, 10, Sort.by(DESC, "age").and(Sort.by("id"))));
p.getContent(); p.getTotalElements();                       // Page = find + count (2 queries)

// template
Query q = new Query(Criteria.where("age").gte(30).and("status").is("active"))
        .with(Sort.by(DESC, "age").and(Sort.by("id")))
        .skip(20).limit(10)
        .maxTime(Duration.ofSeconds(2));
q.fields().include("name", "email").exclude("id");
List<User> users = template.find(q, User.class);
User u  = template.findOne(Query.query(Criteria.where("email").is("ana@x.io")), User.class);
User by = template.findById("664f...", User.class);
long n  = template.count(Query.query(Criteria.where("status").is("active")), User.class);
boolean e = template.exists(q, User.class);
List<String> statuses = template.findDistinct(q, "status", User.class, String.class);

Criteria.where("address.city").is("Austin");
Criteria.where("tags").all("a", "b");
Criteria.where("name").regex("^an", "i");
Criteria.where("phone").exists(false);
Criteria.where("items").elemMatch(Criteria.where("qty").gt(5).and("price").lt(10));
new Criteria().orOperator(Criteria.where("age").lt(18), Criteria.where("age").gt(65));
Criteria.where("age").gt(1).lt(5);          // NOT .gt(1).and("age").lt(5) — throws on duplicate key

// raw JSON escape hatch
template.find(new BasicQuery("{ age: { $gte: 30 } }", "{ name: 1 }"), User.class);

// streaming large results (closes server cursor on stream close)
try (Stream<User> st = template.stream(q, User.class)) { st.forEach(this::handle); }

// keyset pagination
Query kp = new Query(Criteria.where("userId").is(u).orOperator(
        Criteria.where("createdAt").lt(lastTs),
        Criteria.where("createdAt").is(lastTs).and("id").lt(lastId)))
    .with(Sort.by(DESC, "createdAt", "id")).limit(20);
```

### 5.4 Update

```java
Update u = new Update().set("status", "active").inc("logins", 1).currentDate("updatedAt");
UpdateResult r = template.updateFirst(Query.query(Criteria.where("id").is(id)), u, User.class);
r.getMatchedCount(); r.getModifiedCount();

template.updateMulti(Query.query(Criteria.where("status").is("trial")), Update.update("status", "expired"), User.class);
template.upsert(Query.query(Criteria.where("id").is("orderSeq")),
                new Update().inc("seq", 1).setOnInsert("createdAt", Instant.now()), Counter.class);

new Update().push("tags").each("x", "y").slice(-50);
new Update().addToSet("tags", "z");
new Update().pull("tags", "x");
new Update().unset("legacy").rename("old", "new").min("low", 3).max("high", 9);
template.updateFirst(Query.query(Criteria.where("id").is(id).and("items.sku").is("A1")),
                     new Update().inc("items.$.qty", 1), Order.class);
template.updateFirst(Query.query(Criteria.where("id").is(id)),
                     new Update().set("items.$[i].shipped", true).filterArray(Criteria.where("i.qty").gt(0)), Order.class);
template.updateMulti(new Query(), AggregationUpdate.update()                                   // pipeline update
        .set("total").toValue(ArithmeticOperators.Multiply.valueOf("qty").multiplyBy("price")), Order.class);

// atomic read-modify-write
Counter c = template.findAndModify(Query.query(Criteria.where("id").is("orderSeq")),
        new Update().inc("seq", 1), FindAndModifyOptions.options().upsert(true).returnNew(true), Counter.class);
Job job = template.findAndModify(Query.query(Criteria.where("status").is("queued")).with(Sort.by(DESC, "priority").and(Sort.by("id"))),
        new Update().set("status", "running").set("worker", me), FindAndModifyOptions.options().returnNew(true), Job.class);
User old = template.findAndReplace(q, newUser);                    // whole-doc replace

// optimistic locking: @Version → Spring adds {version: N} to the filter and $inc's it;
// matched 0 ⇒ OptimisticLockingFailureException. The retry loop is yours.
```

### 5.5 Delete

```java
repo.deleteById(id); repo.delete(user); repo.deleteAllById(ids); repo.deleteByStatus("expired");
template.remove(Query.query(Criteria.where("status").is("expired")), User.class);
User gone = template.findAndRemove(q, User.class);
List<User> all = template.findAllAndRemove(q, User.class);     // find + remove, not atomic as a set
template.dropCollection(User.class);
```

### 5.6 Indexes & explain

```java
// annotations — applied only when spring.data.mongodb.auto-index-creation=true
@Document
@CompoundIndex(name = "user_created", def = "{ 'userId': 1, 'createdAt': -1 }")
public class Order {
    @Indexed(unique = true) String number;
    @Indexed(expireAfterSeconds = 3600) Instant lastSeen;
    @TextIndexed(weight = 10) String title;
    @GeoSpatialIndexed(type = GeoSpatialIndexType.GEO_2DSPHERE) Point loc;
}

// explicit, deterministic — preferred in production
@Component
class IndexInit {
    IndexInit(MongoTemplate t) {
        IndexOperations orders = t.indexOps(Order.class);
        orders.ensureIndex(new Index().on("userId", ASC).on("createdAt", DESC).named("user_created"));
        t.indexOps(User.class).ensureIndex(new Index().on("email", ASC).unique()
                .partial(PartialIndexFilter.of(Criteria.where("deletedAt").exists(false))));
        t.indexOps(Session.class).ensureIndex(new Index().on("lastSeen", ASC).expire(Duration.ofHours(1)));
        t.indexOps(User.class).ensureIndex(new Index().on("email", ASC)
                .collation(Collation.of("en").strength(ComparisonLevel.secondary())));
        orders.getIndexInfo(); orders.dropIndex("user_created");
    }
}
// resolve annotations on demand instead of at startup:
// new MongoPersistentEntityIndexResolver(mappingContext).resolveIndexFor(Order.class).forEach(indexOps::ensureIndex);

// explain / hint
Query q = new Query(...).withHint("user_created");
Document plan = template.getCollection("orders").find(q.getQueryObject()).sort(q.getSortObject())
        .explain(ExplainVerbosity.EXECUTION_STATS);
```

Never let a fleet of app instances race to build indexes on a large collection at startup — run it
from a migration job (Mongock / Liquibase-Mongo) or once from mongosh.

### 5.7 Aggregation

```java
import static org.springframework.data.mongodb.core.aggregation.Aggregation.*;

Aggregation agg = newAggregation(
    match(Criteria.where("status").is("paid").and("createdAt").gte(since)),
    unwind("items"),
    group("customerId")
        .sum(ArithmeticOperators.Multiply.valueOf("items.qty").multiplyBy("items.price")).as("revenue")
        .addToSet("_id").as("orders"),
    addFields().addFieldWithValue("orderCount", ArrayOperators.Size.lengthOfArray("orders")).build(),
    sort(Sort.by(DESC, "revenue")),
    limit(10),
    lookup("customers", "_id", "_id", "customer"),
    unwind("customer", true),
    project("revenue", "orderCount").and("_id").as("customerId").and("customer.name").as("name").andExclude("_id")
).withOptions(newAggregationOptions().allowDiskUse(true).build());

AggregationResults<CustomerRevenue> res = template.aggregate(agg, "orders", CustomerRevenue.class);
List<CustomerRevenue> rows = res.getMappedResults();

// $facet
facet(sort(Sort.by("price")), limit(20)).as("results").and(count().as("n")).as("total");
// raw stage when the typed API can't express it
stage("{ $setWindowFields: { partitionBy: '$customerId', sortBy: { createdAt: 1 }, " +
      "output: { runningTotal: { $sum: '$total', window: { documents: ['unbounded','current'] } } } } }");
merge().into("customer_revenue").whenMatched(MergeOperation.WhenDocumentsMatch.replaceDocument()).build();
```

- Typed input (`template.aggregate(agg, Order.class, Out.class)`) maps `id` → `_id` through the
  entity metadata; a collection-name string uses field names verbatim. Mixing them is the usual
  "field not found" head-scratcher.
- The `$group` `_id` lands in a result field named `id` unless you `project(...).and("_id").as("x")`.

### 5.8 Transactions

```java
@Service
public class TransferService {
    @Transactional                                        // needs the MongoTransactionManager bean (§5.1)
    public void transfer(String from, String to, long amt) {
        Query q = Query.query(Criteria.where("id").is(from).and("balance").gte(amt));
        if (template.updateFirst(q, new Update().inc("balance", -amt), Account.class).getMatchedCount() == 0)
            throw new InsufficientFundsException();       // RuntimeException ⇒ rollback
        template.updateFirst(Query.query(Criteria.where("id").is(to)), new Update().inc("balance", amt), Account.class);
        // repositories participate automatically — session is bound to the thread
    }
}

// programmatic
TransactionTemplate tx = new TransactionTemplate(transactionManager);
tx.executeWithoutResult(s -> { ... });

// driver-level (gives you the driver's built-in retry on transient errors)
template.withSession(ClientSessionOptions.builder().build())
        .execute(ops -> { ops.updateFirst(...); return null; }, ClientSession::close);

// reactive: ReactiveMongoTransactionManager + TransactionalOperator; @Transactional works on Mono/Flux
```

Traps: no `MongoTransactionManager` bean ⇒ `@Transactional` is a silent no-op; standalone `mongod`
⇒ transactions fail; checked exceptions don't roll back by default; `@Transactional` does not retry
`WriteConflict` (add `@Retryable` or use `withSession`).

### 5.9 Bulk Write

```java
BulkOperations bulk = template.bulkOps(BulkOperations.BulkMode.UNORDERED, User.class);
bulk.insert(new User("E"));
bulk.upsert(Query.query(Criteria.where("id").is("1")), new Update().set("a", 1));
bulk.updateMulti(Query.query(Criteria.where("status").is("x")), Update.update("status", "y"));
bulk.replaceOne(Query.query(Criteria.where("id").is("2")), new User("F"));
bulk.remove(Query.query(Criteria.where("id").is("3")));
BulkWriteResult r = bulk.execute();          // BulkOperationException on partial failure
```

### 5.10 Change Streams

```java
// blocking
@Bean MessageListenerContainer container(MongoTemplate t) {
    var c = new DefaultMessageListenerContainer(t); c.start(); return c;
}
ChangeStreamRequest<Order> req = ChangeStreamRequest.builder(
        (MessageListener<ChangeStreamDocument<Document>, Order>) msg -> handle(msg.getBody()))
    .collection("orders")
    .filter(newAggregation(match(Criteria.where("operationType").in("insert", "update"))))
    .fullDocumentLookup(FullDocument.UPDATE_LOOKUP)
    .resumeToken(savedToken)
    .build();
container.register(req, Order.class);

// reactive (idiomatic)
Flux<ChangeStreamEvent<Order>> flux = reactiveTemplate.changeStream(Order.class)
    .watchCollection("orders").filter(Criteria.where("operationType").is("insert")).listen();
```

### 5.11 Consistency Knobs

```java
// global via URI: ?w=majority&readPreference=secondaryPreferred&readConcernLevel=majority
template.setWriteConcern(WriteConcern.MAJORITY);
template.setWriteConcernResolver(a -> "audit".equals(a.getCollectionName()) ? WriteConcern.W1 : WriteConcern.MAJORITY);
Query q = new Query(...).withReadPreference(ReadPreference.secondaryPreferred()).withReadConcern(ReadConcern.MAJORITY);
@Document @ReadPreference("secondaryPreferred") class Report {}
@Query(value = "{...}", readPreference = "secondary") List<Report> reports();
```

### 5.12 Schema Validation, Collections, Admin

```java
template.createCollection(User.class, CollectionOptions.empty()
        .validator(Validator.schema(MongoJsonSchema.builder()
                .required("email", "createdAt")
                .properties(JsonSchemaProperty.string("email").matching("^.+@.+$"),
                            JsonSchemaProperty.int32("age").gte(0)).build()))
        .moderateValidation().failOnValidationError());
template.createCollection(Metric.class, CollectionOptions.timeSeries("ts").expireAfter(Duration.ofDays(30)));
template.createCollection(Log.class, CollectionOptions.empty().capped().size(1_000_000_000L));
template.getCollectionNames(); template.collectionExists(User.class);
template.executeCommand("{ collStats: 'users' }");
template.executeCommand(new Document("currentOp", 1).append("active", true));
```

### 5.13 Errors (translated by `MongoExceptionTranslator`)

| Situation                      | Spring exception                                        |
| ------------------------------ | ------------------------------------------------------- |
| duplicate key (11000)          | `DuplicateKeyException`                                 |
| `$jsonSchema` failure (121)    | `DataIntegrityViolationException`                       |
| `@Version` mismatch            | `OptimisticLockingFailureException`                     |
| write conflict / other command | `UncategorizedMongoDbException` (wraps `MongoCommandException`; check `getCause()`) |
| timeout / no server / network  | `DataAccessResourceFailureException`                    |
| bulk partial failure           | `BulkOperationException`                                |

---

## 6. Shared Reference

### 6.1 Data Modeling (Embed vs Reference)

| Embed when                                              | Reference when                                       |
| ------------------------------------------------------- | ---------------------------------------------------- |
| child is always read with parent                        | child is read/updated on its own                     |
| bounded, small cardinality (address, line items ≤ ~100) | unbounded growth (comments, events, logs)            |
| child has no identity outside parent                    | many-to-many, or child shared by parents             |
| atomic parent+child update needed (single-doc write)    | doc would approach 16 MB or bloat the working set    |

Patterns as operations:

- **Extended reference** — copy the 2–3 always-displayed fields (`customer: {_id, name}`) into the
  child; on change fan out: `updateMany({"customer._id": id}, {$set: {"customer.name": n}})`.
- **Subset** — latest N inline via `$push` + `$slice: -N`; overflow in a side collection.
- **Bucket** — one doc per (sensor, hour) with an array of readings; upsert with filter
  `{sensor, hour, count: {$lt: 200}}` and `$push` + `$inc: {count: 1}`.
- **Computed** — maintain `commentCount` with `$inc` rather than `$size` at read time.
- **Schema versioning** — `schemaVersion` field; readers branch; migrate lazily on write.
- **Soft delete** — `$set: {deletedAt}` + TTL index on `deletedAt` + partial unique indexes on
  `{ deletedAt: { $exists: false } }` so deleted keys can be reused.

### 6.2 Error Code Map

| Server code / class                     | Meaning                              | PyMongo                          | Java driver                                | Spring                               |
| --------------------------------------- | ------------------------------------ | -------------------------------- | ------------------------------------------ | ------------------------------------ |
| 11000                                   | duplicate key                        | `DuplicateKeyError`              | `MongoWriteException` (DUPLICATE_KEY)      | `DuplicateKeyException`              |
| 121                                     | schema validation failed             | `WriteError`                     | `MongoWriteException`                      | `DataIntegrityViolationException`    |
| 112 + label TransientTransactionError   | write conflict in txn                | `OperationFailure`               | `MongoCommandException`                    | `UncategorizedMongoDbException`      |
| 50                                      | `maxTimeMS` exceeded                 | `ExecutionTimeout`               | `MongoExecutionTimeoutException`           | `UncategorizedMongoDbException`      |
| 43                                      | cursor not found (timed out)         | `CursorNotFound`                 | `MongoCursorNotFoundException`             | `UncategorizedMongoDbException`      |
| 66                                      | `_id` modification                   | `WriteError`                     | `MongoWriteException`                      | `UncategorizedMongoDbException`      |
| 86                                      | index name / spec conflict           | `OperationFailure`               | `MongoCommandException`                    | `UncategorizedMongoDbException`      |
| —                                       | no server within selection timeout   | `ServerSelectionTimeoutError`    | `MongoTimeoutException`                    | `DataAccessResourceFailureException` |
| —                                       | socket / network                     | `AutoReconnect`, `NetworkTimeout`| `MongoSocketException`                     | `DataAccessResourceFailureException` |
| 91 / 189 / 10107                        | shutdown / stepdown / not primary    | `NotPrimaryError` (retried once) | `MongoNotPrimaryException` (retried once)  | —                                    |

- **Retryable writes** retry **once**, only on network error / step-down, only for single-doc
  writes. `updateMany` / `deleteMany` are never retried. Business-level idempotent retry is yours.
- Set `maxTimeMS` on every user-facing query so a bad plan fails fast instead of pinning a
  connection.

### 6.3 Testing

| Stack   | Approach                                                                                                   |
| ------- | ---------------------------------------------------------------------------------------------------------- |
| Python  | `testcontainers[mongodb]` → real `mongod`; `mongomock` only for trivial unit tests (no aggregation fidelity)|
| Java    | `@Testcontainers` + `MongoDBContainer("mongo:8.0")` + `@DynamicPropertySource` for `spring.data.mongodb.uri`; `@DataMongoTest` slice; Flapdoodle embedded is deprecated for Boot 3 |
| Both    | Transactions / change streams need a replica set — `MongoDBContainer` runs `rs.initiate()` for you         |

```java
@SpringBootTest @Testcontainers
class OrderRepoIT {
    @Container static MongoDBContainer mongo = new MongoDBContainer("mongo:8.0");
    @DynamicPropertySource static void props(DynamicPropertyRegistry r) {
        r.add("spring.data.mongodb.uri", mongo::getReplicaSetUrl);
    }
}
```

### 6.4 Interview Quick-Fire

- **Spring `save` vs `insert`?** `save` = upsert-by-id via full replace (clobbers unknown fields);
  `insert` = pure insert, throws on duplicate.
- **Why is `skip` pagination bad?** O(N) index scan per page; use keyset on `(sortKey, _id)`.
- **`matched 1, modified 0`?** Filter hit, update was a no-op — often an idempotent retry that ran twice.
- **Read your own write on a secondary?** Causally consistent session, or read from primary.
- **What must every op in a transaction carry?** The session (`session=` / first arg / Spring
  thread-binding). Missing it silently escapes the transaction.
- **Is `insertMany` atomic?** No — ordered stops at first failure but earlier docs persist.
- **`$` vs `$[]` vs `$[x]`?** First query-matched element / all / those matching `arrayFilters`.
- **Find unused indexes?** `$indexStats`; hide with `hidden: true` before dropping.
- **Are retryable writes a general retry?** No — once, network/stepdown only, single-doc only.
- **`@Transactional` not rolling back?** No `MongoTransactionManager` bean, standalone `mongod`,
  or a checked exception.
- **`$lookup` vs two app queries?** `$lookup` when the join is selective and server-side avoids
  N+1; two queries when the foreign side is cached or the join would explode an intermediate set.
- **One `MongoClient` per what?** Per process. It owns the pool; per-request clients re-run
  discovery and leak connections.
