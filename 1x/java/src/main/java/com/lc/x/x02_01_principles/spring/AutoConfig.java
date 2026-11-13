package com.lc.x.x02_01_principles.spring;

import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 3.4 Convention over configuration — beans that appear by condition and back off when you define your own.
 * - SMS notifier when x.principles.notifier=sms; otherwise a default log notifier.
 * - Real auto-config is listed in META-INF/spring/...AutoConfiguration.imports and processed after user config.
 * - Catch: @ConditionalOnMissingBean in ordinary @Configuration depends on parse order; here both beans
 *   sit in one class, so declaration order (sms first) keeps it deterministic.
 */
public final class AutoConfig {

    private AutoConfig() {
    }

    public static final class LogNotifier implements IocDi.Fix.Notifier {
        public String notify(String orderId) {
            return "log-notified " + orderId;
        }
    }

    public static final class SmsNotifier implements IocDi.Fix.Notifier {
        public String notify(String orderId) {
            return "sms-notified " + orderId;
        }
    }

    // Auto-config style: guarded by the slice flag, conditions decide which Notifier exists.
    // Use for library/starter code that must offer defaults yet yield to the application.
    // Catch: debug with --debug (condition report) or /actuator/conditions.
    @Configuration(proxyBeanMethods = false)
    @ConditionalOnProperty(name = "x.principles.enabled", havingValue = "true")
    public static class NotifierAutoConfiguration {

        @Bean
        @ConditionalOnProperty(name = "x.principles.notifier", havingValue = "sms")
        public IocDi.Fix.Notifier principlesSmsNotifier() {
            return new SmsNotifier();
        }

        @Bean
        @ConditionalOnMissingBean(IocDi.Fix.Notifier.class)
        public IocDi.Fix.Notifier principlesLogNotifier() {
            return new LogNotifier();
        }
    }
}
