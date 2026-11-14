package com.lc.a.domain._04safety_01guardrails;

/**
 * One finding from one guardrail policy.
 * - policy: topic | content | word | managed_word | pii | regex | automated_reasoning
 * - action: BLOCKED | ANONYMIZED | NONE; detected is true also in detect mode (action NONE)
 * - The matched sensitive text is deliberately NOT kept here, so it can't end up in logs or responses.
 */
public record PolicyHit(String policy, String name, String action, boolean detected, String confidence) {
}
