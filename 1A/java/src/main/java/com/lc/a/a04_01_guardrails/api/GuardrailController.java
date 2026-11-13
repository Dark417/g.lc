package com.lc.a.a04_01_guardrails.api;

import com.lc.a.a04_01_guardrails.domain.GuardedReply;
import com.lc.a.a04_01_guardrails.domain.GuardrailVerdict;
import com.lc.a.a04_01_guardrails.infra.GuardrailClient;
import com.lc.a.a04_01_guardrails.service.GuardedChatService;
import java.util.List;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailContentSource;

/** Thin REST adapter under /guardrails. Responses never echo the matched sensitive text. */
@RestController
@RequestMapping("/guardrails")
@ConditionalOnProperty(name = "a.guardrails.enabled", havingValue = "true")
public class GuardrailController {

    public record ApplyRequest(String text, String source) {
    }

    public record ChatRequest(String text, List<String> context) {
        public ChatRequest {
            context = context == null ? List.of() : List.copyOf(context);
        }
    }

    private final GuardrailClient guardrails;
    private final GuardedChatService chat;

    public GuardrailController(GuardrailClient guardrails, GuardedChatService chat) {
        this.guardrails = guardrails;
        this.chat = chat;
    }

    /** source: INPUT (default) or OUTPUT. */
    @PostMapping("/apply")
    public GuardrailVerdict apply(@RequestBody ApplyRequest req) {
        GuardrailContentSource source = "OUTPUT".equalsIgnoreCase(req.source())
                ? GuardrailContentSource.OUTPUT
                : GuardrailContentSource.INPUT;
        return guardrails.apply(req.text(), source);
    }

    /** ApplyGuardrail sandwich: guard input, model, guard output with grounding. */
    @PostMapping("/chat")
    public GuardedReply chat(@RequestBody ChatRequest req) {
        return chat.chat(req.text(), req.context());
    }

    /** One Converse call with guardrailConfig and guardContent tagging. */
    @PostMapping("/converse")
    public GuardedReply converse(@RequestBody ChatRequest req) {
        return chat.chatInOneCall(req.text(), req.context());
    }
}
