# customization Interview Questions

> L4 answers plus L5 extras for model customization, then L5-only design questions.

## Index

- [1. Core Questions](#1-core-questions)
  - [Q1 Fine-Tuning vs RAG vs Prompting](#q1-fine-tuning-vs-rag-vs-prompting)
  - [Q2 LoRA](#q2-lora)
  - [Q3 Serving A Fine-Tuned Model](#q3-serving-a-fine-tuned-model)
  - [Q4 Hyperparameters](#q4-hyperparameters)
  - [Q5 A Good Dataset](#q5-a-good-dataset)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [Q6 Slow, Expensive RAG Assistant](#q6-slow-expensive-rag-assistant)

Back to [00index](customization.00index.md).

---

## 1. Core Questions

These map to [02 types](customization.02types.md) through [06 serving](customization.06serving.md).

### Q1 Fine-Tuning vs RAG vs Prompting

**Q:** Fine-tuning vs Retrieval-Augmented Generation (RAG) vs prompt engineering: how do you choose?

**L4 answer**

- Prompting first: cheapest, fastest
- RAG when the model lacks or needs fresh knowledge
- Fine-tuning when behavior (style, format) must be consistent
  - And prompting is not enough

**L5 extra**

- Deciding variable: knowledge gap vs behavior gap
- Fine-tuning has a serving cost (provisioned throughput)
  - It only pays off at volume
- They combine: a fine-tuned model can still use RAG

### Q2 LoRA

**Q:** What is Low-Rank Adaptation (LoRA) and why is it cheaper?

**L4 answer**

- Freeze the base model, train small low-rank adapter matrices
- Far fewer trainable parameters

**L5 extra**

- Less Graphics Processing Unit (GPU) memory and smaller artifacts (Megabytes (MB))
- Many adapters share one base at serving
- Quality is close to full fine-tuning for many tasks, not all
- On Bedrock the technique is managed
  - You control data and hyperparameters

### Q3 Serving A Fine-Tuned Model

**Q:** How do you serve a fine-tuned Bedrock model?

**L4 answer**

- Buy provisioned throughput and call its Amazon Resource Name (ARN) with Converse

**L5 extra**

- Some models support on-demand deployment of custom models (check support)
- No-commitment Provisioned Throughput (PT) for testing; delete it after
- Tag and alarm: PT bills hourly whether used or not

### Q4 Hyperparameters

**Q:** What do `epochCount`, `batchSize`, and `learningRate` do?

**L4 answer**

- Epochs = passes over data
- Batch = examples per update
- Learning rate = step size

**L5 extra**

- Watch train vs validation loss to detect overfitting
- Tune epochs first; learning rate when loss is unstable
- Ranges and defaults differ per base model

### Q5 A Good Dataset

**Q:** What does a good fine-tuning dataset look like?

**L4 answer**

- JavaScript Object Notation (JSON) Lines (JSONL) in the base model's format
- Clean and representative
- With a validation split

**L5 extra**

- Outputs are the exact target, including refusals and edge cases
- Deduplicated, Personally Identifiable Information (PII)-free, versioned in Simple Storage Service (S3), encrypted
- Hundreds to thousands of examples for a narrow task (order of magnitude)

## 2. L5-Only Questions

Depth and design ownership beyond the L4 baseline.

### Q6 Slow, Expensive RAG Assistant

**Q:** Your RAG assistant is accurate but slow and expensive on a large model. Options?

**L5 answer**

- Measure where time goes
  - retrieval
  - long context
  - generation
- Cheaper first
  - prompt caching
  - shorter context
  - smaller model with better prompts
- Distill the large model's answers into a smaller one
  - Use invocation logs as prompts
- Serve the student via provisioned throughput
  - Only if volume keeps utilization high
- Trade-off: lower per-call cost vs
  - training effort
  - PT commitment
  - retraining on base-model updates
