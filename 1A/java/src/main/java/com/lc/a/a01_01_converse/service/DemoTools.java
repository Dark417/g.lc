package com.lc.a.a01_01_converse.service;

import com.lc.a.a01_01_converse.domain.LocalTool;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/** Two local tools with JSON-schema specs; handlers validate input and throw IllegalArgumentException. */
public final class DemoTools {

    private DemoTools() {
    }

    public static List<LocalTool> all() {
        return List.of(weather(), addNumbers());
    }

    static LocalTool weather() {
        return new LocalTool(
                "get_weather",
                "Current temperature for a city. Use only when the user asks about weather.",
                Map.of("type", "object",
                        "properties", Map.of(
                                "city", Map.of("type", "string", "description", "City name, e.g. Seattle"),
                                "unit", Map.of("type", "string", "enum", List.of("celsius", "fahrenheit"))),
                        "required", List.of("city")),
                input -> {
                    Object city = input.get("city");
                    if (!(city instanceof String c) || c.isBlank()) {
                        throw new IllegalArgumentException("city must be a non-empty string");
                    }
                    int tempC = 18 + Math.floorMod(c.toLowerCase().hashCode(), 10); // fake, deterministic
                    return Map.of("city", c, "temperature", tempC, "unit", "celsius");
                });
    }

    static LocalTool addNumbers() {
        return new LocalTool(
                "add_numbers",
                "Exact sum of a list of numbers. Use instead of mental arithmetic.",
                Map.of("type", "object",
                        "properties", Map.of("values", Map.of("type", "array", "items", Map.of("type", "number"))),
                        "required", List.of("values")),
                input -> {
                    if (!(input.get("values") instanceof List<?> values)) {
                        throw new IllegalArgumentException("values must be a list of numbers");
                    }
                    BigDecimal sum = BigDecimal.ZERO;
                    for (Object v : values) {
                        if (!(v instanceof BigDecimal n)) {
                            throw new IllegalArgumentException("values must be numbers, got " + v);
                        }
                        sum = sum.add(n);
                    }
                    return Map.of("sum", sum);
                });
    }
}
