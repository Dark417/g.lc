---
name: write-knowledge
description: Write or expand a system design knowledge file in sde/. Use when asked to add, expand, or improve a knowledge topic for interview preparation. Produces a comprehensive crash-course covering core concepts, patterns, tradeoffs, frameworks, and interview pitfalls.
---

# write-knowledge

Write a comprehensive knowledge file for the system design topic: **$ARGUMENTS**

The target audience is a software engineer preparing for senior-level (G4/G5) system design interviews. They know the basics — give them depth, tradeoffs, and the details that matter under interview pressure.

---

## Structure to follow

Use this exact structure. Do not omit sections.

```
# <Topic Name>

## Index
- Core concepts
- <thematic section 2>
- <thematic section 3>
- ...
- Popular frameworks
- Interview pitfalls

---

## Core Concepts
[3–6 concepts that define the vocabulary and mental model for this topic]

---

## <Thematic Section — e.g., "Read/Write Patterns", "Scaling Strategies", "Algorithm Choices">
[3–5 patterns/approaches with explicit pros, cons, and when-to-use for each]

---

## Popular Frameworks
[4–8 real tools with: what it is, when to use, how it works, key config/gotchas, clients]

---

## Interview Pitfalls
[5–8 specific, actionable pitfalls — describe the mistake and what to say instead]
```

---

## Rules

### Depth
- Cover the topic as if preparing someone to answer any follow-up an interviewer might ask
- Include non-obvious details: failure modes, edge cases, "why not the simpler approach"
- Use concrete numbers (latency, throughput, storage sizes) not just prose
- If a concept has a formula (e.g., Little's Law, Amdahl's Law), include it with a worked example

### Style
- No filler — every sentence adds information or contrast
- Code blocks for: algorithms, config, API shapes, pseudocode, data formats
- Tables for: comparison of options, feature matrices, isolation levels
- Bullet lists for: tradeoffs, characteristics, steps

### Tradeoffs
- Every approach must have explicit pros, cons, and when-to-use
- Compare 2–3 approaches head-to-head where possible
- Explain the decision criteria, not just the options

### Frameworks section
- Minimum 4 real tools with genuine detail (not just names)
- For each: when to use, how it works internally, what makes it unique, real config or client libraries
- Only include verifiable characteristics

### Interview pitfalls
- Describe the actual mistake (what a candidate says or does wrong)
- Explain what to say instead
- Cover both over-engineering and under-engineering pitfalls

---

## Quality checklist

Before finishing, verify:

- [ ] Core concepts define vocabulary needed to understand everything else
- [ ] Each approach has explicit tradeoffs (not "it depends")
- [ ] At least 4 frameworks with real detail
- [ ] Interview pitfalls are specific and actionable
- [ ] Code blocks for any non-trivial algorithm or data shape
- [ ] Numbers appear throughout — not just prose
- [ ] Reading order: concepts → patterns → frameworks
- [ ] No section is a bare list of names without explanation

---

## Example: good vs bad framework entry

**Bad:**
```
Redis: Fast in-memory key-value store. Use for caching.
```

**Good:**
```
**Redis (in-memory data structure store):**
- **What it is:** Strings, hashes, lists, sets, sorted sets, streams, and more. Single-threaded event loop.
- **When to use:** Shared cache across app servers; rate limiting counters; leaderboards (sorted sets); distributed locks (SETNX + TTL); pub/sub.
- **How it works:** All operations atomic. Data persisted via RDB snapshots or AOF append log. Redis Cluster: 16384 hash slots distributed across N primaries via CRC16.
- **Key config:** `maxmemory-policy allkeys-lru`, `appendonly yes` + `appendfsync everysec`
- **Clients:** redis-py (Python), ioredis (Node.js), Lettuce/Redisson (Java)
```
