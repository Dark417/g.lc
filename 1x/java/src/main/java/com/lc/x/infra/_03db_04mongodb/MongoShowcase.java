package com.lc.x.infra._03db_04mongodb;

import static com.mongodb.client.model.Filters.and;
import static com.mongodb.client.model.Filters.elemMatch;
import static com.mongodb.client.model.Filters.eq;
import static com.mongodb.client.model.Filters.exists;
import static com.mongodb.client.model.Filters.gte;
import static com.mongodb.client.model.Filters.in;
import static com.mongodb.client.model.Filters.lt;
import static com.mongodb.client.model.Filters.or;
import static com.mongodb.client.model.Filters.text;
import static com.mongodb.client.model.Sorts.ascending;
import static com.mongodb.client.model.Sorts.descending;
import static com.mongodb.client.model.Sorts.metaTextScore;
import static com.mongodb.client.model.Sorts.orderBy;

import com.lc.x.config._03db_04mongodb.MongoProperties;
import com.lc.x.domain._03db_04mongodb.BulkSummary;
import com.lc.x.domain._03db_04mongodb.CustomerRevenue;
import com.lc.x.domain._03db_04mongodb.LineItem;
import com.lc.x.domain._03db_04mongodb.NewOrder;
import com.lc.x.domain._03db_04mongodb.Order;
import com.lc.x.domain._03db_04mongodb.OrderNotFoundException;
import com.lc.x.domain._03db_04mongodb.OrderPage;
import com.lc.x.domain._03db_04mongodb.OrderStatus;
import com.lc.x.domain._03db_04mongodb.QueryPlanSummary;
import com.lc.x.domain._03db_04mongodb.StockLevel;
import com.lc.x.domain._03db_04mongodb.VersionConflictException;
import com.mongodb.ClientSessionOptions;
import com.mongodb.ExplainVerbosity;
import com.mongodb.MongoBulkWriteException;
import com.mongodb.MongoCommandException;
import com.mongodb.MongoWriteConcernException;
import com.mongodb.ReadPreference;
import com.mongodb.bulk.BulkWriteResult;
import com.mongodb.client.ClientSession;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Accumulators;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.BulkWriteOptions;
import com.mongodb.client.model.Collation;
import com.mongodb.client.model.CollationStrength;
import com.mongodb.client.model.CreateCollectionOptions;
import com.mongodb.client.model.Facet;
import com.mongodb.client.model.Field;
import com.mongodb.client.model.FindOneAndUpdateOptions;
import com.mongodb.client.model.IndexOptions;
import com.mongodb.client.model.Indexes;
import com.mongodb.client.model.MergeOptions;
import com.mongodb.client.model.Projections;
import com.mongodb.client.model.ReturnDocument;
import com.mongodb.client.model.UnwindOptions;
import com.mongodb.client.model.UpdateOneModel;
import com.mongodb.client.model.UpdateOptions;
import com.mongodb.client.model.Updates;
import com.mongodb.client.model.ValidationAction;
import com.mongodb.client.model.ValidationLevel;
import com.mongodb.client.model.ValidationOptions;
import com.mongodb.client.model.WriteModel;
import com.mongodb.client.result.UpdateResult;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.bson.types.ObjectId;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * MongoDB showcase (Java sync driver): one public method per concept, in x-md/03db/04mongodb.* order.
 * - Filters/Updates/Sorts builders produce the same BSON as mongosh; Document.parse is used where a raw
 *   stage reads clearer than builders.
 * - Every user-facing read carries maxTime: MongoDB has no statement timeout by default.
 * - Transactions: MongoTransactions; change streams: MongoChangeStreams; server/admin commands: MongoAdmin.
 */
@Component
@ConditionalOnProperty(name = "x.mongodb.enabled", havingValue = "true")
public class MongoShowcase {

