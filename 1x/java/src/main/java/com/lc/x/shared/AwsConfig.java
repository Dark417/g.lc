package com.lc.x.shared;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.regions.Region;

/**
 * Cross-slice AWS wiring: one Region and one credentials provider, shared by every SDK client.
 * - Credentials: default chain (env -> profile -> web identity -> ECS/EC2 role); never keys in code.
 * - Creating these beans makes no network call, so the app still starts with no AWS access.
 */
@Configuration(proxyBeanMethods = false)
public class AwsConfig {

    @Bean
    public Region awsRegion(@Value("${x.aws.region:us-east-1}") String region) {
        return Region.of(region);
    }

    @Bean
    public AwsCredentialsProvider awsCredentialsProvider() {
        // Lazy: resolves credentials on first signed request, then caches and refreshes them.
        return DefaultCredentialsProvider.builder().build();
    }
}
