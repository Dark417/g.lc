package com.lc.x.infra._03db_04mongodb;

import static com.mongodb.client.model.Filters.eq;
import static com.mongodb.client.model.Filters.in;

import com.lc.x.domain._03db_04mongodb.OrderChange;
import com.lc.x.domain._03db_04mongodb.OrderStatus;
import com.mongodb.MongoException;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.ReplaceOptions;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import com.mongodb.client.model.changestream.FullDocument;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import org.bson.BsonDocument;
import org.bson.Document;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * Change streams: a resumable cursor over the oplog, emitting only MAJORITY-COMMITTED changes.
 * - That property is why they beat a "write then publish" outbox poller: they can never emit a write
 *   that a failover later rolls back.
 * - Delivery is at-least-once: persist the resume token AFTER handling; consumers must be idempotent.
 * - The token is only valid while its oplog entry exists: a consumer down longer than the oplog window
 *   gets ChangeStreamHistoryLost (286) and must reconcile from the collection, then restart.
 */
@Component
@ConditionalOnProperty(name = "x.mongodb.enabled", havingValue = "true")
public class MongoChangeStreams {

    private final MongoCollection<Document> orders;
    private final MongoCollection<Document> tokens;

    public MongoChangeStreams(MongoDatabase db) {
        this.orders = db.getCollection(OrderDocuments.ORDERS);
        this.tokens = db.getCollection(OrderDocuments.RESUME_TOKENS);
    }

    // ================================================================ 14 change streams

    // Consume up to maxEvents order changes, resuming from the last saved token.
    // tryNext() returns null after maxAwaitTime with no event, so a batch job can stop cleanly.
    // Returns how many events were handled.
    public int consumeOrderChanges(String consumer, int maxEvents, Consumer<OrderChange> handler) {
        var stream = orders.watch(List.of(
                        Aggregates.match(in("operationType", "insert", "update", "replace", "delete"))))
                .fullDocument(FullDocument.UPDATE_LOOKUP) // current doc at lookup time, not at event time
                .maxAwaitTime(1, TimeUnit.SECONDS);
        Optional<BsonDocument> saved = loadToken(consumer);
        if (saved.isPresent()) {
            stream = stream.resumeAfter(saved.get());
        }
        int handled = 0;
        try (MongoChangeStreamCursor<ChangeStreamDocument<Document>> cursor = stream.cursor()) {
            while (handled < maxEvents) {
                ChangeStreamDocument<Document> ev = cursor.tryNext();
                if (ev == null) {
                    break; // no event within maxAwaitTime
                }
                handler.accept(toChange(ev));
                saveToken(consumer, ev.getResumeToken()); // AFTER handling -> at-least-once
                handled++;
            }
        } catch (MongoException e) {
            if (MongoErrors.classify(e) == MongoErrors.Kind.HISTORY_LOST) {
                tokens.deleteOne(eq("_id", consumer)); // next run starts "now"; caller must reconcile the gap
            }
            throw e;
        }
        return handled;
    }

    private static OrderChange toChange(ChangeStreamDocument<Document> ev) {
        Document full = ev.getFullDocument(); // null for delete, or if the doc was deleted before lookup
        String id = ev.getDocumentKey() == null ? null
                : ev.getDocumentKey().getObjectId("_id").getValue().toHexString();
        OrderStatus status = full == null ? null : OrderStatus.valueOf(full.getString("status"));
        return new OrderChange(ev.getOperationTypeString(), id, status, ev.getResumeToken().toJson());
    }

    public Optional<BsonDocument> loadToken(String consumer) {
        Document d = tokens.find(eq("_id", consumer)).first();
        return Optional.ofNullable(d).map(x -> BsonDocument.parse(x.getString("token")));
    }

    // Upsert by consumer name; stored as JSON so it survives any codec. Use majority (the default) so the
    // token itself is not rolled back after we acted on the event.
    public void saveToken(String consumer, BsonDocument token) {
        tokens.replaceOne(eq("_id", consumer),
                new Document("_id", consumer).append("token", token.toJson()).append("at", OrderDocuments.nowMillis()),
                new ReplaceOptions().upsert(true));
    }
}
