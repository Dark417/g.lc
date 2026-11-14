"""Scripted Strands model: implements the Model interface by streaming Converse-style events."""

import itertools
import json
from typing import Any

from strands.models import Model

_ids = itertools.count(1)


def call(name: str, **args) -> dict:
    return {"tool": name, "input": args}


def say(text: str) -> dict:
    return {"text": text}


class ScriptedStrandsModel(Model):
    def __init__(self, script: list[dict] | None = None):
        self.script = list(script or [])
        self.requests: list[dict[str, Any]] = []
        self.config: dict[str, Any] = {"model_id": "scripted"}

    def update_config(self, **model_config) -> None:
        self.config.update(model_config)

    def get_config(self) -> dict:
        return self.config

    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
        self.requests.append(
            {
                "messages": messages,
                "tools": [t["name"] for t in tool_specs or []],
                "system": system_prompt,
            }
        )
        step = self.script.pop(0) if self.script else say("(end of script)")
        yield {"messageStart": {"role": "assistant"}}
        if "tool" in step:
            yield {
                "contentBlockStart": {
                    "start": {"toolUse": {"name": step["tool"], "toolUseId": f"tool_{next(_ids)}"}}
                }
            }
            yield {
                "contentBlockDelta": {"delta": {"toolUse": {"input": json.dumps(step["input"])}}}
            }
            yield {"contentBlockStop": {}}
            yield {"messageStop": {"stopReason": "tool_use"}}
        else:
            yield {"contentBlockDelta": {"delta": {"text": step["text"]}}}
            yield {"contentBlockStop": {}}
            yield {"messageStop": {"stopReason": "end_turn"}}
        yield {
            "metadata": {
                "usage": {"inputTokens": 10, "outputTokens": 5, "totalTokens": 15},
                "metrics": {"latencyMs": 1},
            }
        }

    async def structured_output(self, output_model, prompt, system_prompt=None, **kwargs):
        raise NotImplementedError("structured output goes through the tool path in Strands 1.x")
        yield  # pragma: no cover


class Scripts:
    def __init__(self, **scripts: list[dict]):
        self.models = {role: ScriptedStrandsModel(s) for role, s in scripts.items()}

    def __call__(self, profile, vendor, role: str) -> ScriptedStrandsModel:
        return self.models.setdefault(role, ScriptedStrandsModel())

    def __getitem__(self, role: str) -> ScriptedStrandsModel:
        return self.models[role]
