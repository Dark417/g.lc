# OCI Coding Questions — Reported Sources & Frequency (2026)

> Scope: Oracle / OCI coding-round reports from Jan 2026 back to Sep 2025 (same loop). Target: Senior Platform SWE, IC4, req 338588, Round 1 = live HackerRank.
> Pulled 2026-08-30. Frequency by _named problem_ is thin everywhere; the real signal is by _pattern_ (§3).

## Index

1. [Where Oracle coding questions get reported](#1-where-oracle-coding-questions-get-reported)
2. [Named problems reported](#2-named-problems-reported)
   - 2.1 1point3acres — 2026 reports
   - 2.2 1point3acres — OJ problem list (free)
   - 2.3 LeetCode Discuss — Sep–Dec 2025
   - 2.4 Blind / Glassdoor — format signals
3. [Pattern frequency](#3-pattern-frequency)
4. [Round 1 protocol adjustments](#4-round-1-protocol-adjustments)
5. [Drill list to merge](#5-drill-list-to-merge)
6. [References](#6-references)

---

## 1. Where Oracle coding questions get reported

```
1p3a (paywalled, 416 reports, bank of 100 tagged Qs)  ← primary
   └─ LeetCode Discuss → codingkaro aggregate (free, India-OCI skew)  ← secondary
        └─ Blind / Glassdoor (format + leveling signals only)
             └─ SEO guides (DesignGurus / OphyAI / linkjob)  ← skip
```

| Source                                       | Coverage                                                                    | Access       | Value                                                                                                                               |
| -------------------------------------------- | --------------------------------------------------------------------------- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| **1point3acres** `/interview/company/Oracle` | 416 Oracle reports (21 pages); structured bank of 100 Qs, updated 2026/8/29 | Membership   | **Buy before Round 1.** Two posts match your req exactly: "IC4 \| Seattle" (2026/8/28), "IC4 Full Interview Experience" (2026/8/11) |
| **LeetCode Discuss** → codingkaro.in         | 73 experiences, 496 Qs                                                      | Free         | Best free list of _named_ problems; newest are late-2025                                                                            |
| **Blind** Oracle interview page              | Loop mechanics, leveling, downlevel pattern                                 | Free (login) | Round format, not problems                                                                                                          |
| **Glassdoor**                                | Generic                                                                     | Free         | Low signal                                                                                                                          |
| DesignGurus / OphyAI / linkjob "2026" guides | SEO aggregators                                                             | Free         | Skip — linkjob page is a cheating-tool ad dated Sep 2025                                                                            |

- 1p3a's own framing of Oracle loops
  → OCI: standard LC + system-design loop
  → OHAI (Oracle Health): OOD/class-design around healthcare scenarios
  → Coding bar mostly easy–medium; interviewer variance and post-loop down-level / ghosting unusually common
  ◆ 🗣 "The loop result often determines the eventual level, not just yes/no" — treat every round as a leveling round

---

## 2. Named problems reported

### 2.1 1point3acres — 2026 OCI/SWE reports

```
[Aug 2026] OCI IC4 phone screen (30 min) ── Set Matrix Zeros ──┬─ follow-up: ragged input
                                                                └─ follow-up: char[][] + arbitrary marker
```

| Date          | Round                            | Problem / tags                                                                                             | Notes                                                                                                                                      |
| ------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Aug 2026      | **OCI IC4 phone screen, 30 min** | Set Matrix Zeros (in-place)                                                                                | Free-preview item. Follow-ups: ragged (non-rectangular) input; generalise to `char[][]` with arbitrary marker. Closest match to your round |
| 2026/7/31     | Tech phone screen                | REST API — Medical Records by Age                                                                          | Tags: api-integration / http / json / ambiguous-spec. "Consume an API, aggregate" — not pure DSA                                           |
| 2026/7/17     | Tech phone screen                | PriorityQueue-based problem                                                                                | Heap                                                                                                                                       |
| 2026/3/10     | Senior SWE phone                 | Throttling Design                                                                                          | Rate limiter. 2 reports, last asked 2026-08-19                                                                                             |
| 2026 (locked) | 45 min                           | hashmap + linked-list + **TTL**                                                                            | Expiring KV / TTL cache                                                                                                                    |
| 2026 (locked) | 45–60 min                        | in-memory-database mini-project; concurrency design mini-project                                           | Build-a-component rounds                                                                                                                   |
| 2026 (locked) | 45 min                           | trie + dfs + string                                                                                        | Autocomplete-style                                                                                                                         |
| 2026 (locked) | 45 min                           | heap + linked-list + merge + top-k                                                                         | Merge-K / top-K                                                                                                                            |
| 2026 (locked) | 20–45 min                        | graph + topological-sort (×2 reports)                                                                      | Dependency ordering                                                                                                                        |
| 2026 (locked) | 45 min                           | string + stack + recursion + compression (×2)                                                              | Encode/decode string                                                                                                                       |
| 2026 (locked) | 45 min                           | string + parsing + state-machine (×2)                                                                      | Tokenizer / log parser                                                                                                                     |
| 2026 (locked) | 30 min                           | array + binary-search (easy); array + two-pointer + greedy (medium, ×2); string + sliding-window + hashing | Standard mediums                                                                                                                           |
| 2026 (locked) | 45 min                           | oop-design: filesystem; scheduling; ambiguous-spec                                                         | OOD — more OHAI than OCI                                                                                                                   |

### 2.2 1point3acres — OJ problem list (company-tagged, free)

- Data-structure design
  → Time-Based Key-Value Store; Simplified Time-Based KV Store; Implement LRU Cache; Dropped Requests Rate Limiter; Implement a Queue Using Two Stacks
- Heap / top-K
  → Top K Frequent Elements with Descending Value Tie-Break
- Graph / topo
  → Deploy Packages in Dependency Order; Accounts Merge; Maximum Height of Each Island; Enumerate All Valid Grid Paths
- String
  → Run-Length String Compression; Lexicographically Maximum Substring; Validate Parentheses String; Partition a String into Exactly Three Palindromic Substrings
- Array
  → Best Time to Buy and Sell Stock (×2 variants); Remove Duplicates from Sorted Array with At Most K Occurrences; Partition Unique Cards into Consecutive Groups; Missing Number; Add One to Digits Without ArrayList; Swap Two Variables Without Temp
- Tree
  → Bottom View of a Binary Tree; Compare Two N-ary Trees for Equality
- DP
  → Maximum Movie Rating with No Two Consecutive Skips (house-robber-style)
- Misc
  → Integer Square Root; Generate All Permutations; First Unique Login User; Find Users with Valid Session; Medical Records By Age; Remove Even-Positioned Nodes from Linked List

### 2.3 LeetCode Discuss — OCI-tagged, Sep–Dec 2025 (same loop)

| Date     | Level / round              | Problems                                                                                | Notes                                                                                                  |
| -------- | -------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Dec 2025 | **IC4 tech screen**        | Server Scheduler Design; Course Scheduler with Multiple Servers + Dependencies          | Candidate: "more system design heavy than DSA" — SD-flavored coding at IC4                             |
| Dec 2025 | IC4 (Oracle Health) screen | Maximum Product of Three Numbers; Search in Rotated Sorted Array                        | Plus OOPs, string immutability, serialization, synchronization                                         |
| Nov 2025 | SMTS OCI screening         | Merge K Sorted Lists; Prefix→Postfix; Thread-Safe LRU                                   | Screen also: Spark vs Flink, stateless REST                                                            |
| Nov 2025 | SMTS screening             | 1 LC-medium PriorityQueue Q + Java/Spring Boot Qs; loop: Binary Tree Maximum Path Sum   |                                                                                                        |
| Nov 2025 | 5-round loop               | 2 mediums (arrays / hashmap / sliding window); Design LRU Cache; Implement Custom Stack |                                                                                                        |
| Sep 2025 | **OCI IC3 pre-screen**     | Top K Most Expensive Stocks in Last T Minutes from Stream                               | K varies per call; same stock re-arriving invalidates old price                                        |
| Sep 2025 | PMTS screen                | Kth Largest Element in BST                                                              |                                                                                                        |
| Earlier  | OCI SMTS (IC3)             | Screen: 1 hard + project deep-dive                                                      | All in HackerRank, working code required; asked edge cases + test cases + complexity on nearly every Q |
| Earlier  | OCI networking IC2         | Merge-interval pattern (screen); stock buy/sell (loop)                                  |                                                                                                        |

### 2.4 Blind / Glassdoor 2026 — format signals

- Phone screen HackerRank **enforced Java** (principal MTS candidate) → confirms Java default
- IC4 OCI object storage: "easy interview, all answers" → still rejected → interviewer variance real
- Recent Senior SWE screen: heavy on AI agents + past projects, little traditional coding → resume AI bullets will be probed (agent eval under non-deterministic outputs)
- Glassdoor Jul 2026: gateway with Principal via HackerRank → loop of 3 (LC-style + design); design prompt seen: large-scale data ingestion platform

---

## 3. Pattern frequency

```
DS-design ████████  8+
heap/topK ██████    6
string    ██████    6
array     █████     5
topo      ████      4
tree      ████      4
matrix    ███       3
bsearch   ██        2
DP        ██        2
API-agg   █–██      1–2
```

- Order-of-magnitude count across named reports in §2 (2026 + late 2025) — **not a sourced stat**
  → 1p3a's own tags: only BQ = "very high", CS-fundamentals verbal = "high"; every coding item is 1–2 reports
  → Defeater: skew toward India-OCI screens on LeetCode Discuss; US IC4 bodies are paywalled

| Pattern                                                                                                           | ~Reports | Canonical drills                                                                                      |
| ----------------------------------------------------------------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------- |
| **Design-a-data-structure** (LRU, TTL/time-based KV, rate limiter, in-memory DB, custom stack, queue-from-stacks) | 8+       | LC 146, 981, 359, 362; thread-safe LRU in Java                                                        |
| **Heap / top-K / merge-K / PQ**                                                                                   | 6        | LC 23, 347 (+tie-break), 215; streaming top-K with expiry                                             |
| **String parse / compress / stack**                                                                               | 6        | LC 443, 394, 20, 150 / prefix→postfix; log-line tokenizer                                             |
| **Array two-pointer / greedy / sliding window**                                                                   | 5        | LC 121, 80, 3, 56                                                                                     |
| **Topo sort / dependency scheduling**                                                                             | 4        | LC 207/210, 1136; deploy-packages + multi-server variant                                              |
| **Tree / BST**                                                                                                    | 4        | LC 230 (kth largest), 124, bottom view, N-ary equality                                                |
| **Matrix / grid**                                                                                                 | 3        | LC 73 (+ragged/marker), grid paths, island height                                                     |
| **Binary search**                                                                                                 | 2        | LC 33, 69                                                                                             |
| **DP**                                                                                                            | 2        | movie-rating (house-robber), 3-palindrome partition — low for Oracle; don't overweight vs Google prep |
| **API-consume-and-aggregate**                                                                                     | 1–2      | Medical Records by Age (HackerRank REST API template)                                                 |

---

## 4. Round 1 protocol adjustments

```
intro (5) → 1 problem (~30) → tests/edge cases (5) → project deep-dive (15) → Qs (5)
                 └─ IC4 variant: scheduler-design problem instead of pure DSA
```

- Expect one problem, ~30 min, **working code** in HackerRank
  → Then "what tests would you write / edge cases" — prepare the test-oracle answer out loud
  → Then project deep-dive; AI bullets likely probed (agent eval, non-deterministic outputs)
- IC4 screens sometimes swap DSA for a scheduler-design problem
  → Keep job-scheduler SD file warm; be able to code the topo-sort core in Java in 15 min
- Follow-up style: generalise the same problem (ragged input, arbitrary marker, varying K, invalidation)
  → Write the first solution with the generalisation seam already visible (parameterise marker, don't hardcode `0`)
- Java default; if HackerRank locks language, it will be Java

---

## 5. Drill list to merge

- Add to 30-problem set now
  → LC 73 with both follow-ups (ragged, marker)
  → Streaming top-K in time window with invalidation (Java: `TreeMap` + `HashMap` or PQ + lazy deletion)
  → TTL KV store (get/set/expire; lazy vs scheduled eviction)
  → Prefix→Postfix (stack)
  → Deploy packages in dependency order → multi-server variant (Kahn's + PQ)
  → Thread-safe LRU (`ReentrantLock` vs `synchronized`; `LinkedHashMap` accessOrder)
- One-time, 20 min
  → HackerRank "REST API" problem template (paginated GET, aggregate, return)
- Buy 1p3a membership; read 8/28 IC4 Seattle + 8/11 IC4 Full posts; append findings to §2.1

---

## 6. References

1. 1point3acres Oracle question bank — https://www.1point3acres.com/interview/problems/company/Oracle
2. 1point3acres Oracle reports — https://www.1point3acres.com/interview/company/Oracle
3. LeetCode Discuss aggregate (codingkaro) — https://www.codingkaro.in/jobs-internships/leetcode-interview-experience/Oracle
4. Blind Oracle interview page — https://www.teamblind.com/company/Oracle/posts/oracle-interview
5. LeetCode OCI IC3 experience — https://leetcode.com/discuss/interview-experience/5986069/
