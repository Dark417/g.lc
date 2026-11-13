-- 03.01 Aurora PostgreSQL slice schema (database xdb, app user x_app).
-- Not auto-run: DataSource auto-config is excluded, AuroraJdbcRepository.applySchema() runs it on demand.
-- Real projects use Flyway/Liquibase and CREATE INDEX CONCURRENTLY on live tables.
-- One-time admin step (as the master user): CREATE USER x_app, then GRANT rds_iam TO x_app,
-- then GRANT CREATE ON SCHEMA public TO x_app (PostgreSQL 15+ no longer grants CREATE on public to everyone)

CREATE TABLE IF NOT EXISTS x_order (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     TEXT        NOT NULL,
    sku             TEXT        NOT NULL,
    quantity        INT         NOT NULL CHECK (quantity > 0),
    amount_cents    BIGINT      NOT NULL CHECK (amount_cents >= 0),
    status          TEXT        NOT NULL DEFAULT 'NEW',
    version         INT         NOT NULL DEFAULT 0,          -- optimistic lock counter
    idempotency_key TEXT        UNIQUE,                      -- NULLs allowed (NULLS DISTINCT), set => one row per request
    attrs           JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),      -- now() = transaction start: ties are common
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Keyset pagination: ORDER BY created_at DESC, id DESC within one customer = this index scanned backward,
-- and the row comparison (created_at, id) < (?, ?) becomes an index condition.
-- Also narrows SERIALIZABLE predicate locks for the per-customer credit-limit check.
CREATE INDEX IF NOT EXISTS x_order_customer_created_id_idx
    ON x_order (customer_id, created_at, id);

-- JSONB containment (attrs @> '{...}'). jsonb_path_ops: smaller and faster than jsonb_ops, but only @> and jsonpath.
CREATE INDEX IF NOT EXISTS x_order_attrs_gin
    ON x_order USING GIN (attrs jsonb_path_ops);

CREATE TABLE IF NOT EXISTS x_inventory (
    sku        TEXT        PRIMARY KEY,
    on_hand    INT         NOT NULL CHECK (on_hand >= 0),    -- the CHECK is the last line of defence against oversell
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS x_job (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kind         TEXT        NOT NULL,
    payload      JSONB       NOT NULL,
    status       TEXT        NOT NULL DEFAULT 'READY',       -- READY, RUNNING, DONE, FAILED
    attempts     INT         NOT NULL DEFAULT 0,
    run_after    TIMESTAMPTZ NOT NULL DEFAULT now(),         -- retry backoff: not claimable before this
    locked_by    TEXT,
    locked_until TIMESTAMPTZ,                                -- lease expiry, reaper requeues after it
    last_error   TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Partial index: the claim query only scans READY rows, so DONE history does not slow it down.
CREATE INDEX IF NOT EXISTS x_job_ready_idx
    ON x_job (run_after, id) WHERE status = 'READY';

CREATE INDEX IF NOT EXISTS x_job_running_lease_idx
    ON x_job (locked_until) WHERE status = 'RUNNING';

CREATE TABLE IF NOT EXISTS x_audit (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    action     TEXT        NOT NULL,
    detail     TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()  -- wall clock, not txn start
);
