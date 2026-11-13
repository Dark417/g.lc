package com.lc.x.x02_01_principles.spring;

import org.springframework.beans.factory.ObjectProvider;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;

/**
 * 3.1 IoC — the composition root: the only place that knows how the slice's objects are wired.
 * - Every bean here exists only when x.principles.enabled=true, so the base app is unaffected.
 * - POJOs are built with constructors in @Bean methods; none of them imports Spring.
 * - Catch: business code must never call ApplicationContext.getBean (service locator).
 */
@Configuration(proxyBeanMethods = false)
@ConditionalOnProperty(name = "x.principles.enabled", havingValue = "true")
@EnableConfigurationProperties(PrinciplesProperties.class)
public class PrinciplesConfig {

    // ===== 3.1 / 3.2 / 3.5: POJO wiring with constructor injection =====

    @Bean
    public IocDi.Fix.OrderRepository principlesOrderRepository() {
        return new IocDi.Fix.InMemoryOrderRepository();
    }

    // Notifier comes from AutoConfig.NotifierAutoConfiguration (log or sms, by condition).
    @Bean
    public IocDi.Fix.OrderService principlesOrderService(IocDi.Fix.OrderRepository repo, IocDi.Fix.Notifier notifier) {
        return new IocDi.Fix.OrderService(repo, notifier);
    }

    // ===== 3.3: aspects and the self-invocation trap =====

    @Bean
    public Aop.TimingAspect principlesTimingAspect() {
        return new Aop.TimingAspect();
    }

    @Bean
    public Aop.TxAspect principlesTxAspect() {
        return new Aop.TxAspect();
    }

    @Bean
    public Aop.Violation.Checkout principlesCheckout() {
        return new Aop.Violation.Checkout();
    }

    @Bean
    public Aop.Fix.SelfInjectedCheckout principlesSelfInjectedCheckout(ObjectProvider<Aop.Fix.SelfInjectedCheckout> self) {
        return new Aop.Fix.SelfInjectedCheckout(self);
    }

    @Bean
    public Aop.Fix.LedgerWriter principlesLedgerWriter() {
        return new Aop.Fix.LedgerWriter();
    }

    @Bean
    public Aop.Fix.SplitCheckout principlesSplitCheckout(Aop.Fix.LedgerWriter ledger) {
        return new Aop.Fix.SplitCheckout(ledger);
    }

    // ===== Demo facade used by the controller =====

    @Bean
    public SpringPrinciplesDemo principlesSpringDemo(
            IocDi.Fix.OrderService orderService,
            IocDi.Fix.Notifier notifier,
            Aop.TimingAspect timing,
            Aop.Violation.Checkout checkout,
            Aop.Fix.SelfInjectedCheckout selfInjected,
            Aop.Fix.SplitCheckout split,
            PrinciplesProperties props,
            ExternalConfig.Violation.ValueSettings valueSettings,
            Environment env) {
        return new SpringPrinciplesDemo(orderService, notifier, timing, checkout, selfInjected, split, props,
                valueSettings, env);
    }
}