    public static final String IDX_CUSTOMER_CREATED = "customer_created_id";
    public static final String IDX_PENDING = "pending_created";
    public static final String IDX_ITEMS_SKU = "items_sku";
    public static final String IDX_NOTE_TEXT = "note_text";
    public static final String IDX_PURGE_TTL = "purge_ttl";
    public static final String IDX_EMAIL_CI = "email_ci_unique";
    public static final String IDX_BUCKET = "order_bucket";
    static final int BUCKET_SIZE = 200;
    static final Duration SOFT_DELETE_RETENTION = Duration.ofDays(30);

    private final MongoClient client;
    private final MongoDatabase db;
    private final MongoCollection<Document> orders;
    private final MongoCollection<Document> inventory;
    private final MongoCollection<Document> customers;
    private final long maxTimeMs;

    public MongoShowcase(MongoClient client, MongoDatabase db, MongoProperties props) {
        this.client = client;
        this.db = db;
        this.orders = ConsistencyProfiles.userFacing(db, OrderDocuments.ORDERS);
        this.inventory = db.getCollection(OrderDocuments.INVENTORY);
        this.customers = db.getCollection(OrderDocuments.CUSTOMERS);
        this.maxTimeMs = props.maxTime().toMillis();
    }

    // ================================================================ 01 document model + validation

    // $jsonSchema validator: types and required fields enforced by the server, for every producer.
    // When: the shape has stabilized. Catch: it cannot express "total document bytes"; moderate level
    // skips existing invalid documents so you can tighten the schema without a backfill first.
    public void applyOrderValidator() {
        Document schema = Document.parse("""
                { $jsonSchema: {
                    bsonType: "object",
                    required: ["customerId", "status", "items", "totalCents", "createdAt", "version"],
                    properties: {
                      customerId: { bsonType: "string" },
                      status:     { enum: ["PENDING", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"] },
                      items:      { bsonType: "array", minItems: 1, maxItems: 100,
                                    items: { bsonType: "object", required: ["sku", "qty", "priceCents"],
                                             properties: { qty: { bsonType: ["int", "long"], minimum: 1 },
                                                           priceCents: { bsonType: ["int", "long"] } } } },
                      totalCents: { bsonType: ["int", "long"] },
                      createdAt:  { bsonType: "date" },
                      version:    { bsonType: ["int", "long"] }
                } } }""");
        try {
            db.createCollection(OrderDocuments.ORDERS, new CreateCollectionOptions().validationOptions(
                    new ValidationOptions().validator(schema)
                            .validationLevel(ValidationLevel.MODERATE)
                            .validationAction(ValidationAction.ERROR)));
        } catch (MongoCommandException e) {
            if (e.getErrorCode() != MongoErrors.NAMESPACE_EXISTS) {
                throw e;
            }
            // Collection exists: change the validator in place.
            db.runCommand(new Document("collMod", OrderDocuments.ORDERS)
                    .append("validator", schema)
                    .append("validationLevel", "moderate")
                    .append("validationAction", "error"));
        }
    }

    // ================================================================ 03 schema design

    // Embed + extended reference: items live inside the order, the customer's name is copied onto it.
    // One insert, one document, atomic by construction. Catch: insertOne mutates nothing else; a crash
    // after it but before a follow-up write leaves no partial order.
    public Order insertOrder(NewOrder o) {
        Instant now = OrderDocuments.nowMillis();
        Document doc = OrderDocuments.newOrderDocument(new ObjectId(), o, now);
        orders.insertOne(doc);
        return OrderDocuments.toOrder(doc);
    }

    // Extended-reference fan-out: the duplicated name must be updated everywhere it was copied.
    // When: the copied field is near-immutable. Catch: fan-out = documents touched per change; at 1M orders
    // per customer this is a replication-lag event, so run it async and rate-limited.
    public long renameCustomerEverywhere(String customerId, String newName) {
        customers.updateOne(eq("_id", customerId), Updates.set("name", newName));
        return orders.updateMany(eq("customerId", customerId), Updates.set("customerName", newName))
                .getModifiedCount();
    }

