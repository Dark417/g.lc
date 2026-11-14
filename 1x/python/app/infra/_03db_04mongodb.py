"""MongoDB showcase (PyMongo): one method per concept, in the order of x-md/03db/04mongodb.00index.md.

- Filters, updates and pipelines are plain dicts: exactly what mongosh sends.
- One MongoClient per process (get_client): thread-safe, owns the pool. Not fork-safe: with a pre-fork
  server create it after the fork (lazy creation here does that for free).
- No network call at import time; the client is created on first use.
- Every user-facing read carries max_time_ms: MongoDB has no statement timeout by default.
"""

import base64
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from functools import lru_cache
from typing import Any
from urllib.parse import parse_qs, urlsplit

from bson import ObjectId, json_util
from bson.errors import InvalidId
from pymongo import ASCENDING, DESCENDING, TEXT, MongoClient, ReadPreference, ReturnDocument, UpdateOne
from pymongo.client_session import ClientSession
from pymongo.collation import Collation, CollationStrength
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import (
    AutoReconnect,
    BulkWriteError,
    CollectionInvalid,
    DuplicateKeyError,
    ExecutionTimeout,
    NetworkTimeout,
    NotPrimaryError,
    OperationFailure,
    PyMongoError,
    ServerSelectionTimeoutError,
    WriteConcernError,
    WriteError,
)
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import Secondary, SecondaryPreferred
from pymongo.write_concern import WriteConcern

from app.config._03db_04mongodb import get_mongo_settings
from app.domain._03db_04mongodb import (
    MAX_ITEMS,
    BulkSummary,
    CustomerRevenue,
    InsufficientStockError,
    LineItem,
    NewOrder,
    Order,
    OrderChange,
    OrderNotFoundError,
    OrderPage,
    OrderStatus,
    QueryPlanSummary,
    StockLevel,
    VersionConflictError,
)

Doc = dict[str, Any]

ORDERS = "orders"
INVENTORY = "inventory"
CUSTOMERS = "customers"
ORDER_EVENTS = "order_events"
COUNTERS = "counters"
LEDGER = "ledger"
ROTAS = "oncall_rotas"
RESUME_TOKENS = "resume_tokens"
DAILY_REVENUE = "daily_revenue"

IDX_CUSTOMER_CREATED = "customer_created_id"
IDX_PENDING = "pending_created"
IDX_ITEMS_SKU = "items_sku"
IDX_NOTE_TEXT = "note_text"
IDX_PURGE_TTL = "purge_ttl"
IDX_EMAIL_CI = "email_ci_unique"
IDX_BUCKET = "order_bucket"

BUCKET_SIZE = 200
SOFT_DELETE_RETENTION = timedelta(days=30)
MAX_TX_ATTEMPTS = 5
MAX_STALENESS_S = 90  # minimum allowed maxStalenessSeconds

# Server codes worth naming (see x-md 15errors-timeouts)
DUPLICATE_KEY = 11000
DOCUMENT_VALIDATION_FAILURE = 121
MAX_TIME_MS_EXPIRED = 50
CHANGE_STREAM_HISTORY_LOST = 286


# ================================================================ client + mapping helpers


@lru_cache
def get_client() -> MongoClient:
    """One client per process. Default write concern = majority unless the URI sets w."""
    s = get_mongo_settings()
    options: dict[str, Any] = {
        "appname": s.app_name,
        "maxPoolSize": s.max_pool_size,
        "serverSelectionTimeoutMS": s.server_selection_timeout_ms,
        "connectTimeoutMS": 5000,
        "waitQueueTimeoutMS": 2000,  # fail fast when the pool is exhausted
        "tz_aware": True,  # datetimes come back timezone-aware (UTC)
        "uuidRepresentation": "standard",
    }
    if "w" not in parse_qs(urlsplit(s.uri).query):
        options["w"] = "majority"  # keyword args override the URI, so only set it when the URI is silent
    if s.tls_ca_file:
        options["tlsCAFile"] = s.tls_ca_file  # PyMongo reads the PEM bundle directly (Java needs an SSLContext)
    # Retryable writes stay on the driver default unless the URI says retryWrites=false (DocumentDB).
    return MongoClient(s.uri, **options)


def get_db() -> Database:
    return get_client()[get_mongo_settings().database]


