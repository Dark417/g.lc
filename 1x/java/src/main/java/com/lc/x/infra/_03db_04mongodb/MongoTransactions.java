package com.lc.x.infra._03db_04mongodb;

import static com.mongodb.client.model.Filters.and;
import static com.mongodb.client.model.Filters.eq;
import static com.mongodb.client.model.Filters.exists;
import static com.mongodb.client.model.Filters.gte;

import com.lc.x.domain._03db_04mongodb.InsufficientStockException;
import com.lc.x.domain._03db_04mongodb.LineItem;
import com.lc.x.domain._03db_04mongodb.NewOrder;
import com.lc.x.domain._03db_04mongodb.Order;
import com.lc.x.shared.Retry;
import com.mongodb.MongoException;
import com.mongodb.ReadConcern;
import com.mongodb.ReadPreference;
import com.mongodb.TransactionOptions;
import com.mongodb.WriteConcern;
import com.mongodb.client.ClientSession;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Updates;
import com.mongodb.client.result.UpdateResult;
import java.time.Instant;
import java.util.concurrent.TimeUnit;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * Multi-document transactions (replica set 4.0+, sharded 4.2+): snapshot isolation on WiredTiger MVCC.
 * - Default = single-document atomic updates; a transaction is for an invariant that genuinely spans documents.
 * - EVERY operation inside must carry the session, or it silently runs outside the transaction.
 * - The body re-runs on TransientTransactionError: no HTTP calls, publishes, or emails inside it.
 * - 60 s default lifetime (transactionLifetimeLimitSeconds); an open transaction pins old versions node-wide.
 */
@Component
@ConditionalOnProperty(name = "x.mongodb.enabled", havingValue = "true")
public class MongoTransactions {

    static final int MAX_TX_ATTEMPTS = 5;

    // snapshot reads + majority commit; primary is required for reads inside a transaction anyway.
    static final TransactionOptions TX_OPTIONS = TransactionOptions.builder()
            .readConcern(ReadConcern.SNAPSHOT)
            .writeConcern(WriteConcern.MAJORITY)
            .readPreference(ReadPreference.primary())
            .maxCommitTime(5L, TimeUnit.SECONDS)
            .build();

    private final MongoClient client;
    private final MongoCollection<Document> orders;
    private final MongoCollection<Document> inventory;
    private final MongoCollection<Document> rotas;

    public MongoTransactions(MongoClient client, MongoDatabase db) {
        this.client = client;
        this.orders = db.getCollection(OrderDocuments.ORDERS);
        this.inventory = db.getCollection(OrderDocuments.INVENTORY);
        this.rotas = db.getCollection(OrderDocuments.ROTAS);
    }

    // ================================================================ 12 transactions

    // Order + inventory decrement, both or neither, via the callback API. withTransaction retries the body on
    // TransientTransactionError and the commit on UnknownTransactionCommitResult, up to ~120 s total.
    // A non-Mongo exception (InsufficientStockException) aborts with NO retry.
    public Order placeOrder(NewOrder o) {
        try (ClientSession session = client.startSession()) {
            return session.withTransaction(() -> placeOrderBody(session, o), TX_OPTIONS);
        }
    }

    // The body: pure database work, safe to run more than once (the ObjectId is generated per attempt).
    private Order placeOrderBody(ClientSession session, NewOrder o) {
        for (LineItem item : o.items()) {
            // Conditional decrement: the $gte predicate and the $inc are one atomic step per document.
            UpdateResult r = inventory.updateOne(session,
                    and(eq("_id", item.sku()), gte("qty", item.qty())),
                    Updates.inc("qty", -item.qty()));
            if (r.getMatchedCount() == 0) {
                throw new InsufficientStockException(item.sku(), item.qty());
            }
        }
        Instant now = OrderDocuments.nowMillis();
        Document doc = OrderDocuments.newOrderDocument(new ObjectId(), o, now);
        orders.insertOne(session, doc); // session is ALWAYS the first argument
        return OrderDocuments.toOrder(doc);
    }

    // The same transaction with the retry loop written out, to show what withTransaction does:
    // - TransientTransactionError -> abort, back off, rerun the WHOLE body (new snapshot).
    // - UnknownTransactionCommitResult -> retry ONLY commitTransaction (idempotent per txnNumber).
    // - Attempt cap: a permanently conflicting transaction (hot counter) must surface, not spin for 120 s.
    public Order placeOrderHandRolled(NewOrder o) {
        Retry backoff = Retry.defaults();
        try (ClientSession session = client.startSession()) {
            for (int attempt = 0; ; attempt++) {
                session.startTransaction(TX_OPTIONS);
                try {
                    Order placed = placeOrderBody(session, o);
                    commitWithRetry(session);
                    return placed;
                } catch (MongoException e) {
                    if (session.hasActiveTransaction()) {
                        session.abortTransaction();
                    }
                    boolean transientError = e.hasErrorLabel(MongoException.TRANSIENT_TRANSACTION_ERROR_LABEL);
                    if (!transientError || attempt + 1 >= MAX_TX_ATTEMPTS) {
                        throw e;
                    }
                    Retry.sleep(backoff.backoff(attempt));
                } catch (RuntimeException e) {
                    if (session.hasActiveTransaction()) {
                        session.abortTransaction(); // business error: abort, never retry
                    }
                    throw e;
                }
            }
        }
    }

    private static void commitWithRetry(ClientSession session) {
        for (int attempt = 0; ; attempt++) {
            try {
                session.commitTransaction();
                return;
            } catch (MongoException e) {
                if (!e.hasErrorLabel(MongoException.UNKNOWN_TRANSACTION_COMMIT_RESULT_LABEL)
                        || attempt + 1 >= MAX_TX_ATTEMPTS) {
                    throw e; // a TransientTransactionError here propagates to the outer loop
                }
            }
        }
    }

    // Write skew, fixed WITHOUT a transaction: the invariant "at least one engineer on call" lives in ONE
    // document, and the predicate "oncall.1 exists" (>= 2 on call) is checked atomically with the $pull.
    // Two concurrent calls cannot both succeed when only two are on call. Snapshot isolation would allow it.
    public boolean goOffCall(String rotaId, String engineer) {
        return rotas.updateOne(
                and(eq("_id", rotaId), eq("oncall", engineer), exists("oncall.1", true)),
                Updates.pull("oncall", engineer))
                .getModifiedCount() == 1;
    }

    // Saga step instead of a cross-shard transaction: reserve stock with a single-document conditional
    // update (atomic, no 2PC), create the order separately, and release the reservation if that fails.
    // A reaper job releases reservations whose holder crashed (TTL on reservedUntil).
    public boolean reserveStock(String sku, int qty, String orderId, Instant reservedUntil) {
        return inventory.updateOne(
                and(eq("_id", sku), gte("qty", qty)),
                Updates.combine(
                        Updates.inc("qty", -qty),
                        Updates.push("reservations",
                                new Document("orderId", orderId).append("qty", qty).append("until", reservedUntil))))
                .getModifiedCount() == 1;
    }
}
