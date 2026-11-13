package com.lc.x.x03_01_aurora.infra;

import com.zaxxer.hikari.HikariDataSource;
import java.util.function.Supplier;
import javax.sql.DataSource;
import org.postgresql.ds.PGSimpleDataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.support.JdbcTransactionManager;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.rds.RdsUtilities;

/**
 * Aurora wiring: two Hikari pools (writer endpoint, reader endpoint), one JdbcTemplate and one transaction manager each.
 * - Spring Boot's DataSource auto-config is excluded (XApplication), and with two DataSources and no @Primary
 *   Boot also skips its JdbcTemplate / transaction-manager auto-config, so nothing here clashes with other slices.
 * - Bean names are prefixed "aurora" and exposed as constants for @Qualifier and @Transactional(transactionManager = ...).
 * - No bean opens a connection at startup: pools start lazily on the first getConnection().
 */
@Configuration(proxyBeanMethods = false)
@ConditionalOnProperty(name = "x.aurora.enabled", havingValue = "true")
@EnableConfigurationProperties(AuroraProperties.class)
public class AuroraConfig {

    public static final String WRITER_DS = "auroraWriterDataSource";
    public static final String READER_DS = "auroraReaderDataSource";
    public static final String WRITER_JDBC = "auroraWriterJdbc";
    public static final String READER_JDBC = "auroraReaderJdbc";
    public static final String WRITER_TX = "auroraWriterTxManager";
    public static final String READER_TX = "auroraReaderTxManager";

    // ------------------------------------------------------------------ IAM auth token

    // RdsUtilities signs tokens locally with SigV4 (no network call per token).
    // Use it whenever iam-auth is on; the catch: the token is signed for one host:port:user, so sign the endpoint you dial.
    @Bean
    public RdsUtilities auroraRdsUtilities(Region region, AwsCredentialsProvider credentials) {
        return RdsUtilities.builder().region(region).credentialsProvider(credentials).build();
    }

    // Supplier called once per new physical connection: a fresh 15-minute token for every login.
    // When to use: always with IAM auth; a token created once at startup breaks every connection opened after 15 min.
    // Catch: the token only gates login, so open connections outlive it; that is fine and expected.
    static Supplier<String> tokenSupplier(AuroraProperties p, String host, RdsUtilities rds) {
        if (!p.iamAuth()) {
            String password = p.password();
            return () -> password; // local Postgres only; value comes from env, never from code
        }
        return () -> rds.generateAuthenticationToken(b -> b.hostname(host).port(p.port()).username(p.username()));
    }

    // ------------------------------------------------------------------ driver + pools

    // pgjdbc DataSource for one endpoint: TLS verify-full, timeouts, batch rewrite.
    // When to use: the physical-connection factory under Hikari. Catch: socketTimeout must exceed statement_timeout,
    // or the driver kills healthy long queries; without socketTimeout a half-open TCP socket after failover hangs forever.
    static PGSimpleDataSource pgDataSource(AuroraProperties p, String host) {
        PGSimpleDataSource pg = new PGSimpleDataSource();
        pg.setServerNames(new String[] {host});
        pg.setPortNumbers(new int[] {p.port()});
        pg.setDatabaseName(p.database());
        pg.setApplicationName(p.applicationName());   // shows in pg_stat_activity: who holds that lock?
        pg.setSslMode(p.sslMode());                   // verify-full = CA chain + hostname; "require" skips both checks
        if (p.sslMode().startsWith("verify")) {
            pg.setSslRootCert(p.sslRootCert());       // RDS CA bundle on disk
        }
        pg.setConnectTimeout(5);                      // seconds: TCP + TLS handshake
        pg.setLoginTimeout(10);                       // seconds: whole login incl. auth
        pg.setSocketTimeout(Math.max(30, p.statementTimeoutMs() / 1000 * 2)); // seconds, > statement_timeout
        pg.setTcpKeepAlive(true);
        pg.setReWriteBatchedInserts(true);            // batch of INSERT ... VALUES -> multi-row VALUES, fewer round trips
        pg.setOptions("-c statement_timeout=" + p.statementTimeoutMs()); // server cancels runaway queries (57014)
        return pg;
    }