def now_millis() -> datetime:
    """BSON Date is millisecond precision: truncate BEFORE writing so memory equals storage."""
    t = datetime.now(timezone.utc)
    return t.replace(microsecond=t.microsecond // 1000 * 1000)


def object_id(hex_id: str) -> ObjectId:
    try:
        return ObjectId(hex_id)
    except (InvalidId, TypeError) as e:
        raise ValueError(f"not an ObjectId: {hex_id}") from e


def item_document(i: LineItem) -> Doc:
    return {"sku": i.sku, "qty": i.qty, "priceCents": i.price_cents}


def new_order_document(oid: ObjectId, o: NewOrder, now: datetime) -> Doc:
    return {
        "_id": oid,
        "customerId": o.customer_id,
        "customerName": o.customer_name,  # extended reference: no $lookup on the read path
        "status": OrderStatus.PENDING.value,
        "items": [item_document(i) for i in o.items],  # embedded, bounded
        "totalCents": o.total_cents,  # Python int -> BSON int32/int64
        "note": o.note,
        "createdAt": now,
        "updatedAt": now,
        "version": 1,
    }


def to_order(d: Doc) -> Order:
    return Order(
        id=str(d["_id"]),
        customer_id=d["customerId"],
        customer_name=d.get("customerName"),
        status=OrderStatus(d["status"]),
        items=tuple(LineItem(i["sku"], int(i["qty"]), int(i["priceCents"])) for i in d.get("items", [])),
        total_cents=int(d.get("totalCents", 0)),
        note=d.get("note"),
        created_at=d["createdAt"],
        updated_at=d.get("updatedAt"),
        version=int(d.get("version", 0)),
    )


def encode_cursor(created_at: datetime, oid: ObjectId) -> str:
    """Keyset cursor = sort key of the last row: (createdAt millis, _id). _id breaks createdAt ties."""
    raw = f"{int(created_at.timestamp() * 1000)}.{oid}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def decode_cursor(cursor: str | None) -> tuple[datetime, ObjectId] | None:
    if not cursor:
        return None
    try:
        raw = base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)).decode()
        millis, hex_id = raw.split(".", 1)
        return datetime.fromtimestamp(int(millis) / 1000, tz=timezone.utc), ObjectId(hex_id)
    except (ValueError, InvalidId) as e:
        raise ValueError("invalid cursor") from e


# ================================================================ errors


class ErrorKind(StrEnum):
    DUPLICATE_KEY = "DUPLICATE_KEY"  # terminal for this write
    VALIDATION_FAILED = "VALIDATION_FAILED"  # terminal: same bytes fail again
    TRANSIENT_TRANSACTION = "TRANSIENT_TRANSACTION"  # rerun the WHOLE transaction
    UNKNOWN_COMMIT_RESULT = "UNKNOWN_COMMIT_RESULT"  # retry commit only
    WRITE_CONCERN_AMBIGUOUS = "WRITE_CONCERN_AMBIGUOUS"  # applied locally, majority unknown: re-check
    TIMEOUT = "TIMEOUT"  # maxTimeMS: degrade, don't retry
    NO_SERVER = "NO_SERVER"  # server selection timed out
    NETWORK = "NETWORK"  # the driver already retried once if retryable
    HISTORY_LOST = "HISTORY_LOST"  # change-stream token fell off the oplog
    TERMINAL = "TERMINAL"


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


# ================================================================ consistency profiles


def ledger_collection(db: Database, name: str) -> Collection:
    """Ledger / payments: rollback-safe write, never read a doomed write, primary only. No j=True."""
    return db.get_collection(
        name,
        write_concern=WriteConcern("majority", wtimeout=5000),
        read_concern=ReadConcern("majority"),
        read_preference=ReadPreference.PRIMARY,
    )


def user_facing_collection(db: Database, name: str) -> Collection:
    """Majority write, primary read: read-your-writes without sessions."""
    return db.get_collection(
        name,
        write_concern=WriteConcern("majority"),
        read_concern=ReadConcern("local"),
        read_preference=ReadPreference.PRIMARY,
    )


def telemetry_collection(db: Database, name: str) -> Collection:
    """Telemetry: w=1 is a documented decision here (losing a few points on failover is acceptable)."""
    return db.get_collection(
        name,
        write_concern=WriteConcern(w=1),
        read_concern=ReadConcern("local"),
        read_preference=SecondaryPreferred(max_staleness=MAX_STALENESS_S),
    )


def analytics_collection(db: Database, name: str) -> Collection:
    """BI: Secondary (not SecondaryPreferred) on a tagged member, so it fails CLOSED, never onto the primary."""
    return db.get_collection(
        name,
        read_concern=ReadConcern("local"),
        read_preference=Secondary(tag_sets=[{"nodeType": "analytics"}], max_staleness=MAX_STALENESS_S),
    )


# ================================================================ showcase


class LedgerWrite(StrEnum):
    APPLIED = "APPLIED"
    ALREADY_APPLIED = "ALREADY_APPLIED"
    UNKNOWN_RECHECK = "UNKNOWN_RECHECK"


