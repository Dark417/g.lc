"""Vertex AI Gen AI evaluation service on our harness results ("bring your own response").

Our harness produces (prompt, response) per target and case; EvalTask scores them with
model-based pointwise metrics (an autorater on Vertex), so any framework's output, including
ones not hosted on GCP, can be judged by the managed service.
"""

from app.config import Settings
from app.evals.scorers import Case


def to_dataset(rows: list[dict], cases: list[Case]):
    import pandas as pd

    prompts = {c.id: c.input for c in cases}
    return pd.DataFrame(
        [
            {
                "target": r["target"],
                "case": r["case"],
                "prompt": prompts[r["case"]],
                "response": r["output"] if isinstance(r["output"], str) else str(r["output"]),
            }
            for r in rows
            if not r["error"]
        ]
    )


def run_vertex_eval(rows: list[dict], cases: list[Case], settings: Settings):
    import vertexai
    from vertexai.evaluation import EvalTask, MetricPromptTemplateExamples

    vertexai.init(project=settings.google_cloud_project, location=settings.google_cloud_location)
    task = EvalTask(
        dataset=to_dataset(rows, cases),
        metrics=[
            MetricPromptTemplateExamples.Pointwise.QUESTION_ANSWERING_QUALITY,
            MetricPromptTemplateExamples.Pointwise.GROUNDEDNESS,
            MetricPromptTemplateExamples.Pointwise.SAFETY,
        ],
        experiment="ai-sdk-frameworks",
    )
    result = task.evaluate()
    table = result.metrics_table
    return table.groupby("target")[[c for c in table.columns if c.endswith("/score")]].mean()
