package com.lc.a.a01_01_converse.domain;

import java.util.List;

/**
 * Parsed Converse response.
 * - stopReason: end_turn | tool_use | max_tokens | stop_sequence | guardrail_intervened | content_filtered | ...
 * - latencyMs = metrics.latencyMs (server-side); rounds = model calls made by the tool loop.
 */
public record ConverseResult(
        String text, String stopReason, TokenUsage usage, long latencyMs, List<ToolCall> toolCalls, int rounds) {
}
