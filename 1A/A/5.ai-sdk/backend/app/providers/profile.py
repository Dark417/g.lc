"""ProviderProfile: everything a pattern needs from a provider branch, resolved once.

A pattern never checks `if provider == "bedrock"`. It asks the profile:
  profile.vendor(...) / profile.model_id(...)   which model family and id
  profile.retriever                             RAG backend for search_docs
  profile.memory                                long-term memory for remember/recall
  profile.browser / profile.code_sandbox        Playwright target, code sandbox
  profile.guardrail                             input/output screening
Framework-native services (ADK session service, LangGraph checkpointer, Strands session manager)
are built inside each adapter from the same settings, because their types are framework-specific.
"""

from dataclasses import dataclass, field
from typing import Literal

from app.config import Settings
from app.guardrails.base import Guardrail
from app.memory.base import LongTermMemory
from app.rag.base import Retriever
from app.tools.browser import Browser
from app.tools.code import CodeSandbox

ModelVendor = Literal["anthropic", "gemini", "converse"]


@dataclass
class ProviderProfile:
    name: str  # raw | bedrock | vertex
    settings: Settings
    retriever: Retriever
    memory: LongTermMemory
    browser: Browser
    guardrail: Guardrail
    code_sandbox: CodeSandbox | None = None
    notes: dict[str, str] = field(default_factory=dict)

    def missing(self) -> list[str]:
        return self.settings.provider_missing(self.name)

    @property
    def available(self) -> bool:
        return not self.missing()

    def vendor(self, requested: str | None = None) -> ModelVendor:
        """Model family for adk / langgraph / strands on this branch.

        raw:     anthropic or gemini (request override, else RAW_VENDOR; falls back to whichever
                 key is set)
        bedrock: always the Converse API (any Bedrock model, including Claude)
        vertex:  gemini or anthropic (Claude on Vertex)
        """
        s = self.settings
        if self.name == "bedrock":
            return "converse"
        if self.name == "vertex":
            return requested or s.vertex_vendor  # type: ignore[return-value]
        vendor = requested or s.raw_vendor
        if vendor == "anthropic" and not s.anthropic_api_key and s.google_api_key:
            return "gemini"
        if vendor == "gemini" and not s.google_api_key and s.anthropic_api_key:
            return "anthropic"
        return vendor  # type: ignore[return-value]

    def model_id(self, vendor: ModelVendor) -> str:
        s = self.settings
        if vendor == "converse":
            return s.bedrock_model_id
        if self.name == "vertex":
            return s.vertex_claude_model if vendor == "anthropic" else s.vertex_gemini_model
        return s.anthropic_model if vendor == "anthropic" else s.gemini_model

    def services(self) -> dict[str, str]:
        return {
            "rag": self.retriever.name,
            "memory": self.memory.name,
            "browser": self.browser.name,
            "code_sandbox": self.code_sandbox.name if self.code_sandbox else "none",
            "guardrail": self.guardrail.name,
            **self.notes,
        }
