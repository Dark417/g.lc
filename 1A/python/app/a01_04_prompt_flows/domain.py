"""Domain for flows: the flow definition as data (same graph as terraform/01.04.prompt-flows.tf) and run results.

No boto3 here. The definition dict is the CreateFlow/UpdateFlow "definition" shape.
"""

from dataclasses import dataclass, field
from typing import Any

INPUT_NODE = "FlowInput"
INPUT_OUTPUT_NAME = "document"  # the Input node's single output
PROMPT_NODE = "Summarize"
OUTPUT_NODE = "FlowOutput"


def build_summary_flow(model_id: str) -> dict[str, Any]:
    """Input -> Prompt (inline TEXT template) -> Output.

    Wiring rules: a Data connection maps sourceOutput (a node output name) -> targetInput (a node input name);
    input expressions select from the incoming value ($.data = everything, $.data.x = a field of an Object).
    Prompt nodes always output "modelCompletion"; Input nodes output "document"; Output nodes take "document".
    """
    return {
        "nodes": [
            {
                "name": INPUT_NODE,
                "type": "Input",
                "configuration": {"input": {}},
                "outputs": [{"name": INPUT_OUTPUT_NAME, "type": "String"}],  # String | Number | Boolean | Object | Array
            },
            {
                "name": PROMPT_NODE,
                "type": "Prompt",
                "configuration": {
                    "prompt": {
                        "sourceConfiguration": {
                            # Alternative: {"resource": {"promptArn": "<managed prompt version ARN>"}} (01.03)
                            "inline": {
                                "modelId": model_id,
                                "templateType": "TEXT",
                                "templateConfiguration": {
                                    "text": {
                                        "text": "Summarize the following for an on-call engineer in at most 3 bullets:\n<input>{{topic}}</input>",
                                        "inputVariables": [{"name": "topic"}],
                                    }
                                },
                                "inferenceConfiguration": {"text": {"maxTokens": 300, "temperature": 0.2, "topP": 0.9}},
                            }
                        },
                        # "guardrailConfiguration": {"guardrailIdentifier": "...", "guardrailVersion": "1"},  # 04.01
                    }
                },
                "inputs": [{"name": "topic", "type": "String", "expression": "$.data"}],
                "outputs": [{"name": "modelCompletion", "type": "String"}],
            },
            {
                "name": OUTPUT_NODE,
                "type": "Output",
                "configuration": {"output": {}},
                "inputs": [{"name": "document", "type": "String", "expression": "$.data"}],
            },
        ],
        "connections": [
            {
                "name": "InputToSummarize",
                "source": INPUT_NODE,
                "target": PROMPT_NODE,
                "type": "Data",  # Data | Conditional
                "configuration": {"data": {"sourceOutput": INPUT_OUTPUT_NAME, "targetInput": "topic"}},
            },
            {
                "name": "SummarizeToOutput",
                "source": PROMPT_NODE,
                "target": OUTPUT_NODE,
                "type": "Data",
                "configuration": {"data": {"sourceOutput": "modelCompletion", "targetInput": "document"}},
            },
        ],
    }


@dataclass
class FlowRun:
    """Result of one InvokeFlow: outputs per Output node, completion reason, optional traces."""

    execution_id: str = ""
    outputs: dict[str, Any] = field(default_factory=dict)  # Output node name -> content.document
    completion_reason: str = ""  # SUCCESS | INPUT_REQUIRED
    input_request: dict[str, Any] | None = None  # multi-turn: an Agent node asks for more input
    traces: list[dict[str, Any]] = field(default_factory=list)
