package com.lc.a.a04_01_guardrails.domain;

import java.util.List;

/**
 * Parsed ApplyGuardrail result.
 * - intervened: action == GUARDRAIL_INTERVENED (block OR anonymize)
 * - blocked: at least one BLOCKED hit, so outputText is the canned blocked message
 * - outputText: masked text, blocked message, or the original text when nothing intervened
 */
public record GuardrailVerdict(
        boolean intervened,
        boolean blocked,
        String outputText,
        List<PolicyHit> hits,
        List<GroundingScore> grounding,
        int guardedChars,
        int totalChars) {

    public GuardrailVerdict {
        hits = List.copyOf(hits);
        grounding = List.copyOf(grounding);
    }
}
