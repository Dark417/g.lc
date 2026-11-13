package com.lc.x.x02_01_principles.spring;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import java.math.BigDecimal;
import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

/**
 * 3.6 Externalized configuration — typed, grouped, immutable, validated at startup.
 * - Bound from x.principles.* (yml, env X_PRINCIPLES_MAX_ATTEMPTS, command line), relaxed binding.
 * - Registered by @EnableConfigurationProperties in PrinciplesConfig, so only when the slice is on.
 * - Catch: unknown yml keys are ignored by default; a misspelled key silently keeps the default.
 */
@Validated
@ConfigurationProperties(prefix = "x.principles")
public record PrinciplesProperties(
        boolean enabled,
        @DefaultValue("log") @NotNull @Pattern(regexp = "log|sms") String notifier,
        @DefaultValue("3") @Min(1) @Max(10) int maxAttempts,
        @DefaultValue("2s") @NotNull Duration timeout,
        @DefaultValue("0.08") @NotNull @DecimalMin("0") @DecimalMax("0.5") BigDecimal taxRate) {
}