    // Bucket pattern: append to the open bucket (count < 200) or upsert a new one. Caps array growth
    // structurally, so no document ever approaches 16 MB. Catch: under a race two buckets can open at once;
    // harmless because readers sort by firstAt and the count bound still holds per bucket.
    public void appendOrderEvent(String orderId, String event) {
        Instant now = OrderDocuments.nowMillis();
        db.getCollection(OrderDocuments.ORDER_EVENTS).updateOne(
                and(eq("orderId", orderId), lt("count", BUCKET_SIZE)),
                Updates.combine(
                        Updates.push("events", new Document("at", now).append("event", event)),
                        Updates.inc("count", 1),
                        Updates.setOnInsert("firstAt", now)),
                new UpdateOptions().upsert(true));
    }

    // ================================================================ 04 CRUD + update operators

    public Optional<Order> findOrder(String orderId) {
        Document d = orders.find(eq("_id", OrderDocuments.objectId(orderId)))
                .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
                .first();
        return Optional.ofNullable(d).map(OrderDocuments::toOrder);
    }

    // $elemMatch: ONE array element must satisfy both predicates. Without it, {items.sku: X, items.qty: {$gte: n}}
    // matches when different elements satisfy each part. Projection drops the free-text note.
    public List<Order> findOpenOrdersWithSku(String sku, int minQty, int limit) {
        return orders.find(and(
                        in("status", OrderStatus.PENDING.name(), OrderStatus.PAID.name()),
                        elemMatch("items", and(eq("sku", sku), gte("qty", minQty)))))
                .projection(Projections.exclude("note"))
                .sort(orderBy(descending("createdAt"), descending("_id"))) // _id = tiebreaker, stable order
                .limit(limit)
                .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
                .map(OrderDocuments::toOrder)
                .into(new ArrayList<>());
    }

    // $push + $inc + $currentDate in ONE atomic update; the filter bounds the array ("items.99" must not exist).
    // Returns the document AFTER the update: no read-after-write round trip.
    public Optional<Order> addItem(String orderId, LineItem item) {
        Document after = orders.findOneAndUpdate(
                and(eq("_id", OrderDocuments.objectId(orderId)),
                        eq("status", OrderStatus.PENDING.name()),
                        exists("items." + (NewOrder.MAX_ITEMS - 1), false)),
                Updates.combine(
                        Updates.push("items", OrderDocuments.itemDocument(item)),
                        Updates.inc("totalCents", item.subtotalCents()),
                        Updates.inc("version", 1L),
                        Updates.currentDate("updatedAt")),
                new FindOneAndUpdateOptions().returnDocument(ReturnDocument.AFTER));
        return Optional.ofNullable(after).map(OrderDocuments::toOrder);
    }

    // Positional $: updates the FIRST element matched by the query, so the array field must be in the filter.
    // The total is then recomputed by a pipeline update instead of trusting client arithmetic.
    public Optional<Order> incrementItemQty(String orderId, String sku, int by) {
        UpdateResult r = orders.updateOne(
                and(eq("_id", OrderDocuments.objectId(orderId)), eq("items.sku", sku)),
                Updates.combine(Updates.inc("items.$.qty", by), Updates.inc("version", 1L)));
        return r.getMatchedCount() == 0 ? Optional.empty() : recomputeTotal(orderId);
    }

    // Filtered positional $[i] + arrayFilters: touch every element matching a named filter.
    public long markBackordered(String orderId, Set<String> skus) {
        return orders.updateOne(
                eq("_id", OrderDocuments.objectId(orderId)),
                Updates.set("items.$[i].backordered", true),
                new UpdateOptions().arrayFilters(List.of(in("i.sku", skus))))
                .getModifiedCount();
    }

