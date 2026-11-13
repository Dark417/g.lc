package com.lc.a.a01_01_converse.infra;

/**
 * Slice settings (application.yml a.models.* and a.converse.*; defaults in ConverseConfig).
 * - modelId: model ID, cross-Region profile ID (us.anthropic...), or app inference profile ARN.
 * - sendSampling=false for models that reject temperature/topP (some newer Claude models).
 */
public record ConverseProperties(
        String modelId, int maxTokens, float temperature, float topP, boolean sendSampling, int maxToolRounds) {
}
