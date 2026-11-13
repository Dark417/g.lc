package com.lc.x.x02_01_principles.spring;

import java.util.Arrays;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

/**
 * 3.6 Externalized configuration — @Value (violation for grouped config) vs @ConfigurationProperties (fix).
 * - Violation: string keys scattered, no validation; a typo in the key silently uses the default.
 * - Fix: PrinciplesProperties record, validated at startup (fail fast).
 * - Catch: profiles are for environment wiring only, never `if (prod)` branches in business code.
 */
public final class ExternalConfig {

    private ExternalConfig() {
    }

    // ===== Violation: @Value strings =====

    public static final class Violation {

        private Violation() {
        }

        /**
         * Note the deliberate typo "max-attemps": no error, the default 3 is used forever.
         * Also no range check: X_PRINCIPLES_MAX_ATTEMPTS=0 would be accepted.
         */
        @Component
        @ConditionalOnProperty(name = "x.principles.enabled", havingValue = "true")
        public static class ValueSettings {
            private final int maxAttempts;
            private final String taxRate;

            public ValueSettings(@Value("${x.principles.max-attemps:3}") int maxAttempts,
                                 @Value("${x.principles.tax-rate:0.08}") String taxRate) {
                this.maxAttempts = maxAttempts;
                this.taxRate = taxRate;
            }

            public int maxAttempts() {
                return maxAttempts;
            }

            public String taxRate() {
                return taxRate;
            }
        }
    }

    // Shows both binding styles side by side plus active profiles.
    // Use @ConfigurationProperties for any group of related keys.
    // Catch: secrets never go in application.yml; inject them at runtime.
    public static String describe(PrinciplesProperties props, Violation.ValueSettings values, Environment env) {
        return "@Value:                   maxAttempts=" + values.maxAttempts() + " taxRate(String)=" + values.taxRate()
                + "\n@ConfigurationProperties: " + props
                + "\nactive profiles:          " + Arrays.toString(env.getActiveProfiles());
    }
}