    // Pipeline update (4.2+): the new value is computed from other fields of the same document, server-side.
    // Integer arithmetic only: $multiply on int64 stays int64; one double operand would widen everything.
    public Optional<Order> recomputeTotal(String orderId) {
        List<Bson> pipeline = List.of(Document.parse("""
                { $set: { totalCents: { $sum: { $map: { input: "$items",
                            in: { $multiply: ["$$this.qty", "$$this.priceCents"] } } } },
                          updatedAt: "$$NOW" } }"""));
        Document after = orders.findOneAndUpdate(eq("_id", OrderDocuments.objectId(orderId)), pipeline,
                new FindOneAndUpdateOptions().returnDocument(ReturnDocument.AFTER));
        return Optional.ofNullable(after).map(OrderDocuments::toOrder);
    }

    // Atomic counter: findOneAndUpdate + upsert + $inc returns the new value in one round trip.
    // Catch: one hot document serializes every caller (write conflicts); shard the counter if it is hot.
    public long nextSequence(String name) {
        Document d = db.getCollection(OrderDocuments.COUNTERS).findOneAndUpdate(
                eq("_id", name),
                Updates.combine(Updates.inc("seq", 1L), Updates.setOnInsert("createdAt", OrderDocuments.nowMillis())),
                new FindOneAndUpdateOptions().upsert(true).returnDocument(ReturnDocument.AFTER));
        return OrderDocuments.num(d, "seq");
    }

    // Work-queue claim: find the oldest unclaimed PENDING order and claim it atomically. Two workers can
    // never claim the same order because the filter (claimedBy absent) and the $set are one atomic step.
    public Optional<Order> claimOldestPending(String worker) {
        Document d = orders.findOneAndUpdate(
                and(eq("status", OrderStatus.PENDING.name()), exists("claimedBy", false)),
                Updates.combine(Updates.set("claimedBy", worker), Updates.currentDate("claimedAt")),
                new FindOneAndUpdateOptions()
                        .sort(ascending("createdAt"))       // served by the partial pending index
                        .returnDocument(ReturnDocument.AFTER));
        return Optional.ofNullable(d).map(OrderDocuments::toOrder);
    }

    // Optimistic lock: the version is part of the filter; no match = someone else won (or no such order).
    // No transaction needed: a single-document update is atomic.
    public Order changeStatusWithVersion(String orderId, OrderStatus status, long expectedVersion) {
        ObjectId id = OrderDocuments.objectId(orderId);
        Document after = orders.findOneAndUpdate(
                and(eq("_id", id), eq("version", expectedVersion)),
                Updates.combine(
                        Updates.set("status", status.name()),
                        Updates.inc("version", 1L),
                        Updates.currentDate("updatedAt")),
                new FindOneAndUpdateOptions().returnDocument(ReturnDocument.AFTER));
        if (after != null) {
            return OrderDocuments.toOrder(after);
        }
        // Disambiguate with one read: missing order vs. version moved (return the winner's state).
        Order current = findOrder(orderId).orElseThrow(() -> new OrderNotFoundException(orderId));
        throw new VersionConflictException(orderId, expectedVersion, current);
    }

    // Soft delete: mark now, let the TTL index purge 30 days later. Catch: TTL deletion runs every ~60 s
    // and can lag under load, so readers must still filter deletedAt.
    public boolean softDelete(String orderId) {
        Instant now = OrderDocuments.nowMillis();
        return orders.updateOne(
                and(eq("_id", OrderDocuments.objectId(orderId)), exists("deletedAt", false)),
                Updates.combine(Updates.set("deletedAt", now), Updates.set("purgeAt", now.plus(SOFT_DELETE_RETENTION))))
                .getModifiedCount() == 1;
    }

    public long deleteCancelledBefore(Instant cutoff) {
        return orders.deleteMany(and(eq("status", OrderStatus.CANCELLED.name()), lt("createdAt", cutoff)))
                .getDeletedCount();
    }

    // ================================================================ 05 bulk write

