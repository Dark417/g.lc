package com.lc.x.x02_01_principles.general;

import com.lc.x.shared.Retry;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * 2.6 Composition over inheritance — assemble behavior from parts.
 * - Violation: EmailNotifier -> RetryingEmailNotifier -> LoggingRetryingEmailNotifier (2^n subclasses for n features).
 * - Fix: Retrying and Logging decorators around any Notifier; order is chosen at wiring time.
 * - Catch: decorator order is a contract (logging outside retry logs requests, inside logs attempts).
 */
public final class CompositionOverInheritance {

    private CompositionOverInheritance() {
    }

    // ===== Violation: feature combinations as a class tree =====

    public static final class Violation {

        private Violation() {
        }

        public static class EmailNotifier {
            protected int attempts;

            public String send(String to, String msg) {
                attempts++;
                return "email to " + to + ": " + msg;
            }
        }

        /** Retry is welded to email; SMS needs its own RetryingSmsNotifier. */
        public static class RetryingEmailNotifier extends EmailNotifier {
            @Override
            public String send(String to, String msg) {
                for (int i = 0; ; i++) {
                    try {
                        return super.send(to, msg);
                    } catch (RuntimeException e) {
                        if (i == 2) {
                            throw e;
                        }
                    }
                }
            }
        }

        /** Third level: depends on both parents' internals (fragile base class). */
        public static class LoggingRetryingEmailNotifier extends RetryingEmailNotifier {
            public final List<String> log = new ArrayList<>();

            @Override
            public String send(String to, String msg) {
                log.add("send " + to);
                return super.send(to, msg);
            }
        }
    }

    // ===== Fix: small parts composed at runtime =====

    public static final class Fix {

        private Fix() {
        }

        public interface Notifier {
            String send(String to, String msg);
        }

        /** Fails the first N calls to make retries visible. */
        public static final class FlakyEmail implements Notifier {
            private int failuresLeft;
            private int calls;

            public FlakyEmail(int failures) {
                this.failuresLeft = failures;
            }

            public String send(String to, String msg) {
                calls++;
                if (failuresLeft-- > 0) {
                    throw new IllegalStateException("smtp timeout");
                }
                return "email to " + to + ": " + msg;
            }

            public int calls() {
                return calls;
            }
        }

        /** Retry decorator reusing the shared full-jitter helper; only safe for idempotent sends. */
        public static final class Retrying implements Notifier {
            private final Notifier inner;
            private final Retry retry;

            public Retrying(Notifier inner, int maxAttempts) {
                this.inner = inner;
                this.retry = new Retry(maxAttempts, Duration.ofMillis(1), Duration.ofMillis(5));
            }

            public String send(String to, String msg) {
                return retry.call(() -> inner.send(to, msg), e -> e instanceof IllegalStateException);
            }
        }

        public static final class Logging implements Notifier {
            private final Notifier inner;
            private final List<String> log;

            public Logging(Notifier inner, List<String> log) {
                this.inner = inner;
                this.log = log;
            }

            public String send(String to, String msg) {
                log.add("send " + to);
                return inner.send(to, msg);
            }
        }
    }

    // Shows the same parts composed in two orders: log lines = requests vs attempts.
    // Use when features combine freely (retry, logging, metrics, rate limit).
    // Catch: inheritance is still right for bases designed for extension (framework abstract classes).
    public static String demo() {
        Violation.LoggingRetryingEmailNotifier tree = new Violation.LoggingRetryingEmailNotifier();
        String bad = tree.send("a@example.com", "hi");

        List<String> outer = new ArrayList<>();
        Fix.FlakyEmail email1 = new Fix.FlakyEmail(2);
        String r1 = new Fix.Logging(new Fix.Retrying(email1, 3), outer).send("a@example.com", "hi");

        List<String> inner = new ArrayList<>();
        Fix.FlakyEmail email2 = new Fix.FlakyEmail(2);
        new Fix.Retrying(new Fix.Logging(email2, inner), 3).send("a@example.com", "hi");

        return "Composition violation: " + bad + " (class per combination)"
                + "\nComposition fix:       " + r1
                + "\n  Logging(Retrying(email)) log lines=" + outer.size() + " (requests), email calls=" + email1.calls()
                + "\n  Retrying(Logging(email)) log lines=" + inner.size() + " (attempts)";
    }
}
