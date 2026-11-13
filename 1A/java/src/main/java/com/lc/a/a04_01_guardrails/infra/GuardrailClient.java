package com.lc.a.a04_01_guardrails.infra;

import com.lc.a.a04_01_guardrails.domain.GroundingScore;
import com.lc.a.a04_01_guardrails.domain.GuardedReply;
import com.lc.a.a04_01_guardrails.domain.GuardrailVerdict;
import com.lc.a.a04_01_guardrails.domain.PolicyHit;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.springframework.beans.factory.DisposableBean;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.core.client.config.ClientOverrideConfiguration;
import software.amazon.awssdk.core.retry.RetryMode;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;
import software.amazon.awssdk.services.bedrockruntime.model.ApplyGuardrailRequest;
import software.amazon.awssdk.services.bedrockruntime.model.ApplyGuardrailResponse;
import software.amazon.awssdk.services.bedrockruntime.model.ContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.ConversationRole;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseRequest;
import software.amazon.awssdk.services.bedrockruntime.model.ConverseResponse;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailAction;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailAssessment;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailConfiguration;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailContentQualifier;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailContentSource;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailConverseContentBlock;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailConverseContentQualifier;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailConverseTextBlock;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailOutputContent;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailOutputScope;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailTextBlock;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailTrace;
import software.amazon.awssdk.services.bedrockruntime.model.GuardrailTraceAssessment;
import software.amazon.awssdk.services.bedrockruntime.model.InferenceConfiguration;
import software.amazon.awssdk.services.bedrockruntime.model.Message;
import software.amazon.awssdk.services.bedrockruntime.model.SystemContentBlock;

/**
 * Bedrock Guardrails data-plane showcase (AWS SDK v2), in the order of docs/04.01.guardrails.md.
 * - apply: standalone ApplyGuardrail on INPUT or OUTPUT; works for any model, even non-Bedrock
 * - checkGrounding: contextual grounding of a RAG answer (grounding_source + query + guard_content)
 * - converseGuarded: Converse with GuardrailConfiguration and guardContent blocks (guard only user text)
 * - Owns its own BedrockRuntimeClient (not a bean) so it never clashes with other slices' clients.
 * - Guardrail config itself (policies, versions) is Terraform's job (terraform/04.01.guardrails.tf);
 *   the Python slice shows create/update/version through the control-plane SDK.
 */
@Component
@ConditionalOnProperty(name = "a.guardrails.enabled", havingValue = "true")
public class GuardrailClient implements DisposableBean {

    private final BedrockRuntimeClient runtime;
    private final String guardrailId;
    private final String guardrailVersion;
    private final String modelId;

    public GuardrailClient(
            Region region,
            AwsCredentialsProvider credentials,
            @Value("${a.guardrails.guardrail-id}") String guardrailId,
            @Value("${a.guardrails.guardrail-version}") String guardrailVersion,
            @Value("${a.models.text}") String modelId) {
        this.runtime = BedrockRuntimeClient.builder()
                .region(region)
                .credentialsProvider(credentials)
                .overrideConfiguration(ClientOverrideConfiguration.builder()
                        .retryStrategy(RetryMode.ADAPTIVE_V2) // backoff + client-side rate limit on throttling
                        .apiCallAttemptTimeout(Duration.ofSeconds(60)) // model calls are slow
                        .build())
                .build();
        this.guardrailId = guardrailId;
        this.guardrailVersion = guardrailVersion; // pin a number in prod; DRAFT changes under you
        this.modelId = modelId;
    }

    // ================================================================ ApplyGuardrail (standalone)

    /**
     * Standalone check of plain text. source INPUT = user side, OUTPUT = model side.
     * Use around any model; catch: one extra round trip per check (order of magnitude: 100s of ms).
     */
    public GuardrailVerdict apply(String text, GuardrailContentSource source) {
        GuardrailContentBlock block = GuardrailContentBlock.fromText(GuardrailTextBlock.builder().text(text).build());
        return apply(List.of(block), source, text);
    }