    // Unordered bulk upsert: one round trip for N ops, keeps going past a failing op. Catch: NOT atomic;
    // successful ops stay applied, so the error list must be reconciled, and a blind resend must be idempotent
    // (upsert by _id is). ordered=true would stop at the first error and still keep the earlier writes.
    public BulkSummary upsertStock(List<StockLevel> levels) {
        Instant now = OrderDocuments.nowMillis();
        List<WriteModel<Document>> ops = new ArrayList<>();
        for (StockLevel s : levels) {
            ops.add(new UpdateOneModel<>(
                    eq("_id", s.sku()),
                    Updates.combine(Updates.set("qty", s.qty()), Updates.set("updatedAt", now),
                            Updates.setOnInsert("createdAt", now)),
                    new UpdateOptions().upsert(true)));
        }
        try {
            return summary(inventory.bulkWrite(ops, new BulkWriteOptions().ordered(false)), List.of());
        } catch (MongoBulkWriteException e) {
            List<String> errors = e.getWriteErrors().stream()
                    .map(w -> w.getIndex() + ":" + w.getCode() + ":" + w.getMessage())
                    .toList();
            return summary(e.getWriteResult(), errors);
        }
    }

    private static BulkSummary summary(BulkWriteResult r, List<String> errors) {
        if (!r.wasAcknowledged()) {
            return new BulkSummary(0, 0, 0, 0, 0, errors);
        }
        return new BulkSummary(r.getInsertedCount(), r.getMatchedCount(), r.getModifiedCount(),
                r.getUpserts().size(), r.getDeletedCount(), errors);
    }

    // ================================================================ 06 indexes

    // Idempotent index set. Each index names the query it serves; ESR = Equality, Sort, Range.
    // Catch: createIndex on a large collection is online but saturates disk/cache; run it from a migration
    // job, never from every app instance at startup.
    public List<String> ensureIndexes() {
        List<String> names = new ArrayList<>();
        // E = customerId, S = createdAt desc, then _id desc as the keyset tiebreaker.
        names.add(orders.createIndex(
                Indexes.compoundIndex(Indexes.ascending("customerId"), Indexes.descending("createdAt"),
                        Indexes.descending("_id")),
                new IndexOptions().name(IDX_CUSTOMER_CREATED)));
        // Partial: only PENDING orders are indexed (a few % of the collection) -> small, cache-resident.
        // The planner uses it ONLY when the query provably implies status == "PENDING".
        names.add(orders.createIndex(
                Indexes.compoundIndex(Indexes.ascending("status"), Indexes.ascending("createdAt")),
                new IndexOptions().name(IDX_PENDING).partialFilterExpression(eq("status", OrderStatus.PENDING.name()))));
        // Multikey: one index entry per array element; can never cover a query.
        names.add(orders.createIndex(Indexes.ascending("items.sku"), new IndexOptions().name(IDX_ITEMS_SKU)));
        // Text: one per collection; term matching with a crude score, not relevance ranking.
        names.add(orders.createIndex(Indexes.text("note"), new IndexOptions().name(IDX_NOTE_TEXT)));
        // TTL: background thread deletes when purgeAt < now (runs ~every 60 s, primary only). Date type only.
        names.add(orders.createIndex(Indexes.ascending("purgeAt"),
                new IndexOptions().name(IDX_PURGE_TTL).expireAfter(0L, TimeUnit.SECONDS)));
        // Unique + case-insensitive: queries must pass the SAME collation to use it.
        names.add(customers.createIndex(Indexes.ascending("email"), new IndexOptions()
                .name(IDX_EMAIL_CI).unique(true)
                .collation(Collation.builder().locale("en").collationStrength(CollationStrength.SECONDARY).build())));
        names.add(db.getCollection(OrderDocuments.ORDER_EVENTS).createIndex(
                Indexes.compoundIndex(Indexes.ascending("orderId"), Indexes.ascending("count")),
                new IndexOptions().name(IDX_BUCKET)));
        return names;
    }

