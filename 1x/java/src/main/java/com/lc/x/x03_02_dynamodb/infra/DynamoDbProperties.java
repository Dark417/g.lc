package com.lc.x.x03_02_dynamodb.infra;

/** Table and index names from application.yml (x.dynamodb.*); they match terraform/03.02.dynamodb.tf. */
public record DynamoDbProperties(String ordersTable, String idempotencyTable, String gsi1Name) {
}