class MongoShowcase:
    """CRUD, operators, bulk, indexes, explain, pagination, aggregation, concerns."""

    def __init__(self, db: Database | None = None) -> None:
        self._db = db
        self.max_time_ms = get_mongo_settings().max_time_ms

    @property
    def db(self) -> Database:
        if self._db is None:
            self._db = get_db()  # lazy: first use, not import
        return self._db

    @property
    def orders(self) -> Collection:
        return user_facing_collection(self.db, ORDERS)

    # ------------------------------------------------------------ 01 document model + validation

    def apply_order_validator(self) -> None:
        """$jsonSchema validator, moderate level: existing invalid docs are skipped, new writes are checked."""
        schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["customerId", "status", "items", "totalCents", "createdAt", "version"],
                "properties": {
                    "customerId": {"bsonType": "string"},
                    "status": {"enum": [s.value for s in OrderStatus]},
                    "items": {
                        "bsonType": "array",
                        "minItems": 1,
                        "maxItems": MAX_ITEMS,
                        "items": {
                            "bsonType": "object",
                            "required": ["sku", "qty", "priceCents"],
                            "properties": {
                                "qty": {"bsonType": ["int", "long"], "minimum": 1},
                                "priceCents": {"bsonType": ["int", "long"]},
                            },
                        },
                    },
                    "totalCents": {"bsonType": ["int", "long"]},
                    "createdAt": {"bsonType": "date"},
                    "version": {"bsonType": ["int", "long"]},
                },
            }
        }
        try:
            self.db.create_collection(ORDERS, validator=schema, validationLevel="moderate", validationAction="error")
        except CollectionInvalid:  # already exists: change the validator in place
            self.db.command("collMod", ORDERS, validator=schema, validationLevel="moderate", validationAction="error")

    # ------------------------------------------------------------ 03 schema design

    def insert_order(self, o: NewOrder) -> Order:
        """Embed items + copy the customer name: one document, atomic by construction."""
        doc = new_order_document(ObjectId(), o, now_millis())
        self.orders.insert_one(doc)  # also sets doc["_id"] if missing (PyMongo mutates the dict)
        return to_order(doc)

    def rename_customer_everywhere(self, customer_id: str, new_name: str) -> int:
        """Extended-reference fan-out: every copied name must change. Bound the fan-out at design time."""
        self.db[CUSTOMERS].update_one({"_id": customer_id}, {"$set": {"name": new_name}})
        return self.orders.update_many({"customerId": customer_id}, {"$set": {"customerName": new_name}}).modified_count

    def append_order_event(self, order_id: str, event: str) -> None:
        """Bucket pattern: append to the open bucket (count < 200) or upsert a new one; caps array growth."""
        now = now_millis()
        self.db[ORDER_EVENTS].update_one(
            {"orderId": order_id, "count": {"$lt": BUCKET_SIZE}},
            {"$push": {"events": {"at": now, "event": event}}, "$inc": {"count": 1}, "$setOnInsert": {"firstAt": now}},
            upsert=True,
        )

    # ------------------------------------------------------------ 04 CRUD + update operators

    def find_order(self, order_id: str) -> Order | None:
        d = self.orders.find_one({"_id": object_id(order_id)}, max_time_ms=self.max_time_ms)
        return to_order(d) if d else None

    def find_open_orders_with_sku(self, sku: str, min_qty: int, limit: int) -> list[Order]:
        """$elemMatch: ONE element must satisfy both predicates (not "some element each")."""
        cur = (
            self.orders.find(
                {
                    "status": {"$in": [OrderStatus.PENDING.value, OrderStatus.PAID.value]},
                    "items": {"$elemMatch": {"sku": sku, "qty": {"$gte": min_qty}}},
                },
                {"note": 0},  # projection is the 2nd positional argument
            )
            .sort([("createdAt", DESCENDING), ("_id", DESCENDING)])  # list of tuples, not a dict
            .limit(limit)
            .max_time_ms(self.max_time_ms)
        )
        return [to_order(d) for d in cur]

    def add_item(self, order_id: str, item: LineItem) -> Order | None:
        """$push + $inc + $currentDate in one atomic update; the filter bounds the array."""
        d = self.orders.find_one_and_update(
            {
                "_id": object_id(order_id),
                "status": OrderStatus.PENDING.value,
                f"items.{MAX_ITEMS - 1}": {"$exists": False},
            },
            {
                "$push": {"items": item_document(item)},
                "$inc": {"totalCents": item.subtotal_cents, "version": 1},
                "$currentDate": {"updatedAt": True},
            },
            return_document=ReturnDocument.AFTER,
        )
        return to_order(d) if d else None

    def increment_item_qty(self, order_id: str, sku: str, by: int) -> Order | None:
        """Positional $: the first element matched by the QUERY, so the array field must be in the filter."""
        r = self.orders.update_one(
            {"_id": object_id(order_id), "items.sku": sku},
            {"$inc": {"items.$.qty": by, "version": 1}},
        )
        return self.recompute_total(order_id) if r.matched_count else None

    def mark_backordered(self, order_id: str, skus: set[str]) -> int:
        """Filtered positional $[i] + array_filters: every element matching the named filter."""
        return self.orders.update_one(
            {"_id": object_id(order_id)},
            {"$set": {"items.$[i].backordered": True}},
            array_filters=[{"i.sku": {"$in": sorted(skus)}}],
        ).modified_count

    def recompute_total(self, order_id: str) -> Order | None:
        """Pipeline update (4.2+): compute from other fields server-side; int arithmetic stays int."""
        pipeline = [
            {
                "$set": {
                    "totalCents": {
                        "$sum": {"$map": {"input": "$items", "in": {"$multiply": ["$$this.qty", "$$this.priceCents"]}}}
                    },
                    "updatedAt": "$$NOW",
                }
            }
        ]
        d = self.orders.find_one_and_update(
            {"_id": object_id(order_id)}, pipeline, return_document=ReturnDocument.AFTER
        )
        return to_order(d) if d else None

    def next_sequence(self, name: str) -> int:
        """Atomic counter: upsert + $inc returns the new value. A hot counter serializes callers."""
        d = self.db[COUNTERS].find_one_and_update(
            {"_id": name},
            {"$inc": {"seq": 1}, "$setOnInsert": {"createdAt": now_millis()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return int(d["seq"])

    def claim_oldest_pending(self, worker: str) -> Order | None:
        """Work-queue claim: filter + $set are one atomic step, so two workers never claim the same order."""
        d = self.orders.find_one_and_update(
            {"status": OrderStatus.PENDING.value, "claimedBy": {"$exists": False}},
            {"$set": {"claimedBy": worker}, "$currentDate": {"claimedAt": True}},
            sort=[("createdAt", ASCENDING)],  # served by the partial pending index
            return_document=ReturnDocument.AFTER,
        )
        return to_order(d) if d else None

    def change_status_with_version(self, order_id: str, status: OrderStatus, expected_version: int) -> Order:
        """Optimistic lock: version in the filter; no match = someone else won, or no such order."""
        d = self.orders.find_one_and_update(
            {"_id": object_id(order_id), "version": expected_version},
            {"$set": {"status": status.value}, "$inc": {"version": 1}, "$currentDate": {"updatedAt": True}},
            return_document=ReturnDocument.AFTER,
        )
        if d:
            return to_order(d)
        current = self.find_order(order_id)  # one read to tell "missing" from "version moved"
        if current is None:
            raise OrderNotFoundError(order_id)
        raise VersionConflictError(order_id, expected_version, current)

    def soft_delete(self, order_id: str) -> bool:
        """Mark now; the TTL index purges later (TTL runs ~every 60 s, readers still filter deletedAt)."""
        now = now_millis()
        return (
            self.orders.update_one(
                {"_id": object_id(order_id), "deletedAt": {"$exists": False}},
                {"$set": {"deletedAt": now, "purgeAt": now + SOFT_DELETE_RETENTION}},
            ).modified_count
            == 1
        )

    def delete_cancelled_before(self, cutoff: datetime) -> int:
        return self.orders.delete_many(
            {"status": OrderStatus.CANCELLED.value, "createdAt": {"$lt": cutoff}}
        ).deleted_count

    # ------------------------------------------------------------ 05 bulk write

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

    # ------------------------------------------------------------ 06 indexes

    def ensure_indexes(self) -> list[str]:
        """Idempotent index set; each index names the query it serves (ESR = Equality, Sort, Range)."""
        orders = self.db[ORDERS]
        return [
            # E = customerId, S = createdAt desc, _id desc = keyset tiebreaker
            orders.create_index(
                [("customerId", ASCENDING), ("createdAt", DESCENDING), ("_id", DESCENDING)],
                name=IDX_CUSTOMER_CREATED,
            ),
            # Partial: only PENDING orders; used only when the query provably implies status == PENDING
            orders.create_index(
                [("status", ASCENDING), ("createdAt", ASCENDING)],
                name=IDX_PENDING,
                partialFilterExpression={"status": OrderStatus.PENDING.value},
            ),
            orders.create_index([("items.sku", ASCENDING)], name=IDX_ITEMS_SKU),  # multikey: never covers
            orders.create_index([("note", TEXT)], name=IDX_NOTE_TEXT),  # one text index per collection
            orders.create_index([("purgeAt", ASCENDING)], name=IDX_PURGE_TTL, expireAfterSeconds=0),  # Date only
            self.db[CUSTOMERS].create_index(
                [("email", ASCENDING)],
                name=IDX_EMAIL_CI,
                unique=True,
                collation=Collation(locale="en", strength=CollationStrength.SECONDARY),  # queries must match it
            ),
            self.db[ORDER_EVENTS].create_index([("orderId", ASCENDING), ("count", ASCENDING)], name=IDX_BUCKET),
        ]

    def set_index_hidden(self, index_name: str, hidden: bool) -> None:
        """Hide before drop: still maintained, ignored by the planner, un-hide is instant."""
        self.db.command("collMod", ORDERS, index={"name": index_name, "hidden": hidden})

    def unused_indexes(self) -> list[str]:
        """$indexStats counters reset on restart: snapshot them over 35+ days before trusting "unused"."""
        return [
            s["name"]
            for s in self.db[ORDERS].aggregate([{"$indexStats": {}}])
            if int(s["accesses"]["ops"]) == 0 and s["name"] != "_id_"
        ]

    def search_notes(self, terms: str, limit: int) -> list[Order]:
        """$text sorted by textScore; needs the text index, cannot be hinted."""
        cur = (
            self.orders.find({"$text": {"$search": terms}}, {"score": {"$meta": "textScore"}})
            .sort([("score", {"$meta": "textScore"})])
            .limit(limit)
            .max_time_ms(self.max_time_ms)
        )
        return [to_order(d) for d in cur]

    # ------------------------------------------------------------ 07 query planner + explain

    def explain_customer_orders(self, customer_id: str) -> QueryPlanSummary:
        """explain with executionStats: keysExamined / nReturned is the evidence, not the stage name."""
        plan = self.db.command(
            "explain",
            {
                "find": ORDERS,
                "filter": {"customerId": customer_id},
                "sort": {"createdAt": -1, "_id": -1},
                "limit": 20,
            },
            verbosity="executionStats",
        )
        stats = plan["executionStats"]
        stages: list[str] = []
        index = _collect_stages(plan["queryPlanner"]["winningPlan"], stages)
        return QueryPlanSummary(
            winning_stage=stages[0] if stages else "UNKNOWN",
            index_name=index,
            keys_examined=int(stats["totalKeysExamined"]),
            docs_examined=int(stats["totalDocsExamined"]),
            n_returned=int(stats["nReturned"]),
            execution_millis=int(stats["executionTimeMillis"]),
            blocking_sort="SORT" in stages,
            covered="IXSCAN" in stages and "FETCH" not in stages,
        )

    def customer_orders_hinted(self, customer_id: str, limit: int) -> list[Order]:
        """hint(): pin the plan where a wrong pick breaches the SLO; you own the choice from now on."""
        cur = (
            self.orders.find({"customerId": customer_id})
            .sort([("createdAt", DESCENDING), ("_id", DESCENDING)])
            .hint(IDX_CUSTOMER_CREATED)
            .limit(limit)
            .max_time_ms(self.max_time_ms)
        )
        return [to_order(d) for d in cur]

    # ------------------------------------------------------------ 08 pagination

    def list_customer_orders(self, customer_id: str, limit: int, cursor: str | None) -> OrderPage:
        """Keyset on (createdAt, _id): one bounded index seek per page; fetch limit+1 to detect a next page."""
        flt: Doc = {"customerId": customer_id}
        after = decode_cursor(cursor)
        if after:
            ts, oid = after
            flt["$or"] = [{"createdAt": {"$lt": ts}}, {"createdAt": ts, "_id": {"$lt": oid}}]
        rows = list(
            self.orders.find(flt)
            .sort([("createdAt", DESCENDING), ("_id", DESCENDING)])  # must match the index direction
            .limit(limit + 1)
            .max_time_ms(self.max_time_ms)
        )
        page = rows[:limit]
        nxt = encode_cursor(page[-1]["createdAt"], page[-1]["_id"]) if len(rows) > limit else None
        return OrderPage([to_order(d) for d in page], nxt)

    def list_customer_orders_by_skip(self, customer_id: str, page: int, size: int) -> list[Order]:
        """Anti-pattern for contrast: skip(N) walks N keys per page; rows shift under concurrent inserts."""
        cur = (
            self.orders.find({"customerId": customer_id})
            .sort([("createdAt", DESCENDING), ("_id", DESCENDING)])
            .skip(page * size)
            .limit(size)
            .max_time_ms(self.max_time_ms)
        )
        return [to_order(d) for d in cur]

    # ------------------------------------------------------------ 09 aggregation

    def revenue_by_customer(self, since: datetime, limit: int) -> list[CustomerRevenue]:
        """$match first -> $unwind -> $group -> $sort+$limit (top-k) -> $lookup after the limit -> $project."""
        pipeline: list[Doc] = [
            {"$match": {"status": {"$in": ["PAID", "SHIPPED", "DELIVERED"]}, "createdAt": {"$gte": since}}},
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$customerId",
                    "revenueCents": {"$sum": {"$multiply": ["$items.qty", "$items.priceCents"]}},
                    "orderIds": {"$addToSet": "$_id"},
                }
            },
            {"$addFields": {"orderCount": {"$size": "$orderIds"}}},
            {"$sort": {"revenueCents": -1}},
            {"$limit": limit},
            {"$lookup": {"from": CUSTOMERS, "localField": "_id", "foreignField": "_id", "as": "customer"}},
            {"$unwind": {"path": "$customer", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "customerId": "$_id",
                    "customerName": "$customer.name",
                    "revenueCents": 1,
                    "orderCount": 1,
                }
            },
        ]
        rows = self.orders.aggregate(pipeline, allowDiskUse=True, maxTimeMS=self.max_time_ms)
        return [
            CustomerRevenue(r["customerId"], r.get("customerName"), int(r["revenueCents"]), int(r["orderCount"]))
            for r in rows
        ]

    def status_facets(self, customer_id: str) -> Doc:
        """$facet: several sub-pipelines over one input in one round trip; output must stay < 16 MB."""
        pipeline: list[Doc] = [
            {"$match": {"customerId": customer_id}},
            {
                "$facet": {
                    "byStatus": [{"$group": {"_id": "$status", "n": {"$sum": 1}}}],
                    "latest": [
                        {"$sort": {"createdAt": -1}},
                        {"$limit": 5},
                        {"$project": {"status": 1, "totalCents": 1, "createdAt": 1}},
                    ],
                    "total": [{"$count": "n"}],
                }
            },
        ]
        return next(self.orders.aggregate(pipeline, maxTimeMS=self.max_time_ms), {})

    def running_totals(self, customer_id: str) -> list[Doc]:
        """$setWindowFields (5.0+): running total without a self-join."""
        pipeline: list[Doc] = [
            {"$match": {"customerId": customer_id}},
            {
                "$setWindowFields": {
                    "partitionBy": "$customerId",
                    "sortBy": {"createdAt": 1},
                    "output": {
                        "runningTotalCents": {"$sum": "$totalCents", "window": {"documents": ["unbounded", "current"]}}
                    },
                }
            },
            {"$project": {"createdAt": 1, "totalCents": 1, "runningTotalCents": 1}},
        ]
        return list(self.orders.aggregate(pipeline, maxTimeMS=self.max_time_ms))

    def materialize_daily_revenue(self, since: datetime) -> None:
        """$merge a daily rollup (upsert per day); readers hit the small daily_revenue collection."""
        pipeline: list[Doc] = [
            {"$match": {"status": {"$in": ["PAID", "SHIPPED", "DELIVERED"]}, "createdAt": {"$gte": since}}},
            {
                "$group": {
                    "_id": {"$dateTrunc": {"date": "$createdAt", "unit": "day"}},
                    "revenueCents": {"$sum": "$totalCents"},
                    "orders": {"$sum": 1},
                }
            },
            {"$merge": {"into": DAILY_REVENUE, "whenMatched": "replace", "whenNotMatched": "insert"}},
        ]
        self.orders.aggregate(pipeline, allowDiskUse=True)  # $merge runs as part of the command

    # ------------------------------------------------------------ 11 read/write concern

    def record_ledger_entry(self, payment_id: str, amount_cents: int) -> LedgerWrite:
        """Idempotent upsert keyed by payment id; a wtimeout is ambiguous, so re-check instead of retrying."""
        try:
            r = ledger_collection(self.db, LEDGER).update_one(
                {"_id": payment_id},
                {"$setOnInsert": {"amountCents": amount_cents, "at": now_millis()}},
                upsert=True,
            )
            return LedgerWrite.APPLIED if r.upserted_id is not None else LedgerWrite.ALREADY_APPLIED
        except WriteConcernError:
            return LedgerWrite.UNKNOWN_RECHECK

    def insert_then_read_from_secondary(self, o: NewOrder) -> Order | None:
        """Causal session: the secondary waits for afterClusterTime, so we read our own write (slowly)."""
        with get_client().start_session(causal_consistency=True) as s:
            doc = new_order_document(ObjectId(), o, now_millis())
            self.orders.insert_one(doc, session=s)
            d = self.orders.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).find_one(
                {"_id": doc["_id"]}, session=s, max_time_ms=self.max_time_ms
            )
            return to_order(d) if d else None


