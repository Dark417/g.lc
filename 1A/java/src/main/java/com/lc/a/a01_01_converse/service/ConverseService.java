package com.lc.a.a01_01_converse.service;

import com.lc.a.a01_01_converse.domain.ConverseException;
import com.lc.a.a01_01_converse.domain.ConverseResult;
import com.lc.a.a01_01_converse.domain.LocalTool;
import com.lc.a.a01_01_converse.domain.TokenUsage;
import com.lc.a.a01_01_converse.domain.ToolCall;
import com.lc.a.a01_01_converse.infra.ConverseProperties;
import com.lc.a.shared.Retry;
import java.time.Duration;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.core.SdkNumber;
import software.amazon.awssdk.core.document.Document;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeAsyncClient;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;
import software.amazon.awssdk.services.bedrockruntime.model.AccessDeniedException;
import software.amazon.awssdk.services.bedrockruntime.model.ContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.ConversationRole;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseRequest;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseResponse;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseStreamRequest;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseStreamResponseHandler;
import software.amazon.awssdk.services.bedrockruntime.model.InferenceConfiguration;
import software.amazon.awssdk.services.bedrockruntime.model.InternalServerException;
import software.amazon.awssdk.services.bedrockruntime.model.Message;
import software.amazon.awssdk.services.bedrockruntime.model.ModelNotReadyException;
import software.amazon.awssdk.services.bedrockruntime.model.ModelTimeoutException;
import software.amazon.awssdk.services.bedrockruntime.model.ServiceUnavailableException;
import software.amazon.awssdk.services.bedrockruntime.model.SystemContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.ThrottlingException;
import software.amazon.awssdk.services.bedrockruntime.model.Tool;
import software.amazon.awssdk.services.bedrockruntime.model.ToolChoice;
import software.amazon.awssdk.services.bedrockruntime.model.ToolConfiguration;
import software.amazon.awssdk.services.bedrockruntime.model.ToolInputSchema;
import software.amazon.awssdk.services.bedrockruntime.model.ToolResultBlock;
import software.amazon.awssdk.services.bedrockruntime.model.ToolResultContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.ToolResultStatus;
import software.amazon.awssdk.services.bedrockruntime.model.ToolSpecification;
import software.amazon.awssdk.services.bedrockruntime.model.ToolUseBlock;
import software.amazon.awssdk.services.bedrockruntime.model.ValidationException;

/**
 * Converse showcase on the backend call path, in the order of docs/01.01.bedrock-converse.md.
 * - converse: sync request/response with system prompt + inferenceConfig, app-level retry on capacity errors.
 * - converseWithTools: toolUse -> toolResult loop, capped.
 * - converseStream: async client + ConverseStreamResponseHandler, text deltas pushed to a callback.
 * IAM: Converse = bedrock:InvokeModel, ConverseStream = bedrock:InvokeModelWithResponseStream.
 */
@Service
@ConditionalOnProperty(name = "a.converse.enabled", havingValue = "true")
public class ConverseService {

    private static final String DEFAULT_SYSTEM = "You are a concise assistant for backend engineers.";

    private final BedrockRuntimeClient client;
    private final BedrockRuntimeAsyncClient asyncClient;
    private final ConverseProperties props;
    private final Retry retry = new Retry(3, Duration.ofMillis(500), Duration.ofSeconds(8));

    public ConverseService(BedrockRuntimeClient client, BedrockRuntimeAsyncClient asyncClient, ConverseProperties props) {
        this.client = client;
        this.asyncClient = asyncClient;
        this.props = props;
    }

    // ================================================================ basic Converse

    /**
     * Shows: one Converse call (system + inferenceConfig) wrapped in an app-level retry.
     * Use for single-shot tasks. Catch: check stopReason == max_tokens before trusting the text;
     * SDK retries (adaptive) x app retries (3) multiply under load.
     */
    public ConverseResult converse(String prompt, String system) {
        ConverseRequest request = ConverseRequest.builder()
                .modelId(props.modelId())
                .system(SystemContentBlock.fromText(system == null ? DEFAULT_SYSTEM : system))
                .messages(userText(prompt))
                .inferenceConfig(inferenceConfig())
                .requestMetadata(Map.of("feature", "converse-basic")) // filterable in invocation logs (05.01)
                .build();
        try {
            ConverseResponse response = retry.call(() -> client.converse(request), ConverseService::isRetryable);
            return toResult(response, 1);
        } catch (ValidationException | AccessDeniedException e) {
            // Fix the request: role order, unsupported field, bare ID of a profile-only model, missing IAM.
            throw new ConverseException(e.awsErrorDetails().errorCode() + ": " + e.awsErrorDetails().errorMessage(), e);
        }
    }

