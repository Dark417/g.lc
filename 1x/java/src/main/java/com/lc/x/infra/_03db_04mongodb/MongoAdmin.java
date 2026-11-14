package com.lc.x.infra._03db_04mongodb;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Accumulators;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.Projections;
import com.mongodb.client.model.Sorts;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import org.bson.BsonTimestamp;
import org.bson.Document;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * Server-side diagnostics and admin commands: the numbers an on-call engineer reads first.
 * - All are runCommand calls; the same commands work from mongosh (db.serverStatus(), rs.status(), sh.*).
 * - DocumentDB answers serverStatus/replSetGetStatus with a reduced shape and has no shardCollection;
 *   see the gaps table in x-md 98tradeoffs.
 */
@Component
@ConditionalOnProperty(name = "x.mongodb.enabled", havingValue = "true")
public class MongoAdmin {

    private final MongoClient client;
    private final MongoDatabase db;

    public MongoAdmin(MongoClient client, MongoDatabase db) {
        this.client = client;
        this.db = db;
    }

    // ================================================================ 01 document model

    // Document-size distribution via $bsonSize: alert at ~4 MB p99, a quarter of the 16 MB cap, so there is
    // time for a migration. Full scan: run it on a secondary / analytics node with allowDiskUse.
    public Document documentSizeStats(String collection) {
        return ConsistencyProfiles.analytics(db, collection).aggregate(List.of(
                        Aggregates.project(new Document("size", new Document("$bsonSize", "$$ROOT"))),
                        Aggregates.group(null,
                                Accumulators.avg("avgBytes", "$size"),
                                Accumulators.max("maxBytes", "$size"),
                                Accumulators.sum("docs", 1))))
                .allowDiskUse(true)
                .first();
    }

    // ================================================================ 02 WiredTiger storage

    // Cache health: the signal is the RATE of "bytes read into cache" (misses) and any eviction done by
    // application threads, not utilization (which sits near 80% by design).
    public Document cacheHealth() {
        Document cache = db.runCommand(new Document("serverStatus", 1))
                .get("wiredTiger", Document.class)
                .get("cache", Document.class);
        return new Document("maxBytes", cache.get("maximum bytes configured"))
                .append("currentBytes", cache.get("bytes currently in the cache"))
                .append("dirtyBytes", cache.get("tracked dirty bytes in the cache"))
                .append("bytesReadIntoCache", cache.get("bytes read into cache"))
                .append("pagesEvictedByAppThreads", cache.get("pages evicted by application threads"));
    }

    // ================================================================ 07 query planner

    // Profiler at slowms for a sampled window, not permanently (it writes system.profile on every slow op).
    public Document enableSampledProfiler(int slowMs, double sampleRate) {
        return db.runCommand(new Document("profile", 1).append("slowms", slowMs).append("sampleRate", sampleRate));
    }

    // ================================================================ 10 replica set + oplog

    // Member states, replication lag, and the oplog WINDOW in seconds: the number that decides whether a
    // lagging secondary can catch up or needs a full initial sync.
    public Document replicaSetSummary() {
        Document status = client.getDatabase("admin").runCommand(new Document("replSetGetStatus", 1));
        List<Document> members = new ArrayList<>();
        Date primaryOptime = null;
        for (Document m : status.getList("members", Document.class)) {
            if ("PRIMARY".equals(m.getString("stateStr"))) {
                primaryOptime = m.getDate("optimeDate");
            }
        }
        for (Document m : status.getList("members", Document.class)) {
            Date optime = m.getDate("optimeDate");
            long lagS = primaryOptime == null || optime == null ? -1
                    : (primaryOptime.getTime() - optime.getTime()) / 1000;
            members.add(new Document("name", m.getString("name"))
                    .append("state", m.getString("stateStr"))
                    .append("lagSeconds", lagS)
                    .append("syncSource", m.getString("syncSourceHost")));
        }
        return new Document("set", status.getString("set"))
                .append("term", status.get("term"))
                .append("members", members)
                .append("oplogWindowSeconds", oplogWindowSeconds());
    }

    // Window = newest oplog ts - oldest oplog ts. Alert on this in SECONDS (as a fraction of your longest
    // maintenance operation), not on oplog size in GB.
    public long oplogWindowSeconds() {
        var oplog = client.getDatabase("local").getCollection("oplog.rs");
        Document first = oplog.find().sort(Sorts.ascending("$natural")).limit(1)
                .projection(Projections.include("ts")).first();
        Document last = oplog.find().sort(Sorts.descending("$natural")).limit(1)
                .projection(Projections.include("ts")).first();
        if (first == null || last == null) {
            return -1;
        }
        BsonTimestamp a = first.get("ts", BsonTimestamp.class);
        BsonTimestamp b = last.get("ts", BsonTimestamp.class);
        return (long) b.getTime() - a.getTime();
    }

    // ================================================================ 13 sharding

    // Shard orders on {customerId: 1, _id: 1}: tenant-targeted queries (customerId is in every hot query),
    // and the _id suffix lets a whale customer's range split instead of forming a jumbo chunk.
    // Run via mongos, once; resharding later (5.0+) rewrites the whole collection.
    public Document shardOrdersCollection() {
        return client.getDatabase("admin").runCommand(new Document("shardCollection",
                db.getName() + "." + OrderDocuments.ORDERS)
                .append("key", new Document("customerId", 1).append("_id", 1)));
    }
}
