package com.lc.x.x03_01_aurora.domain;

/** Order lifecycle. NEW and PAID count as "open" for the credit-limit invariant. */
public enum OrderStatus {
    NEW,
    PAID,
    SHIPPED,
    CANCELLED
}
