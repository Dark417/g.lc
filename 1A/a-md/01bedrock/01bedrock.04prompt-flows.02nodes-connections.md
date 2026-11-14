# 01bedrock.04prompt-flows Nodes And Connections

> A flow definition is nodes with named inputs and outputs, wired by connections, checked before use.

## Index

- [1. Nodes](#1-nodes)
  - [1.1 Node Types](#11-node-types)
  - [1.2 Node Inputs And Expressions](#12-node-inputs-and-expressions)
- [2. Connections](#2-connections)
- [3. The Definition As Data](#3-the-definition-as-data)
- [4. Validation](#4-validation)
- [5. Creating From Code](#5-creating-from-code)

Back to [00index](01bedrock.04prompt-flows.00index.md).

---

## 1. Nodes

A node = `name`, `type`, `configuration`, `inputs`, `outputs`.

### 1.1 Node Types

- **Input**: the flow's entry
  - One output named `document`
  - Types: String, Number, Boolean, Object, Array
- **Output**: the flow's exit
  - One input `document`
  - Each Output node emits one `flowOutputEvent`
- **Prompt**
  - Inline template (model, template, inference config)
  - Or a managed prompt Amazon Resource Name (ARN) ([01bedrock.03prompt-management](01bedrock.03prompt-management.00index.md))
  - Optional guardrail
- **KnowledgeBase**
  - Retrieve, or retrieve-and-generate with a model
  - See [02rag.04knowledge-bases](../02rag/02rag.04knowledge-bases.00index.md)
- **Condition**
  - Named conditions with expressions over its inputs
  - First match wins, plus a default branch
- **LambdaFunction**: arbitrary code
  - validation, Application Programming Interface (API) calls, Database (DB) writes
- **Agent**: call a Bedrock Agent alias
- **Iterator / Collector**: fan out over an array, gather results
- **InlineCode**: small Python snippets inside the flow
- **Storage / Retrieval**: write to / read from Simple Storage Service (S3)
- **Lex, Loop** nodes: niche; check the docs

### 1.2 Node Inputs And Expressions

- Node input = `name`, `type`, `expression`
- **`expression`**: a JSONPath-like selector over the incoming data
  - `$.data` = everything
  - `$.data.field` = a field of an Object
- Fixed output names
  - Prompt nodes always output `modelCompletion`
  - Input nodes output `document`
  - Output nodes take `document`

## 2. Connections

Connections move data between named ports.

- **`Data`**: `sourceOutput` of one node → `targetInput` of another
- **`Conditional`**: from a Condition node's named condition to the next node

## 3. The Definition As Data

- The graph is a plain dict in the `CreateFlow` / `UpdateFlow` `definition` shape.
- It is the same graph as the Terraform `a-flow`.

```python
# app/domain/_01bedrock_04prompt_flows.py
INPUT_NODE = "FlowInput"
INPUT_OUTPUT_NAME = "document"  # the Input node's single output
PROMPT_NODE = "Summarize"
OUTPUT_NODE = "FlowOutput"

def build_summary_flow(model_id: str) -> dict[str, Any]:
    return {
        "nodes": [
            {"name": INPUT_NODE, "type": "Input", "configuration": {"input": {}},
             "outputs": [{"name": INPUT_OUTPUT_NAME, "type": "String"}]},  # String | Number | Boolean | Object | Array
            {
                "name": PROMPT_NODE,
                "type": "Prompt",
                "configuration": {"prompt": {
                    "sourceConfiguration": {
                        # Alternative: {"resource": {"promptArn": "<managed prompt version ARN>"}} (01bedrock.03)
                        "inline": {
                            "modelId": model_id,
                            "templateType": "TEXT",
                            "templateConfiguration": {"text": {
                                "text": "Summarize the following for an on-call engineer in at most 3 bullets:\n<input>{{topic}}</input>",
                                "inputVariables": [{"name": "topic"}],
                            }},
                            "inferenceConfiguration": {"text": {"maxTokens": 300, "temperature": 0.2, "topP": 0.9}},
                        }
                    },
                    # "guardrailConfiguration": {"guardrailIdentifier": "...", "guardrailVersion": "1"},  # 04safety.01
                }},
                "inputs": [{"name": "topic", "type": "String", "expression": "$.data"}],
                "outputs": [{"name": "modelCompletion", "type": "String"}],  # fixed name for Prompt nodes
            },
            {"name": OUTPUT_NODE, "type": "Output", "configuration": {"output": {}},
             "inputs": [{"name": "document", "type": "String", "expression": "$.data"}]},
        ],
        "connections": [
            {"name": "InputToSummarize", "source": INPUT_NODE, "target": PROMPT_NODE,
             "type": "Data",  # Data | Conditional
             "configuration": {"data": {"sourceOutput": INPUT_OUTPUT_NAME, "targetInput": "topic"}}},
            {"name": "SummarizeToOutput", "source": PROMPT_NODE, "target": OUTPUT_NODE, "type": "Data",
             "configuration": {"data": {"sourceOutput": "modelCompletion", "targetInput": "document"}}},
        ],
    }
```

- Catch: a wrong `sourceOutput` / `targetInput` name breaks the wiring.
- Catch: a `$.data.x` path that does not exist yields empty or failed output.

## 4. Validation

Check the graph before it reaches a DRAFT.

- **`ValidateFlowDefinition`** checks the graph before you create it
  - Run it in Continuous Integration (CI)
  - Empty list = valid
- **`PrepareFlow`** also validates
  - Status `Prepared` or `Failed` with `validations`

```python
# app/infra/_01bedrock_04prompt_flows.py
def validate_definition(self, definition: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    resp = self.agent.validate_flow_definition(definition=definition or build_summary_flow(self.settings.model()))
    return resp.get("validations", [])  # [{"message", "severity": Error|Warning, "type", "details"}]
```

- Limit: validation checks wiring and types.
  - It does not check whether prompts produce good output.

## 5. Creating From Code

- `CreateFlow` takes `executionRoleArn` + `definition` and makes a DRAFT.
- A `clientToken` makes the create idempotent.

```python
# app/infra/_01bedrock_04prompt_flows.py
def create_flow(self, name: str) -> dict[str, str]:
    kwargs: dict[str, Any] = {
        "name": name,
        "description": "Input -> Prompt -> Output (created from Python)",
        "executionRoleArn": self.settings.execution_role_arn,  # caller needs iam:PassRole on it
        "definition": build_summary_flow(self.settings.model()),
        "clientToken": str(uuid.uuid5(uuid.NAMESPACE_URL, f"flow/{name}")),  # idempotent create
        "tags": {"Component": "01.04"},
    }
    if self.settings.kms_key_arn:
        kwargs["customerEncryptionKeyArn"] = self.settings.kms_key_arn
    resp = self.agent.create_flow(**kwargs)
    return {"id": resp["id"], "arn": resp["arn"], "status": resp["status"]}  # status NotPrepared
```

- Catch: the caller needs `iam:PassRole` on the execution role.
- Catch: the DRAFT must be prepared before use ([03 lifecycle](01bedrock.04prompt-flows.03lifecycle.md)).
