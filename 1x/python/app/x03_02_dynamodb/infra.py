"""DynamoDB showcase (boto3): one method per scenario, in the order of docs/03.02.dynamodb.md.

- Two APIs side by side:
  - client("dynamodb"): low-level, AttributeValue maps ({"S": "x"}), TypeSerializer/TypeDeserializer
  - resource("dynamodb").Table: plain Python values, Key/Attr condition builders, batch_writer
- Numbers come back as Decimal from both APIs; floats are rejected on write (use int or Decimal).
- No AWS call at import time: clients are created on first use via app.shared.aws.
- "status" is a reserved word in expressions: always use #name placeholders with the client API.
"""

import base64
import json
import time
import uuid
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from boto3.dynamodb.conditions import Attr, Key
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from botocore.exceptions import ClientError

from app.shared import aws
from app.shared.config import get_settings
from app.shared.retry import backoff, call_with_retry
from app.x03_02_dynamodb.domain import (
    ENTITY_ORDER,
    ORDER_PREFIX,
    PROFILE_SK,
    ChangeType,
    CursorPage,
    IdempotencyRecord,
    Order,
    OrderChange,
    OrderRef,
    OrderStatus,
    OrderSummary,
    PlaceAttempt,
    PlaceStatus,
    ProfileStats,
    VersionConflictError,
    gsi1_pk,
    gsi1_pk_shard,
    gsi1_pk_sharded,
    gsi1_sk,
    iso,
    parse_iso,
    pk_customer,
    sk_order,
    sk_order_bound,
)

Item = dict[str, Any]  # plain Python values (resource API)
AvItem = dict[str, dict[str, Any]]  # AttributeValue map (client API)

BATCH_WRITE_MAX = 25  # BatchWriteItem: up to 25 put/delete requests per call (Developer Guide, Service quotas)
BATCH_GET_MAX = 100  # BatchGetItem: up to 100 keys per call
MAX_BATCH_ATTEMPTS = 5
TX_LABELS = ["order", "idempotency", "profile"]
TTL_PRINCIPAL = "dynamodb.amazonaws.com"  # TTL deletes show up in streams with this principal

_SER = TypeSerializer()
_DESER = TypeDeserializer()


# ================================================================ mapping helpers


def to_av(item: Item) -> AvItem:
    """Plain dict -> AttributeValue map (client API)."""
    return {k: _SER.serialize(v) for k, v in item.items()}


def from_av(av: AvItem) -> Item:
    """AttributeValue map -> plain dict (numbers become Decimal)."""
    return {k: _DESER.deserialize(v) for k, v in av.items()}


def to_item(order: Order) -> Item:
    """Order -> plain item. GSI1 keys only for non-terminal statuses (sparse index)."""
    item: Item = {
        "PK": pk_customer(order.customer_id),
        "SK": sk_order(order.created_at, order.order_id),
        "entityType": ENTITY_ORDER,
        "customerId": order.customer_id,
        "orderId": order.order_id,
        "createdAt": iso(order.created_at),
        "status": order.status.value,
        "amountCents": order.amount_cents,
        "version": order.version,
    }
    if not order.status.is_terminal:
        item["GSI1PK"] = gsi1_pk(order.status)
        item["GSI1SK"] = gsi1_sk(order.created_at)
    if order.expires_at is not None:
        item["expiresAt"] = order.expires_at
    return item


def from_item(item: Item) -> Order:
    expires = item.get("expiresAt")
    return Order(
        customer_id=item["customerId"],
        order_id=item["orderId"],
        created_at=parse_iso(item["createdAt"]),
        status=OrderStatus(item["status"]),
        amount_cents=int(item["amountCents"]),
        version=int(item["version"]),
        expires_at=None if expires is None else int(expires),
    )


def summary_from_item(item: Item) -> OrderSummary:
    """GSI1 item: keys + INCLUDE projection only."""
    return OrderSummary(
        customer_id=item["customerId"],
        order_id=item["orderId"],
        created_at=parse_iso(item["GSI1SK"]),
        amount_cents=int(item["amountCents"]),
    )


def idempotency_to_item(r: IdempotencyRecord) -> Item:
    return {
        "idempotencyKey": r.idempotency_key,
        "requestHash": r.request_hash,
        "customerId": r.customer_id,
        "orderId": r.order_id,
        "orderCreatedAt": r.order_created_at,
        "expiresAt": r.expires_at,
    }


