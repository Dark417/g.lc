"""Evals: opt-in because they call the real model.

    uv sync --extra eval
    GOOGLE_API_KEY=... uv run pytest -m eval -s

The eval-set files themselves are validated in the default test run (no key needed).
"""

import os
from pathlib import Path

import pytest
from google.adk.evaluation.eval_set import EvalSet

EVALS = Path(__file__).resolve().parents[1] / "evals"


@pytest.mark.parametrize(
    "path", sorted(EVALS.glob("*/*.evalset.json")), ids=lambda p: p.parent.name
)
def test_evalset_files_are_valid(path):
    es = EvalSet.model_validate_json(path.read_text())
    assert es.eval_cases, path


@pytest.mark.eval
@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="needs GOOGLE_API_KEY")
@pytest.mark.parametrize("folder", ["tools", "knowledge"])
async def test_agent_against_evalset(folder):
    pytest.importorskip("rouge_score", reason="uv sync --extra eval")
    from google.adk.evaluation.agent_evaluator import AgentEvaluator

    # Each folder has its own test_config.json (criteria). See evals/README.md.
    await AgentEvaluator.evaluate(
        agent_module="app.agents.agent",
        eval_dataset_file_path_or_dir=str(EVALS / folder),
        num_runs=1,
    )
