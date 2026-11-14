package com.lc.x.domain._03db_02dynamodb;

/**
 * Outcome of the "order + idempotency record" transaction.
 * - KEY_ALREADY_USED carries the stored record (from ReturnValuesOnConditionCheckFailure=ALL_OLD).
 */
public record PlaceAttempt(Status status, IdempotencyRecord existing) {

    public enum Status {
        COMMITTED,
        KEY_ALREADY_USED,
        ORDER_ALREADY_EXISTS
    }

    public static PlaceAttempt committed() {
        return new PlaceAttempt(Status.COMMITTED, null);
    }

    public static PlaceAttempt keyAlreadyUsed(IdempotencyRecord existing) {
        return new PlaceAttempt(Status.KEY_ALREADY_USED, existing);
    }

    public static PlaceAttempt orderAlreadyExists() {
        return new PlaceAttempt(Status.ORDER_ALREADY_EXISTS, null);
    }
}
