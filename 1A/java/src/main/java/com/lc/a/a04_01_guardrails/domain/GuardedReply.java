package com.lc.a.a04_01_guardrails.domain;

/** Final answer of a guarded turn; stopReason "guardrail_intervened" means text is a blocked message. */
public record GuardedReply(String text, String stopReason, GuardrailVerdict input, GuardrailVerdict output) {

    public boolean intervened() {
        return "guardrail_intervened".equals(stopReason);
    }
}
