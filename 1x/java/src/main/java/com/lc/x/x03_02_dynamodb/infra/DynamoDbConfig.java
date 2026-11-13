package com.lc.x.x03_02_dynamodb.infra;

import java.net.URI;
import java.time.Duration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.core.client.config.ClientOverrideConfiguration;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.DynamoDbClientBuilder;

/**
 * DynamoDB wiring for the slice: one sync low-level client + one Enhanced Client on top of it.
 * - Clients are thread-safe and hold an HTTP connection pool: one per app, never one per request.
 * - Building them makes no network call; the first request resolves credentials and the endpoint.
 */
@Configuration(proxyBeanMethods = false)
@ConditionalOnProperty(name = "x.dynamodb.enabled", havingValue = "true")
public class DynamoDbConfig {

    @Bean
    public DynamoDbProperties dynamoDbProperties(
            @Value("${x.dynamodb.orders-table}") String ordersTable,
            @Value("${x.dynamodb.idempotency-table}") String idempotencyTable,
            @Value("${x.dynamodb.gsi1-name}") String gsi1Name) {
        return new DynamoDbProperties(ordersTable, idempotencyTable, gsi1Name);
    }

    // Sync client: DynamoDB calls are short (single-digit ms), so blocking threads are fine here.
    // Timeouts: attempt timeout bounds one HTTP try; call timeout bounds all SDK retries together.
    // The SDK retries throttling and 5xx with backoff; app-level retries are only for conditional work.
    // Optional endpoint override (x.dynamodb.endpoint-override) points at DynamoDB Local for laptops.
    @Bean(destroyMethod = "close")
    public DynamoDbClient dynamoDbClient(
            Region region,
            AwsCredentialsProvider credentialsProvider,
            @Value("${x.dynamodb.endpoint-override:}") String endpointOverride) {
        DynamoDbClientBuilder builder = DynamoDbClient.builder()
                .region(region)
                .credentialsProvider(credentialsProvider)
                .overrideConfiguration(ClientOverrideConfiguration.builder()
                        .apiCallAttemptTimeout(Duration.ofSeconds(2))
                        .apiCallTimeout(Duration.ofSeconds(10))
                        .build());
        if (!endpointOverride.isBlank()) {
            builder.endpointOverride(URI.create(endpointOverride));
        }
        return builder.build();
    }

    // Enhanced Client: maps beans <-> AttributeValue maps. Default extensions are on:
    // VersionedRecordExtension (@DynamoDbVersionAttribute) and AtomicCounterExtension.
    @Bean
    public DynamoDbEnhancedClient dynamoDbEnhancedClient(DynamoDbClient dynamoDbClient) {
        return DynamoDbEnhancedClient.builder().dynamoDbClient(dynamoDbClient).build();
    }
}
