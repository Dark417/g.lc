"""Guardrail protocol: check text on the way in (user prompt) and on the way out (answer)."""

from dataclasses import dataclass, field
from typing import Literal, Protocol

Source = Literal["INPUT", "OUTPUT"]


@dataclass
class GuardrailResult:
    allowed: bool
    text: str  # possibly masked
    reasons: list[str] = field(default_factory=list)


class Guardrail(Protocol):
    name: str

    async def check(self, text: str, source: Source) -> GuardrailResult: ...


class NoGuardrail:
    name = "off"

    async def check(self, text: str, source: Source) -> GuardrailResult:
        return GuardrailResult(True, text)
