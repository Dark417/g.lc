package com.lc.x.x02_01_principles.spring;

import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * 3.1 IoC + 3.2 DI + 3.5 POJO — the container builds the graph; classes only declare what they need.
 * - Violation: field injection hides dependencies and leaves them null outside the container.
 * - Fix: constructor injection into a POJO with no Spring imports (wired in PrinciplesConfig).
 * - Catch: a 9-arg constructor is an SRP alarm; don't silence it by switching to fields.
 */
public final class IocDi {

    private IocDi() {
    }

    // ===== Violation: field injection =====

    public static final class Violation {

        private Violation() {
        }

        /** Hidden dependency, not final, null when built with new (unit tests NPE far from the cause). */
        public static class FieldInjected {
            @Autowired
            private Fix.OrderRepository repo;

            public String place(String orderId) {
                repo.save(orderId);
                return "placed " + orderId;
            }
        }
    }

    // ===== Fix: POJO + constructor injection =====

    public static final class Fix {

        private Fix() {
        }

        /** Port (no Spring types). */
        public interface OrderRepository {
            void save(String orderId);

            int count();
        }

        /** Port; implementations are chosen by auto-config style conditions (AutoConfig). */
        public interface Notifier {
            String notify(String orderId);
        }

        public static class InMemoryOrderRepository implements OrderRepository {
            private final Set<String> ids = ConcurrentHashMap.newKeySet();

            public void save(String orderId) {
                ids.add(orderId);
            }

            public int count() {
                return ids.size();
            }
        }

        /**
         * Non-invasive POJO: no Spring imports, final fields, testable with new.
         * Not final so Spring can CGLIB-proxy it for the TimingAspect (bean-name pointcut).
         */
        public static class OrderService {
            private final OrderRepository repo;
            private final Notifier notifier;

            public OrderService(OrderRepository repo, Notifier notifier) {
                this.repo = repo;
                this.notifier = notifier;
            }

            public String place(String orderId) {
                repo.save(orderId);
                return notifier.notify(orderId) + " stored=" + repo.count();
            }
        }

        /** Setter injection: only for optional deps with a sane default; object may be half-configured. */
        public static class SetterInjected {
            private Notifier notifier = id -> "default-notifier " + id;

            @Autowired(required = false)
            public void setNotifier(Notifier notifier) {
                this.notifier = notifier;
            }

            public String ping(String id) {
                return notifier.notify(id);
            }
        }
    }

    // Shows field injection failing outside the container vs a constructor-injected POJO built with new.
    // Use constructor injection for every required dependency.
    // Catch: cycles fail at startup with constructors (Boot >= 2.6 forbids cycles); fix the design, not with @Lazy.
    public static String demo() {
        String field;
        try {
            new Violation.FieldInjected().place("o-1");
            field = "worked";
        } catch (NullPointerException e) {
            field = "NullPointerException (repo was never injected)";
        }
        Fix.OrderService service = new Fix.OrderService(new Fix.InMemoryOrderRepository(), id -> "test-notified " + id);
        return "DI violation: new FieldInjected().place -> " + field
                + "\nDI fix:       new OrderService(fakeRepo, fakeNotifier).place -> " + service.place("o-1")
                + "\nsetter:       " + new Fix.SetterInjected().ping("o-2");
    }
}
