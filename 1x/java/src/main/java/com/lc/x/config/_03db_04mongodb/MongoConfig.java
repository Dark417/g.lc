package com.lc.x.config._03db_04mongodb;

import com.mongodb.ConnectionString;
import com.mongodb.MongoClientSettings;
import com.mongodb.WriteConcern;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoDatabase;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.security.cert.Certificate;
import java.security.cert.CertificateFactory;
import java.time.Duration;
import java.util.concurrent.TimeUnit;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;
import org.bson.UuidRepresentation;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * MongoDB wiring: ONE MongoClient per process (thread-safe, owns the pool and the topology monitor).
 * - A per-request client re-runs server discovery and leaks connections: the #1 driver performance bug.
 * - Spring Boot's own MongoAutoConfiguration is excluded in application.yml, so nothing connects
 *   unless x.mongodb.enabled=true.
 * - Building the client makes no blocking call; background monitors connect, the first operation waits
 *   up to serverSelectionTimeout for a suitable server.
 */
@Configuration(proxyBeanMethods = false)
@ConditionalOnProperty(name = "x.mongodb.enabled", havingValue = "true")
public class MongoConfig {

    @Bean
    public MongoProperties mongoProperties(
            @Value("${x.mongodb.uri}") String uri,
            @Value("${x.mongodb.database}") String database,
            @Value("${x.mongodb.app-name:x-mongodb}") String appName,
            @Value("${x.mongodb.max-pool-size:50}") int maxPoolSize,
            @Value("${x.mongodb.server-selection-timeout:5s}") Duration serverSelectionTimeout,
            @Value("${x.mongodb.max-time:2s}") Duration maxTime,
            @Value("${x.mongodb.tls-ca-file:}") String tlsCaFile) {
        return new MongoProperties(uri, database, appName, maxPoolSize, serverSelectionTimeout, maxTime, tlsCaFile);
    }

    @Bean(destroyMethod = "close")
    public MongoClient mongoClient(MongoProperties props) {
        ConnectionString cs = new ConnectionString(props.uri());
        MongoClientSettings.Builder builder = MongoClientSettings.builder()
                .applyConnectionString(cs)
                .applicationName(props.appName())
                .uuidRepresentation(UuidRepresentation.STANDARD) // portable UUID bytes across drivers
                .applyToConnectionPoolSettings(b -> b
                        .maxSize(props.maxPoolSize())
                        .maxWaitTime(2, TimeUnit.SECONDS)) // fail fast when the pool is exhausted
                .applyToClusterSettings(b -> b
                        .serverSelectionTimeout(props.serverSelectionTimeout().toMillis(), TimeUnit.MILLISECONDS))
                .applyToSocketSettings(b -> b.connectTimeout(5, TimeUnit.SECONDS));
        // Default write concern = majority (server default since 5.0) unless the URI says otherwise.
        // Retryable writes/reads stay on the driver default (true) unless the URI turns them off:
        // DocumentDB does NOT support retryable writes, so its URI carries retryWrites=false.
        if (cs.getWriteConcern() == null) {
            builder.writeConcern(WriteConcern.MAJORITY);
        }
        if (!props.tlsCaFile().isBlank()) {
            builder.applyToSslSettings(b -> b.enabled(true).context(sslContextFromPem(Path.of(props.tlsCaFile()))));
        }
        return MongoClients.create(builder.build());
    }

    @Bean
    public MongoDatabase mongoDatabase(MongoClient client, MongoProperties props) {
        return client.getDatabase(props.database());
    }

    // The Java driver ignores tlsCAFile in the URI; a private CA (RDS/DocumentDB bundle) needs an SSLContext.
    private static SSLContext sslContextFromPem(Path pemBundle) {
        try (InputStream in = Files.newInputStream(pemBundle)) {
            KeyStore trust = KeyStore.getInstance(KeyStore.getDefaultType());
            trust.load(null, null);
            int i = 0;
            for (Certificate cert : CertificateFactory.getInstance("X.509").generateCertificates(in)) {
                trust.setCertificateEntry("ca-" + i++, cert); // the bundle holds one cert per region/rotation
            }
            TrustManagerFactory tmf = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
            tmf.init(trust);
            SSLContext ctx = SSLContext.getInstance("TLS");
            ctx.init(null, tmf.getTrustManagers(), null);
            return ctx;
        } catch (IOException | GeneralSecurityException e) {
            throw new IllegalStateException("cannot load TLS CA bundle " + pemBundle, e);
        }
    }
}
