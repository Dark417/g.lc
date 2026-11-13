"""Aurora PostgreSQL showcase (psycopg 3 + psycopg_pool), in the order of docs/03.01.aurora-postgres.md.

- Two pools: writer (cluster endpoint) and reader (reader endpoint), created lazily on first use, never at import.
- Connections run in autocommit mode; transactions are explicit `with conn.transaction():` blocks.
- Each new physical connection logs in with a fresh 15-minute IAM token (callable pool kwargs).
- PgOrderStore = one method per scenario, bound to the connection of one transaction.
"""

from __future__ import annotations

import base64
import threading
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from datetime import datetime, timedelta
from typing import Any

import psycopg
from psycopg import errors, pq
from psycopg.rows import DictRow, dict_row
from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool, PoolTimeout

from app.shared import aws
from app.shared.config import Settings, get_settings
from app.x03_01_aurora.domain import (
    BusinessRuleViolation,
    Isolation,
    Job,
    JobStatus,
    LeaseLost,
    NewOrder,
    Order,
    OrderNotFound,
    OrderStatus,
    Page,
    StockLevel,
    VersionConflict,
)

# Slice-local knobs not (yet) in Settings; see the coordinator note in the slice report.
POOL_TIMEOUT_S = (
    3.0  # wait for a free connection, then fail fast (Hikari connectionTimeout)
)
POOL_MAX_IDLE_S = 300.0  # close idle connections above min_size (Hikari idleTimeout)
STATEMENT_TIMEOUT_MS = 15_000  # server cancels runaway statements (57014)
LOCK_TIMEOUT = "2s"  # SET LOCAL before FOR UPDATE: 55P03 instead of an endless wait
SSL_MODE = "verify-full"  # CA chain + hostname; "require" checks neither
SSL_ROOT_CERT = "/etc/ssl/certs/rds-global-bundle.pem"
APPLICATION_NAME = "x-aurora-py"

ORDER_COLUMNS = "id, customer_id, sku, quantity, amount_cents, status, version, idempotency_key, attrs, created_at, updated_at"

