---
name: ask-sd-question
description: Generate system design interview questions grouped by topic and calibrated by Google L4/L5 level and difficulty.
---

# ask-sd-question

1. Read `1sd/build.md` and `1sd/1index.md` before adding questions.
2. Confirm target level, role, and domain.
3. Reuse the canonical `1AX/` packet when Alex Xu already covers the prompt; do not add a duplicate elsewhere.
4. Produce ordered sets from fundamentals to advanced.
5. For each question include a bounded interviewer prompt, clarification directions, core primitives, and follow-up pressure points.
6. Label with `[4E] [4M] [4H] [5E] [5M] [5H]`.
7. Prefer classic, high-frequency interview problems first and update `1sd/1index.md` for every file change.
8. For an existing role-specific bank, use its local index and evidence. If the user requests only ranked questions, omit answers and follow-up expansions; for Oracle use `1infra`, `1infra-pki` (certificates/keys/trust), `1infra+` (general platform), and `2business`, in that order, descending within each group by role fit and infrastructure relevance. Keep roughly 10–15 supplements across the PKI and general platform groups. Preserve the table columns `# | Prompt | Evidence | Type | Priority`, including P0/P1/P2 and source evidence.
