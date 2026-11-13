package com.lc.x.x03_01_aurora.infra;

import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.SQLFeatureNotSupportedException;
import java.util.function.Supplier;
import java.util.logging.Logger;
import javax.sql.DataSource;

/**
 * DataSource wrapper that asks for a password every time a physical connection is opened.
 * - Hikari calls getConnection() (no user set on the pool) only when it opens a new physical connection,
 *   so each login gets a fresh 15-minute IAM token; pooled reuse never calls this.
 * - Why not override HikariDataSource.getPassword(): HikariCP 6.x reads credentials via getCredentials(),
 *   so that override is silently ignored (verified on 6.3.3). A wrapper works on every pool version.
 * - Catch: the supplier runs on Hikari's connection-adder thread; it must be fast and must not block on I/O
 *   for long (RdsUtilities signs locally; credentials are cached by the provider).
 */
public final class IamAuthDataSource implements DataSource {

    private final DataSource delegate;
    private final String username;
    private final Supplier<String> passwordSupplier;

    public IamAuthDataSource(DataSource delegate, String username, Supplier<String> passwordSupplier) {
        this.delegate = delegate;
        this.username = username;
        this.passwordSupplier = passwordSupplier;
    }

    @Override
    public Connection getConnection() throws SQLException {
        return delegate.getConnection(username, passwordSupplier.get());
    }

    @Override
    public Connection getConnection(String user, String password) throws SQLException {
        // Explicit credentials bypass token generation; only used if someone configures a user on the pool.
        return delegate.getConnection(user, password);
    }

    @Override
    public PrintWriter getLogWriter() throws SQLException {
        return delegate.getLogWriter();
    }

    @Override
    public void setLogWriter(PrintWriter out) throws SQLException {
        delegate.setLogWriter(out);
    }

    @Override
    public void setLoginTimeout(int seconds) throws SQLException {
        delegate.setLoginTimeout(seconds);
    }

    @Override
    public int getLoginTimeout() throws SQLException {
        return delegate.getLoginTimeout();
    }

    @Override
    public Logger getParentLogger() throws SQLFeatureNotSupportedException {
        return delegate.getParentLogger();
    }

    @Override
    public <T> T unwrap(Class<T> iface) throws SQLException {
        return iface.isInstance(this) ? iface.cast(this) : delegate.unwrap(iface);
    }

    @Override
    public boolean isWrapperFor(Class<?> iface) throws SQLException {
        return iface.isInstance(this) || delegate.isWrapperFor(iface);
    }
}
