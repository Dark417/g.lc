package com.lc.a.domain._01bedrock_01converse;

/** Converse usage block. cacheRead > 0 proves a cachePoint prefix was reused. */
public record TokenUsage(int inputTokens, int outputTokens, int totalTokens, int cacheReadInputTokens) {

    public static final TokenUsage ZERO = new TokenUsage(0, 0, 0, 0);

    public TokenUsage plus(TokenUsage o) {
        return new TokenUsage(inputTokens + o.inputTokens, outputTokens + o.outputTokens,
                totalTokens + o.totalTokens, cacheReadInputTokens + o.cacheReadInputTokens);
    }
}
