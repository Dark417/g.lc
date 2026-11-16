# customization Low-Rank Adaptation (LoRA) In Brief

> Why low-rank adapters make fine-tuning cheap, and how much of that Bedrock exposes.

## Index

- [1. Full Fine-Tuning Cost](#1-full-fine-tuning-cost)
- [2. LoRA Mechanism](#2-lora-mechanism)
- [3. On Bedrock](#3-on-bedrock)

Back to [00index](customization.00index.md).

---

## 1. Full Fine-Tuning Cost

Updating every weight copies the whole model per task.

- Full fine-tuning updates every weight

⇒ a full copy of the model per task  
⇒ expensive to train and to store

## 2. LoRA Mechanism

Low-Rank Adaptation (LoRA) learns a small low-rank correction instead of new weights.

- **LoRA** (low-rank adaptation)
  - Freezes the base weights
  - Learns two small matrices per layer
  - Their product (rank r, e.g. 8–64) approximates the weight update
- Effects
  - Trainable parameters drop by orders of magnitude
    - Order of magnitude: under 1% of the model
  - Training needs less Graphics Processing Unit (GPU) memory
  - Adapters are megabytes, not gigabytes
  - Many adapters can share one base model at serving time

```python
# illustrative: no repo code for LoRA; Bedrock manages the technique
import numpy as np

d, r = 4096, 16                       # layer width, adapter rank
W = np.random.randn(d, d)             # frozen base weight: d*d = 16.7M params
A = np.random.randn(r, d) * 0.01      # trainable, r*d
B = np.zeros((d, r))                  # trainable, d*r; zero init => no change at step 0
W_eff = W + B @ A                     # effective weight; only A and B are trained
print((A.size + B.size) / W.size)     # ~0.008 => under 1% of this layer
```

- Catch: quality is close to full fine-tuning for many tasks, not all.

## 3. On Bedrock

- Bedrock does not expose the method as a knob
  - The service picks the technique per model
  - You control data and hyperparameters
- Self-managed LoRA → SageMaker or open-source (Parameter-Efficient Fine-Tuning (PEFT))
- Custom Model Import brings weights into Bedrock
  - See [06 serving](customization.06serving.md)