    // Hide before drop: the planner ignores a hidden index but it is still maintained, so un-hiding is
    // instant. Dropping and rebuilding a multi-TB index is hours.
    public void setIndexHidden(String indexName, boolean hidden) {
        db.runCommand(new Document("collMod", OrderDocuments.ORDERS)
                .append("index", new Document("name", indexName).append("hidden", hidden)));
    }

    // $indexStats: per-index access counters since the last restart. Snapshot them over 35+ days before
    // trusting "unused": monthly jobs and restarts both fool a single reading.
    public List<String> unusedIndexes() {
        List<String> unused = new ArrayList<>();
        for (Document s : orders.aggregate(List.of(new Document("$indexStats", new Document())))) {
            long ops = OrderDocuments.num(s.get("accesses", Document.class), "ops");
            if (ops == 0 && !"_id_".equals(s.getString("name"))) {
                unused.add(s.getString("name"));
            }
        }
        return unused;
    }

    // $text search sorted by relevance score. Catch: needs the text index; cannot be hinted.
    public List<Order> searchNotes(String terms, int limit) {
        return orders.find(text(terms))
                .projection(Projections.metaTextScore("score"))
                .sort(metaTextScore("score"))
                .limit(limit)
                .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
                .map(OrderDocuments::toOrder)
                .into(new ArrayList<>());
    }

    // ================================================================ 07 query planner + explain

    // explain("executionStats") and the four numbers that matter. Run it on production-shaped data:
    // the planner's trial stops at 101 results, so small fixtures pick different plans.
    public QueryPlanSummary explainCustomerOrders(String customerId) {
        Document plan = orders.find(eq("customerId", customerId))
                .sort(orderBy(descending("createdAt"), descending("_id")))
                .limit(20)
                .explain(ExplainVerbosity.EXECUTION_STATS);
        Document stats = plan.get("executionStats", Document.class);
        Document winning = plan.get("queryPlanner", Document.class).get("winningPlan", Document.class);
        List<String> stages = new ArrayList<>();
        String index = collectStages(winning, stages);
        return new QueryPlanSummary(
                stages.isEmpty() ? "UNKNOWN" : stages.get(0),
                index,
                OrderDocuments.num(stats, "totalKeysExamined"),
                OrderDocuments.num(stats, "totalDocsExamined"),
                OrderDocuments.num(stats, "nReturned"),
                OrderDocuments.num(stats, "executionTimeMillis"),
                stages.contains("SORT"),
                !stages.contains("FETCH") && stages.contains("IXSCAN"));
    }

    // Walks stage -> inputStage (SBE plans nest under queryPlan); returns the index name if any.
    private static String collectStages(Document node, List<String> out) {
        if (node == null) {
            return null;
        }
        Document plan = node.containsKey("queryPlan") ? node.get("queryPlan", Document.class) : node;
        out.add(plan.getString("stage"));
        String index = plan.getString("indexName");
        String below = collectStages(plan.get("inputStage", Document.class), out);
        return index != null ? index : below;
    }

    // hint(): pin the plan for a shape where a wrong pick breaches the SLO (e.g. multi-tenant skew).
    // Catch: you now own the choice forever; a renamed index fails the query, a better new index is ignored.
    public List<Order> customerOrdersHinted(String customerId, int limit) {
        return orders.find(eq("customerId", customerId))
                .sort(orderBy(descending("createdAt"), descending("_id")))
                .hintString(IDX_CUSTOMER_CREATED)
                .limit(limit)
                .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
                .map(OrderDocuments::toOrder)
                .into(new ArrayList<>());
    }

    // ================================================================ 08 pagination

