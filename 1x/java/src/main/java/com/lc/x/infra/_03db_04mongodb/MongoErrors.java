package com.lc.x.infra._03db_04mongodb;

import com.mongodb.ErrorCategory;
import com.mongodb.MongoBulkWriteException;
import com.mongodb.MongoException;
import com.mongodb.MongoExecutionTimeoutException;
import com.mongodb.MongoNotPrimaryException;
import com.mongodb.MongoSocketException;
import com.mongodb.MongoTimeoutException;
import com.mongodb.MongoWriteConcernException;
import com.mongodb.MongoWriteException;

/**
 * Error classification: the decision is "retry, re-check, or give up", not "which exception class".
 * - Error LABELS beat codes for transactions: TransientTransactionError = rerun the whole transaction,
 *   UnknownTransactionCommitResult = retry only the commit.
 * - writeConcernError is NOT a failure: the write may be applied and may still replicate (ambiguous).
 * - Server codes: 11000 duplicate key, 121 validation, 50 maxTimeMS, 112 write conflict, 286 change-stream history lost.
 */
public final class MongoErrors {

    public static final int DUPLICATE_KEY = 11000;
    public static final int DOCUMENT_VALIDATION_FAILURE = 121;
    public static final int MAX_TIME_MS_EXPIRED = 50;
    public static final int CHANGE_STREAM_HISTORY_LOST = 286;
    public static final int NAMESPACE_EXISTS = 48;

    /** What the caller should do next. */
    public enum Kind {
        DUPLICATE_KEY,             // terminal for this write; fine if the intent was "create once"
        VALIDATION_FAILED,         // terminal: the document is wrong, the same bytes fail again
        TRANSIENT_TRANSACTION,     // rerun the WHOLE transaction (fresh snapshot)
        UNKNOWN_COMMIT_RESULT,     // retry commitTransaction only (idempotent per txnNumber)
        WRITE_CONCERN_AMBIGUOUS,   // applied locally, majority unknown: re-check state, never blind-retry
        TIMEOUT,                   // maxTimeMS hit: the same query takes the same time; degrade, don't retry
        NO_SERVER,                 // server selection timed out (no primary / network partition)
        NETWORK,                   // socket error; the driver already retried once if retryable
        HISTORY_LOST,              // change-stream resume token fell off the oplog: reconcile, then restart
        TERMINAL
    }

    private MongoErrors() {
    }

    public static Kind classify(Throwable t) {
        if (t instanceof MongoException me) {
            // Labels first: a WriteConflict (112) inside a transaction carries TransientTransactionError.
            if (me.hasErrorLabel(MongoException.TRANSIENT_TRANSACTION_ERROR_LABEL)) {
                return Kind.TRANSIENT_TRANSACTION;
            }
            if (me.hasErrorLabel(MongoException.UNKNOWN_TRANSACTION_COMMIT_RESULT_LABEL)) {
                return Kind.UNKNOWN_COMMIT_RESULT;
            }
        }
        if (t instanceof MongoWriteConcernException) {
            return Kind.WRITE_CONCERN_AMBIGUOUS;
        }
        if (t instanceof MongoWriteException we) {
            if (we.getError().getCategory() == ErrorCategory.DUPLICATE_KEY) {
                return Kind.DUPLICATE_KEY;
            }
            return we.getError().getCode() == DOCUMENT_VALIDATION_FAILURE ? Kind.VALIDATION_FAILED : Kind.TERMINAL;
        }
        if (t instanceof MongoBulkWriteException) {
            return Kind.TERMINAL; // inspect getWriteErrors() per op; successful ops are not rolled back
        }
        if (t instanceof MongoExecutionTimeoutException) {
            return Kind.TIMEOUT;
        }
        if (t instanceof MongoTimeoutException) {
            return Kind.NO_SERVER;
        }
        if (t instanceof MongoSocketException || t instanceof MongoNotPrimaryException) {
            return Kind.NETWORK;
        }
        if (t instanceof MongoException me && me.getCode() == CHANGE_STREAM_HISTORY_LOST) {
            return Kind.HISTORY_LOST;
        }
        return Kind.TERMINAL;
    }

    public static boolean isDuplicateKey(Throwable t) {
        return classify(t) == Kind.DUPLICATE_KEY;
    }
}
