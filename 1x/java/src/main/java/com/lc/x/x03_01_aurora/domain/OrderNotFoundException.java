package com.lc.x.x03_01_aurora.domain;

/** No order with this id (HTTP 404). */
public class OrderNotFoundException extends RuntimeException {

    public OrderNotFoundException(long id) {
        super("order " + id + " not found");
    }
}
