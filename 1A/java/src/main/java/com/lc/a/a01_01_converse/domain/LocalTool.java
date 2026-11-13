package com.lc.a.a01_01_converse.domain;

import java.util.Map;
import java.util.function.Function;

/**
 * A tool the model may call. Bedrock never runs it: our process does, after validating the input.
 * - inputSchema: JSON Schema as plain maps (no SDK types in the domain).
 * - handler: input -> result JSON; throw IllegalArgumentException for bad input (sent back as status=error).
 */
public record LocalTool(
        String name,
        String description,
        Map<String, Object> inputSchema,
        Function<Map<String, Object>, Map<String, Object>> handler) {
}