    // Keyset pagination on (createdAt, _id): each page is one bounded index seek, O(page) not O(offset).
    // Fetch limit+1 to know whether a next page exists without a count query.
    public OrderPage listCustomerOrders(String customerId, int limit, String cursor) {
        OrderCursor after = OrderCursor.decode(cursor);
        Bson filter = eq("customerId", customerId);
        if (after != null) {
            filter = and(filter, or(
                    lt("createdAt", after.createdAt()),
                    and(eq("createdAt", after.createdAt()), lt("_id", after.id()))));
        }
        List<Document> rows = orders.find(filter)
                .sort(orderBy(descending("createdAt"), descending("_id"))) // must match the index direction
                .limit(limit + 1)
                .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
                .into(new ArrayList<>());
        boolean more = rows.size() > limit;
        List<Order> page = rows.stream().limit(limit).map(OrderDocuments::toOrder).toList();
        String next = null;
        if (more) {
            Document last = rows.get(limit - 1);
            next = new OrderCursor(OrderDocuments.instant(last, "createdAt"), last.getObjectId("_id")).encode();
        }
        return new OrderPage(page, next);
    }

    // Anti-pattern kept for contrast: skip(N) walks and discards N index keys per page, and rows shift
    // under concurrent inserts (duplicates / gaps between pages).
    public List<Order> listCustomerOrdersBySkip(String customerId, int page, int size) {
        return orders.find(eq("customerId", customerId))
                .sort(orderBy(descending("createdAt"), descending("_id")))
                .skip(page * size)
                .limit(size)
                .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
                .map(OrderDocuments::toOrder)
                .into(new ArrayList<>());
    }

    // ================================================================ 09 aggregation

    // $match first (index-eligible) -> $unwind -> $group -> $sort+$limit (top-k, memory-bounded)
    // -> $lookup AFTER the limit (10 lookups, not one per order) -> $project.
    public List<CustomerRevenue> revenueByCustomer(Instant since, int limit) {
        List<Bson> pipeline = List.of(
                Aggregates.match(and(in("status", "PAID", "SHIPPED", "DELIVERED"), gte("createdAt", since))),
                Aggregates.unwind("$items"),
                Aggregates.group("$customerId",
                        Accumulators.sum("revenueCents",
                                new Document("$multiply", List.of("$items.qty", "$items.priceCents"))),
                        Accumulators.addToSet("orderIds", "$_id")),
                Aggregates.addFields(new Field<>("orderCount", new Document("$size", "$orderIds"))),
                Aggregates.sort(descending("revenueCents")),
                Aggregates.limit(limit),
                Aggregates.lookup(OrderDocuments.CUSTOMERS, "_id", "_id", "customer"),
                Aggregates.unwind("$customer", new UnwindOptions().preserveNullAndEmptyArrays(true)),
                Aggregates.project(Projections.fields(
                        Projections.computed("customerId", "$_id"),
                        Projections.computed("customerName", "$customer.name"),
                        Projections.include("revenueCents", "orderCount"))));
        List<CustomerRevenue> out = new ArrayList<>();
        for (Document d : orders.aggregate(pipeline).allowDiskUse(true).maxTime(maxTimeMs, TimeUnit.MILLISECONDS)) {
            out.add(new CustomerRevenue(d.getString("customerId"), d.getString("customerName"),
                    OrderDocuments.num(d, "revenueCents"), (int) OrderDocuments.num(d, "orderCount")));
        }
        return out;
    }

    // $facet: several sub-pipelines over ONE input in one round trip (counts by status + latest 5 + total).
    // Catch: the facet output is one document, so it must stay under 16 MB.
    public Document statusFacets(String customerId) {
        return orders.aggregate(List.of(
                        Aggregates.match(eq("customerId", customerId)),
                        Aggregates.facet(
                                new Facet("byStatus", Aggregates.group("$status", Accumulators.sum("n", 1))),
                                new Facet("latest", Aggregates.sort(descending("createdAt")), Aggregates.limit(5),
                                        Aggregates.project(Projections.include("status", "totalCents", "createdAt"))),
                                new Facet("total", Aggregates.count("n")))))
                .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
                .first();
    }

