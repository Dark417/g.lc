package com.lc.x.domain._03db_01aurora;

/** No order with this id (HTTP 404). */
public class OrderNotFoundException extends RuntimeException {

    public OrderNotFoundException(long id) {
        super("order " + id + " not found");
    }
}
