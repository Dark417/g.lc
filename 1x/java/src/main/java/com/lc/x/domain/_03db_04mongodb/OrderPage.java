package com.lc.x.domain._03db_04mongodb;

import java.util.List;

/** One keyset page. nextCursor == null means there are no more pages. */
public record OrderPage(List<Order> items, String nextCursor) {
}
