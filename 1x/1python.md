# 1python — Python project guide

- Project: `python/` — one FastAPI project, Python 3.11+ (task X-002)
- Rules: [AGENTS.md §8, §10](AGENTS.md#10-python-rules)

## Index
- [1. Setup and run](#1-setup-and-run)
- [2. Layout](#2-layout)
- [3. Slices](#3-slices)

## 1. Setup and run
- Windows: `cd 1x\python; py -m venv .venv; .venv\Scripts\activate; pip install -e .`
- Linux/macOS: `cd 1x/python && python -m venv .venv && . .venv/bin/activate && pip install -e .`
- Check: `python -m compileall -q app`
- Run: `uvicorn app.main:app --reload`; enable slices with `X_ENABLED=aurora,dynamodb`

## 2. Layout
```
python/
  pyproject.toml
  app/
    main.py
    shared/             config.py, aws.py
    x03_01_aurora/      domain.py, service.py, infra.py, api.py
```

## 3. Slices
| Number | Package | Status |
|---|---|---|
| 03.01 | `app/x03_01_aurora` | ⬜ X-010 |
| 03.02 | `app/x03_02_dynamodb` | ⬜ X-011 |
| 03.03 | `app/x03_03_s3` | ⬜ X-012 |
| 04.01 | `app/x04_01_athena` | ⬜ X-013 |
| 04.02 | `app/x04_02_redshift` | ⬜ X-014 |
| 05.01 | `app/x05_01_kinesis` | ⬜ X-015 |
| 05.02 | `app/x05_02_kafka` | ⬜ X-016 |
