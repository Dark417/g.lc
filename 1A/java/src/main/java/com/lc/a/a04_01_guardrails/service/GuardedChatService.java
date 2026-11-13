package com.lc.a.a04_01_guardrails.service;

import com.lc.a.a04_01_guardrails.domain.GuardedReply;
import com.lc.a.a04_01_guardrails.domain.GuardrailVerdict;
import com.lc.a.a04_01_guardrails.infra.GuardrailClient;
import java.util.List;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailContentSource;

/**
 * The backend request path: guard input, call the model, guard output (with grounding when context exists).
 * - Input blocked: return the blocked message, no model call, no model tokens billed.
 * - Input anonymized: the MASKED text is what the model sees and what gets logged.
 * - Output: content / topics / words / PII always; contextual grounding against the passages when given.
 * - Alternative in one call: GuardrailClient.converseGuarded (Bedrock models only).
 */
@Service
@ConditionalOnProperty(name = "a.guardrails.enabled", havingValue = "true")
public class GuardedChatService {

    private static final String SYSTEM = "You are a support assistant for a bank. Answer briefly from the context.";

    private final GuardrailClient guardrails;

    public GuardedChatService(GuardrailClient guardrails) {
        this.guardrails = guardrails;
    }

    public GuardedReply chat(String userText, List<String> passages) {
        GuardrailVerdict in = guardrails.apply(userText, GuardrailContentSource.INPUT);
        if (in.blocked()) {
            return new GuardedReply(in.outputText(), "guardrail_intervened", in, null);
        }
        String safeInput = in.outputText();

        String prompt = passages.isEmpty()
                ? safeInput
                : "Context:\n" + String.join("\n---\n", passages) + "\n\nQuestion: " + safeInput;
        String answer = guardrails.converse(SYSTEM, prompt);

        GuardrailVerdict out = passages.isEmpty()
                ? guardrails.apply(answer, GuardrailContentSource.OUTPUT)
                : guardrails.checkGrounding(passages, safeInput, answer);
        return new GuardedReply(out.outputText(), out.blocked() ? "guardrail_intervened" : "end_turn", in, out);
    }

    /** Same turn as one Converse call with guardrailConfig + guardContent tagging. */
    public GuardedReply chatInOneCall(String userText, List<String> passages) {
        return guardrails.converseGuarded(SYSTEM, userText, passages);
    }
}
