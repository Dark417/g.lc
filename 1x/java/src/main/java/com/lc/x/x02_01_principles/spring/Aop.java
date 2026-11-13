package com.lc.x.x02_01_principles.spring;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import org.aopalliance.intercept.MethodInterceptor;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.aop.framework.ProxyFactory;
import org.springframework.aop.support.AopUtils;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.core.annotation.Order;

/**
 * 3.3 AOP — cross-cutting code applied by proxies around Spring beans.
 * - TimingAspect: times the POJO OrderService by bean name; the POJO has no annotation (non-invasive).
 * - TxAspect + @DemoTransactional: mimics @Transactional so the self-invocation trap is observable without a DB.
 * - Catch: calls through `this` skip the proxy; final/private methods are never advised.
 */
public final class Aop {

    private Aop() {
    }

    // ===== Building blocks: a @Transactional look-alike =====

    /** Stand-in for @Transactional: same proxy mechanics, no DataSource needed. */
    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface DemoTransactional {
    }

    /** Thread-bound "transaction", like TransactionSynchronizationManager. */
    public static final class TxContext {
        private static final ThreadLocal<String> CURRENT = new ThreadLocal<>();

        private TxContext() {
        }

        public static boolean active() {
            return CURRENT.get() != null;
        }

        static void begin(String name) {
            CURRENT.set(name);
        }

        static void end() {
            CURRENT.remove();
        }
    }

    // ===== Aspects =====

    /** Outer aspect (lower @Order = runs first): timing wraps the transaction, so it measures the whole call. */
    @Aspect
    @Order(0)
    public static class TimingAspect {
        private final Map<String, Long> lastMicros = new ConcurrentHashMap<>();
        private final AtomicLong calls = new AtomicLong();

        @Around("bean(principlesOrderService)")
        public Object time(ProceedingJoinPoint pjp) throws Throwable {
            long start = System.nanoTime();
            try {
                return pjp.proceed();
            } finally {
                calls.incrementAndGet();
                lastMicros.put(pjp.getSignature().toShortString(), (System.nanoTime() - start) / 1_000);
            }
        }

        public String report() {
            return "timed calls=" + calls.get() + " last(us)=" + lastMicros;
        }
    }

    /** Joins an existing "transaction" (like REQUIRED) or opens one around the annotated method. */
    @Aspect
    @Order(1)
    public static class TxAspect {
        @Around("@annotation(tx)")
        public Object inTransaction(ProceedingJoinPoint pjp, DemoTransactional tx) throws Throwable {
            if (TxContext.active()) {
                return pjp.proceed();
            }
            TxContext.begin(pjp.getSignature().toShortString());
            try {
                return pjp.proceed();
            } finally {
                TxContext.end();
            }
        }
    }

    // ===== Violation: self-invocation bypasses the proxy =====

    public static final class Violation {

        private Violation() {
        }

        /** checkout() calls this.writeLedger(): the call never reaches the proxy, so no transaction. */
        public static class Checkout {
            public String checkout(String orderId) {
                return "checkout -> " + writeLedger(orderId);
            }

            @DemoTransactional
            public String writeLedger(String orderId) {
                return "ledger(" + orderId + ") inTx=" + TxContext.active();
            }
        }
    }

    // ===== Fixes: call through a proxy =====

    public static final class Fix {

        private Fix() {
        }

        /** Fix 1: inject yourself lazily; getObject() returns the proxy, so advice applies. */
        public static class SelfInjectedCheckout {
            private final ObjectProvider<SelfInjectedCheckout> self;

            public SelfInjectedCheckout(ObjectProvider<SelfInjectedCheckout> self) {
                this.self = self;
            }

            public String checkout(String orderId) {
                return "checkout -> " + self.getObject().writeLedger(orderId);
            }

            @DemoTransactional
            public String writeLedger(String orderId) {
                return "ledger(" + orderId + ") inTx=" + TxContext.active();
            }
        }

        /** Fix 2 (preferred): the advised method lives in another bean. */
        public static class LedgerWriter {
            @DemoTransactional
            public String write(String orderId) {
                return "ledger(" + orderId + ") inTx=" + TxContext.active();
            }
        }

        public static class SplitCheckout {
            private final LedgerWriter ledger;

            public SplitCheckout(LedgerWriter ledger) {
                this.ledger = ledger;
            }

            public String checkout(String orderId) {
                return "checkout -> " + ledger.write(orderId);
            }
        }
    }

    // ===== JDK dynamic proxy vs CGLIB, without a container =====

    public interface Greeter {
        String greet();
    }

    public static class PlainGreeter implements Greeter {
        private final String name;

        public PlainGreeter(String name) {
            this.name = name;
        }

        public String greet() {
            return "hello " + name;
        }

        /** final: CGLIB cannot override it, so it runs on the proxy instance whose fields were never set. */
        public final String finalGreet() {
            return "final hello " + name;
        }
    }

    // Shows JDK proxy (interface only, cast to class fails) vs CGLIB (subclass; final methods unadvised, fields null).
    // Use to explain why Spring Boot defaults to CGLIB and why advised methods must be non-final.
    // Catch: CGLIB proxies are built via Objenesis without running the constructor.
    public static String proxyKinds() {
        MethodInterceptor advice = inv -> "[advised] " + inv.proceed();

        ProxyFactory jdkFactory = new ProxyFactory(new PlainGreeter("ada"));
        jdkFactory.addInterface(Greeter.class);
        jdkFactory.setProxyTargetClass(false);
        jdkFactory.addAdvice(advice);
        Object jdk = jdkFactory.getProxy();

        ProxyFactory cglibFactory = new ProxyFactory(new PlainGreeter("ada"));
        cglibFactory.setProxyTargetClass(true);
        cglibFactory.addAdvice(advice);
        PlainGreeter cglib = (PlainGreeter) cglibFactory.getProxy();

        return "JDK proxy:   isJdk=" + AopUtils.isJdkDynamicProxy(jdk) + " instanceof PlainGreeter="
                + (jdk instanceof PlainGreeter) + " greet=" + ((Greeter) jdk).greet()
                + "\nCGLIB proxy: isCglib=" + AopUtils.isCglibProxy(cglib) + " greet=" + cglib.greet()
                + " finalGreet=" + cglib.finalGreet();
    }
}