    /** Retry capacity/transient errors only; ValidationException and AccessDenied are request bugs. */
    public static boolean isRetryable(Throwable e) {
        return e instanceof ThrottlingException
                || e instanceof ServiceUnavailableException
                || e instanceof InternalServerException
                || e instanceof ModelNotReadyException
                || e instanceof ModelTimeoutException;
    }

    // ================================================================ tool use loop

    /**
     * Shows: toolConfig + toolChoice and the loop: tool_use -> run locally -> toolResult (same toolUseId) -> again.
     * Catch: send toolConfig on every call; answer all parallel toolUse blocks in ONE user message; cap rounds.
     */
    public ConverseResult converseWithTools(String prompt, List<LocalTool> tools) {
        Map<String, LocalTool> byName = tools.stream().collect(Collectors.toMap(LocalTool::name, t -> t));
        ToolConfiguration toolConfig = ToolConfiguration.builder()
                .tools(tools.stream().map(ConverseService::toSdkTool).toList())
                .toolChoice(ToolChoice.fromAuto(a -> { })) // auto | any | tool(name) for a forced call
                .build();
        List<Message> messages = new ArrayList<>(List.of(userText(prompt)));
        TokenUsage total = TokenUsage.ZERO;
        for (int round = 1; round <= props.maxToolRounds(); round++) {
            ConverseResponse response = client.converse(ConverseRequest.builder()
                    .modelId(props.modelId())
                    .system(SystemContentBlock.fromText("Use the tools when they help. Answer briefly."))
                    .messages(messages)
                    .inferenceConfig(inferenceConfig())
                    .toolConfig(toolConfig)
                    .build());
            ConverseResult result = toResult(response, round);
            total = total.plus(result.usage());
            messages.add(response.output().message()); // assistant message unchanged
            if (!"tool_use".equals(response.stopReasonAsString())) {
                return new ConverseResult(result.text(), result.stopReason(), total, result.latencyMs(),
                        result.toolCalls(), round);
            }
            List<ContentBlock> results = result.toolCalls().stream().map(call -> runTool(byName, call)).toList();
            messages.add(Message.builder().role(ConversationRole.USER).content(results).build());
        }
        throw new ConverseException("tool loop exceeded " + props.maxToolRounds() + " rounds");
    }

    private static ContentBlock runTool(Map<String, LocalTool> byName, ToolCall call) {
        LocalTool tool = byName.get(call.name());
        ToolResultBlock.Builder result = ToolResultBlock.builder().toolUseId(call.toolUseId());
        if (tool == null) {
            result.status(ToolResultStatus.ERROR).content(ToolResultContentBlock.fromText("unknown tool " + call.name()));
        } else {
            try {
                result.content(ToolResultContentBlock.fromJson(toDocument(tool.handler().apply(call.input()))));
            } catch (IllegalArgumentException e) { // bad input: let the model see the error and retry
                result.status(ToolResultStatus.ERROR).content(ToolResultContentBlock.fromText(e.getMessage()));
            }
        }
        return ContentBlock.fromToolResult(result.build());
    }

    // ================================================================ ConverseStream

