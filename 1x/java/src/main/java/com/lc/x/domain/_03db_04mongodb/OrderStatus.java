package com.lc.x.domain._03db_04mongodb;

/** Order lifecycle. Terminal statuses leave the partial "open orders" index (see MongoShowcase.ensureIndexes). */
public enum OrderStatus {
    PENDING, PAID, SHIPPED, DELIVERED, CANCELLED;

    public boolean isTerminal() {
        return this == DELIVERED || this == CANCELLED;
    }
}
