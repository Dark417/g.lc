package com.lc.x.x02_01_principles.spring;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Supplier;
import org.springframework.aop.support.AopUtils;
import org.springframework.core.env.Environment;

/**
 * Part C runnable entry points: each method exercises real container behavior (proxies, conditions, binding).
 * - Built by PrinciplesConfig, so it exists only when the slice is enabled.
 * - Each method returns a human-readable trace for GET /principles/{name}.
 * - Catch: output reflects the running context (profiles, x.principles.notifier), so it varies by environment.
 */
public class SpringPrinciplesDemo {

    private final IocDi.Fix.OrderService orderService;
    private final IocDi.Fix.Notifier notifier;
    private final Aop.TimingAspect timing;
    private final Aop.Violation.Checkout checkout;
    private final Aop.Fix.SelfInjectedCheckout selfInjected;
    private final Aop.Fix.SplitCheckout split;
    private final PrinciplesProperties props;
    private final ExternalConfig.Violation.ValueSettings valueSettings;
    private final Environment env;

    public SpringPrinciplesDemo(IocDi.Fix.OrderService orderService, IocDi.Fix.Notifier notifier,
                                Aop.TimingAspect timing, Aop.Violation.Checkout checkout,
                                Aop.Fix.SelfInjectedCheckout selfInjected, Aop.Fix.SplitCheckout split,
                                PrinciplesProperties props, ExternalConfig.Violation.ValueSettings valueSettings,
                                Environment env) {
        this.orderService = orderService;
        this.notifier = notifier;
        this.timing = timing;
        this.checkout = checkout;
        this.selfInjected = selfInjected;
        this.split = split;
        this.props = props;
        this.valueSettings = valueSettings;
        this.env = env;
    }

    // ===== 3.1 IoC =====

    // Shows the container-built graph: OrderService arrived wired, and wrapped in a proxy by a post-processor.
    // Use to explain "the framework calls you".
    // Catch: the bean you hold is a proxy subclass, not your class (see getClass()).
    public String ioc() {
        return "OrderService bean class=" + orderService.getClass().getSimpleName()
                + " aopProxy=" + AopUtils.isAopProxy(orderService)
                + "\nplace -> " + orderService.place("o-ioc");
    }

    // ===== 3.2 DI =====

    // Shows field vs constructor injection outside the container (IocDi.demo).
    // Use constructor injection for required deps.
    // Catch: setter injection allows half-configured objects.
    public String di() {
        return IocDi.demo();
    }

    // ===== 3.3 AOP =====

    // Shows the self-invocation trap (inTx=false) and both fixes (inTx=true), plus timing on a POJO.
    // Use to explain why @Transactional/@Async/@Cacheable "do nothing" on internal calls.
    // Catch: calling writeLedger directly on the proxy works; only this.writeLedger() is skipped.
    public String aop() {
        orderService.place("o-aop");
        return "self-invocation:   " + checkout.checkout("o-1")
                + "\ndirect via proxy:  " + checkout.writeLedger("o-1")
                + "\nfix ObjectProvider: " + selfInjected.checkout("o-1")
                + "\nfix split bean:    " + split.checkout("o-1")
                + "\n" + timing.report()
                + "\n" + Aop.proxyKinds();
    }

    // ===== 3.4 Auto-config =====

    // Shows which Notifier the conditions produced (x.principles.notifier=sms -> SmsNotifier, else LogNotifier).
    // Use to explain back-off: define your own Notifier bean and the default disappears.
    // Catch: run with --debug to see the condition evaluation report.
    public String autoconfig() {
        return "x.principles.notifier=" + env.getProperty("x.principles.notifier", "(unset)")
                + " -> Notifier bean=" + notifier.getClass().getSimpleName();
    }

    // ===== 3.5 POJO =====

    // Shows the same POJO class used with and without Spring.
    // Use to argue domain code survives framework changes.
    // Catch: proxies need non-final classes; records can't be advised.
    public String pojo() {
        IocDi.Fix.OrderService plain = new IocDi.Fix.OrderService(new IocDi.Fix.InMemoryOrderRepository(), id -> "plain " + id);
        return "without Spring: " + plain.place("o-plain")
                + "\nwith Spring:    " + orderService.place("o-spring");
    }

    // ===== 3.6 External config =====

    // Shows typed validated properties vs @Value strings, and active profiles.
    // Use @ConfigurationProperties + @Validated for grouped keys.
    // Catch: the @Value typo key silently uses its default.
    public String config() {
        return ExternalConfig.describe(props, valueSettings, env);
    }

    // ===== 3.7 Templates =====

    // Shows the mini template retrying a transient failure, attempts from typed config.
    // Use template + callback for any fixed resource lifecycle.
    // Catch: retries are only safe for idempotent callbacks.
    public String template() {
        return TemplateMethod.demo(props.maxAttempts());
    }

    public Map<String, Supplier<String>> demos() {
        Map<String, Supplier<String>> m = new LinkedHashMap<>();
        m.put("ioc", this::ioc);
        m.put("di", this::di);
        m.put("aop", this::aop);
        m.put("autoconfig", this::autoconfig);
        m.put("pojo", this::pojo);
        m.put("config", this::config);
        m.put("template", this::template);
        return m;
    }
}