    /**
     * Contextual grounding of a RAG answer: passages tagged grounding_source, question tagged query, answer tagged
     * guard_content. Without all three qualifiers the grounding policy is silently skipped.
     */
    public GuardrailVerdict checkGrounding(List<String> passages, String query, String answer) {
        List<GuardrailContentBlock> blocks = new ArrayList<>();
        for (String p : passages) {
            blocks.add(textBlock(p, GuardrailContentQualifier.GROUNDING_SOURCE));
        }
        blocks.add(textBlock(query, GuardrailContentQualifier.QUERY));
        blocks.add(textBlock(answer, GuardrailContentQualifier.GUARD_CONTENT));
        return apply(blocks, GuardrailContentSource.OUTPUT, answer);
    }

    private GuardrailVerdict apply(List<GuardrailContentBlock> blocks, GuardrailContentSource source, String original) {
        ApplyGuardrailResponse resp = runtime.applyGuardrail(ApplyGuardrailRequest.builder()
                .guardrailIdentifier(guardrailId)
                .guardrailVersion(guardrailVersion)
                .source(source)
                .content(blocks)
                .outputScope(GuardrailOutputScope.INTERVENTIONS) // FULL = every assessment, for eval/tuning
                .build());
        return toVerdict(resp, original);
    }

    private static GuardrailContentBlock textBlock(String text, GuardrailContentQualifier qualifier) {
        return GuardrailContentBlock.fromText(GuardrailTextBlock.builder().text(text).qualifiers(qualifier).build());
    }

    /** ApplyGuardrail response -> verdict. outputs[] is filled only when the guardrail intervened. */
    public static GuardrailVerdict toVerdict(ApplyGuardrailResponse resp, String original) {
        List<PolicyHit> hits = new ArrayList<>();
        List<GroundingScore> grounding = new ArrayList<>();
        resp.assessments().forEach(a -> collect(a, hits, grounding));
        boolean intervened = resp.action() == GuardrailAction.GUARDRAIL_INTERVENED;
        String out = resp.outputs().stream().map(GuardrailOutputContent::text).collect(Collectors.joining("\n"));
        int guarded = 0;
        int total = 0;
        if (resp.guardrailCoverage() != null && resp.guardrailCoverage().textCharacters() != null) {
            guarded = nz(resp.guardrailCoverage().textCharacters().guarded());
            total = nz(resp.guardrailCoverage().textCharacters().total());
        }
        return new GuardrailVerdict(intervened, isBlocked(hits, grounding),
                intervened && !out.isEmpty() ? out : original, hits, grounding, guarded, total);
    }

    /** Flattens one GuardrailAssessment; same shape in ApplyGuardrail and in the Converse trace. */
    static void collect(GuardrailAssessment a, List<PolicyHit> hits, List<GroundingScore> grounding) {
        if (a.topicPolicy() != null) {
            a.topicPolicy().topics().forEach(t -> hits.add(
                    new PolicyHit("topic", t.name(), t.actionAsString(), bool(t.detected(), true), "")));
        }
        if (a.contentPolicy() != null) {
            a.contentPolicy().filters().forEach(f -> hits.add(new PolicyHit("content", f.typeAsString(),
                    f.actionAsString(), bool(f.detected(), !"NONE".equals(f.actionAsString())), f.confidenceAsString())));
        }
        if (a.wordPolicy() != null) {
            a.wordPolicy().customWords().forEach(w -> hits.add(
                    new PolicyHit("word", "CUSTOM", w.actionAsString(), bool(w.detected(), true), "")));
            a.wordPolicy().managedWordLists().forEach(w -> hits.add(
                    new PolicyHit("managed_word", w.typeAsString(), w.actionAsString(), bool(w.detected(), true), "")));
        }
        if (a.sensitiveInformationPolicy() != null) {
            a.sensitiveInformationPolicy().piiEntities().forEach(p -> hits.add(
                    new PolicyHit("pii", p.typeAsString(), p.actionAsString(), bool(p.detected(), true), "")));
            a.sensitiveInformationPolicy().regexes().forEach(r -> hits.add(
                    new PolicyHit("regex", r.name(), r.actionAsString(), bool(r.detected(), true), "")));
        }
        if (a.contextualGroundingPolicy() != null) {
            a.contextualGroundingPolicy().filters().forEach(f -> grounding.add(new GroundingScore(
                    f.typeAsString(), f.score(), f.threshold(), f.actionAsString())));
        }
    }

    // ================================================================ Converse + guardrailConfig