def _collect_stages(node: Doc | None, out: list[str]) -> str | None:
    """stage -> inputStage walk (SBE plans nest under queryPlan); returns the index name if any."""
    if not node:
        return None
    plan = node.get("queryPlan", node)
    out.append(plan.get("stage", "UNKNOWN"))
    below = _collect_stages(plan.get("inputStage"), out)
    return plan.get("indexName") or below


# ================================================================ 12 transactions


class MongoTransactions:
    """Snapshot-isolation transactions. Every op carries session=; the body may run more than once."""

    def __init__(self, db: Database | None = None) -> None:
        self._db = db

    @property
    def db(self) -> Database:
        if self._db is None:
            self._db = get_db()
        return self._db

    def _place_order_body(self, s: ClientSession, o: NewOrder) -> Order:
        for item in o.items:
            r = self.db[INVENTORY].update_one(
                {"_id": item.sku, "qty": {"$gte": item.qty}},  # predicate + $inc are one atomic step
                {"$inc": {"qty": -item.qty}},
                session=s,
            )
            if r.matched_count == 0:
                raise InsufficientStockError(item.sku, item.qty)  # non-PyMongo error: abort, no retry
        doc = new_order_document(ObjectId(), o, now_millis())
        self.db[ORDERS].insert_one(doc, session=s)  # forgetting session= silently escapes the transaction
        return to_order(doc)

    def place_order(self, o: NewOrder) -> Order:
        """Callback API: retries the body on TransientTransactionError and the commit on UnknownCommitResult."""
        with get_client().start_session() as s:
            return s.with_transaction(
                lambda session: self._place_order_body(session, o),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority"),
                read_preference=ReadPreference.PRIMARY,
                max_commit_time_ms=5000,
            )

    def place_order_hand_rolled(self, o: NewOrder) -> Order:
        """What with_transaction does, written out, plus an attempt cap and backoff."""
        with get_client().start_session() as s:
            for attempt in range(MAX_TX_ATTEMPTS):
                s.start_transaction(
                    read_concern=ReadConcern("snapshot"), write_concern=WriteConcern("majority"), max_commit_time_ms=5000
                )
                try:
                    placed = self._place_order_body(s, o)
                    _commit_with_retry(s)
                    return placed
                except PyMongoError as e:
                    if s.in_transaction:
                        s.abort_transaction()
                    if not e.has_error_label("TransientTransactionError") or attempt + 1 >= MAX_TX_ATTEMPTS:
                        raise
                    time.sleep(min(2.0, 0.05 * 2**attempt))  # back off: retrying harder adds contention
                except Exception:
                    if s.in_transaction:
                        s.abort_transaction()  # business error: abort, never retry
                    raise
        raise RuntimeError("unreachable")

    def go_off_call(self, rota_id: str, engineer: str) -> bool:
        """Write-skew fix without a transaction: the invariant lives in ONE document ("oncall.1" exists = >= 2)."""
        return (
            self.db[ROTAS]
            .update_one(
                {"_id": rota_id, "oncall": engineer, "oncall.1": {"$exists": True}},
                {"$pull": {"oncall": engineer}},
            )
            .modified_count
            == 1
        )

    def reserve_stock(self, sku: str, qty: int, order_id: str, reserved_until: datetime) -> bool:
        """Saga step instead of a cross-shard transaction: single-document conditional reserve."""
        return (
            self.db[INVENTORY]
            .update_one(
                {"_id": sku, "qty": {"$gte": qty}},
                {"$inc": {"qty": -qty}, "$push": {"reservations": {"orderId": order_id, "qty": qty, "until": reserved_until}}},
            )
            .modified_count
            == 1
        )