    // One Hikari pool. Knobs map 1:1 to x.aurora.pool.*.
    // When to use: one pool per endpoint and role. Catch: total connections = pods x pools x maxSize must stay under
    // max_connections (derived from instance memory / max ACU), with headroom for admin and failover reconnects.
    static HikariDataSource pool(AuroraProperties p, String name, String host, RdsUtilities rds, boolean readOnly) {
        HikariDataSource ds = new HikariDataSource(); // no-arg constructor: pool starts on first getConnection()
        ds.setPoolName(name);
        // No username on the pool => Hikari calls getConnection() on the wrapper, which injects user + fresh token.
        DataSource physical = new IamAuthDataSource(pgDataSource(p, host), p.username(), tokenSupplier(p, host, rds));
        ds.setDataSource(physical);
        ds.setMaximumPoolSize(p.pool().maxSize());
        // Below max so idleTimeout can shrink the pool, and fewer connections reconnect at once after failover.
        ds.setMinimumIdle(Math.max(1, p.pool().maxSize() / 2));
        ds.setConnectionTimeout(p.pool().connectionTimeoutMs()); // wait for a free connection, then fail fast
        ds.setMaxLifetime(p.pool().maxLifetimeMs());             // Hikari subtracts up to 2.5% jitter per connection
        ds.setIdleTimeout(p.pool().idleTimeoutMs());
        ds.setKeepaliveTime(120_000);                            // ping idle connections; finds dead ones between uses
        ds.setValidationTimeout(1_000);                          // isValid() budget on checkout
        ds.setInitializationFailTimeout(-1);                     // don't fail app startup if Aurora is mid-failover
        ds.setLeakDetectionThreshold(30_000);                    // log a stack when a connection is held > 30 s
        ds.setReadOnly(readOnly);                                // reader: driver marks transactions READ ONLY
        return ds;
    }

    @Bean(name = WRITER_DS, destroyMethod = "close")
    public HikariDataSource auroraWriterDataSource(AuroraProperties p, RdsUtilities rds) {
        HikariDataSource ds = pool(p, "x-aurora-writer", p.writerEndpoint(), rds, false);
        ds.setExceptionOverride(new AuroraEvictionOverride()); // evict on 25006: stale DNS reached a demoted writer
        return ds;
    }

    @Bean(name = READER_DS, destroyMethod = "close")
    public HikariDataSource auroraReaderDataSource(AuroraProperties p, RdsUtilities rds) {
        return pool(p, "x-aurora-reader", p.readerEndpoint(), rds, true);
    }

    // ------------------------------------------------------------------ templates + transaction managers

    @Bean(name = WRITER_JDBC)
    public NamedParameterJdbcTemplate auroraWriterJdbc(@Qualifier(WRITER_DS) DataSource writer) {
        return new NamedParameterJdbcTemplate(writer);
    }

    @Bean(name = READER_JDBC)
    public NamedParameterJdbcTemplate auroraReaderJdbc(@Qualifier(READER_DS) DataSource reader) {
        return new NamedParameterJdbcTemplate(reader);
    }

    // Transaction manager bound to the writer pool (JdbcTransactionManager = DataSourceTransactionManager that also
    // translates commit/rollback SQLExceptions). Use via @Transactional(transactionManager = WRITER_TX).
    // Catch: the JdbcTemplate joins the transaction only because it wraps the SAME DataSource object.
    @Bean(name = WRITER_TX)
    public JdbcTransactionManager auroraWriterTxManager(@Qualifier(WRITER_DS) DataSource writer) {
        return new JdbcTransactionManager(writer);
    }

    // Reader transaction manager for consistent multi-query reads (REPEATABLE READ snapshot on a replica).
    // enforceReadOnly sends SET TRANSACTION READ ONLY. Catch: SERIALIZABLE is not available on replicas (hot standby).
    @Bean(name = READER_TX)
    public JdbcTransactionManager auroraReaderTxManager(@Qualifier(READER_DS) DataSource reader) {
        JdbcTransactionManager tm = new JdbcTransactionManager(reader);
        tm.setEnforceReadOnly(true);
        return tm;
    }
}
