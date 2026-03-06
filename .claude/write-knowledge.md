# write-knowledge skill

Use this skill when asked to write or expand a knowledge file in `sde/` or a similar crash-course reference.

## What "knowledge" means here

A knowledge file is a self-contained crash course on one system design topic. The reader is a software engineer preparing for senior-level (L4/L5) system design interviews. They may already know the basics but need:
- The right vocabulary and mental model
- The canonical patterns and when to apply them
- The tradeoffs between competing approaches — not just which to pick, but why
- The most popular frameworks/tools, with enough detail to discuss them fluently
- The common interview mistakes to avoid

The file must be interview-ready: someone could read it the night before an interview and be prepared to discuss the topic in depth.

---

## Structure of a knowledge file

Follow this template exactly. Do not omit sections.

```markdown
# <Topic Name>

## Index
- Core concepts
- <Section 2>
- <Section 3>
- ...
- Popular frameworks
- Interview pitfalls

---

## Core Concepts

**<Concept name>:** One-sentence definition. Then explain the problem it solves, and the intuition behind it.

**<Concept name>:** ...

(Continue for 3-6 core concepts. These are the vocabulary and mental models the reader needs first.)

---

## <Thematic Section — e.g., "Read/Write Patterns" or "Scaling Strategies">

**<Pattern name>:**
```
<code block or diagram illustrating the pattern>
```

**Pros:** ...
**Cons:** ...
**Use when:** ...

(Repeat for 3-5 patterns. Show tradeoffs between them, not just their descriptions.)

---

## <Another Thematic Section>

...

---

## Popular Frameworks

**<Framework name> (<language/type>):**
- **What it is:** One-sentence description
- **When to use:** The specific problem or constraint that points to this tool
- **How it works:** Key internals or design decisions that matter (not just marketing copy)
- **Key config / gotchas:** The 1-2 things that trip people up in practice
- **Clients:** Common client libraries (languages)

(Repeat for 4-8 frameworks. Cover the major ecosystem players. Don't save ink — give real detail.)

---

## Interview Pitfalls

- **"<Bad pattern>"** — what's wrong with it and what to say instead
- **Not mentioning <X>** — when X is commonly overlooked and why it matters
- ...

(5-8 pitfalls. Make them specific and actionable — not generic advice.)
```

---

## Rules for writing knowledge files

### Depth and coverage
- Cover the topic as if preparing someone to answer any follow-up question an interviewer might ask
- Include the non-obvious details: the failure modes, the edge cases, the "why not the simpler approach"
- Use concrete numbers and examples, not just abstract descriptions
- If a concept has a formula (e.g., Little's Law), include it with an example

### Tone and style
- Write in the second person where it helps clarity ("Use this when...")
- No filler — every sentence should add information or contrast
- Use code blocks for: algorithms, config, API shapes, pseudocode, data formats
- Use tables for: comparison of options, isolation levels, feature matrices
- Use bullet lists for: lists of trade-offs, characteristics, steps

### Frameworks section
- Include at least 4 real tools with genuine detail (not just "Redis is fast")
- For each framework: when to use it, how it works, what makes it unique, real config or client libraries
- Don't invent fake characteristics — only write what is true and verifiable

### Tradeoffs
- Every pattern section must have explicit tradeoffs (pros, cons, when-to-use)
- The best knowledge files compare 2-3 approaches head-to-head
- Don't just list options — explain the decision criteria

### Interview pitfalls
- Each pitfall should describe the mistake and the correct behavior
- Phrase them as things a candidate actually says or does wrong, not abstract warnings
- Include pitfalls about both over-engineering and under-engineering

---

## Quality checklist

Before finishing a knowledge file, verify:

- [ ] Core concepts section defines the vocabulary needed to understand everything else
- [ ] Each pattern/approach has explicit tradeoffs (not just "it depends")
- [ ] At least 4 frameworks with real detail (not just names)
- [ ] Interview pitfalls are specific and actionable
- [ ] Code blocks are used for any non-trivial algorithm or data shape
- [ ] Numbers appear throughout (latency, throughput, storage) not just prose
- [ ] Reading order makes sense: concepts before patterns before frameworks
- [ ] No section is a list of names without explanation

---

## Example of a good vs bad entry

**Bad (too shallow):**
```
**Redis:** Fast in-memory key-value store. Use for caching.
```

**Good (interview-ready):**
```
**Redis:**
- **What it is:** In-memory data structure store. Strings, hashes, lists, sets, sorted sets, streams, and more.
- **When to use:** Shared cache across multiple app servers; rate limiting counters; pub/sub; leaderboards (sorted sets); distributed locks (SETNX + TTL).
- **How it works:** Single-threaded event loop (I/O threads added in Redis 6+). All operations are atomic. Data is persisted via RDB snapshots or AOF append log (or both).
- **Key config:**
  - `maxmemory-policy allkeys-lru` — evict LRU keys when memory is full
  - `appendonly yes` + `appendfsync everysec` — AOF with 1s durability window
  - `save 900 1` — RDB snapshot if at least 1 write in last 15 minutes
- **Sentinel vs Cluster:**
  - Sentinel: HA for a single shard (leader election on failure). Max data = one server's RAM.
  - Cluster: 16384 hash slots distributed across N masters. Horizontal scale. Each key maps to one slot via CRC16.
- **Clients:** redis-py (Python), ioredis (Node.js), Lettuce / Redisson (Java)
```
