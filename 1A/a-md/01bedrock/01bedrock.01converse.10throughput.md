# 01bedrock.01converse Throughput Modes

> How you buy model capacity: shared on-demand, cross-Region, provisioned, batch, and service tiers.

## Index

- [1. Modes](#1-modes)
  - [1.1 On-Demand](#11-on-demand)
  - [1.2 Cross-Region Inference](#12-cross-region-inference)
  - [1.3 Provisioned Throughput](#13-provisioned-throughput)
  - [1.4 Batch Inference](#14-batch-inference)
- [2. Service Tiers And Latency-Optimized Inference](#2-service-tiers-and-latency-optimized-inference)
- [3. Mode Comparison](#3-mode-comparison)

Back to [00index](01bedrock.01converse.00index.md).

---

## 1. Modes

Each mode trades price, capacity, and latency differently.

### 1.1 On-Demand

- Pay per input/output token
- Shared capacity
- Quotas apply ([09 quotas](01bedrock.01converse.09errors-retries.md#4-quotas))

### 1.2 Cross-Region Inference

- On-demand price
- More capacity
- Data crosses Regions in the set
- How it is called: [02 inference profiles](01bedrock.01converse.02model-ids.md#3-inference-profiles)

### 1.3 Provisioned Throughput

- Buy model units per hour
  - No commitment, 1-month, or 6-month
- Needed for most custom (fine-tuned) models
  - See [01bedrock.02customization](01bedrock.02customization.00index.md)
- Pay while idle

### 1.4 Batch Inference

→ JavaScript Object Notation (JSON) Lines (JSONL) in Simple Storage Service (S3)  
→ async job  
→ JSONL out

- About 50% of on-demand price for supported models
  - Source: pricing page; verify
- Results in hours, not seconds
- Not coded here (`CreateModelInvocationJob` is a [gap](01bedrock.01converse.00index.md#5-gaps))

## 2. Service Tiers And Latency-Optimized Inference

Two per-request switches on Converse select a capacity class.

- **`serviceTier`**: `priority`, `default`, `flex`
- **Latency-optimized inference**: `performanceConfig.latency = optimized`
- Only some models and Regions
  - Check before relying on them

```python
# illustrative (not in the repo): both switches on one Converse call
resp = runtime.converse(
    modelId=model_id,
    messages=[{"role": "user", "content": [{"text": prompt}]}],
    performanceConfig={"latency": "optimized"},  # latency-optimized inference, where offered
    serviceTier={"type": "flex"},  # priority | default | flex
)
```

- Catch: an unsupported model or Region rejects or ignores these switches.
  - Keep them in config per model, like sampling knobs.

## 3. Mode Comparison

| Mode | Price | Capacity | Latency |
|---|---|---|---|
| On-demand | Per token | Shared, quota-bound | Seconds |
| Cross-Region | Same as on-demand | Pooled over Regions | Seconds |
| Provisioned | Per model unit-hour | Dedicated, paid while idle | Seconds |
| Batch | About 50% of on-demand | Async job | Hours |

- Pick: on-demand via a cross-Region profile, unless load is steady and high (provisioned) or offline (batch).
