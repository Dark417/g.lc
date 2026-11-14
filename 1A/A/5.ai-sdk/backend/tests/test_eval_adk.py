"""ADK's own evaluator on an .evalset.json (opt-in: calls the real model).

uv run pytest -m eval tests/test_eval_adk.py
"""

import pytest

from app.config import BACKEND_DIR


@pytest.mark.eval
async def test_adk_evalset():
    from google.adk.evaluation.agent_evaluator import AgentEvaluator

    await AgentEvaluator.evaluate(
        agent_module="app.adk_eval_agent",
        eval_dataset_file_path_or_dir=str(BACKEND_DIR / "evals" / "adk" / "research.evalset.json"),
        num_runs=1,
    )
