# 03db.04mongodb.14change-streams Change Streams

> Subscribe to the oplog through a resumable cursor instead of polling.

## Index

- [1. What A Change Stream Is](#1-what-a-change-stream-is)
- [2. Resume Tokens](#2-resume-tokens)
- [Related](#related)

## 1. What A Change Stream Is

A change stream is a cursor over the oplog, filtered by a pipeline.

- Needs a replica set; events arrive once majority-committed ⇒ no rollback surprises
- `fullDocument: updateLookup` returns the current document, not the state at the change
- Use cases: outbox relay, cache invalidation, search indexing

```java
// infra/_03db_04mongodb/MongoChangeStreams.java
// Consume up to maxEvents order changes, resuming from the last saved token.
// tryNext() returns null after maxAwaitTime with no event, so a batch job can stop cleanly.
// Returns how many events were handled.
public int consumeOrderChanges(String consumer, int maxEvents, Consumer<OrderChange> handler) {
    var stream = orders.watch(List.of(
                    Aggregates.match(in("operationType", "insert", "update", "replace", "delete"))))
            .fullDocument(FullDocument.UPDATE_LOOKUP) // current doc at lookup time, not at event time
            .maxAwaitTime(1, TimeUnit.SECONDS);
    Optional<BsonDocument> saved = loadToken(consumer);
    if (saved.isPresent()) {
        stream = stream.resumeAfter(saved.get());
    }
    int handled = 0;
    try (MongoChangeStreamCursor<ChangeStreamDocument<Document>> cursor = stream.cursor()) {
        while (handled < maxEvents) {
            ChangeStreamDocument<Document> ev = cursor.tryNext();
            if (ev == null) {
                break; // no event within maxAwaitTime
            }
            handler.accept(toChange(ev));
            saveToken(consumer, ev.getResumeToken()); // AFTER handling -> at-least-once
            handled++;
        }
    } catch (MongoException e) {
        if (MongoErrors.classify(e) == MongoErrors.Kind.HISTORY_LOST) {
            tokens.deleteOne(eq("_id", consumer)); // next run starts "now"; caller must reconcile the gap
        }
        throw e;
    }
    return handled;
}
```

```python
# app/infra/_03db_04mongodb.py
def consume_order_changes(self, consumer: str, max_events: int, handler: Callable[[OrderChange], None]) -> int:
    """Resume from the saved token; try_next() returns None after max_await_time_ms with no event."""
    pipeline = [{"$match": {"operationType": {"$in": ["insert", "update", "replace", "delete"]}}}]
    handled = 0
    try:
        with self.db[ORDERS].watch(
            pipeline,
            full_document="updateLookup",  # current doc at lookup time, not at event time
            resume_after=self.load_token(consumer),
            max_await_time_ms=1000,
        ) as stream:
            while handled < max_events:
                ev = stream.try_next()
                if ev is None:
                    break
                handler(_to_change(ev))
                self.save_token(consumer, ev["_id"])  # AFTER handling -> at-least-once
                handled += 1
    except OperationFailure as e:
        if classify_error(e) is ErrorKind.HISTORY_LOST:
            self.db[RESUME_TOKENS].delete_one({"_id": consumer})  # caller reconciles the gap
        raise
    return handled
```

## 2. Resume Tokens

Store the resume token after each processed event; restart from it after a crash.

- Process-then-save ⇒ at-least-once; the handler must be idempotent
- Token older than the oplog window ⇒ `ChangeStreamHistoryLost`; resync from a snapshot
- Watch the oplog window (hours) against the longest expected consumer outage

```java
// infra/_03db_04mongodb/MongoChangeStreams.java
// Upsert by consumer name; stored as JSON so it survives any codec. Use majority (the default) so the
// token itself is not rolled back after we acted on the event.
public void saveToken(String consumer, BsonDocument token) {
    tokens.replaceOne(eq("_id", consumer),
            new Document("_id", consumer).append("token", token.toJson()).append("at", OrderDocuments.nowMillis()),
            new ReplaceOptions().upsert(true));
}
```

```python
# app/infra/_03db_04mongodb.py
def save_token(self, consumer: str, token: Doc) -> None:
    self.db[RESUME_TOKENS].replace_one(
        {"_id": consumer},
        {"_id": consumer, "token": json_util.dumps(token), "at": now_millis()},
        upsert=True,
    )
```

```java
// infra/_03db_04mongodb/MongoAdmin.java
// Window = newest oplog ts - oldest oplog ts. Alert on this in SECONDS (as a fraction of your longest
// maintenance operation), not on oplog size in GB.
public long oplogWindowSeconds() {
    var oplog = client.getDatabase("local").getCollection("oplog.rs");
    Document first = oplog.find().sort(Sorts.ascending("$natural")).limit(1)
            .projection(Projections.include("ts")).first();
    Document last = oplog.find().sort(Sorts.descending("$natural")).limit(1)
            .projection(Projections.include("ts")).first();
    if (first == null || last == null) {
        return -1;
    }
    BsonTimestamp a = first.get("ts", BsonTimestamp.class);
    BsonTimestamp b = last.get("ts", BsonTimestamp.class);
    return (long) b.getTime() - a.getTime();
}
```

## Related

- [Index](04mongodb.00index.md)
- [Replica sets and oplog](04mongodb.10replica-sets-oplog.md)
- [DynamoDB streams](02dynamodb.10streams-ttl.md)
