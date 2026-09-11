# Oracle System Design Bank

## Index

- [Loop context](#loop-context)
- [Question naming](#question-naming)
- [Question file structure](#question-file-structure)
- [Answer depth and formatting](#answer-depth-and-formatting)
- [Quality checklist](#quality-checklist)
- [Refactor checks](#refactor-checks)

## Loop context

- Status 2026-09-09: Round 1 passed; the final loop is next.
  - 4 rounds in about 4 hours: 2 system design, 1 bar raiser, 1 coding.
  - Preparation focus is the two system design rounds.
- Target: sound like a solid IC3 at minimum; add IC4 signals where they cost no clock time.
  - The req targets IC3 and IC4 is unlikely to be negotiable.
  - Prepare to the higher bar anyway to raise the pass probability.
- Depth labels
  - `IC3 baseline`: what must land in every phase to pass.
  - `IC4 stretch`: additive depth under stronger requirements; never a rewrite of the baseline.
  - These are preparation labels, not Oracle's official rubric.
- Assume a 60-minute round unless the prompt says otherwise.
  - Intro slice, 45 minutes of design, questions at the end.
  - If the interviewer states 45 minutes, compress every phase proportionally and drop the intro to 2 minutes.

## Question naming

- `2.sd.md` owns the ranked question order and provenance.
- Question files use `s<group>.<two-digit-position>.<Descriptive-hyphenated-name>.md`.
  - `s1` maps to `1infra`.
  - `s2` maps to `1infra-pki`.
  - `s3` maps to `1infra+`.
  - `s4` maps to `2business`.
  - `s5` holds supporting references (mechanism packets, LLD staples, drafts).
    - They do not occupy ranked question positions.
    - Order them by role relevance.
- Restart numbering at `01` inside each group.
- Give each bank question one dedicated file.
  - Keep shared mechanisms linked rather than combining distinct bank prompts into one file.
- Keep `2.sd1.md` as the shared algorithm implementation drill.
- Files under `pdf/` are historical snapshots unless explicitly regenerated.
- Links to the API/schema companion use `../../1sde/1.backend/2.rest102.md#<anchor>`.

## Question file structure

- Every `s1`–`s4` question file uses this section order and these headings.
  - `# s<g>.<nn> — <Prompt>`
  - `## Index` with a hyperlink to every `##` section.
  - `## Interview framing`
    - Role target and label note.
    - Evidence line linking to the bank.
    - Why this is hard: naive approach, first break, minimum primitives.
    - 🗣 crux one-liner.
    - Opening script: 4–6 verbatim sentences, one per bullet.
    - Phase table `Phase | Clock | Deliverable` on the 60-minute clock.
  - `## Requirements — IC3 baseline`
    - Clarifying-questions table `Question | Assumed answer | Why it changes the design`.
    - Functional scope.
    - NFR table `Requirement | Target | Enforced by`; every row carries a number.
    - Invariants.
    - Non-goals.
  - `## Capacity and consequence — IC3 baseline`
    - Every estimate ends with the decision it forces.
  - `## Architecture and flow — IC3 baseline`
    - Diagram first, then ownership bullets, then one request trace on arrow lines.
  - `## API and data model — IC3 baseline`
    - Endpoint table with idempotency and conflict behavior.
    - Keyed state table.
    - Reference DDL: a `sql` block with `CREATE TABLE` statements after the state table.
      - Composite tenant-scoped primary keys, uniqueness constraints, access-path indexes, and `CHECK` constraints for stated invariants.
      - Aligned with the companion schema in `2.rest102.md`; the question file's names win and deviations are noted.
      - Model only relational state; say explicitly which state lives in memory, Redis, log segments, or an HSM.
  - One or two deep-dive sections `— IC3 baseline`
    - Algorithm or data structure, concurrency, consistency boundary, concrete values, exact failure.
  - `## Failure, operations, and security`
    - Table `Failure | Blast radius | Detection | Degraded behavior | Recovery`.
    - Observe, retry discipline, tenant isolation, rollout and rollback safety.
  - `## Alternatives and IC4 stretch`
    - Option table `Option | What it is | Strength | Weakness | Choose when`.
    - IC4 stretch items: stronger requirement, 10× load, cost and blast radius, migration or rollout.
    - Weakest assumption.
    - Over-engineering warning.
  - `## Level signal — IC3 baseline vs IC4 stretch`
    - Table `Phase | IC3 must land | IC4 adds | Separating signal`.
  - `## Interview pushback and validation`
    - 6–8 pushbacks, each with an `IC3 baseline` answer and an `IC4 stretch` answer.
    - At least one pushback reverses a premise.
    - Validation scenarios list.
  - `## Recall card`
    - 4–5 quotable one-liners.
    - Wrap-up script: 4 verbatim sentences.
  - `## References`
    - Bank link, role framing, API/schema companion, primary sources with the mechanism each supports.
- `s5` reference files are mechanism packets, not 60-minute question answers.
  - They carry no opening script, no phase table, and no level-signal table.
  - They use this section order and these headings.
    - `# s5.<nn> — <Title> — supporting reference`
    - Header note block: bank link, what the file backs, depth-label line, JD tie-in.
    - `## Index` with a hyperlink to every `##` section and an explicit `<a id="s5nn-<n>"></a>` anchor before each.
    - `## 1. Crux and why it is hard` — naive approach, first break, minimum primitives, 🗣 one-liner.
    - `## 2. Clarifying questions` — table `Question | Assumed answer | Why it changes the design`.
    - `## 3. Requirements` — NFR table `Requirement | Target | Enforced by`; every row carries a number.
    - `## 4. Capacity and consequence` — every estimate ends with the decision it forces.
    - `## 5. Architecture and flow` — diagram first, then ownership bullets, then one trace on arrow lines.
    - `## 6. API and data model` — endpoint or operation table, keyed state table, reference DDL where relational state exists.
    - Mechanism deep-dive sections in the middle, each labelled `— IC3 baseline`.
    - `## Failure, operations, and security` — table `Failure | Blast radius | Detection | Degraded behavior | Recovery`.
    - `## Alternatives and IC4 stretch` — option table `Option | What it is | Strength | Weakness | Choose when`, then stretch items, weakest assumption, over-engineering warning.
    - `## Interview pushback and validation` — 6–8 pushbacks, each with an `IC3 baseline` and an `IC4 stretch` answer; at least one reverses a premise.
    - `## Recall card` — 4–5 quotable one-liners.
    - `## References` — bank link, siblings, primary sources with the mechanism each supports.
  - Use `IC3 baseline` and `IC4 stretch` labels; do not use the retired `L4` and `L5 extra` labels.
  - A file whose subject has no relational state says so explicitly instead of inventing DDL.

## Answer depth and formatting

- Prepare OCI IC3 answers with ownership of a bounded platform component.
  - Keep `IC3 baseline` as the preparation baseline.
  - Keep `IC4 stretch` as additive depth under stronger requirements.
  - Do not claim an official equivalence between company ladders.
- Scope depth upgrades to the batch requested by the user.
  - A naming refactor does not imply a full content audit of other batches.
- Read and apply [repository authoring rules](../../.agents/rules.md) before writing.
- Write explanatory prose as nested bullets.
  - Keep each parallel concept on its own line.
  - Indent supporting details under their parent.
  - Avoid long prose paragraphs.
- Keep flows on standalone arrow lines with Markdown hard breaks.
  - Never combine a bullet marker with a flow arrow.
- Label assumptions and distinguish proposed designs from actual OCI API behavior.
- Preserve first-hand report evidence separately from supplemental preparation rationale.
- Prefer Java 17 or pseudocode only where prose cannot carry the mechanism.

## Quality checklist

- Run before finishing any `s1`–`s4` file, and every applicable row before finishing an `s5` file; fix every "no".
  - Does every NFR row carry a number and an enforcing mechanism?
  - Does every estimate force a decision or get removed?
  - Is the diagram drawn before the prose that explains it?
  - Does every named component state the mechanism bought and the cost paid?
  - Does every property claim carry its defeater?
  - Does the data model include DDL with keys, uniqueness, and the indexes the access paths need?
  - Is every number sourced or labeled as an assumption or order of magnitude?
  - Is `IC4 stretch` structurally different from the baseline, not just longer?
  - Does at least one pushback reverse a premise?
  - Is there a specific over-engineering warning and a named weakest assumption?
  - Are the opening and wrap-up scripts speakable in under 60 seconds each?
  - Would a principal engineer call any line hand-wavy?

## Refactor checks

- Update the bank and incoming links with every rename.
- Verify consecutive numbering within each group.
- Verify local file links and fragment anchors.
- Verify balanced code fences and unique explicit anchors.
- Check changed prose against the nested-bullet rule.
- Preserve unrelated user changes.
- Do not claim a push unless a commit and remote push were performed and verified.