def idempotency_from_item(item: Item) -> IdempotencyRecord:
    return IdempotencyRecord(
        idempotency_key=item["idempotencyKey"],
        request_hash=item["requestHash"],
        customer_id=item["customerId"],
        order_id=item["orderId"],
        order_created_at=item["orderCreatedAt"],
        expires_at=int(item["expiresAt"]),
    )


def key_of(ref: OrderRef) -> Item:
    return {"PK": ref.pk, "SK": ref.sk}


def _error_code(e: ClientError) -> str:
    return str(e.response.get("Error", {}).get("Code", ""))


# ================================================================ pagination cursor

TABLE_KEYS = frozenset({"PK", "SK"})
GSI1_KEYS = frozenset({"PK", "SK", "GSI1PK", "GSI1SK"})


def encode_cursor(last_evaluated_key: Item | None) -> str | None:
    """Plain LastEvaluatedKey -> opaque base64url cursor. None/empty -> None (= no more pages).

    Works because every key attribute of x-orders / GSI1 is a string.
    Catch: base64 is not secrecy; HMAC-sign or encrypt the cursor if key values are sensitive.
    """
    if not last_evaluated_key:
        return None
    if not all(isinstance(v, str) for v in last_evaluated_key.values()):
        raise ValueError("cursor supports string keys only")
    raw = json.dumps(last_evaluated_key, sort_keys=True, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(cursor: str | None, expected_names: frozenset[str], pk_name: str, expected_pk: str) -> Item | None:
    """Cursor -> plain ExclusiveStartKey; validates key names and the partition so clients can't jump partitions."""
    if not cursor:
        return None
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        key = json.loads(base64.urlsafe_b64decode(padded.encode()))
    except (ValueError, json.JSONDecodeError) as e:
        raise ValueError("malformed cursor") from e
    if not isinstance(key, dict) or set(key) != expected_names:
        raise ValueError("cursor keys do not match this query")
    if key.get(pk_name) != expected_pk:
        raise ValueError("cursor belongs to another partition")
    return key


# ================================================================ transaction cancellation reasons


@dataclass(frozen=True)
class CancellationReason:
    index: int
    label: str
    code: str
    message: str | None
    item: Item  # old item, only when that action asked for ReturnValuesOnConditionCheckFailure=ALL_OLD


_TRANSIENT_CODES = {"None", "TransactionConflict", "ThrottlingError", "ProvisionedThroughputExceeded"}


def parse_cancellation(e: ClientError, labels: list[str]) -> list[CancellationReason]:
    """TransactionCanceledException -> labeled reasons. Positional: reasons[i] belongs to TransactItems[i].

    ConditionalCheckFailed = business outcome (don't retry); TransactionConflict = concurrent writer (retry).
    botocore puts the modeled CancellationReasons list at the top level of e.response.
    """
    raw: list[dict[str, Any]] = e.response.get("CancellationReasons") or []
    reasons: list[CancellationReason] = []
    for i, r in enumerate(raw):
        reasons.append(
            CancellationReason(
                index=i,
                label=labels[i] if i < len(labels) else f"item{i}",
                code=str(r.get("Code", "None")),
                message=r.get("Message"),
                item=from_av(r["Item"]) if r.get("Item") else {},
            )
        )
    return reasons


def is_retryable_transaction_error(e: Exception) -> bool:
    if not isinstance(e, ClientError):
        return False
    code = _error_code(e)
    if code == "TransactionInProgressException":
        return True  # same ClientRequestToken still being applied: wait and resend
    if code != "TransactionCanceledException":
        return False
    reasons = parse_cancellation(e, TX_LABELS)
    return bool(reasons) and all(r.code in _TRANSIENT_CODES for r in reasons) and any(r.code != "None" for r in reasons)


def _failed_with(reasons: list[CancellationReason], label: str, code: str) -> CancellationReason | None:
    return next((r for r in reasons if r.label == label and r.code == code), None)


# ================================================================ streams record shape


def handle_stream_record(record: dict[str, Any]) -> OrderChange | None:
    """Parse one DynamoDB Streams record (NEW_AND_OLD_IMAGES) into an OrderChange; non-order items -> None.

    Shape (GetRecords and the Lambda event): eventID, eventName INSERT|MODIFY|REMOVE,
    dynamodb.{Keys, NewImage, OldImage, SequenceNumber}, userIdentity for TTL deletes.
    Catch: processing is at-least-once (consumers retry batches); dedupe by eventID or item version.
    Catch: streams keep records 24 h; a consumer down longer loses changes.
    """
    ddb = record.get("dynamodb", {})
    keys = from_av(ddb.get("Keys", {}))
    if not str(keys.get("SK", "")).startswith(ORDER_PREFIX):
        return None
    before = from_item(from_av(ddb["OldImage"])) if ddb.get("OldImage") else None
    after = from_item(from_av(ddb["NewImage"])) if ddb.get("NewImage") else None
    identity = record.get("userIdentity") or {}
    ttl = (
        record.get("eventName") == "REMOVE"
        and identity.get("type") == "Service"
        and identity.get("principalId") == TTL_PRINCIPAL
    )
    return OrderChange(
        event_id=str(record.get("eventID", "")),
        sequence_number=str(ddb.get("SequenceNumber", "")),
        type=ChangeType(record["eventName"]),
        before=before,
        after=after,
        ttl_expiry=ttl,
    )


def sample_modify_record(before: Order, after: Order) -> dict[str, Any]:
    """Hand-built MODIFY record: documents the exact shape and lets tests run without AWS."""
    new_av = to_av(to_item(after))
    return {
        "eventID": "sample-event-1",
        "eventName": "MODIFY",
        "eventSource": "aws:dynamodb",
        "dynamodb": {
            "Keys": {"PK": new_av["PK"], "SK": new_av["SK"]},
            "OldImage": to_av(to_item(before)),
            "NewImage": new_av,
            "SequenceNumber": "100000000000000000001",
            "StreamViewType": "NEW_AND_OLD_IMAGES",
        },
    }


# ================================================================ showcase


def _chunks(items: list[Any], size: int) -> Iterator[list[Any]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


class DynamoDbShowcase:
    """All scenarios; methods ending in _resource use the Table API, the others the low-level client."""

    def __init__(self) -> None:
        s = get_settings()
        self.orders_table = s.dynamodb_orders_table
        self.idempotency_table = s.dynamodb_idempotency_table
        self.gsi1 = s.dynamodb_gsi1_name

    # Lazy: created on first call; boto3 clients are thread-safe, resources are not (one per thread in real apps).
    @property
    def client(self) -> Any:
        return aws.client("dynamodb")

    @property
    def table(self) -> Any:
        return aws.resource("dynamodb").Table(self.orders_table)

    # ------------------------------------------------------------ 1. put create-only, get strong vs eventual

    def put_order_create_only(self, order: Order) -> bool:
        """Create-only put (client): attribute_not_exists(PK) checks the ONE item with this PK+SK, not the partition.

        Use for every insert; a plain PutItem silently replaces the whole item.
        Catch: a failed condition still consumes WCU; ALL_OLD returns the existing item in e.response["Item"].
        """
        try:
            self.client.put_item(
                TableName=self.orders_table,
                Item=to_av(to_item(order)),
                ConditionExpression="attribute_not_exists(PK)",
                ReturnValuesOnConditionCheckFailure="ALL_OLD",
            )
            return True
        except ClientError as e:
            if _error_code(e) == "ConditionalCheckFailedException":
                return False
            raise

    def put_order_create_only_resource(self, order: Order) -> bool:
        """Same create-only put with the Table API: plain values + Attr condition builder (placeholders auto-made).

        Catch: the exception class lives on table.meta.client.exceptions; matching the error code is simpler.
        """
        try:
            self.table.put_item(Item=to_item(order), ConditionExpression=Attr("PK").not_exists())
            return True
        except ClientError as e:
            if _error_code(e) == "ConditionalCheckFailedException":
                return False
            raise

    def get_order(self, ref: OrderRef, consistent: bool = False) -> Order | None:
        """GetItem (client). Eventual (default): 0.5 RCU per 4 KB, may miss the latest write.

        ConsistentRead=True: 2x cost, served by the partition leader; base table and LSI only.
        Catch: a missing item is a response without "Item", not an error.
        """
        resp = self.client.get_item(
            TableName=self.orders_table, Key=to_av(key_of(ref)), ConsistentRead=consistent
        )
        return from_item(from_av(resp["Item"])) if "Item" in resp else None

    def get_order_resource(self, ref: OrderRef, consistent: bool = False) -> Order | None:
        """GetItem (Table API): already-deserialized values, numbers as Decimal."""
        resp = self.table.get_item(Key=key_of(ref), ConsistentRead=consistent)
        return from_item(resp["Item"]) if "Item" in resp else None

    # ------------------------------------------------------------ 2. UpdateItem: SET / ADD / REMOVE + ReturnValues

    def record_order_on_profile(self, customer_id: str, amount_cents: int, at: datetime) -> ProfileStats:
        """All clause kinds on the PROFILE item (upsert). SET overwrites, if_not_exists keeps the first value,
        ADD increments atomically, REMOVE deletes an attribute. ReturnValues=UPDATED_NEW: no read-after-write.

        Catch: ADD is not idempotent; a blind retry after a timeout double-counts.
        """
        resp = self.client.update_item(
            TableName=self.orders_table,
            Key=to_av({"PK": pk_customer(customer_id), "SK": PROFILE_SK}),
            UpdateExpression=(
                "SET lastOrderAt = :at, displayName = if_not_exists(displayName, :anon) "
                "ADD orderCount :one, totalSpentCents :amount "
                "REMOVE pendingCartId"
            ),
            ExpressionAttributeValues=to_av({":at": iso(at), ":anon": "anonymous", ":one": 1, ":amount": amount_cents}),
            ReturnValues="UPDATED_NEW",
        )
        return self._profile_stats(customer_id, from_av(resp.get("Attributes", {})))

    def record_order_on_profile_resource(self, customer_id: str, amount_cents: int, at: datetime) -> ProfileStats:
        """Same update with the Table API: expression strings stay, values are plain Python."""
        resp = self.table.update_item(
            Key={"PK": pk_customer(customer_id), "SK": PROFILE_SK},
            UpdateExpression=(
                "SET lastOrderAt = :at, displayName = if_not_exists(displayName, :anon) "
                "ADD orderCount :one, totalSpentCents :amount "
                "REMOVE pendingCartId"
            ),
            ExpressionAttributeValues={":at": iso(at), ":anon": "anonymous", ":one": 1, ":amount": amount_cents},
            ReturnValues="UPDATED_NEW",
        )
        return self._profile_stats(customer_id, resp.get("Attributes", {}))

    @staticmethod
    def _profile_stats(customer_id: str, attrs: Item) -> ProfileStats:
        return ProfileStats(
            customer_id=customer_id,
            order_count=int(attrs.get("orderCount", 0)),
            total_spent_cents=int(attrs.get("totalSpentCents", 0)),
            last_order_at=attrs.get("lastOrderAt"),
        )

    # ------------------------------------------------------------ 3. optimistic lock (version condition)

    def change_status_with_version(self, ref: OrderRef, status: OrderStatus, expected_version: int) -> Order:
        """Status change guarded by version = :expected, incrementing version in the same write.

        Terminal statuses REMOVE GSI1PK/GSI1SK so the order leaves the "pending" index (sparse GSI).
        Catch: on conflict ALL_OLD returns the winner's item; no item at all = the order doesn't exist.
        """
        values: Item = {":new": status.value, ":expected": expected_version, ":one": 1}
        if status.is_terminal:
            update = "SET #status = :new, #version = #version + :one REMOVE GSI1PK, GSI1SK"
        else:
            update = "SET #status = :new, #version = #version + :one, GSI1PK = :gsiPk"
            values[":gsiPk"] = gsi1_pk(status)
        try:
            resp = self.client.update_item(
                TableName=self.orders_table,
                Key=to_av(key_of(ref)),
                UpdateExpression=update,
                ConditionExpression="attribute_exists(PK) AND #version = :expected",
                ExpressionAttributeNames={"#status": "status", "#version": "version"},
                ExpressionAttributeValues=to_av(values),
                ReturnValues="ALL_NEW",
                ReturnValuesOnConditionCheckFailure="ALL_OLD",
            )
            return from_item(from_av(resp["Attributes"]))
        except ClientError as e:
            if _error_code(e) == "ConditionalCheckFailedException":
                old = e.response.get("Item")
                raise VersionConflictError(from_item(from_av(old)) if old else None) from e
            raise

    def change_status_with_version_resource(self, ref: OrderRef, status: OrderStatus, expected_version: int) -> Order:
        """Same optimistic lock with Attr builders; boto3 merges its generated placeholders with ours.

        Catch: error responses are NOT deserialized by the resource layer; e.response["Item"] is still AttributeValue.
        """
        names = {"#status": "status", "#version": "version"}
        values: Item = {":new": status.value, ":one": 1}
        if status.is_terminal:
            update = "SET #status = :new, #version = #version + :one REMOVE GSI1PK, GSI1SK"
        else:
            update = "SET #status = :new, #version = #version + :one, GSI1PK = :gsiPk"
            values[":gsiPk"] = gsi1_pk(status)
        try:
            resp = self.table.update_item(
                Key=key_of(ref),
                UpdateExpression=update,
                ConditionExpression=Attr("PK").exists() & Attr("version").eq(expected_version),
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
                ReturnValues="ALL_NEW",
                ReturnValuesOnConditionCheckFailure="ALL_OLD",
            )
            return from_item(resp["Attributes"])
        except ClientError as e:
            if _error_code(e) == "ConditionalCheckFailedException":
                old = e.response.get("Item")
                raise VersionConflictError(from_item(from_av(old)) if old else None) from e
            raise

    # ------------------------------------------------------------ 4. Query: PK + begins_with / between, GSI

    def query_orders_by_prefix(self, customer_id: str, limit: int) -> list[Order]:
        """Newest orders first: PK equality + begins_with(SK) skips the PROFILE item.

        Key conditions narrow the read itself (you pay only for matches), unlike filters.
        Catch: one call returns at most Limit items or 1 MB; this is a single page.
        """
        resp = self.client.query(
            TableName=self.orders_table,
            KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
            ExpressionAttributeValues=to_av({":pk": pk_customer(customer_id), ":prefix": ORDER_PREFIX}),
            ScanIndexForward=False,
            Limit=limit,
        )
        return [from_item(from_av(i)) for i in resp.get("Items", [])]

    def query_orders_between(self, customer_id: str, start: datetime, end: datetime) -> list[Order]:
        """Time range with BETWEEN (inclusive); SKs end in '#<orderId>' so it behaves as [start, end).

        Uses the paginator, which follows LastEvaluatedKey to the end of the range.
        Catch: only correct with fixed-width timestamps (domain.iso).
        """
        paginator = self.client.get_paginator("query")
        pages = paginator.paginate(
            TableName=self.orders_table,
            KeyConditionExpression="PK = :pk AND SK BETWEEN :from AND :to",
            ExpressionAttributeValues=to_av(
                {":pk": pk_customer(customer_id), ":from": sk_order_bound(start), ":to": sk_order_bound(end)}
            ),
        )
        return [from_item(from_av(i)) for page in pages for i in page.get("Items", [])]

    def query_orders_resource(
        self, customer_id: str, limit: int, start: datetime | None = None, end: datetime | None = None
    ) -> list[Order]:
        """Table API query with Key builders: begins_with, or between when a range is given.

        Catch: Key(...) is for KeyConditionExpression only; Attr(...) is for filters/conditions.
        """
        pk_cond = Key("PK").eq(pk_customer(customer_id))
        if start is not None and end is not None:
            cond = pk_cond & Key("SK").between(sk_order_bound(start), sk_order_bound(end))
        else:
            cond = pk_cond & Key("SK").begins_with(ORDER_PREFIX)
        resp = self.table.query(KeyConditionExpression=cond, ScanIndexForward=False, Limit=limit)
        return [from_item(i) for i in resp.get("Items", [])]

    def query_by_status(self, status: OrderStatus, limit: int) -> list[OrderSummary]:
        """GSI query: all orders in a status, oldest first. Keys + INCLUDE projection only.

        GSIs are updated asynchronously: eventually consistent only; ConsistentRead=True is a ValidationException.
        Catch: never decide a write from a GSI read; re-read the base item with a strong read.
        """
        resp = self.client.query(
            TableName=self.orders_table,
            IndexName=self.gsi1,
            KeyConditionExpression="GSI1PK = :pk",
            ExpressionAttributeValues=to_av({":pk": gsi1_pk(status)}),
            ScanIndexForward=True,
            Limit=limit,
        )
        return [summary_from_item(from_av(i)) for i in resp.get("Items", [])]

    def query_by_status_resource(self, status: OrderStatus, limit: int) -> list[OrderSummary]:
        """Same GSI query with the Table API."""
        resp = self.table.query(
            IndexName=self.gsi1, KeyConditionExpression=Key("GSI1PK").eq(gsi1_pk(status)), Limit=limit
        )
        return [summary_from_item(i) for i in resp.get("Items", [])]

    # ------------------------------------------------------------ 5. pagination: LastEvaluatedKey <-> cursor

    def query_orders_page(self, customer_id: str, limit: int, cursor: str | None) -> CursorPage:
        """API pagination: one Query per call; LastEvaluatedKey -> opaque cursor -> ExclusiveStartKey.

        The cursor is validated against this customer's PK, so a client can't page another partition.
        Catch: a short or empty page can still carry a cursor (1 MB cap, filters); only None means done.
        """
        pk = pk_customer(customer_id)
        start_key = decode_cursor(cursor, TABLE_KEYS, "PK", pk)
        kwargs: dict[str, Any] = {
            "TableName": self.orders_table,
            "KeyConditionExpression": "PK = :pk AND begins_with(SK, :prefix)",
            "ExpressionAttributeValues": to_av({":pk": pk, ":prefix": ORDER_PREFIX}),
            "ScanIndexForward": False,
            "Limit": limit,
        }
        if start_key:
            kwargs["ExclusiveStartKey"] = to_av(start_key)
        resp = self.client.query(**kwargs)
        items = [from_item(from_av(i)) for i in resp.get("Items", [])]
        lek = resp.get("LastEvaluatedKey")
        return CursorPage(items=items, next_cursor=encode_cursor(from_av(lek)) if lek else None)

    def query_all_orders(self, customer_id: str, page_size: int = 100) -> list[Order]:
        """Internal 'read everything': the paginator loops on LastEvaluatedKey lazily.

        PaginationConfig.PageSize sets Limit per request. Catch: the paginator's StartingToken is botocore's own
        format, not the raw key; don't hand it to API clients (use query_orders_page). Not a snapshot.
        """
        pages = self.client.get_paginator("query").paginate(
            TableName=self.orders_table,
            KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
            ExpressionAttributeValues=to_av({":pk": pk_customer(customer_id), ":prefix": ORDER_PREFIX}),
            PaginationConfig={"PageSize": page_size},
        )
        return [from_item(from_av(i)) for page in pages for i in page.get("Items", [])]

    # ------------------------------------------------------------ 6. Scan + parallel Scan (and why to avoid)

    def scan_all_orders(self) -> Iterator[Order]:
        """Full-table Scan: reads EVERY item, then filters. You pay for ScannedCount, not Count.

        Avoid in request paths; prefer a GSI, or Export to S3 + Athena for analytics. Generator keeps memory flat.
        """
        pages = self.client.get_paginator("scan").paginate(
            TableName=self.orders_table,
            FilterExpression="entityType = :order",
            ExpressionAttributeValues=to_av({":order": ENTITY_ORDER}),
        )
        for page in pages:
            for i in page.get("Items", []):
                yield from_item(from_av(i))

    def parallel_scan(self, total_segments: int) -> list[Order]:
        """Parallel Scan: TotalSegments splits the key space; each worker loops its own LastEvaluatedKey.

        Use only for offline jobs (backfills, migrations). Shares the client (thread-safe), not a resource.
        Catch: N workers consume N times the throughput at once and can throttle live traffic.
        """

        def scan_segment(segment: int) -> list[Order]:
            out: list[Order] = []
            kwargs: dict[str, Any] = {
                "TableName": self.orders_table,
                "Segment": segment,
                "TotalSegments": total_segments,
                "FilterExpression": "entityType = :order",
                "ExpressionAttributeValues": to_av({":order": ENTITY_ORDER}),
            }
            while True:
                resp = self.client.scan(**kwargs)
                out.extend(from_item(from_av(i)) for i in resp.get("Items", []))
                lek = resp.get("LastEvaluatedKey")
                if not lek:
                    return out
                kwargs["ExclusiveStartKey"] = lek

        with ThreadPoolExecutor(max_workers=total_segments) as pool:
            results = list(pool.map(scan_segment, range(total_segments)))
        return [o for seg in results for o in seg]

    # ------------------------------------------------------------ 7. BatchWriteItem / BatchGetItem + unprocessed retry

    def batch_put_orders(self, orders: list[Order]) -> None:
        """Manual BatchWriteItem: chunks of 25, resend only UnprocessedItems with full-jitter backoff.

        Not atomic, no conditions. A 200 response with UnprocessedItems is a partial failure.
        Catch: duplicate keys inside one request -> ValidationException; give up loudly after N attempts.
        """
        for chunk in _chunks(orders, BATCH_WRITE_MAX):
            keys = {(o.ref.pk, o.ref.sk) for o in chunk}
            if len(keys) != len(chunk):
                raise ValueError("duplicate key in one batch")
            pending: dict[str, list[Any]] = {
                self.orders_table: [{"PutRequest": {"Item": to_av(to_item(o))}} for o in chunk]
            }
            for attempt in range(MAX_BATCH_ATTEMPTS):
                if attempt > 0:
                    time.sleep(backoff(attempt))
                resp = self.client.batch_write_item(RequestItems=pending)
                pending = resp.get("UnprocessedItems") or {}
                if not pending:
                    break
            if pending:
                left = sum(len(v) for v in pending.values())
                raise RuntimeError(f"{left} items still unprocessed after retries")

    def batch_put_orders_resource(self, orders: list[Order]) -> None:
        """Table.batch_writer: buffers 25 items per call and automatically re-queues UnprocessedItems.

        overwrite_by_pkeys de-duplicates keys inside a buffer (avoids the duplicate-key ValidationException).
        Catch: the re-queue has no backoff of its own (it relies on the client's retry config) and is not atomic.
        """
        with self.table.batch_writer(overwrite_by_pkeys=["PK", "SK"]) as writer:
            for o in orders:
                writer.put_item(Item=to_item(o))

    def batch_get_orders(self, refs: list[OrderRef], consistent: bool = False) -> list[Order]:
        """Manual BatchGetItem: chunks of 100 unique keys, follow UnprocessedKeys with full-jitter backoff.

        Results are unordered and missing keys are simply absent.
        Catch: there is no batch_reader helper; this loop is the pattern.
        """
        unique = list({(r.pk, r.sk): r for r in refs}.values())  # duplicate keys -> ValidationException
        found: list[Order] = []
        for chunk in _chunks(unique, BATCH_GET_MAX):
            pending: dict[str, Any] = {
                self.orders_table: {"Keys": [to_av(key_of(r)) for r in chunk], "ConsistentRead": consistent}
            }
            for attempt in range(MAX_BATCH_ATTEMPTS):
                if attempt > 0:
                    time.sleep(backoff(attempt))
                resp = self.client.batch_get_item(RequestItems=pending)
                found.extend(from_item(from_av(i)) for i in resp.get("Responses", {}).get(self.orders_table, []))
                pending = resp.get("UnprocessedKeys") or {}
                if not pending:
                    break
            if pending:
                raise RuntimeError("keys still unprocessed after retries")
        return found

    # ------------------------------------------------------------ 8. TransactWriteItems + cancellation reasons

    def place_order_transaction(self, order: Order, record: IdempotencyRecord, now: datetime) -> PlaceAttempt:
        """Atomic: order (create-only) + idempotency record (create-only or expired) + profile counters. 2x WCU.

        ClientRequestToken makes resends of THIS call idempotent for 10 minutes; the idempotency item covers
        later client retries. Conflicts/throttling are retried with backoff; condition failures are outcomes.
        Catch: TTL deletion is lazy, so an expired-but-present record must count as absent (expiresAt < :now).
        """
        epoch_now = int(now.timestamp())
        items = [
            {
                "Put": {
                    "TableName": self.orders_table,
                    "Item": to_av(to_item(order)),
                    "ConditionExpression": "attribute_not_exists(PK)",
                }
            },
            {
                "Put": {
                    "TableName": self.idempotency_table,
                    "Item": to_av(idempotency_to_item(record)),
                    "ConditionExpression": "attribute_not_exists(idempotencyKey) OR expiresAt < :now",
                    "ExpressionAttributeValues": to_av({":now": epoch_now}),
                    "ReturnValuesOnConditionCheckFailure": "ALL_OLD",  # stored record comes back in the reason
                }
            },
            {
                "Update": {
                    "TableName": self.orders_table,
                    "Key": to_av({"PK": pk_customer(order.customer_id), "SK": PROFILE_SK}),
                    "UpdateExpression": "SET lastOrderAt = :at ADD orderCount :one, totalSpentCents :amount",
                    "ExpressionAttributeValues": to_av(
                        {":at": iso(order.created_at), ":one": 1, ":amount": order.amount_cents}
                    ),
                }
            },
        ]  # order MUST match TX_LABELS
        # Token (1-36 chars): derived from key + fresh order id, so a different request never reuses it
        # (IdempotentParameterMismatchException) while resends of this exact call still dedupe.
        token = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{record.idempotency_key}|{order.order_id}"))

        def call() -> Any:
            return self.client.transact_write_items(TransactItems=items, ClientRequestToken=token)

        try:
            call_with_retry(call, is_retryable_transaction_error)
            return PlaceAttempt(PlaceStatus.COMMITTED)
        except ClientError as e:
            if _error_code(e) != "TransactionCanceledException":
                raise
            reasons = parse_cancellation(e, TX_LABELS)
            idem = _failed_with(reasons, "idempotency", "ConditionalCheckFailed")
            if idem is not None:
                return PlaceAttempt(PlaceStatus.KEY_ALREADY_USED, idempotency_from_item(idem.item))
            if _failed_with(reasons, "order", "ConditionalCheckFailed"):
                return PlaceAttempt(PlaceStatus.ORDER_ALREADY_EXISTS)
            raise

    # ------------------------------------------------------------ 9. TTL write + expired-item filter

    def expire_order_after(self, ref: OrderRef, ttl: timedelta) -> int:
        """TTL: expiresAt = epoch SECONDS; a background process deletes the item later, at no WCU cost.

        Catch: deletion is not exact (typically within days); epoch millis would mean 'never' in practice.
        """
        expires_at = int((datetime.now(timezone.utc) + ttl).timestamp())
        self.client.update_item(
            TableName=self.orders_table,
            Key=to_av(key_of(ref)),
            UpdateExpression="SET expiresAt = :exp",
            ConditionExpression="attribute_exists(PK)",  # don't create a stub item for a missing order
            ExpressionAttributeValues=to_av({":exp": expires_at}),
        )
        return expires_at

    def query_live_orders(self, customer_id: str, now: datetime) -> list[Order]:
        """Hide expired items TTL hasn't deleted yet. The filter runs after the read (you still pay for them).

        Catch: Limit counts items before the filter, so pages can come back short.
        """
        resp_items: list[Order] = []
        pages = self.client.get_paginator("query").paginate(
            TableName=self.orders_table,
            KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
            FilterExpression="attribute_not_exists(expiresAt) OR expiresAt > :now",
            ExpressionAttributeValues=to_av(
                {":pk": pk_customer(customer_id), ":prefix": ORDER_PREFIX, ":now": int(now.timestamp())}
            ),
        )
        for page in pages:
            resp_items.extend(from_item(from_av(i)) for i in page.get("Items", []))
        return resp_items

    # ------------------------------------------------------------ 10. hot partition: write sharding + scatter-gather

    def put_order_sharded_status(self, order: Order, shards: int) -> bool:
        """Every new order writes GSI1PK=STATUS#PENDING: one GSI partition (max 1,000 WCU) takes all writes, and
        GSI throttling back-pressures base writes. Sharding spreads it over STATUS#PENDING#0..N-1.

        Catch: a variant of the .tf key design; every writer and reader must use the same N and suffix function.
        """
        item = to_item(order)
        if not order.status.is_terminal:
            item["GSI1PK"] = gsi1_pk_sharded(order.status, order.order_id, shards)
        try:
            self.client.put_item(
                TableName=self.orders_table, Item=to_av(item), ConditionExpression="attribute_not_exists(PK)"
            )
            return True
        except ClientError as e:
            if _error_code(e) == "ConditionalCheckFailedException":
                return False
            raise

    def scatter_gather_by_status(self, status: OrderStatus, shards: int, limit: int) -> list[OrderSummary]:
        """Query all N shards in parallel, merge by GSI1SK, keep the oldest `limit` (exact: each shard returns <= limit).

        Catch: N requests per read (N x cost, latency = slowest shard); pick N from peak writes / 1,000 WCU.
        """

        def query_shard(shard: int) -> list[OrderSummary]:
            resp = self.client.query(
                TableName=self.orders_table,
                IndexName=self.gsi1,
                KeyConditionExpression="GSI1PK = :pk",
                ExpressionAttributeValues=to_av({":pk": gsi1_pk_shard(status, shard)}),
                ScanIndexForward=True,
                Limit=limit,
            )
            return [summary_from_item(from_av(i)) for i in resp.get("Items", [])]

        with ThreadPoolExecutor(max_workers=min(shards, 16)) as pool:
            merged = [s for part in pool.map(query_shard, range(shards)) for s in part]
        return sorted(merged, key=lambda s: s.created_at)[:limit]


# ================================================================ port adapter


class DynamoDbOrderStore:
    """domain.OrderStore backed by the low-level showcase methods."""

    def __init__(self, dynamo: DynamoDbShowcase) -> None:
        self.dynamo = dynamo

    def place_order(self, order: Order, record: IdempotencyRecord, now: datetime) -> PlaceAttempt:
        return self.dynamo.place_order_transaction(order, record, now)

    def get_order(self, ref: OrderRef, consistent: bool) -> Order | None:
        return self.dynamo.get_order(ref, consistent)

    def list_orders(self, customer_id: str, limit: int, cursor: str | None) -> CursorPage:
        return self.dynamo.query_orders_page(customer_id, limit, cursor)

    def list_by_status(self, status: OrderStatus, limit: int) -> list[OrderSummary]:
        return self.dynamo.query_by_status(status, limit)

    def change_status(self, ref: OrderRef, status: OrderStatus, expected_version: int) -> Order:
        return self.dynamo.change_status_with_version(ref, status, expected_version)
