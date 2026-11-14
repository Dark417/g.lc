package com.lc.x.domain._03db_01aurora;

/** Order lifecycle. NEW and PAID count as "open" for the credit-limit invariant. */
public enum OrderStatus {
    NEW,
    PAID,
    SHIPPED,
    CANCELLED
}
