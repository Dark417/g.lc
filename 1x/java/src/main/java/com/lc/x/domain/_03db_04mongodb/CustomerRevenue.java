package com.lc.x.domain._03db_04mongodb;

/** Row of the revenue-by-customer aggregation ($match -> $unwind -> $group -> $lookup). */
public record CustomerRevenue(String customerId, String customerName, long revenueCents, int orderCount) {
}
