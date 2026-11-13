# 1python — Python project guide (1A)

- Project: `python/` — one FastAPI project, Python 3.11+, the primary 1A language
- Rules: [AGENTS.md §8, §10](AGENTS.md#10-python-rules)

## Index
- [1. Setup and run](#1-setup-and-run)
- [2. Layout](#2-layout)
- [3. Slices](#3-slices)

## 1. Setup and run
- Windows: `cd 1A\python; py -m venv .venv; .venv\Scripts\activate; pip install -e .`
- Linux/macOS: `cd 1A/python && python -m venv .venv && . .venv/bin/activate && pip install -e .`
- Check: `python -m compileall -q app`
- Run: `uvicorn app.main:app --reload --port 8001`; enable slices with `A_ENABLED=converse,guardrails`
- Slice settings: env prefix `A_<SLICE>_` (e.g. `A_GUARDRAILS_GUARDRAIL_ID`), defined in each slice's `config.py`

## 2. Layout
```
python/
  pyproject.toml
  app/
    main.py               SLICES map: slice name -> package
    shared/               config.py (region, data bucket, model ids), aws.py, retry.py
    a04_01_guardrails/    config.py, domain.py, infra.py, service.py, api.py
```

## 3. Slices
| Number | Slice (`A_ENABLED`) | Package | Status |
|---|---|---|---|
| 01.01 | `converse` | `app/a01_01_converse` | ✅ A-010 |
| 01.02 | `customization` | `app/a01_02_customization` | ✅ A-011 |
| 01.03 | `prompts` | `app/a01_03_prompt_management` | ✅ A-012 |
| 01.04 | `flows` | `app/a01_04_prompt_flows` | ✅ A-013 |
| 01.05 | `prompting` | `app/a01_05_prompt_engineering` | ✅ A-014 |
| 02.01 | `embeddings` | `app/a02_01_embeddings` | ✅ A-020 |
| 02.02 | `opensearch` | `app/a02_02_opensearch` | ✅ A-021 |
| 02.03 | `chunking` | `app/a02_03_chunking` | ✅ A-022 |
| 02.04 | `kb` | `app/a02_04_knowledge_bases` | ✅ A-023 |
| 03.01 | `bda` | `app/a03_01_data_automation` | ✅ A-030 |
| 03.02 | `glue_dq` | `app/a03_02_glue_data_quality` | ✅ A-031 |
| 03.03 | `transcribe` | `app/a03_03_transcribe` | ✅ A-032 |
| 03.04 | `comprehend` | `app/a03_04_comprehend` | ✅ A-033 |
| 04.01 | `guardrails` | `app/a04_01_guardrails` | ✅ A-040 |
| 04.02 | `pii` | `app/a04_02_pii_redaction` | ✅ A-041 |
| 04.03 | `evals` | `app/a04_03_evaluations` | ✅ A-042 |
| 05.01 | `observability` | `app/a05_01_observability` | ✅ A-050 |
