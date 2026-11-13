package com.lc.x.x03_01_aurora.domain;

import java.util.List;

/** Report built from several queries that must agree with each other (one REPEATABLE READ snapshot). */
public record CustomerSummary(String customerId, long orderCount, long totalCents, List<Order> latest) {

    public CustomerSummary {
        latest = List.copyOf(latest);
    }
}