def _commit_with_retry(s: ClientSession) -> None:
    for attempt in range(MAX_TX_ATTEMPTS):
        try:
            s.commit_transaction()
            return
        except PyMongoError as e:
            if not e.has_error_label("UnknownTransactionCommitResult") or attempt + 1 >= MAX_TX_ATTEMPTS:
                raise  # TransientTransactionError here propagates to the outer loop


# ================================================================ 14 change streams


class MongoChangeStreams:
    """Majority-committed, resumable oplog cursor; at-least-once when the token is saved after handling."""

    def __init__(self, db: Database | None = None) -> None:
        self._db = db

    @property
    def db(self) -> Database:
        if self._db is None:
            self._db = get_db()
        return self._db

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

    def load_token(self, consumer: str) -> Doc | None:
        d = self.db[RESUME_TOKENS].find_one({"_id": consumer})
        return json_util.loads(d["token"]) if d else None

    def save_token(self, consumer: str, token: Doc) -> None:
        self.db[RESUME_TOKENS].replace_one(
            {"_id": consumer},
            {"_id": consumer, "token": json_util.dumps(token), "at": now_millis()},
            upsert=True,
        )


def _to_change(ev: Doc) -> OrderChange:
    full = ev.get("fullDocument")  # None for delete, or when the doc vanished before the lookup
    key = ev.get("documentKey") or {}
    return OrderChange(
        operation_type=ev["operationType"],
        order_id=str(key["_id"]) if "_id" in key else None,
        status=OrderStatus(full["status"]) if full else None,
        resume_token=json_util.dumps(ev["_id"]),
    )


