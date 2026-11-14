package com.lc.x.config._03db_04mongodb;

import java.time.Duration;

/**
 * Slice settings from application.yml (x.mongodb.*); the URI comes from env X_MONGODB_URI.
 * - Local: mongodb://localhost:27017/?replicaSet=rs0 (1x/local/mongodb, single-node replica set).
 * - DocumentDB: the cluster endpoint from Terraform output docdb_endpoint, with tls=true, replicaSet=rs0,
 *   readPreference=secondaryPreferred, retryWrites=false; tlsCaFile points at the RDS CA bundle.
 *
 * @param uri                    connection string; options in it (w, readPreference, retryWrites) win over code defaults
 * @param database               database name
 * @param appName                shows up in server logs and currentOp: find your app's slow ops
 * @param maxPoolSize            connections per host (driver default 100)
 * @param serverSelectionTimeout how long to wait for a suitable server (driver default 30 s): "no primary" fails here
 * @param maxTime                default maxTimeMS for user-facing queries; MongoDB has no statement timeout by default
 * @param tlsCaFile              PEM bundle for a private CA (DocumentDB); blank = JVM default trust store
 */
public record MongoProperties(
        String uri,
        String database,
        String appName,
        int maxPoolSize,
        Duration serverSelectionTimeout,
        Duration maxTime,
        String tlsCaFile) {
}
