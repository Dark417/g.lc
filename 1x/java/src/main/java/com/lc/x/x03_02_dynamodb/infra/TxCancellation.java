package com.lc.x.x03_02_dynamodb.infra;

import java.util.List;
import java.util.Map;
import java.util.Set;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;

/**
 * Parsed TransactionCanceledException: one reason per action, in the SAME order as TransactItems.
 * - Code "None" = this action was fine; another action cancelled the transaction.
 * - item = old item, only when that action set ReturnValuesOnConditionCheckFailure=ALL_OLD.
 */
public record TxCancellation(List<Reason> reasons) {

    /** Codes that mean "try again later", not "your condition is false". */
    private static final Set<String> TRANSIENT =
            Set.of("None", "TransactionConflict", "ThrottlingError", "ProvisionedThroughputExceeded");

    public record Reason(int index, String label, String code, String message, Map<String, AttributeValue> item) {
    }

    public boolean failedWith(String label, String code) {
        return reasons.stream().anyMatch(r -> r.label().equals(label) && code.equals(r.code()));
    }

    public Map<String, AttributeValue> itemOf(String label) {
        return reasons.stream().filter(r -> r.label().equals(label)).findFirst().map(Reason::item).orElse(Map.of());
    }

    /** Retry only when every failing action failed for a transient reason (conflict, throttling). */
    public boolean retryable() {
        return reasons.stream().allMatch(r -> TRANSIENT.contains(r.code()))
                && reasons.stream().anyMatch(r -> !"None".equals(r.code()));
    }
}
