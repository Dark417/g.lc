package com.lc.x.x03_01_aurora.infra;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

/**
 * Binds x.aurora.* from application.yml (endpoints match Terraform outputs aurora_writer_endpoint / aurora_reader_endpoint).
 * - iamAuth=true: password is a fresh IAM token per physical connection; password below is ignored.
 * - iamAuth=false: local Postgres only (e.g. Docker); password comes from env X_AURORA_PASSWORD, never from code.
 * - sslMode / sslRootCert / statementTimeoutMs / applicationName have defaults here (not yet in application.yml).
 */
@ConfigurationProperties(prefix = "x.aurora")
public record AuroraProperties(
        String writerEndpoint,
        String readerEndpoint,
        @DefaultValue("5432") int port,
        @DefaultValue("xdb") String database,
        @DefaultValue("x_app") String username,
        @DefaultValue("true") boolean iamAuth,
        @DefaultValue("") String password,
        @DefaultValue("verify-full") String sslMode,
        @DefaultValue("/etc/ssl/certs/rds-global-bundle.pem") String sslRootCert,
        @DefaultValue("15000") int statementTimeoutMs,
        @DefaultValue("x-aurora") String applicationName,
        @DefaultValue Pool pool) {

    /**
     * Hikari pool knobs.
     * - maxLifetimeMs (14 min) < 15 min IAM token life by convention; the real reason is DNS re-resolution
     *   after failover and rebalancing across readers (an open connection outlives its token).
     */
    public record Pool(
            @DefaultValue("10") int maxSize,
            @DefaultValue("3000") long connectionTimeoutMs,
            @DefaultValue("840000") long maxLifetimeMs,
            @DefaultValue("300000") long idleTimeoutMs) {
    }
}
