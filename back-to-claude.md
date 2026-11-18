# Back To Claude

> Message log written from the IDE or locally; Claude Cowork reads it and acts on each entry.

- Two tiers: Queue, then Finish
  - Local agents (IDE, Claude Code, Codex) write **only to Queue**
  - Claude Cowork acts on a Queue entry, then moves it to Finish with ✅ and a one-line result
- Entry format: `yymmdd-hh:mm · <ask>`, newest on top
- Never delete entries

## Index

- [Queue](#queue)
- [Finish](#finish)

## Queue

- 261118-13:15 · Apply D:\1lc\dist\GAX-20261118-handoff\1lc-writing-workflows.patch at the 1lc root to align .agents/rules.md and the writing and interview workflows with the root rules. ⏸ 目标是 D:\1lc 根目录，超出本任务范围（只改项目文档 / memory / 1D 镜像）；请直接在本地应用，或改成 1D 范围内的要求

## Finish

- ✅ 261118-13:15 · Apply D:\1lc\dist\GAX-20261118-handoff\1D-interview-docs.patch at the 1D root. It creates 1T/1T.md, merges the three stories into 1me.md, archives 1me-stories.md under _to_delete, repairs sibling references, moves the delivery playbook into bq-templates.md, and reformats 2bq-itv.md by company. It also aligns both 0sys formatting rules. After applying, sync the file changes and refresh the 1D maps. → 补丁已套用到本地 1D（dry-run 全部命中）：新建 1T/1T.md；改 1me、1me-email-agent、bq-core、bq-templates、2bq-itv、rule-Doc Gen Format、rule-interview-log；1me-stories 移到 1T/1bq/_to_delete/（备份在本机 TEMP\gax-apply）；已同步项目：1T、1me、1me-email-agent、bq-templates、2bq-itv、两份规则、README / 1sys / Docs Map 已刷新；bq-core 和 0sys/skills/* 留给下一次 hourly 补传 (done 261118-13:43)
