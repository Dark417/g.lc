package com.lc.x.infra._03db_04mongodb;

import com.mongodb.ReadConcern;
import com.mongodb.ReadPreference;
import com.mongodb.Tag;
import com.mongodb.TagSet;
import com.mongodb.WriteConcern;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import java.util.concurrent.TimeUnit;
import org.bson.Document;

/**
 * Write concern + read concern + read preference, decided ONCE per data flow and named here.
 * - The three knobs are orthogonal: "we write with majority" says nothing about what reads see.
 * - The failure mode is drift: someone copies the telemetry w:1 into a ledger path. Named profiles stop that.
 * - maxStalenessSeconds minimum is 90; without it the driver may route to a member hours behind.
 * - DocumentDB: no tag sets, no linearizable/snapshot read concern outside transactions; check before reuse.
 */
public final class ConsistencyProfiles {

    private static final long MAX_STALENESS_S = 90;

    private ConsistencyProfiles() {
    }

    /** Ledger / payments: rollback-safe write, never read a doomed write, primary only. No j:true (majority covers it). */
    public static MongoCollection<Document> ledger(MongoDatabase db, String name) {
        return db.getCollection(name)
                .withWriteConcern(WriteConcern.MAJORITY.withWTimeout(5, TimeUnit.SECONDS))
                .withReadConcern(ReadConcern.MAJORITY)
                .withReadPreference(ReadPreference.primary());
    }

    /** User-facing entity (profile, order): majority write, read from primary for read-your-writes. */
    public static MongoCollection<Document> userFacing(MongoDatabase db, String name) {
        return db.getCollection(name)
                .withWriteConcern(WriteConcern.MAJORITY)
                .withReadConcern(ReadConcern.LOCAL)
                .withReadPreference(ReadPreference.primary());
    }

    /** Telemetry: losing a few points on failover is acceptable, so w:1 is a documented decision here. */
    public static MongoCollection<Document> telemetry(MongoDatabase db, String name) {
        return db.getCollection(name)
                .withWriteConcern(WriteConcern.W1)
                .withReadConcern(ReadConcern.LOCAL)
                .withReadPreference(ReadPreference.secondaryPreferred(MAX_STALENESS_S, TimeUnit.SECONDS));
    }

    /**
     * Analytics / BI: secondary (NOT secondaryPreferred) on a tagged analytics member, so it fails CLOSED
     * when that member is gone instead of landing on the primary and evicting the OLTP working set.
     */
    public static MongoCollection<Document> analytics(MongoDatabase db, String name) {
        return db.getCollection(name)
                .withReadConcern(ReadConcern.LOCAL)
                .withReadPreference(ReadPreference.secondary(
                        new TagSet(new Tag("nodeType", "analytics")), MAX_STALENESS_S, TimeUnit.SECONDS));
    }
}
