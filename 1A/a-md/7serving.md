# 7serving — Self-Hosted Model Serving

> How an LLM is served on your own GPUs: prefill and decode, the KV cache, batching, quantization, the main engines, and how to size and scale it.
> Group 7 (AI infra). Related: [2models.md](2models.md) §6, [6cost-latency.md](6cost-latency.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16. Numbers are order of magnitude unless cited.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept: prefill and decode](#1-concept-prefill-and-decode)
- [2. The KV cache](#2-the-kv-cache)
- [3. Batching and scheduling](#3-batching-and-scheduling)
- [4. Making it smaller and faster](#4-making-it-smaller-and-faster)
- [5. Serving engines compared](#5-serving-engines-compared)
- [6. Metrics and sizing](#6-metrics-and-sizing)
- [7. Scaling a serving fleet](#7-scaling-a-serving-fleet)
- [8. System design view: choosing](#8-system-design-view-choosing)
- [9. Failure modes](#9-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** serving = running a model behind an API with good throughput and latency on GPUs you pay for.
- **Why:** needed for data control, very high steady volume, or specialized open models. It's the core of AI-infra roles.
- **How:** a serving engine (vLLM, SGLang, TensorRT-LLM) batches many requests together, manages the KV cache in GPU memory, and streams tokens.
- **Catch:** GPU memory, mostly the KV cache, limits how many requests run at once. Throughput and latency trade against each other.
- 🗣 "Serving is a memory-management problem: weights plus KV cache must fit, and batching decides throughput versus latency."

---

## 1. Concept: prefill and decode
`AI` ★★★

- **Plain idea:** a request has two phases. Reading the prompt (prefill) is one big parallel pass; writing the answer (decode) is one token at a time.
- **Picture it:** reading a 10-page brief at a glance, then writing a reply word by word, re-glancing at your notes for each word.
- **How it works**
  1. **Prefill:** process all prompt tokens at once; compute-heavy; sets time to first token.
  2. Store each token's attention keys and values (the KV cache).
  3. **Decode:** generate one token per step, reading the whole KV cache each time; memory-bandwidth-heavy; sets time per output token.
  4. Repeat until a stop token or the limit.
- **Why it matters:** prefill and decode stress the GPU differently. Long prompts hurt first-token time; long outputs hurt total time.
- **Advanced:** some systems run prefill and decode on different GPU pools (disaggregated serving) so each can be tuned.
- 🗣 "Prefill is compute-bound and sets first-token time; decode is memory-bound and sets tokens per second."

---

## 2. The KV cache
`AI` ★★★

- **Plain idea:** the model's notes on everything it has read so far, kept in GPU memory so it doesn't reread.
- **Size per token** = 2 (keys and values) × layers × KV heads × head dimension × bytes per value.
- **Worked example (a Llama-3-8B-class model):** 32 layers, 8 KV heads (grouped-query attention), head dimension 128, 16-bit values.
  - 2 × 32 × 8 × 128 × 2 bytes ≈ 128 KB per token.
  - An 8k-token request ≈ 1 GB of KV cache.
  - Weights ≈ 8B × 2 bytes ≈ 16 GB.
  - On an 80 GB GPU: 80 − 16 − overhead leaves roughly 50–60 GB, so about 50–60 such requests at once.
- **Levers on KV size:** grouped-query attention (model design), 8-bit KV cache, shorter contexts, prefix sharing.
- **PagedAttention (vLLM):** stores the KV cache in fixed-size pages, like OS virtual memory, so memory isn't wasted on reserved space and pages can be shared between requests with the same prefix.
- **Prefix caching:** requests sharing a system prompt reuse its KV pages. The same idea as provider prompt caching ([2models.md](2models.md) §5).
- 🗣 "KV cache per token is two times layers times KV heads times head dim times bytes. That number sets my concurrency."

---

## 3. Batching and scheduling
`AI` ★★★

| Approach | How | Good at | Weak at |
|---|---|---|---|
| No batching | one request at a time | simple | GPU mostly idle |
| Static batching | wait for N requests, run together to the end | better throughput | short requests wait for long ones |
| Continuous batching | add and remove requests at every decode step | high throughput and good latency | scheduler complexity (engines handle it) |
| Chunked prefill | split long prompts into chunks mixed with decode steps | smooths latency spikes from long prompts | tuning |

- **Continuous batching is the default** in modern engines. It's the main reason they beat naive serving by large factors.
- **The trade-off knob:** a bigger batch gives more total tokens per second, but slower tokens for each user.
- 🗣 "Continuous batching swaps requests in and out every step, so the GPU stays full without making short requests wait."

---

## 4. Making it smaller and faster
`AI` ★★

| Technique | What it does | Gain | Cost |
|---|---|---|---|
| Quantization (8-bit, 4-bit; FP8, AWQ, GPTQ) | fewer bits per weight | less memory, often faster | some quality loss, more at 4-bit |
| KV cache quantization | fewer bits for the cache | more concurrent requests | small quality risk |
| Speculative decoding | a small draft model proposes tokens; the big model verifies several at once | faster decode | extra draft model; gains vary with acceptance rate |
| Tensor parallelism | split each layer across GPUs | fits big models; lower latency | GPU interconnect needed |
| Pipeline parallelism | split layers across GPUs or nodes | fits very big models | bubbles; latency |
| Distillation (high level) | train a small model to imitate a big one | cheaper serving | training pipeline |

- **Pick:** 8-bit weights first; 4-bit when memory is tight and evals still pass; speculative decoding when decode speed matters.

---

## 5. Serving engines compared
`software` ★★

| Option | What it is | Good at | Bad at | Choose when |
|---|---|---|---|---|
| vLLM | open-source engine with PagedAttention and continuous batching | wide model support, OpenAI-compatible API, big community | top-end tuning per hardware | default open-source choice |
| SGLang | open-source engine with strong prefix caching and structured generation | shared-prefix and agent workloads, structured output | smaller ecosystem than vLLM | many requests share prefixes |
| TensorRT-LLM | NVIDIA's optimized engine | highest performance on NVIDIA GPUs | build complexity, NVIDIA-only | squeezing max performance at scale |
| Hugging Face TGI | Hugging Face's server | easy with the Hugging Face stack | check current maintenance status | existing Hugging Face deployments |
| Managed endpoints (SageMaker, Vertex endpoints, Bedrock custom models) | cloud-hosted serving | less ops | less control, cost | team lacks GPU ops |
| Local runners (Ollama, llama.cpp) | single-machine serving | laptops, edge | not for multi-user scale | development, edge |

- **Default:** vLLM, unless prefix-heavy agent traffic favors SGLang or maximum NVIDIA performance justifies TensorRT-LLM.

---

## 6. Metrics and sizing
`software` ★★★

| Metric | Meaning | Driven by |
|---|---|---|
| Time to first token (TTFT) | wait before the first token | prefill, queueing |
| Time per output token (TPOT) or inter-token latency | speed of streaming | decode, batch size |
| Throughput | tokens per second per GPU or cluster | batching, quantization |
| Concurrency | requests in flight | KV cache memory |
| Goodput | requests meeting latency targets per second | all of the above |
| GPU utilization and memory | how full the hardware is | batch and cache |

- **Sizing method**
  1. Pick the model and precision; compute weight memory.
  2. Compute KV cache per request at your typical context length.
  3. Concurrency per GPU ≈ (GPU memory − weights − overhead) ÷ KV per request.
  4. Measure throughput at that concurrency with a load test.
  5. GPUs needed = peak tokens per second ÷ measured tokens per second per GPU, plus headroom.
- **Measure with your traffic shape.** Prompt and output lengths change everything.
- 🗣 "Weights plus KV per request gives concurrency; a load test gives tokens per second; peak demand divided by that gives GPUs."

---

## 7. Scaling a serving fleet
`software` ★★

- **Routing:** send requests with the same prefix to the same replica to reuse its KV cache (prefix-aware routing).
- **Autoscaling:** on queue depth and KV cache usage, not CPU. GPU nodes start slowly (model load takes time), so keep warm capacity.
- **Multiple models:** share GPUs across small models, or serve adapters (LoRA) on one base model.
- **Admission control:** reject or queue when KV memory is full instead of slowing everyone down.
- **Gateway in front:** routing, quotas, fallback to a provider API if the fleet is saturated ([1architecture.md](1architecture.md) §3.3).
- **Kubernetes tooling:** projects such as KServe and llm-d help run engines on Kubernetes; check maturity before adopting.

---

## 8. System design view: choosing
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Self-host at all | API vs self-host | data rules, steady volume, model control |
| Engine | vLLM, SGLang, TensorRT-LLM, managed | workload shape and team skills |
| Precision | 16-bit, 8-bit, 4-bit | memory vs eval quality |
| Parallelism | one GPU, tensor, pipeline | model size vs GPU memory |
| Latency vs throughput | small vs large batches | product latency targets |
| Scaling signal | queue depth, KV usage | not CPU |

- **Default:** vLLM with 8-bit weights on one GPU per replica if the model fits, continuous batching and prefix caching on, prefix-aware routing, autoscale on queue depth with warm spares, a gateway with provider fallback.

---

## 9. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Out of KV memory | long contexts or high concurrency | preemptions, latency spikes | admission control; shorter contexts; KV quantization |
| TTFT spikes | long prompts block decode | first-token latency tail | chunked prefill; separate pools |
| Slow scale-up | cold GPU nodes, model load time | queue grows during spikes | warm capacity; faster model loading |
| Quality drop after quantization | too aggressive precision | eval regression | 8-bit; re-evaluate |
| Cache misses across replicas | random routing | low prefix hit rate | prefix-aware routing |
| Low utilization | small batches | GPU idle with queue empty | right-size fleet; batch offline work |

---

## Where this fits
- **Place:** L2 of [1a-bp.md](../1a-bp.md) (model layer), "after the gate" serving. Most useful for AI-infra roles.
- **Time it deserves:** 25 minutes; §1, §2 and §6.
- **I should be able to…**
  - Explain prefill vs decode and which metric each drives.
  - Compute KV cache per token and estimate concurrency per GPU.
  - Explain continuous batching and PagedAttention.
  - Pick an engine and size a fleet from traffic numbers.

## References
1. [vLLM — PagedAttention paper (Kwon et al., 2023)](https://arxiv.org/abs/2309.06180) — KV cache paging.
2. [vLLM docs](https://docs.vllm.ai/) — engine features.
3. [SGLang](https://github.com/sgl-project/sglang) — prefix caching, structured generation.
4. [NVIDIA TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) — optimized NVIDIA serving.
5. [Speculative decoding (Leviathan et al., 2023)](https://arxiv.org/abs/2211.17192) — draft and verify.
