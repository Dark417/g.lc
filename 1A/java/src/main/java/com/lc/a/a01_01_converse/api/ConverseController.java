package com.lc.a.a01_01_converse.api;

import com.lc.a.a01_01_converse.domain.ConverseException;
import com.lc.a.a01_01_converse.domain.ConverseResult;
import com.lc.a.a01_01_converse.service.ConverseService;
import com.lc.a.a01_01_converse.service.DemoTools;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import java.io.IOException;
import java.util.Map;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

/**
 * Thin REST adapter at /converse.
 * - POST /converse         sync Converse
 * - POST /converse/tools   tool-use loop with two demo tools
 * - POST /converse/stream  Server-Sent Events: "text" per delta, then "done" with stopReason + usage
 */
@RestController
@RequestMapping("/converse")
@ConditionalOnProperty(name = "a.converse.enabled", havingValue = "true")
public class ConverseController {

    public record PromptRequest(@NotBlank String prompt, String system) {
    }

    private final ConverseService service;

    public ConverseController(ConverseService service) {
        this.service = service;
    }

    @PostMapping
    public ConverseResult converse(@Valid @RequestBody PromptRequest body) {
        return service.converse(body.prompt(), body.system());
    }

    @PostMapping("/tools")
    public ConverseResult tools(@Valid @RequestBody PromptRequest body) {
        return service.converseWithTools(body.prompt(), DemoTools.all());
    }

    // SseEmitter keeps the servlet thread free: deltas are pushed from the SDK's Netty event-loop thread.
    // Timeout 120 s bounds the HTTP response; the model call itself is bounded by the async client config.
    @PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter stream(@Valid @RequestBody PromptRequest body) {
        SseEmitter emitter = new SseEmitter(120_000L);
        service.converseStream(body.prompt(), delta -> send(emitter, "text", Map.of("text", delta)))
                .whenComplete((result, error) -> {
                    if (error != null) {
                        // Mid-stream failure: the client already has partial text; tell it explicitly.
                        send(emitter, "error", Map.of("message", String.valueOf(error.getMessage())));
                        emitter.completeWithError(error);
                    } else {
                        send(emitter, "done", Map.of("stopReason", result.stopReason(), "usage", result.usage(),
                                "latencyMs", result.latencyMs()));
                        emitter.complete();
                    }
                });
        return emitter;
    }

    private static void send(SseEmitter emitter, String event, Object data) {
        try {
            emitter.send(SseEmitter.event().name(event).data(data, MediaType.APPLICATION_JSON));
        } catch (IOException | IllegalStateException e) {
            // Client went away: nothing to do; the stream keeps running until the model finishes.
        }
    }

    @ExceptionHandler(ConverseException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Map<String, String> badRequest(ConverseException e) {
        return Map.of("error", e.getMessage());
    }
}
