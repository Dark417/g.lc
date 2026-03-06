# Message Log

| time | user-input | response |
| --- | --- | --- |
| 260305-23:48 | Commit and push current branch to main | Staged all tracked changes, created commit `a46fed2` with workspace + SD scaffolding updates, then pushed `HEAD -> main` via remote `lc` (since `origin` is not configured locally) |
| 260305-22:46 | Rename `02.social-media`, reorder/rename question files by ranked order, and simplify questions index to hyperlink names only | Renamed social folder to dashed form, renumbered all 80 question files per type based on ranking order (with updated in-file IDs), and rewrote `sd/questions.md` to compact linked entries like `0101.rate limiter` without rank/id table columns |
| 260305-22:41 | Reorganize SD question files into typed folders and rank each type by interview relevance/likelihood | Moved all 80 SD question files into type folders like `sd/01.core/` and `sd/02.social media/`, then rewrote `sd/questions.md` with per-type ranked tables ordered by likelihood then relevance |
| 260305-22:11 | Reorganize instructions into AGENTS, create `.ai` agents/skills, scaffold SD/SDE docs, and generate top 80 system design questions (no solutions) | Moved instruction system to `AGENTS.md`, created agent and skill hierarchy including `p-swe` and `update-ai`, generated `sd/questions.md` and 80 per-question files, added `sd/flow.md`, and created `sde/` knowledge graph index/modules |
