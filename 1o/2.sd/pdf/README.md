# PDF Exports

## Index

- [Current set](#current-set)
- [Historical snapshots](#historical-snapshots)
- [Regenerating](#regenerating)

## Current set

- Generated on 2026-09-10 from the v2 question files.
  - One PDF per `s1`–`s5` Markdown file, same basename.
  - `2.sd.md` and `2.sd1.md` are not exported.
  - Content includes the IC3 baseline / IC4 stretch structure and the reference DDL blocks.
- Source of truth stays the Markdown.
  - Regenerate after any edit; PDFs are not hand-edited.

## Historical snapshots

- [pdf/](pdf/) holds the exports made before the 2026-09-09 refactor.
  - Original filenames are retained as snapshot identifiers.
  - They predate the `s*` naming, the v2 structure, and the DDL blocks.

## Regenerating

- Pipeline: python-markdown (tables, fenced code, two-space list nesting doubled to four) → HTML → headless Chrome `--print-to-pdf`.
- A4, 10 pt body, tables and code blocks kept on one page where possible.