    // $setWindowFields (5.0+): running total per customer without a self-join.
    public List<Document> runningTotals(String customerId) {
        return orders.aggregate(List.of(
                        Aggregates.match(eq("customerId", customerId)),
                        Document.parse("""
                                { $setWindowFields: { partitionBy: "$customerId", sortBy: { createdAt: 1 },
                                    output: { runningTotalCents: { $sum: "$totalCents",
                                              window: { documents: ["unbounded", "current"] } } } } }"""),
                        Aggregates.project(Projections.include("createdAt", "totalCents", "runningTotalCents"))))
                .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
                .into(new ArrayList<>());
    }

    // $merge: materialize a daily revenue rollup (upsert per day) instead of recomputing it on every read.
    // Run it on a schedule; readers hit the small daily_revenue collection.
    public void materializeDailyRevenue(Instant since) {
        orders.aggregate(List.of(
                        Aggregates.match(and(in("status", "PAID", "SHIPPED", "DELIVERED"), gte("createdAt", since))),
                        Document.parse("""
                                { $group: { _id: { $dateTrunc: { date: "$createdAt", unit: "day" } },
                                            revenueCents: { $sum: "$totalCents" }, orders: { $sum: 1 } } }"""),
                        Aggregates.merge(OrderDocuments.DAILY_REVENUE, new MergeOptions()
                                .whenMatched(MergeOptions.WhenMatched.REPLACE)
                                .whenNotMatched(MergeOptions.WhenNotMatched.INSERT))))
                .allowDiskUse(true)
                .toCollection(); // $merge runs only when the result is consumed or toCollection() is called
    }

    // ================================================================ 11 read/write concern

    /** Outcome of an idempotent ledger write. */
    public enum LedgerWrite { APPLIED, ALREADY_APPLIED, UNKNOWN_RECHECK }

    // Idempotent write under majority + wtimeout. The payment id IS the _id, and the write is an upsert with
    // $setOnInsert, so a retry converges instead of duplicating. A wtimeout (write concern error) is
    // ambiguous: the write may be applied and may still replicate; the caller re-checks, never blind-retries.
    public LedgerWrite recordLedgerEntry(String paymentId, long amountCents) {
        MongoCollection<Document> ledger = ConsistencyProfiles.ledger(db, OrderDocuments.LEDGER);
        try {
            UpdateResult r = ledger.updateOne(eq("_id", paymentId),
                    Updates.combine(Updates.setOnInsert("amountCents", amountCents),
                            Updates.setOnInsert("at", OrderDocuments.nowMillis())),
                    new UpdateOptions().upsert(true));
            return r.getUpsertedId() != null ? LedgerWrite.APPLIED : LedgerWrite.ALREADY_APPLIED;
        } catch (MongoWriteConcernException e) {
            return LedgerWrite.UNKNOWN_RECHECK;
        }
    }

    // Read-your-writes on a secondary: a causally consistent session sends afterClusterTime, so the
    // secondary WAITS until it has replicated our write. Catch: stale read becomes a slow read; and the
    // guarantee is per session, so it breaks across services unless the cluster time is propagated.
    public Optional<Order> insertThenReadFromSecondary(NewOrder o) {
        try (ClientSession session = client.startSession(
                ClientSessionOptions.builder().causallyConsistent(true).build())) {
            Instant now = OrderDocuments.nowMillis();
            Document doc = OrderDocuments.newOrderDocument(new ObjectId(), o, now);
            orders.insertOne(session, doc); // majority write (userFacing profile)
            Document read = orders.withReadPreference(ReadPreference.secondaryPreferred())
                    .find(session, eq("_id", doc.getObjectId("_id")))
                    .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
                    .first();
            return Optional.ofNullable(read).map(OrderDocuments::toOrder);
        }
    }
}