# ================================================================ admin: 01, 02, 07, 10, 13


@dataclass
class MongoAdmin:
    """runCommand diagnostics: the numbers an on-call engineer reads first."""

    _db: Database | None = None

    @property
    def db(self) -> Database:
        if self._db is None:
            self._db = get_db()
        return self._db

    def document_size_stats(self, collection: str) -> Doc:
        """$bsonSize distribution; alert near 4 MB p99. Full scan: analytics member, allowDiskUse."""
        pipeline: list[Doc] = [
            {"$project": {"size": {"$bsonSize": "$$ROOT"}}},
            {"$group": {"_id": None, "avgBytes": {"$avg": "$size"}, "maxBytes": {"$max": "$size"}, "docs": {"$sum": 1}}},
        ]
        return next(analytics_collection(self.db, collection).aggregate(pipeline, allowDiskUse=True), {})

    def cache_health(self) -> Doc:
        """Watch the RATE of bytes read into cache and app-thread eviction, not utilization (~80% by design)."""
        cache = self.db.command("serverStatus")["wiredTiger"]["cache"]
        return {
            "maxBytes": cache["maximum bytes configured"],
            "currentBytes": cache["bytes currently in the cache"],
            "dirtyBytes": cache["tracked dirty bytes in the cache"],
            "bytesReadIntoCache": cache["bytes read into cache"],
            "pagesEvictedByAppThreads": cache["pages evicted by application threads"],
        }

    def enable_sampled_profiler(self, slow_ms: int, sample_rate: float) -> Doc:
        """Profiler at slowms for a sampled window, not permanently."""
        return self.db.command("profile", 1, slowms=slow_ms, sampleRate=sample_rate)

    def replica_set_summary(self) -> Doc:
        """Member states, lag, and the oplog window in seconds."""
        status = get_client().admin.command("replSetGetStatus")
        primary = next((m["optimeDate"] for m in status["members"] if m["stateStr"] == "PRIMARY"), None)
        members = [
            {
                "name": m["name"],
                "state": m["stateStr"],
                "lagSeconds": int((primary - m["optimeDate"]).total_seconds()) if primary and "optimeDate" in m else -1,
                "syncSource": m.get("syncSourceHost"),
            }
            for m in status["members"]
        ]
        return {"set": status["set"], "term": status.get("term"), "members": members,
                "oplogWindowSeconds": self.oplog_window_seconds()}

    def oplog_window_seconds(self) -> int:
        """Newest minus oldest oplog ts. Alert in SECONDS, as a fraction of the longest maintenance op."""
        oplog = get_client().local["oplog.rs"]
        first = oplog.find_one({}, {"ts": 1}, sort=[("$natural", ASCENDING)])
        last = oplog.find_one({}, {"ts": 1}, sort=[("$natural", DESCENDING)])
        if not first or not last:
            return -1
        return last["ts"].time - first["ts"].time

    def shard_orders_collection(self) -> Doc:
        """{customerId: 1, _id: 1}: tenant-targeted routing; the _id suffix keeps a whale splittable."""
        return get_client().admin.command(
            "shardCollection", f"{self.db.name}.{ORDERS}", key={"customerId": 1, "_id": 1}
        )


# ================================================================ adapter


class MongoOrderStore:
    """OrderStore port on top of the showcase classes."""

    def __init__(self, showcase: MongoShowcase, transactions: MongoTransactions) -> None:
        self.showcase = showcase
        self.transactions = transactions

    def place_order(self, order: NewOrder) -> Order:
        return self.transactions.place_order(order)

    def find_order(self, order_id: str) -> Order | None:
        return self.showcase.find_order(order_id)

    def list_customer_orders(self, customer_id: str, limit: int, cursor: str | None) -> OrderPage:
        return self.showcase.list_customer_orders(customer_id, limit, cursor)

    def change_status(self, order_id: str, status: OrderStatus, expected_version: int) -> Order:
        return self.showcase.change_status_with_version(order_id, status, expected_version)

    def revenue_by_customer(self, since: datetime, limit: int) -> list[CustomerRevenue]:
        return self.showcase.revenue_by_customer(since, limit)

    def explain_customer_orders(self, customer_id: str) -> QueryPlanSummary:
        return self.showcase.explain_customer_orders(customer_id)

    def ensure_indexes(self) -> list[str]:
        return self.showcase.ensure_indexes()
