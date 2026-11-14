"""Eval scoring logic (no model), plus the opt-in real run (`pytest -m eval`)."""

import json
import os
from pathlib import Path

import pytest

from app.evals.run import CASES, passed, score_case, summarize


def test_golden_set_is_well_formed():
    cases = json.loads(Path(CASES).read_text())
    assert len(cases) >= 10
    labels = {"COMPLIANT", "CONDITIONALLY_COMPLIANT", "NON_COMPLIANT", "NEEDS_MORE_INFO"}
    for c in cases:
        assert c["expected_verdict"] in labels and set(c["must_not_verdict"]) <= labels
        assert c["expected_verdict"] not in c["must_not_verdict"]


def test_scoring():
    case = {
        "id": "x",
        "expected_verdict": "NON_COMPLIANT",
        "must_cite": ["A-1", "B-1"],
        "must_not_verdict": ["COMPLIANT"],
    }
    good = {
        "verdict": "NON_COMPLIANT",
        "findings": [
            {"rule_code": "A-1", "status": "violated"},
            {"rule_code": "B-1", "status": "satisfied"},
        ],
    }
    r = score_case(case, good)
    assert r.verdict_ok and r.safe and r.citation_recall == 0.5
    bad = score_case(case, {"verdict": "COMPLIANT", "findings": []})
    assert not bad.verdict_ok and not bad.safe
    s = summarize([r, bad])
    assert s == {"cases": 2, "accuracy": 0.5, "safety_failures": 1, "citation_recall": 0.25}
    assert not passed(s)


@pytest.mark.eval
@pytest.mark.skipif(
    not (os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_USE_VERTEXAI")),
    reason="needs a model",
)
async def test_golden_verdicts_with_real_model():
    from app.evals.run import main

    assert await main() == 0
