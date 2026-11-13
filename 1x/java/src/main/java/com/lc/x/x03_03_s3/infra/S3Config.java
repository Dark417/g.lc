package com.lc.x.x03_03_s3.infra;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3AsyncClient;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.transfer.s3.S3TransferManager;

/**
 * S3 beans of slice 03.03. Off unless x.s3.enabled=true; creating them makes no network call.
 * Every client reuses the shared Region + credentials provider (one credential cache).
 */
@Configuration(proxyBeanMethods = false)
@ConditionalOnProperty(name = "x.s3.enabled", havingValue = "true")
public class S3Config {

    // Sync client: the default for request/response calls. SDK retries (standard mode) are built in.
    @Bean(destroyMethod = "close")
    public S3Client s3Client(Region region, AwsCredentialsProvider credentials) {
        return S3Client.builder().region(region).credentialsProvider(credentials).build();
    }

    // Presigner signs locally with the caller's credentials: no network call, URL dies with the credentials.
    @Bean(destroyMethod = "close")
    public S3Presigner s3Presigner(Region region, AwsCredentialsProvider credentials) {
        return S3Presigner.builder().region(region).credentialsProvider(credentials).build();
    }

    // multipartEnabled(true): the async client splits large putObject/getObject into parts by itself
    // (Java-based, no CRT needed). Catch: without it, a big putObject is ONE request (5 GiB cap).
    @Bean(destroyMethod = "close")
    public S3AsyncClient s3AsyncClient(Region region, AwsCredentialsProvider credentials) {
        return S3AsyncClient.builder().region(region).credentialsProvider(credentials)
                .multipartEnabled(true).build();
    }

    // Transfer Manager = file/dir upload+download with parallel parts and progress, on top of the async client.
    @Bean(destroyMethod = "close")
    public S3TransferManager s3TransferManager(S3AsyncClient asyncClient) {
        return S3TransferManager.builder().s3Client(asyncClient).build();
    }
}