# Same DDL as the Java resource x03_01_aurora/schema.sql. Statements are split on ';' (no ';' inside comments).
# Admin prerequisite (master user): CREATE USER x_app, GRANT rds_iam TO x_app, GRANT CREATE ON SCHEMA public TO x_app.
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS x_order (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     TEXT        NOT NULL,
    sku             TEXT        NOT NULL,
    quantity        INT         NOT NULL CHECK (quantity > 0),
    amount_cents    BIGINT      NOT NULL CHECK (amount_cents >= 0),
    status          TEXT        NOT NULL DEFAULT 'NEW',
    version         INT         NOT NULL DEFAULT 0,
    idempotency_key TEXT        UNIQUE,
    attrs           JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS x_order_customer_created_id_idx ON x_order (customer_id, created_at, id);
CREATE INDEX IF NOT EXISTS x_order_attrs_gin ON x_order USING GIN (attrs jsonb_path_ops);
CREATE TABLE IF NOT EXISTS x_inventory (
    sku        TEXT        PRIMARY KEY,
    on_hand    INT         NOT NULL CHECK (on_hand >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS x_job (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kind         TEXT        NOT NULL,
    payload      JSONB       NOT NULL,
    status       TEXT        NOT NULL DEFAULT 'READY',
    attempts     INT         NOT NULL DEFAULT 0,
    run_after    TIMESTAMPTZ NOT NULL DEFAULT now(),
    locked_by    TEXT,
    locked_until TIMESTAMPTZ,
    last_error   TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS x_job_ready_idx ON x_job (run_after, id) WHERE status = 'READY';
CREATE INDEX IF NOT EXISTS x_job_running_lease_idx ON x_job (locked_until) WHERE status = 'RUNNING';
CREATE TABLE IF NOT EXISTS x_audit (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    action     TEXT        NOT NULL,
    detail     TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);
"""


# ===================================================================== IAM auth token


def iam_token(host: str, port: int, user: str, region: str) -> str:
    """Fresh IAM auth token for one login: SigV4-presigned rds-db:connect, signed locally (no network call).

    When to use: every new physical connection when IAM auth is on.
    Catch: valid 15 min and checked only at login; signed for this exact host/port/user, so sign the endpoint you dial.
    """
    return aws.client("rds").generate_db_auth_token(
        DBHostname=host, Port=port, DBUsername=user, Region=region
    )


# ===================================================================== retry classification

_RETRYABLE_STATES = {"40001", "40P01", "25006", "55P03", "57P01", "57P02", "57P03"}


def is_retryable(exc: BaseException) -> bool:
    """True when a fresh transaction may succeed.

    - SerializationFailure (40001) / DeadlockDetected (40P01): the server picked this transaction as the victim.
    - OperationalError with SQLSTATE 08xxx or none (client side): connection lost, e.g. failover; commit may be unknown.
    - AdminShutdown / CrashShutdown / CannotConnectNow (57P0x): node restarting during failover.
    - ReadOnlySqlTransaction (25006): writer pool reached a demoted writer (stale DNS); that connection is discarded.
    - LockNotAvailable (55P03): lock_timeout under contention.
    - Not retried: PoolTimeout (saturated: shed load), constraint violations, QueryCanceled (statement_timeout).
    """
    if isinstance(exc, PoolTimeout):
        return False
    if isinstance(exc, (errors.SerializationFailure, errors.DeadlockDetected)):
        return True
    if isinstance(exc, psycopg.Error):
        state = exc.sqlstate
        if state is None:
            return isinstance(exc, psycopg.OperationalError)
        return state in _RETRYABLE_STATES or state.startswith("08")
    return False


# ===================================================================== pools


class AuroraPools:
    """Writer + reader ConnectionPool, created on first use (thread-safe), so importing makes no connection."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._lock = threading.Lock()
        self._writer: ConnectionPool[psycopg.Connection[DictRow]] | None = None
        self._reader: ConnectionPool[psycopg.Connection[DictRow]] | None = None

    def writer(self) -> ConnectionPool[psycopg.Connection[DictRow]]:
        with self._lock:
            if self._writer is None:
                self._writer = self._make_pool(
                    "x-aurora-writer", self._settings.aurora_writer_endpoint, False
                )
            return self._writer

    def reader(self) -> ConnectionPool[psycopg.Connection[DictRow]]:
        with self._lock:
            if self._reader is None:
                self._reader = self._make_pool(
                    "x-aurora-reader", self._settings.aurora_reader_endpoint, True
                )
            return self._reader

    def _base_kwargs(self, host: str, read_only: bool) -> dict[str, Any]:
        """libpq connection keys: TLS verify-full, timeouts, keepalives, autocommit, dict rows.

        Catch: without TCP keepalives a half-open socket after failover can hang until the OS gives up.
        """
        s = self._settings
        options = f"-c statement_timeout={STATEMENT_TIMEOUT_MS}"
        if read_only:
            options += " -c default_transaction_read_only=on"  # an accidental write to a reader fails loudly
        kwargs: dict[str, Any] = {
            "host": host,
            "port": s.aurora_port,
            "dbname": s.aurora_database,
            "user": s.aurora_username,
            "sslmode": SSL_MODE,
            "connect_timeout": 5,
            "application_name": APPLICATION_NAME,
            "options": options,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 3,
            "autocommit": True,  # transactions are explicit: with conn.transaction()
            "row_factory": dict_row,
        }
        if SSL_MODE.startswith("verify"):
            kwargs["sslrootcert"] = SSL_ROOT_CERT
        return kwargs

    def _kwargs_supplier(
        self, host: str, read_only: bool
    ) -> Callable[[], dict[str, Any]]:
        """Callable pool kwargs: psycopg_pool (>= 3.3) calls it once per NEW physical connection.

        When to use: IAM auth, so every login carries a fresh token.
        Catch: a token computed once and stored in static kwargs breaks every connection opened after 15 min.
        """
        base = self._base_kwargs(host, read_only)
        s = self._settings

        def supply() -> dict[str, Any]:
            if not s.aurora_iam_auth:
                return base  # local Postgres: password via PGPASSWORD / .pgpass, never in code
            return {
                **base,
                "password": iam_token(
                    host, s.aurora_port, s.aurora_username, s.aws_region
                ),
            }

        return supply

    def _make_pool(
        self, name: str, host: str, read_only: bool
    ) -> ConnectionPool[psycopg.Connection[DictRow]]:
        """One pool per endpoint.

        - max_size: cap per process; pods x pools x max_size must stay under max_connections.
        - max_lifetime 840 s (< 15 min token life by convention): the real reason is DNS re-resolution after
          failover and rebalancing across readers; psycopg_pool adds jitter so connections don't expire together.
        - check: validates a connection on checkout (one round trip) so a dead one is replaced, not served.
        - open(wait=False): connections are made in the background; the first request waits at most `timeout`.
        """
        s = self._settings
        pool: ConnectionPool[psycopg.Connection[DictRow]] = ConnectionPool(
            kwargs=self._kwargs_supplier(host, read_only),
            min_size=max(1, s.aurora_pool_max_size // 2),
            max_size=s.aurora_pool_max_size,
            timeout=POOL_TIMEOUT_S,
            max_lifetime=float(s.aurora_pool_max_lifetime_s),
            max_idle=POOL_MAX_IDLE_S,
            reconnect_timeout=60.0,
            check=ConnectionPool.check_connection,
            name=name,
            open=False,
        )
        pool.open(wait=False)
        return pool

    def close(self) -> None:
        with self._lock:
            for pool in (self._writer, self._reader):
                if pool is not None:
                    pool.close()
            self._writer = self._reader = None


# ===================================================================== unit of work (scenarios)


class PgOrderStore:
    """All scenarios on one connection. Writer vs reader is decided by the transaction that created this store."""

    def __init__(self, conn: psycopg.Connection[DictRow]) -> None:
        self._conn = conn

    # ---------------------------------------------------------------- CRUD

    def insert(self, order: NewOrder) -> Order:
        """Plain INSERT ... RETURNING. Catch: no idempotency key => never retry (a lost ack can't be resolved)."""
        row = self._conn.execute(
            "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
            "VALUES (%(customer_id)s, %(sku)s, %(quantity)s, %(amount_cents)s, %(key)s, %(attrs)s) "
            f"RETURNING {ORDER_COLUMNS}",
            _order_params(order),
        ).fetchone()
        assert row is not None
        return _order(row)

    def insert_idempotent(self, order: NewOrder) -> Order | None:
        """ON CONFLICT (idempotency_key) DO NOTHING RETURNING; None = key exists (re-read by key).

        Catch: under REPEATABLE READ / SERIALIZABLE a conflicting row the snapshot can't see raises 40001 instead.
        """
        if not order.idempotency_key:
            raise ValueError("idempotency_key is required for an idempotent insert")
        row = self._conn.execute(
            "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
            "VALUES (%(customer_id)s, %(sku)s, %(quantity)s, %(amount_cents)s, %(key)s, %(attrs)s) "
            f"ON CONFLICT (idempotency_key) DO NOTHING RETURNING {ORDER_COLUMNS}",
            _order_params(order),
        ).fetchone()
        return _order(row) if row else None

    def find_by_id(self, order_id: int) -> Order | None:
        """Primary-key read. On a writer store it sees the latest commit, on a reader store it may lag."""
        row = self._conn.execute(
            f"SELECT {ORDER_COLUMNS} FROM x_order WHERE id = %s", (order_id,)
        ).fetchone()
        return _order(row) if row else None

    def find_by_idempotency_key(self, key: str) -> Order | None:
        """Resolve a replay. READ COMMITTED: each statement takes a new snapshot, so it sees a just-committed row."""
        row = self._conn.execute(
            f"SELECT {ORDER_COLUMNS} FROM x_order WHERE idempotency_key = %s", (key,)
        ).fetchone()
        return _order(row) if row else None

    def delete(self, order_id: int) -> bool:
        """Idempotent DELETE. Catch: the old row version stays as a dead tuple until VACUUM."""
        return (
            self._conn.execute(
                "DELETE FROM x_order WHERE id = %s", (order_id,)
            ).rowcount
            == 1
        )

    # ---------------------------------------------------------------- batch insert

    def batch_insert(self, orders: list[NewOrder]) -> int:
        """executemany: psycopg 3 pipelines the statements (no round trip per row); rowcount = rows inserted.

        When to use: bulk loads inside one transaction (all-or-nothing). Catch: for millions of rows COPY is faster.
        """
        with self._conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
                "VALUES (%(customer_id)s, %(sku)s, %(quantity)s, %(amount_cents)s, %(key)s, %(attrs)s) "
                "ON CONFLICT (idempotency_key) DO NOTHING",
                [_order_params(o) for o in orders],
            )
            return max(cur.rowcount, 0)

    # ---------------------------------------------------------------- upsert

    def upsert_stock(self, sku: str, on_hand: int) -> StockLevel:
        """INSERT ... ON CONFLICT (sku) DO UPDATE: atomic insert-or-update, no SELECT-then-INSERT race.

        Catch: SET on_hand = EXCLUDED.on_hand is idempotent; an additive on_hand + EXCLUDED.on_hand is NOT retry-safe.
        """
        row = self._conn.execute(
            "INSERT INTO x_inventory (sku, on_hand) VALUES (%s, %s) "
            "ON CONFLICT (sku) DO UPDATE SET on_hand = EXCLUDED.on_hand, updated_at = now() "
            "RETURNING sku, on_hand, updated_at",
            (sku, on_hand),
        ).fetchone()
        assert row is not None
        return StockLevel(
            sku=row["sku"], on_hand=row["on_hand"], updated_at=row["updated_at"]
        )

    # ---------------------------------------------------------------- pagination

    def page_by_offset(self, customer_id: str, page: int, size: int) -> Page[Order]:
        """OFFSET page. Catch: the server reads and discards page*size rows; inserts shift rows between pages."""
        rows = self._conn.execute(
            f"SELECT {ORDER_COLUMNS} FROM x_order WHERE customer_id = %s "
            "ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s",
            (customer_id, size + 1, page * size),
        ).fetchall()
        more = len(rows) > size
        return Page(
            items=[_order(r) for r in rows[:size]], next=str(page + 1) if more else None
        )

    def page_by_keyset(
        self, customer_id: str, cursor: str | None, size: int
    ) -> Page[Order]:
        """Keyset page: WHERE (created_at, id) < cursor, index (customer_id, created_at, id) scanned backward.

        Catch: id is the tie-breaker (rows of one transaction share now()); no jump to page k.
        """
        if cursor:
            created_at, last_id = decode_cursor(cursor)
            rows = self._conn.execute(
                f"SELECT {ORDER_COLUMNS} FROM x_order WHERE customer_id = %s AND (created_at, id) < (%s, %s) "
                "ORDER BY created_at DESC, id DESC LIMIT %s",
                (customer_id, created_at, last_id, size + 1),
            ).fetchall()
        else:
            rows = self._conn.execute(
                f"SELECT {ORDER_COLUMNS} FROM x_order WHERE customer_id = %s "
                "ORDER BY created_at DESC, id DESC LIMIT %s",
                (customer_id, size + 1),
            ).fetchall()
        items = [_order(r) for r in rows[:size]]
        if len(rows) <= size:
            return Page(items=items, next=None)
        last = items[-1]
        return Page(items=items, next=_encode_cursor(last.created_at, last.id))

    # ---------------------------------------------------------------- optimistic lock

    def update_status_if_version(
        self, order_id: int, expected_version: int, status: OrderStatus
    ) -> Order:
        """UPDATE ... WHERE id AND version RETURNING; no row => re-read to tell 404 from 409."""
        row = self._conn.execute(
            "UPDATE x_order SET status = %s, version = version + 1, updated_at = now() "
            f"WHERE id = %s AND version = %s RETURNING {ORDER_COLUMNS}",
            (status.value, order_id, expected_version),
        ).fetchone()
        if row:
            return _order(row)
        current = self.find_by_id(order_id)
        if current is None:
            raise OrderNotFound(f"order {order_id} not found")
        raise VersionConflict(
            f"order {order_id} is at version {current.version}, expected {expected_version}"
        )

    # ---------------------------------------------------------------- pessimistic lock

    def lock_stock_for_update(self, sku: str) -> int:
        """SELECT ... FOR UPDATE with SET LOCAL lock_timeout: row lock until the transaction ends.

        Catch: must be inside `with conn.transaction()` (autocommit would release the lock at once);
        lock several rows in key order to avoid 40P01.
        """
        self._require_transaction("lock_stock_for_update")
        self._conn.execute(
            f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT}'"
        )  # constant, not user input
        row = self._conn.execute(
            "SELECT on_hand FROM x_inventory WHERE sku = %s FOR UPDATE", (sku,)
        ).fetchone()
        if row is None:
            raise BusinessRuleViolation(f"unknown sku {sku}")
        return int(row["on_hand"])

    def decrement_stock(self, sku: str, quantity: int) -> None:
        """Decrement after lock_stock_for_update in the same transaction; CHECK (on_hand >= 0) is the last guard."""
        self._require_transaction("decrement_stock")
        self._conn.execute(
            "UPDATE x_inventory SET on_hand = on_hand - %s, updated_at = now() WHERE sku = %s",
            (quantity, sku),
        )

    def decrement_stock_if_available(self, sku: str, quantity: int) -> bool:
        """Atomic conditional UPDATE: check + write in one statement; READ COMMITTED re-checks WHERE on the new row."""
        cur = self._conn.execute(
            "UPDATE x_inventory SET on_hand = on_hand - %s, updated_at = now() WHERE sku = %s AND on_hand >= %s",
            (quantity, sku, quantity),
        )
        return cur.rowcount == 1

    def sum_open_amount_cents(self, customer_id: str) -> int:
        """Read half of the credit-limit invariant; under SERIALIZABLE it takes SIREAD locks on the index range."""
        row = self._conn.execute(
            "SELECT COALESCE(SUM(amount_cents), 0) AS total FROM x_order "
            "WHERE customer_id = %s AND status IN ('NEW', 'PAID')",
            (customer_id,),
        ).fetchone()
        return int(row["total"]) if row else 0

    # ---------------------------------------------------------------- job queue (SKIP LOCKED + lease)

    def enqueue(self, kind: str, payload: dict[str, Any]) -> int:
        """Insert a job. Catch: no dedup key, so the caller must not blindly retry."""
        row = self._conn.execute(
            "INSERT INTO x_job (kind, payload) VALUES (%s, %s) RETURNING id",
            (kind, Jsonb(payload)),
        ).fetchone()
        assert row is not None
        return int(row["id"])

    def claim(self, worker_id: str, limit: int, lease: timedelta) -> list[Job]:
        """One statement: lock READY rows FOR UPDATE SKIP LOCKED, mark RUNNING with a lease.

        Catch: run it in autocommit (or a tiny transaction) and process afterwards; at-least-once delivery.
        """
        rows = self._conn.execute(
            "WITH next AS ("
            "  SELECT id FROM x_job WHERE status = 'READY' AND run_after <= now()"
            "  ORDER BY run_after, id LIMIT %(limit)s FOR UPDATE SKIP LOCKED) "
            "UPDATE x_job j SET status = 'RUNNING', locked_by = %(worker)s, attempts = j.attempts + 1, "
            "  locked_until = now() + %(lease)s "
            "FROM next WHERE j.id = next.id "
            "RETURNING j.id, j.kind, j.payload, j.status, j.attempts, j.locked_by, j.locked_until",
            {"limit": limit, "worker": worker_id, "lease": lease},
        ).fetchall()
        return [_job(r) for r in rows]

    def complete(self, job_id: int, worker_id: str) -> None:
        """Complete if still the lease owner; DONE keeps locked_by so a retried complete is a no-op."""
        cur = self._conn.execute(
            "UPDATE x_job SET status = 'DONE', locked_until = NULL "
            "WHERE id = %s AND locked_by = %s AND status IN ('RUNNING', 'DONE')",
            (job_id, worker_id),
        )
        if cur.rowcount == 0:
            raise LeaseLost(f"job {job_id} is not leased by {worker_id}")

    def fail(
        self,
        job_id: int,
        worker_id: str,
        error: str,
        retry_delay: timedelta,
        max_attempts: int,
    ) -> None:
        """Back to READY after retry_delay, or FAILED after max_attempts; guarded by lease ownership."""
        cur = self._conn.execute(
            "UPDATE x_job SET status = CASE WHEN attempts >= %(max)s THEN 'FAILED' ELSE 'READY' END, "
            "run_after = now() + %(delay)s, locked_by = NULL, locked_until = NULL, last_error = %(error)s "
            "WHERE id = %(id)s AND locked_by = %(worker)s AND status = 'RUNNING'",
            {
                "max": max_attempts,
                "delay": retry_delay,
                "error": error,
                "id": job_id,
                "worker": worker_id,
            },
        )
        if cur.rowcount == 0:
            raise LeaseLost(f"job {job_id} is not leased by {worker_id}")

    def requeue_expired(self, max_attempts: int) -> int:
        """Reaper: expired leases back to READY (or FAILED). Catch: lease must exceed the slowest legitimate job."""
        cur = self._conn.execute(
            "UPDATE x_job SET status = CASE WHEN attempts >= %s THEN 'FAILED' ELSE 'READY' END, "
            "locked_by = NULL, locked_until = NULL, last_error = 'lease expired' "
            "WHERE status = 'RUNNING' AND locked_until < now()",
            (max_attempts,),
        )
        return cur.rowcount

    # ---------------------------------------------------------------- JSONB + GIN

    def find_by_attrs(self, containment: dict[str, Any], limit: int) -> list[Order]:
        """attrs @> %s served by the GIN (jsonb_path_ops) index. Jsonb() adapts the dict to a jsonb parameter."""
        rows = self._conn.execute(
            f"SELECT {ORDER_COLUMNS} FROM x_order WHERE attrs @> %s ORDER BY id DESC LIMIT %s",
            (Jsonb(containment), limit),
        ).fetchall()
        return [_order(r) for r in rows]

    # ---------------------------------------------------------------- reports (run in one REPEATABLE READ snapshot)

    def count_and_sum(self, customer_id: str) -> tuple[int, int]:
        row = self._conn.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(amount_cents), 0) AS total FROM x_order WHERE customer_id = %s",
            (customer_id,),
        ).fetchone()
        return (int(row["n"]), int(row["total"])) if row else (0, 0)

    def latest(self, customer_id: str, limit: int) -> list[Order]:
        rows = self._conn.execute(
            f"SELECT {ORDER_COLUMNS} FROM x_order WHERE customer_id = %s ORDER BY created_at DESC, id DESC LIMIT %s",
            (customer_id, limit),
        ).fetchall()
        return [_order(r) for r in rows]

    # ---------------------------------------------------------------- audit

    def append_audit(self, action: str, detail: str | None) -> None:
        """Audit row; it commits with whichever transaction this store belongs to."""
        self._conn.execute(
            "INSERT INTO x_audit (action, detail) VALUES (%s, %s)", (action, detail)
        )

    def _require_transaction(self, op: str) -> None:
        if self._conn.info.transaction_status == pq.TransactionStatus.IDLE:
            raise RuntimeError(
                f"{op} needs an open transaction (the row lock would end at once)"
            )


# ===================================================================== repository: transactions per endpoint


class AuroraRepository:
    """Opens transactions on the writer or reader pool and hands out a PgOrderStore bound to that connection."""

    def __init__(self, pools: AuroraPools) -> None:
        self._pools = pools

    @contextmanager
    def _connection(
        self,
        pool: ConnectionPool[psycopg.Connection[DictRow]],
        evict_on_read_only: bool,
    ) -> Iterator[psycopg.Connection[DictRow]]:
        """Borrow a connection; on 25006 from the writer pool close it so the pool discards it.

        Why: after failover a cached DNS answer can put a writer-pool connection on the demoted node.
        """
        with pool.connection() as conn:
            try:
                yield conn
            except errors.ReadOnlySqlTransaction:
                if evict_on_read_only:
                    conn.close()  # closed connections are dropped and replaced when returned to the pool
                raise

    @contextmanager
    def writer_tx(
        self, isolation: Isolation = Isolation.READ_COMMITTED
    ) -> Iterator[PgOrderStore]:
        """One writer transaction: BEGIN on enter, COMMIT on clean exit, ROLLBACK on exception.

        SET TRANSACTION as the first statement scopes the level to this transaction only,
        so it never leaks to the next borrower of the pooled connection.
        """
        with (
            self._connection(self._pools.writer(), evict_on_read_only=True) as conn,
            conn.transaction(),
        ):
            if isolation is not Isolation.READ_COMMITTED:
                conn.execute(
                    f"SET TRANSACTION ISOLATION LEVEL {isolation.value}"
                )  # enum constant
            yield PgOrderStore(conn)

    @contextmanager
    def reader_tx(
        self, isolation: Isolation = Isolation.REPEATABLE_READ
    ) -> Iterator[PgOrderStore]:
        """Read-only transaction on the reader endpoint.

        Catch: may lag the writer; SERIALIZABLE is not available on replicas, so it is downgraded to REPEATABLE READ.
        """
        level = (
            Isolation.REPEATABLE_READ
            if isolation is Isolation.SERIALIZABLE
            else isolation
        )
        with (
            self._connection(self._pools.reader(), evict_on_read_only=False) as conn,
            conn.transaction(),
        ):
            conn.execute(
                f"SET TRANSACTION ISOLATION LEVEL {level.value}, READ ONLY"
            )  # enum constant
            yield PgOrderStore(conn)

    def independent_tx(self) -> AbstractContextManager[PgOrderStore]:
        """REQUIRES_NEW analogue: a separate writer connection and transaction that commits on its own.

        Catch: opened while another writer_tx is open, it holds a second pooled connection (pool starvation risk).
        """
        return self.writer_tx(Isolation.READ_COMMITTED)

    def apply_schema(self) -> None:
        """Run SCHEMA_SQL in one transaction (PostgreSQL DDL is transactional). Real projects use migrations."""
        statements = [stmt.strip() for stmt in SCHEMA_SQL.split(";") if stmt.strip()]
        with (
            self._connection(self._pools.writer(), evict_on_read_only=True) as conn,
            conn.transaction(),
        ):
            for stmt in statements:
                conn.execute(stmt)

    def replica_lag_ms(self) -> dict[str, int]:
        """Per-reader lag from aurora_replica_status() (Aurora-only), sampled on the writer.

        Catch: a point-in-time sample, and the function may need extra privileges for x_app;
        CloudWatch AuroraReplicaLag is the alarm source.
        """
        with self._connection(self._pools.writer(), evict_on_read_only=True) as conn:
            rows = conn.execute(
                "SELECT server_id, replica_lag_in_msec FROM aurora_replica_status() "
                "WHERE session_id <> 'MASTER_SESSION_ID'"
            ).fetchall()
        return {
            str(r["server_id"]): round(float(r["replica_lag_in_msec"] or 0))
            for r in rows
        }


# ===================================================================== mapping helpers


def _order_params(o: NewOrder) -> dict[str, Any]:
    return {
        "customer_id": o.customer_id,
        "sku": o.sku,
        "quantity": o.quantity,
        "amount_cents": o.amount_cents,
        "key": o.idempotency_key,
        "attrs": Jsonb(o.attrs),
    }


def _order(r: DictRow) -> Order:
    return Order(
        id=r["id"],
        customer_id=r["customer_id"],
        sku=r["sku"],
        quantity=r["quantity"],
        amount_cents=r["amount_cents"],
        status=OrderStatus(r["status"]),
        version=r["version"],
        idempotency_key=r["idempotency_key"],
        attrs=r["attrs"] or {},
        created_at=r["created_at"],
        updated_at=r["updated_at"],
    )


def _job(r: DictRow) -> Job:
    return Job(
        id=r["id"],
        kind=r["kind"],
        payload=r["payload"] or {},
        status=JobStatus(r["status"]),
        attempts=r["attempts"],
        locked_by=r["locked_by"],
        locked_until=r["locked_until"],
    )


def _encode_cursor(created_at: datetime, last_id: int) -> str:
    """Opaque keyset cursor: base64url("iso-timestamp|id")."""
    raw = f"{created_at.isoformat()}|{last_id}".encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(token: str) -> tuple[datetime, int]:
    """Inverse of _encode_cursor; ValueError on a malformed token (HTTP 400)."""
    try:
        padded = token + "=" * (-len(token) % 4)
        ts, _, last_id = base64.urlsafe_b64decode(padded).decode().rpartition("|")
        return datetime.fromisoformat(ts), int(last_id)
    except (ValueError, UnicodeDecodeError) as e:
        raise ValueError("invalid cursor") from e
