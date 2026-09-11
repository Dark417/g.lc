# AGENTS — 26U

Directory-scoped rules for `26U/` (interview prep).  
Root `AGENTS.md` still applies (LeetCode formats, logs, push behavior).

## Formatting-only passes

- When asked to change only line breaks, limit study-note edits to whitespace outside code.
  - Preserve fenced and unfenced code exactly.
  - Separate existing index titles, descriptions, and tags without inventing missing content.
  - Preserve wording, links, anchors, question order, and practice-log counts.
  - A request for root Markdown files covers direct children of `26U/` only.

## System design rules (`1o/2.sd/` and any future SD folder)

### Sources of truth

- The JD and recruiter docs live in `1o/0.req/`; `1o/0.req/0.req.md` is the 3-in-1 Markdown consolidation and the file to read first.
  - `Senior Platform Software Engineer - OCI - Oracle Careers.pdf` = JD for req 338592, PKI team.
  - `oracle interview.pdf` = recruiter process, loop shape, and coding scoring.
  - `OCI Interview Prep Pack - Technical_02052024.pdf` = official prep guidance and the ten core values.  
  Every SD file should tie its framing back to them where relevant (a `> JD tie-in:` line in the header quote).
- `2.sd.md` is the question bank + coverage map; full designs live in their own files.
- For Oracle question-ranking requests, use `1infra` (collected infrastructure), `1infra-pki` (certificate, key, and trust questions), `1infra+` (general platform supplements), and `2business` (collected business), in that order, each descending by role relevance and infrastructure depth.  
  Keep supplemental questions bounded at roughly 10–15 across the two supplement groups.  
  Keep the existing table style: `# | Prompt | Evidence | Type | Priority`, including P0/P1/P2 and source evidence.  
  Distinguish report evidence from preparation suggestions and do not generate full answers unless asked.

### File naming

- One full design per file: `sd##.problem-name.md` (two digits, no dot after `sd`, kebab-case problem name), e.g. `sd11.kv-store.md`.
- Number = priority order from the `2.sd.md` question bank, not creation order.

### Full-design template (follow `sd10.job-scheduler.md`)

- Sections §0–§17: time budget · why hard (naive → what breaks → minimum primitive) · crux · clarifying questions (with assumed answers) · FR / NFR (table with targets + "enforced by") · back-of-envelope (end each with "so what") · HLD (ASCII diagram with `[hot path]` / `[async]` / `[control plane]` tags + walkthroughs) · API · data model · 3–4 deep dives · hygiene checklist · ops readiness · pop-up questions · trade-offs + defeaters · wrap-up script · memorization card · references.
- `❓` marks a likely follow-up with the answer to give; `🗣` marks a line to say aloud verbatim; `**L5:**` marks senior-level extensions.
- Shorter segment-style topics (lock manager, warm-up designs) may compress to §0–§14 but keep crux, code, schema, defeaters, and card.

### Example code — mandatory

- Every full design includes runnable example code for its **key function(s)** — the 1–2 mechanisms an interviewer asks you to write (claim/lease, token bucket, LRU node surgery, ring lookup, idempotent submit, rotation tick).
- Show **Python first, then Java, together** (adjacent blocks, same mechanism), like the LRU cache treatment in `sd03` — Python for whiteboard speed, Java because it matches the JD.
- End code blocks with a `# Time/Space` or trailing comment stating the complexity or the one caveat that matters.

### Schema code — mandatory when data is designed

- If the design has a DB/entity model, write actual `CREATE TABLE` DDL (or the KV/logical record layout) in §9 — keys, state columns, the indexes that serve the hot queries, and comments for state machines.  
  No prose-only schemas.
- Redis/queue key layouts count as schema: show the exact key format and TTL.

### Drafts

- Bank questions without a full `sd##` file get a **draft** in `2.sd.md` (§ Drafts): crux in one line, HLD one-liner, data/API hint, key code pointer (which `sd##` mechanism it reuses), one defeater.  
  Promote a draft to a full file when its priority rises.

## OCI architecture file

- `1o/4.1o-arch.md` is the "sound native in the OCI interview" file: OCI concepts always paired with the AWS analogy (user's real experience is AWS at JPMC) so any pop-up question can be answered by mapping.  
  Keep the honesty script ("I haven't run OCI, here's the AWS equivalent I ran") current.
