package com.lc.a.domain._01bedrock_01converse;

import java.util.Map;

/** One toolUse block requested by the model; input is already plain Java (maps, lists, strings, numbers). */
public record ToolCall(String toolUseId, String name, Map<String, Object> input) {
}
