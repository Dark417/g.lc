package com.lc.a.a04_01_guardrails.domain;

/** Contextual grounding result: type GROUNDING | RELEVANCE, score 0..1, BLOCKED when score < threshold. */
public record GroundingScore(String type, double score, double threshold, String action) {
}
