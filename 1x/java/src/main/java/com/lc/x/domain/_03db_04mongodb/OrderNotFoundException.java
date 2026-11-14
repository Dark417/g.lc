package com.lc.x.domain._03db_04mongodb;

public class OrderNotFoundException extends RuntimeException {

    public OrderNotFoundException(String orderId) {
        super("order " + orderId + " not found");
    }
}
