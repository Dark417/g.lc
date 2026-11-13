package com.lc.a.a01_01_converse.domain;

import java.util.Map;

/** One toolUse block requested by the model; input is already plain Java (maps, lists, strings, numbers). */
public record ToolCall(String toolUseId, String name, Map<String, Object> input) {
}