    /**
     * Converse with GuardrailConfiguration: Bedrock runs input check, model, output check in one call.
     * Only guardContent blocks are evaluated: passages (grounding_source) and the user text (query); the plain
     * instruction block is not, which avoids prompt-attack false positives on your own instructions.
     * stopReason guardrail_intervened means the returned text is the blocked message.
     */
    public GuardedReply converseGuarded(String system, String userText, List<String> passages) {
        List<ContentBlock> content = new ArrayList<>();
        content.add(ContentBlock.fromText("Use the context below to answer the question."));
        for (String p : passages) {
            content.add(guardContent(p, GuardrailConverseContentQualifier.GROUNDING_SOURCE));
        }
        content.add(guardContent(userText, GuardrailConverseContentQualifier.QUERY));

        ConverseResponse resp = runtime.converse(ConverseRequest.builder()
                .modelId(modelId)
                .system(SystemContentBlock.fromText(system))
                .messages(Message.builder().role(ConversationRole.USER).content(content).build())
                .inferenceConfig(InferenceConfiguration.builder().maxTokens(512).temperature(0.0f).build())
                .guardrailConfig(GuardrailConfiguration.builder()
                        .guardrailIdentifier(guardrailId)
                        .guardrailVersion(guardrailVersion)
                        .trace(GuardrailTrace.ENABLED) // ENABLED_FULL adds raw model output: never log it
                        .build())
                .build());

        String text = resp.output().message().content().stream()
                .map(ContentBlock::text).filter(t -> t != null).collect(Collectors.joining());
        GuardrailVerdict in = null;
        GuardrailVerdict out = null;
        if (resp.trace() != null && resp.trace().guardrail() != null) {
            GuardrailTraceAssessment g = resp.trace().guardrail();
            in = traceVerdict(g.inputAssessment().values());
            out = traceVerdict(g.outputAssessments().values().stream().flatMap(List::stream).toList());
        }
        return new GuardedReply(text, resp.stopReasonAsString(), in, out);
    }

    /** Plain Converse without a guardrail: the model call inside the ApplyGuardrail sandwich (service layer). */
    public String converse(String system, String userText) {
        ConverseResponse resp = runtime.converse(ConverseRequest.builder()
                .modelId(modelId)
                .system(SystemContentBlock.fromText(system))
                .messages(Message.builder().role(ConversationRole.USER).content(ContentBlock.fromText(userText)).build())
                .inferenceConfig(InferenceConfiguration.builder().maxTokens(512).temperature(0.2f).build())
                .build());
        return resp.output().message().content().stream()
                .map(ContentBlock::text).filter(t -> t != null).collect(Collectors.joining());
    }

    private static ContentBlock guardContent(String text, GuardrailConverseContentQualifier qualifier) {
        return ContentBlock.fromGuardContent(GuardrailConverseContentBlock.fromText(
                GuardrailConverseTextBlock.builder().text(text).qualifiers(qualifier).build()));
    }

    private static GuardrailVerdict traceVerdict(Collection<GuardrailAssessment> assessments) {
        if (assessments.isEmpty()) {
            return null;
        }
        List<PolicyHit> hits = new ArrayList<>();
        List<GroundingScore> grounding = new ArrayList<>();
        assessments.forEach(a -> collect(a, hits, grounding));
        boolean blocked = isBlocked(hits, grounding);
        return new GuardrailVerdict(!hits.isEmpty() || blocked, blocked, "", hits, grounding, 0, 0);
    }

    // ================================================================ helpers

    private static boolean isBlocked(List<PolicyHit> hits, List<GroundingScore> grounding) {
        return hits.stream().anyMatch(h -> "BLOCKED".equals(h.action()))
                || grounding.stream().anyMatch(g -> "BLOCKED".equals(g.action()));
    }

    private static boolean bool(Boolean b, boolean fallback) {
        return b == null ? fallback : b;
    }

    private static int nz(Integer i) {
        return i == null ? 0 : i;
    }

    /** Units per policy = what you are billed for; exposed for metrics. */
    public static Map<String, Integer> usage(ApplyGuardrailResponse resp) {
        if (resp.usage() == null) {
            return Map.of();
        }
        return Map.of(
                "topic", nz(resp.usage().topicPolicyUnits()),
                "content", nz(resp.usage().contentPolicyUnits()),
                "word", nz(resp.usage().wordPolicyUnits()),
                "pii", nz(resp.usage().sensitiveInformationPolicyUnits()),
                "grounding", nz(resp.usage().contextualGroundingPolicyUnits()));
    }

    @Override
    public void destroy() {
        runtime.close();
    }
}
