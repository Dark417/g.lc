# 03db.01aurora.05iam-auth-tls Identity and Access Management (IAM) Auth Tokens And Transport Layer Security (TLS)

> A fresh 15-minute Identity and Access Management (IAM) token per new physical connection, over Transport Layer Security (TLS) `verify-full`, replaces a stored password.

## Index

- [1. The Token](#1-the-token)
  - [1.1 What It Is](#11-what-it-is)
  - [1.2 Validity](#12-validity)
  - [1.3 Requirements](#13-requirements)
  - [1.4 Why Not A Password](#14-why-not-a-password)
- [2. Token Per Physical Connection In Code](#2-token-per-physical-connection-in-code)
- [3. TLS Mode](#3-tls-mode)
  - [3.1 Driver Options In Code](#31-driver-options-in-code)
- [4. Limits](#4-limits)
- [Related](#related)

## 1. The Token

The token is a short-lived signed Uniform Resource Locator (URL) that the database checks at login.

### 1.1 What It Is

- Token = a Signature Version 4 (SigV4)-presigned request for action `rds-db:connect`
- Generated locally by the Software Development Kit (SDK)
  - No network call
  - Credentials resolve once, then cache
- Java: `RdsUtilities.generateAuthenticationToken`
- Python: `boto3 client("rds").generate_db_auth_token`

### 1.2 Validity

- Valid 15 minutes, checked **only at login**
- An open connection outlives its token
- A token reused for a new connection after 15 min fails with `PAM authentication failed`
- Rule: generate a fresh token per new physical connection, never once at startup

### 1.3 Requirements

- database (DB) user granted `rds_iam` (here `x_app`)
  - One-time admin step in `schema.sql`: `CREATE USER x_app`, `GRANT rds_iam TO x_app`
- IAM policy on `arn:aws:rds-db:<region>:<account>:dbuser:<cluster-resource-id>/x_app`
  - Terraform `app_aurora` ([`modules/03db_01aurora/iam.tf`](../../terraform/modules/03db_01aurora/iam.tf))
- TLS required for IAM auth
  - The parameter group also sets `rds.force_ssl = 1`

### 1.4 Why Not A Password

- Rotates automatically
- No secret in config
- Revoked with the IAM role

## 2. Token Per Physical Connection In Code

The pool must ask for a password on every new login, not once.

- Java: a `DataSource` wrapper that calls a supplier on each `getConnection()`
  - Hikari calls it only when opening a new physical connection
  - Verified on HikariCP 6.3.3: the pool reads credentials via `getCredentials()`
    - So overriding `getPassword()` in a subclass does nothing
- Python: callable pool kwargs
  - psycopg_pool (>= 3.3) calls it once per new physical connection

**Java**

```java
// config/_03db_01aurora/AuroraConfig.java
// RdsUtilities signs tokens locally with SigV4 (no network call per token).
@Bean
public RdsUtilities auroraRdsUtilities(Region region, AwsCredentialsProvider credentials) {
    return RdsUtilities.builder().region(region).credentialsProvider(credentials).build();
}

// Called once per new physical connection: a fresh 15-minute token for every login.
static Supplier<String> tokenSupplier(AuroraProperties p, String host, RdsUtilities rds) {
    if (!p.iamAuth()) {
        String password = p.password();
        return () -> password; // local Postgres only; value comes from env, never from code
    }
    // signed for one host:port:user, so sign the endpoint you dial
    return () -> rds.generateAuthenticationToken(b -> b.hostname(host).port(p.port()).username(p.username()));
}
```

```java
// infra/_03db_01aurora/IamAuthDataSource.java
// Hikari has no username set => calls getConnection() here only for a NEW physical connection.
public final class IamAuthDataSource implements DataSource {

    private final DataSource delegate;
    private final String username;
    private final Supplier<String> passwordSupplier;

    @Override
    public Connection getConnection() throws SQLException {
        return delegate.getConnection(username, passwordSupplier.get()); // fresh token per login
    }
    // ... other DataSource methods delegate
}
```

```java
// config/_03db_01aurora/AuroraConfig.java  (inside pool(...))
// No username on the pool => Hikari calls getConnection() on the wrapper, which injects user + fresh token.
DataSource physical = new IamAuthDataSource(pgDataSource(p, host), p.username(), tokenSupplier(p, host, rds));
ds.setDataSource(physical);
```

**Python**

```python
# app/infra/_03db_01aurora.py
def iam_token(host: str, port: int, user: str, region: str) -> str:
    """Fresh IAM auth token for one login: SigV4-presigned rds-db:connect, signed locally."""
    return aws.client("rds").generate_db_auth_token(
        DBHostname=host, Port=port, DBUsername=user, Region=region
    )

def _kwargs_supplier(self, host: str, read_only: bool) -> Callable[[], dict[str, Any]]:
    """Callable pool kwargs: psycopg_pool calls it once per NEW physical connection."""
    base = self._base_kwargs(host, read_only)
    s = self._settings

    def supply() -> dict[str, Any]:
        if not s.aurora_iam_auth:
            return base  # local Postgres: password via PGPASSWORD / .pgpass, never in code
        return {**base, "password": iam_token(host, s.aurora_port, s.aurora_username, s.aws_region)}

    return supply
```

**Catch**

- A token computed once and stored in static config breaks every connection opened after 15 min
- The supplier runs on Hikari's connection-adder thread
  - It must be fast and must not block on I/O for long
  - `RdsUtilities` signs locally; the credentials provider caches
- The token only gates login; open connections outliving it is expected

## 3. TLS Mode

IAM auth requires TLS; the mode decides whether TLS actually authenticates the server.

- `sslmode=verify-full` checks the Certificate Authority (CA) chain **and** the hostname
- `require` encrypts but accepts any certificate
  - Result: open to man-in-the-middle
- Needs the Relational Database Service (RDS) CA bundle on disk (`sslrootcert`)

### 3.1 Driver Options In Code

**Java**

```java
// config/_03db_01aurora/AuroraConfig.java
static PGSimpleDataSource pgDataSource(AuroraProperties p, String host) {
    PGSimpleDataSource pg = new PGSimpleDataSource();
    pg.setServerNames(new String[] {host});
    pg.setPortNumbers(new int[] {p.port()});
    pg.setDatabaseName(p.database());
    pg.setApplicationName(p.applicationName());   // shows in pg_stat_activity: who holds that lock?
    pg.setSslMode(p.sslMode());                   // verify-full = CA chain + hostname
    if (p.sslMode().startsWith("verify")) {
        pg.setSslRootCert(p.sslRootCert());       // RDS CA bundle on disk
    }
    pg.setConnectTimeout(5);                      // seconds: TCP + TLS handshake
    pg.setLoginTimeout(10);                       // seconds: whole login incl. auth
    pg.setSocketTimeout(Math.max(30, p.statementTimeoutMs() / 1000 * 2)); // > statement_timeout
    pg.setTcpKeepAlive(true);
    pg.setReWriteBatchedInserts(true);            // batch INSERT -> multi-row VALUES
    pg.setOptions("-c statement_timeout=" + p.statementTimeoutMs()); // server cancels runaway queries (57014)
    return pg;
}
```

```java
// config/_03db_01aurora/AuroraProperties.java
@ConfigurationProperties(prefix = "x.aurora")
public record AuroraProperties(
        String writerEndpoint,
        String readerEndpoint,
        @DefaultValue("5432") int port,
        @DefaultValue("xdb") String database,
        @DefaultValue("x_app") String username,
        @DefaultValue("true") boolean iamAuth,
        @DefaultValue("") String password,             // local only, from env X_AURORA_PASSWORD
        @DefaultValue("verify-full") String sslMode,
        @DefaultValue("/etc/ssl/certs/rds-global-bundle.pem") String sslRootCert,
        @DefaultValue("15000") int statementTimeoutMs,
        @DefaultValue("x-aurora") String applicationName,
        @DefaultValue Pool pool) { /* ... */ }
```

**Python**

```python
# app/infra/_03db_01aurora.py
SSL_MODE = "verify-full"  # CA chain + hostname; "require" checks neither
SSL_ROOT_CERT = "/etc/ssl/certs/rds-global-bundle.pem"

def _base_kwargs(self, host: str, read_only: bool) -> dict[str, Any]:
    s = self._settings
    options = f"-c statement_timeout={STATEMENT_TIMEOUT_MS}"
    if read_only:
        options += " -c default_transaction_read_only=on"  # an accidental write to a reader fails loudly
    kwargs: dict[str, Any] = {
        "host": host, "port": s.aurora_port, "dbname": s.aurora_database, "user": s.aurora_username,
        "sslmode": SSL_MODE,
        "connect_timeout": 5,
        "application_name": APPLICATION_NAME,
        "options": options,
        "keepalives": 1, "keepalives_idle": 30, "keepalives_interval": 10, "keepalives_count": 3,
        "autocommit": True,  # transactions are explicit: with conn.transaction()
        "row_factory": dict_row,
    }
    if SSL_MODE.startswith("verify"):
        kwargs["sslrootcert"] = SSL_ROOT_CERT
    return kwargs
```

**Catch**

- `socketTimeout` must exceed `statement_timeout`
  - Else the driver kills healthy long queries
- Without `socketTimeout` / keepalives, a half-open Transmission Control Protocol (TCP) socket after failover hangs
- Never lower `sslmode` in prod

## 4. Limits

- Amazon Web Services (AWS) recommends IAM auth below about 200 new connections per second
- A connection storm after failover (every pod reconnects at once) can exceed it
- Pools with jittered lifetimes and a small min size soften the storm
  - See [06pools-rds-proxy](01aurora.06pools-rds-proxy.md)

## Related

- [00index](01aurora.00index.md)
- [03failover-dns](01aurora.03failover-dns.md)
- [99interview](01aurora.99interview.md): Q4
