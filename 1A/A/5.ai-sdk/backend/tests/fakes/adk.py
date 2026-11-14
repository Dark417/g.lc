"""Scripted ADK models: one script per agent role, so multi-agent patterns run offline."""

from typing import Any

from google.adk.models import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from pydantic import Field


def call(name: str, **args) -> types.Part:
    return types.Part(function_call=types.FunctionCall(name=name, args=args))


def say(text: str) -> types.Part:
    return types.Part(text=text)


class ScriptedLlm(BaseLlm):
    model: str = "scripted"
    script: list[Any] = Field(default_factory=list)
    requests: list[Any] = Field(default_factory=list)

    async def generate_content_async(self, llm_request, stream: bool = False):
        self.requests.append(llm_request)
        part = self.script.pop(0) if self.script else say("(end of script)")
        yield LlmResponse(content=types.Content(role="model", parts=[part]))

    def system(self, i: int = 0) -> str:
        si = self.requests[i].config.system_instruction
        return si if isinstance(si, str) else "".join(p.text or "" for p in si.parts)

    def contents_text(self, i: int = 0) -> str:
        return " ".join(p.text or "" for c in self.requests[i].contents for p in (c.parts or []))


class Scripts:
    """model_factory for AdkAdapter: role -> ScriptedLlm (the same instance on every call)."""

    def __init__(self, **scripts: list[types.Part]):
        self.models = {role: ScriptedLlm(script=list(parts)) for role, parts in scripts.items()}

    def __call__(self, profile, vendor, role: str) -> ScriptedLlm:
        return self.models.setdefault(role, ScriptedLlm())

    def __getitem__(self, role: str) -> ScriptedLlm:
        return self.models[role]