    /**
     * Shows: ConverseStream on the async client; the visitor receives contentBlockDelta (text), messageStop
     * (stopReason) and metadata (usage, latency) events. Use for user-facing answers (time to first token).
     * Catch: errors can arrive mid-stream after HTTP 200 ⇒ the future completes exceptionally; partial text
     * already sent to the user must be marked failed by the caller.
     */
    public CompletableFuture<ConverseResult> converseStream(String prompt, Consumer<String> onText) {
        StringBuilder text = new StringBuilder();
        AtomicReference<String> stopReason = new AtomicReference<>("");
        AtomicReference<TokenUsage> usage = new AtomicReference<>(TokenUsage.ZERO);
        AtomicReference<Long> latency = new AtomicReference<>(0L);

        ConverseStreamResponseHandler handler = ConverseStreamResponseHandler.builder()
                .subscriber(ConverseStreamResponseHandler.Visitor.builder()
                        .onContentBlockDelta(e -> {
                            String delta = e.delta().text(); // null for toolUse / reasoning deltas
                            if (delta != null) {
                                text.append(delta);
                                onText.accept(delta);
                            }
                        })
                        .onMessageStop(e -> stopReason.set(e.stopReasonAsString()))
                        .onMetadata(e -> { // always the last event
                            usage.set(new TokenUsage(e.usage().inputTokens(), e.usage().outputTokens(),
                                    e.usage().totalTokens(), nz(e.usage().cacheReadInputTokens())));
                            latency.set(e.metrics().latencyMs());
                        })
                        .build())
                .build();

        ConverseStreamRequest request = ConverseStreamRequest.builder()
                .modelId(props.modelId())
                .system(SystemContentBlock.fromText(DEFAULT_SYSTEM))
                .messages(userText(prompt))
                .inferenceConfig(inferenceConfig())
                .build();
        return asyncClient.converseStream(request, handler)
                .thenApply(v -> new ConverseResult(text.toString(), stopReason.get(), usage.get(), latency.get(),
                        List.of(), 1));
    }

    // ================================================================ mapping helpers

    private InferenceConfiguration inferenceConfig() {
        InferenceConfiguration.Builder b = InferenceConfiguration.builder().maxTokens(props.maxTokens());
        if (props.sendSampling()) { // some newer models reject temperature/topP
            b.temperature(props.temperature()).topP(props.topP());
        }
        return b.build();
    }

    private static Message userText(String text) {
        return Message.builder().role(ConversationRole.USER).content(ContentBlock.fromText(text)).build();
    }

    private static Tool toSdkTool(LocalTool t) {
        return Tool.fromToolSpec(ToolSpecification.builder()
                .name(t.name())
                .description(t.description())
                .inputSchema(ToolInputSchema.fromJson(toDocument(t.inputSchema())))
                .build());
    }

    /** Converse response -> domain result: text blocks joined, toolUse blocks mapped, usage + latency. */
    public static ConverseResult toResult(ConverseResponse r, int rounds) {
        StringBuilder text = new StringBuilder();
        List<ToolCall> calls = new ArrayList<>();
        for (ContentBlock block : r.output().message().content()) {
            if (block.text() != null) {
                text.append(block.text());
            }
            ToolUseBlock tu = block.toolUse();
            if (tu != null) {
                calls.add(new ToolCall(tu.toolUseId(), tu.name(), asMap(tu.input())));
            }
        }
        TokenUsage usage = new TokenUsage(r.usage().inputTokens(),
                r.usage().outputTokens(), r.usage().totalTokens(), nz(r.usage().cacheReadInputTokens()));
        return new ConverseResult(text.toString(), r.stopReasonAsString(), usage, r.metrics().latencyMs(), calls, rounds);
    }

    private static int nz(Integer v) {
        return v == null ? 0 : v;
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> asMap(Document d) {
        Object plain = unwrap(d);
        return plain instanceof Map<?, ?> m ? (Map<String, Object>) m : Map.of();
    }

    /** SDK Document -> plain Java (Map, List, String, Number, Boolean, null). */
    private static Object unwrap(Document d) {
        if (d == null || d.isNull()) {
            return null;
        }
        if (d.isMap()) {
            Map<String, Object> out = new LinkedHashMap<>();
            d.asMap().forEach((k, v) -> out.put(k, unwrap(v)));
            return out;
        }
        if (d.isList()) {
            return d.asList().stream().map(ConverseService::unwrap).toList();
        }
        if (d.isNumber()) {
            SdkNumber n = d.asNumber();
            return n.bigDecimalValue();
        }
        if (d.isBoolean()) {
            return d.asBoolean();
        }
        return d.asString();
    }

    /** Plain Java -> SDK Document (for JSON schemas and tool results). */
    static Document toDocument(Object o) {
        if (o == null) {
            return Document.fromNull();
        }
        if (o instanceof Map<?, ?> m) {
            Map<String, Document> out = new LinkedHashMap<>();
            m.forEach((k, v) -> out.put(String.valueOf(k), toDocument(v)));
            return Document.fromMap(out);
        }
        if (o instanceof List<?> l) {
            return Document.fromList(l.stream().map(ConverseService::toDocument).toList());
        }
        if (o instanceof Number n) {
            return Document.fromNumber(n.toString());
        }
        if (o instanceof Boolean b) {
            return Document.fromBoolean(b);
        }
        return Document.fromString(String.valueOf(o));
    }
}
