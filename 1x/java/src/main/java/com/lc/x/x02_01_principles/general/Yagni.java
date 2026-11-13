package com.lc.x.x02_01_principles.general;

import java.math.BigDecimal;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 2.3 YAGNI — don't build what no requirement needs yet.
 * - Violation: a reflective plugin loader for a single payment provider.
 * - Fix: one concrete gateway; extract an interface when provider two exists.
 * - Catch: retrofit-expensive properties (idempotency keys) are NOT covered by YAGNI — keep them now.
 */
public final class Yagni {

    private Yagni() {
    }

    // ===== Violation: speculative generality =====

    public static final class Violation {

        private Violation() {
        }

        public interface PaymentProviderPlugin {
            String charge(BigDecimal amount);
        }

        public static final class OnlyProvider implements PaymentProviderPlugin {
            public String charge(BigDecimal amount) {
                return "charged " + amount;
            }
        }

        /** Config-driven class loading: typos fail at runtime, IDE can't follow it, one plugin exists. */
        public static final class PluginLoader {
            public PaymentProviderPlugin load(String className) {
                try {
                    return (PaymentProviderPlugin) Class.forName(className).getDeclaredConstructor().newInstance();
                } catch (ReflectiveOperationException e) {
                    throw new IllegalStateException("cannot load plugin " + className, e);
                }
            }
        }
    }

    // ===== Fix: concrete now, but with the retrofit-expensive part (idempotency) built in =====

    public static final class Fix {

        private Fix() {
        }

        /** Concrete class; the idempotency key is kept because adding it later changes the public API. */
        public static final class CardGateway {
            private final Map<String, String> processed = new ConcurrentHashMap<>();

            public String charge(String idempotencyKey, BigDecimal amount) {
                return processed.computeIfAbsent(idempotencyKey, k -> "charge-" + k + "-" + amount);
            }

            public int charges() {
                return processed.size();
            }
        }
    }

    // Shows reflection indirection vs a concrete class; a retry with the same key charges once.
    // Use YAGNI for features and extension points.
    // Catch: do not use it to skip security, idempotency, schema versioning or observability.
    public static String demo() {
        Violation.PaymentProviderPlugin plugin =
                new Violation.PluginLoader().load(Violation.OnlyProvider.class.getName());
        Fix.CardGateway gateway = new Fix.CardGateway();
        String first = gateway.charge("req-1", BigDecimal.TEN);
        String retry = gateway.charge("req-1", BigDecimal.TEN);
        return "YAGNI violation: " + plugin.charge(BigDecimal.TEN) + " via reflection"
                + "\nYAGNI fix:       " + first + " retrySame=" + first.equals(retry) + " charges=" + gateway.charges();
    }
}
