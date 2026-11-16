# comprehend Interview

> Interview questions on Amazon Comprehend, with Level 4 (L4) answers and Level 5 (L5) extras.

## Index

- [1. Core Questions](#1-core-questions)
  - [Q1 Comprehend Vs Large Language Model (LLM)](#q1-comprehend-vs-large-language-model-llm)
  - [Q2 Processing 1M Documents](#q2-processing-1m-documents)
  - [Q3 ErrorList](#q3-errorlist)
  - [Q4 Comprehend Lambda Bedrock Pattern](#q4-comprehend-lambda-bedrock-pattern)
  - [Q5 Comprehend Medical](#q5-comprehend-medical)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [Q6 Ticket Triage At 5M A Day](#q6-ticket-triage-at-5m-a-day)
  - [Q7 Training A Custom Classifier](#q7-training-a-custom-classifier)

## 1. Core Questions

Each answer gives the L4 baseline, then what L5 adds.

### Q1 Comprehend Vs Large Language Model (LLM)

**Q:** When Comprehend and when an LLM?

**L4 answer**

- Comprehend for fixed, high-volume tasks that need determinism and low cost
- LLM for open-ended or changing tasks

**L5 extra**

- Compare cost per 1k docs and p99 latency on your data
- Accuracy on domain language decides
  - Benchmark both on a golden set

### Q2 Processing 1M Documents

**Q:** How do you process 1M documents?

**L4 answer**

- Async jobs reading Simple Storage Service (S3)
- Or batches of 25 in parallel with retries

**L5 extra**

- Jobs for offline; batch Application Programming Interfaces (APIs) for near-real-time
- Track failed indexes, throttling and cost per document

### Q3 ErrorList

**Q:** What is `ErrorList`?

**L4 answer**

- Per-item failures in batch calls with the item `Index`

**L5 extra**

- The Hypertext Transfer Protocol (HTTP) call succeeds while items fail
  - So retry per item, idempotently

### Q4 Comprehend Lambda Bedrock Pattern

**Q:** Explain the Comprehend + Lambda + Bedrock pattern.

**L4 answer**

- Analyze text first
- Route on the result to a prompt and a model

**L5 extra**

- Saves cost by sending easy cases to a small model
- Risk: misrouting; sample and measure

### Q5 Comprehend Medical

**Q:** What does Comprehend Medical add?

**L4 answer**

- Clinical entities
- Code linking (International Classification of Diseases, 10th Revision, Clinical Modification (ICD-10-CM) etc.)
- Protected Health Information (PHI) detection

**L5 extra**

- Scores per code
- Human review for coding decisions
- Health Insurance Portability and Accountability Act (HIPAA) scope

## 2. L5-Only Questions

These test design ownership and scale.

### Q6 Ticket Triage At 5M A Day

**Q:** Design triage of support tickets at 5M/day.

**L5 answer**

→ Stream → Comprehend language + sentiment (batch) → rules route to LLM tiers  
→ Urgent negative → strong model + human queue  
→ The rest → fast model or templates

- Metrics
  - Routing mix
  - Cost per ticket
  - Escalation rate
- Shadow-evaluate routing weekly

### Q7 Training A Custom Classifier

**Q:** Should you train a custom classifier?

**L5 answer**

- Only with stable labels, volume, and labeled data
- Compare endpoint hours vs per-token LLM cost at your volume
- Start with an LLM labeler to produce the training set, then distill
