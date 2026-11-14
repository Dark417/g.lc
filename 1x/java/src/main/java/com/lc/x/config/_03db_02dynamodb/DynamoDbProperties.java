package com.lc.x.config._03db_02dynamodb;

/** Table and index names from application.yml (x.dynamodb.*); they match terraform/modules/03db_02dynamodb/. */
public record DynamoDbProperties(String ordersTable, String idempotencyTable, String gsi1Name) {
}
