"""Scripted LangChain chat models: one script per role, tool calls included, no network."""

import itertools
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

_ids = itertools.count(1)


def call(name: str, **args) -> AIMessage:
    return AIMessage(
        content="", tool_calls=[{"name": name, "args": args, "id": f"call_{next(_ids)}"}]
    )


def say(text: str) -> AIMessage:
    return AIMessage(content=text)


class ScriptedChatModel(BaseChatModel):
    script: list[AIMessage] = Field(default_factory=list)
    requests: list[list[Any]] = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        self.requests.append(list(messages))
        msg = self.script.pop(0) if self.script else say("(end of script)")
        return ChatResult(generations=[ChatGeneration(message=msg.model_copy())])

    def bind_tools(self, tools, **kwargs):
        return self

    def system_text(self, i: int = 0) -> str:
        return " ".join(str(m.content) for m in self.requests[i] if m.type == "system")

    def all_text(self, i: int = 0) -> str:
        return " ".join(str(m.content) for m in self.requests[i])


class Scripts:
    def __init__(self, **scripts: list[AIMessage]):
        self.models = {role: ScriptedChatModel(script=list(s)) for role, s in scripts.items()}

    def __call__(self, profile, vendor, role: str) -> ScriptedChatModel:
        return self.models.setdefault(role, ScriptedChatModel())

    def __getitem__(self, role: str) -> ScriptedChatModel:
        return self.models[role]
