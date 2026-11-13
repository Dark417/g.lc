package com.lc.a.a01_01_converse.infra;

import java.time.Duration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.core.client.config.ClientOverrideConfiguration;
import software.amazon.awssdk.core.retry.RetryMode;
import software.amazon.awssdk.http.nio.netty.NettyNioAsyncHttpClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeAsyncClient;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;

/**
 * Bedrock runtime wiring: one sync client (Converse, tool loop) + one async client (ConverseStream).
 * - ConverseStream exists only on the async client in SDK v2 (event streams need non-blocking HTTP: Netty).
 * - Clients are thread-safe and pool connections: one per app, never one per request.
 * - Building them makes no network call. IAM: terraform/01.01.bedrock-converse.tf.
 */
@Configuration(proxyBeanMethods = false)
@ConditionalOnProperty(name = "a.converse.enabled", havingValue = "true")
public class ConverseConfig {

    @Bean
    public ConverseProperties converseProperties(
            @Value("${a.models.text}") String modelId,
            @Value("${a.converse.max-tokens:1024}") int maxTokens,
            @Value("${a.converse.temperature:0.2}") float temperature,
            @Value("${a.converse.top-p:0.9}") float topP,
            @Value("${a.converse.send-sampling:true}") boolean sendSampling,
            @Value("${a.converse.max-tool-rounds:5}") int maxToolRounds) {
        return new ConverseProperties(modelId, maxTokens, temperature, topP, sendSampling, maxToolRounds);
    }

    // Sync client for request/response calls.
    // - ADAPTIVE_V2 = standard retries (backoff + jitter on 429/5xx) + client-side rate limiting after throttles.
    // - Attempt timeout must exceed the longest generation (LLM calls take seconds, not ms); call timeout
    //   bounds all retries together.
    @Bean(destroyMethod = "close")
    public BedrockRuntimeClient bedrockRuntimeClient(Region region, AwsCredentialsProvider credentials) {
        return BedrockRuntimeClient.builder()
                .region(region)
                .credentialsProvider(credentials)
                .overrideConfiguration(ClientOverrideConfiguration.builder()
                        .retryStrategy(RetryMode.ADAPTIVE_V2)
                        .apiCallAttemptTimeout(Duration.ofSeconds(60))
                        .apiCallTimeout(Duration.ofSeconds(180))
                        .build())
                .build();
    }

    // Async client for ConverseStream. Netty read timeout = max silence between frames, not total time:
    // a long stream that keeps sending deltas never trips it.
    @Bean(destroyMethod = "close")
    public BedrockRuntimeAsyncClient bedrockRuntimeAsyncClient(Region region, AwsCredentialsProvider credentials) {
        return BedrockRuntimeAsyncClient.builder()
                .region(region)
                .credentialsProvider(credentials)
                .httpClientBuilder(NettyNioAsyncHttpClient.builder()
                        .readTimeout(Duration.ofSeconds(60))
                        .maxConcurrency(64)) // open streams per client; each SSE request holds one
                .overrideConfiguration(ClientOverrideConfiguration.builder()
                        .retryStrategy(RetryMode.ADAPTIVE_V2) // retries only before the first event arrives
                        .build())
                .build();
    }
}
