# 03db.04mongodb.05bulk-write Bulk Writes And Errors

> Batch many writes into one round trip and classify failures before retrying.

## Index

- [1. Ordered Vs Unordered](#1-ordered-vs-unordered)
- [2. Error Classification](#2-error-classification)
- [Related](#related)

## 1. Ordered Vs Unordered

`bulkWrite` sends up to 100,000 operations per batch; the driver splits larger lists.

- **Ordered** (default): stops at the first error ⇒ use when later ops depend on earlier ones
- **Unordered**: runs all, reports every error ⇒ faster, and the right choice for independent upserts
- Upsert + `$setOnInsert` makes the batch idempotent: a retry never creates duplicates

```java
// infra/_03db_04mongodb/MongoShowcase.java
// Unordered bulk upsert: one round trip for N ops, keeps going past a failing op. Catch: NOT atomic;
// successful ops stay applied, so the error list must be reconciled, and a blind resend must be idempotent
// (upsert by _id is). ordered=true would stop at the first error and still keep the earlier writes.
public BulkSummary upsertStock(List<StockLevel> levels) {
    Instant now = OrderDocuments.nowMillis();
    List<WriteModel<Document>> ops = new ArrayList<>();
    for (StockLevel s : levels) {
        ops.add(new UpdateOneModel<>(
                eq("_id", s.sku()),
                Updates.combine(Updates.set("qty", s.qty()), Updates.set("updatedAt", now),
                        Updates.setOnInsert("createdAt", now)),
                new UpdateOptions().upsert(true)));
    }
    try {
        return summary(inventory.bulkWrite(ops, new BulkWriteOptions().ordered(false)), List.of());
    } catch (MongoBulkWriteException e) {
        List<String> errors = e.getWriteErrors().stream()
                .map(w -> w.getIndex() + ":" + w.getCode() + ":" + w.getMessage())
                .toList();
        return summary(e.getWriteResult(), errors);
    }
}
```

```python
# app/infra/_03db_04mongodb.py
def upsert_stock(self, levels: list[StockLevel]) -> BulkSummary:
    """Unordered bulk upsert: not atomic; successful ops stay applied, reconcile the error list."""
    now = now_millis()
    ops = [
        UpdateOne(
            {"_id": s.sku},
            {"$set": {"qty": s.qty, "updatedAt": now}, "$setOnInsert": {"createdAt": now}},
            upsert=True,
        )
        for s in levels
    ]
    try:
        r = self.db[INVENTORY].bulk_write(ops, ordered=False)
        return BulkSummary(r.inserted_count, r.matched_count, r.modified_count, r.upserted_count, r.deleted_count)
    except BulkWriteError as e:
        d = e.details
        errors = [f"{w['index']}:{w['code']}:{w['errmsg']}" for w in d.get("writeErrors", [])]
        return BulkSummary(d["nInserted"], d["nMatched"], d["nModified"], d["nUpserted"], d["nRemoved"], errors)
```

## 2. Error Classification

Retry only what is safe to retry.

- Duplicate key (11000) ⇒ not retryable; usually means "already done"
- Network / not-primary / `RetryableWriteError` label ⇒ retry with backoff
- `TransientTransactionError` ⇒ retry the whole transaction
- Retryable writes (`retryWrites=true`) already retry one time automatically

```java
// infra/_03db_04mongodb/MongoErrors.java
public static Kind classify(Throwable t) {
    if (t instanceof MongoException me) {
        // Labels first: a WriteConflict (112) inside a transaction carries TransientTransactionError.
        if (me.hasErrorLabel(MongoException.TRANSIENT_TRANSACTION_ERROR_LABEL)) {
            return Kind.TRANSIENT_TRANSACTION;
        }
        if (me.hasErrorLabel(MongoException.UNKNOWN_TRANSACTION_COMMIT_RESULT_LABEL)) {
            return Kind.UNKNOWN_COMMIT_RESULT;
        }
    }
    if (t instanceof MongoWriteConcernException) {
        return Kind.WRITE_CONCERN_AMBIGUOUS;
    }
    if (t instanceof MongoWriteException we) {
        if (we.getError().getCategory() == ErrorCategory.DUPLICATE_KEY) {
            return Kind.DUPLICATE_KEY;
        }
        return we.getError().getCode() == DOCUMENT_VALIDATION_FAILURE ? Kind.VALIDATION_FAILED : Kind.TERMINAL;
    }
    if (t instanceof MongoBulkWriteException) {
        return Kind.TERMINAL; // inspect getWriteErrors() per op; successful ops are not rolled back
    }
    if (t instanceof MongoExecutionTimeoutException) {
        return Kind.TIMEOUT;
    }
    if (t instanceof MongoTimeoutException) {
        return Kind.NO_SERVER;
    }
    if (t instanceof MongoSocketException || t instanceof MongoNotPrimaryException) {
        return Kind.NETWORK;
    }
    if (t instanceof MongoException me && me.getCode() == CHANGE_STREAM_HISTORY_LOST) {
        return Kind.HISTORY_LOST;
    }
    return Kind.TERMINAL;
}
```

```python
# app/infra/_03db_04mongodb.py
def classify_error(e: BaseException) -> ErrorKind:
    """Decide retry / re-check / give up. Labels first: they beat codes for transactions."""
    if isinstance(e, PyMongoError):
        if e.has_error_label("TransientTransactionError"):
            return ErrorKind.TRANSIENT_TRANSACTION
        if e.has_error_label("UnknownTransactionCommitResult"):
            return ErrorKind.UNKNOWN_COMMIT_RESULT
    if isinstance(e, WriteConcernError):
        return ErrorKind.WRITE_CONCERN_AMBIGUOUS
    if isinstance(e, DuplicateKeyError):
        return ErrorKind.DUPLICATE_KEY
    if isinstance(e, WriteError):
        return ErrorKind.VALIDATION_FAILED if e.code == DOCUMENT_VALIDATION_FAILURE else ErrorKind.TERMINAL
    if isinstance(e, ExecutionTimeout):
        return ErrorKind.TIMEOUT
    if isinstance(e, ServerSelectionTimeoutError):
        return ErrorKind.NO_SERVER
    if isinstance(e, (AutoReconnect, NetworkTimeout, NotPrimaryError)):
        return ErrorKind.NETWORK
    if isinstance(e, OperationFailure) and e.code == CHANGE_STREAM_HISTORY_LOST:
        return ErrorKind.HISTORY_LOST
    return ErrorKind.TERMINAL
```

## Related

- [Index](04mongodb.00index.md)
- [Create, Read, Update, Delete (CRUD) and update operators](04mongodb.04crud-update-operators.md)
- [Transactions](04mongodb.12transactions.md)
