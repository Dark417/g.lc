"""Domain for prompt management: the prompt/variant model and local rendering. No boto3 here."""

import re
from dataclasses import dataclass, field
from typing import Any

_VAR = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


@dataclass(frozen=True)
class PromptVariant:
    name: str
    template_type: str  # TEXT | CHAT
    model_id: str
    text: str = ""  # TEXT template
    system: str = ""  # CHAT template: system text
    messages: list[dict[str, Any]] = field(default_factory=list)  # CHAT template: Converse-shaped messages
    input_variables: list[str] = field(default_factory=list)
    inference: dict[str, Any] = field(default_factory=dict)  # maxTokens, temperature, topP, stopSequences


@dataclass(frozen=True)
class ManagedPrompt:
    prompt_id: str
    arn: str
    version: str  # "DRAFT" or "1", "2", ...
    default_variant: str
    variants: list[PromptVariant]

    def variant(self, name: str | None = None) -> PromptVariant:
        wanted = name or self.default_variant
        for v in self.variants:
            if v.name == wanted:
                return v
        raise KeyError(f"variant {wanted} not in prompt {self.prompt_id}")


class MissingVariableError(ValueError):
    pass


def render_text(template: str, values: dict[str, str]) -> str:
    """Fills {{name}} placeholders; a missing value raises instead of sending a literal {{name}} to the model."""
    missing = set(_VAR.findall(template)) - values.keys()
    if missing:
        raise MissingVariableError(f"missing variables: {sorted(missing)}")
    return _VAR.sub(lambda m: values[m.group(1)], template)


def render_variant(variant: PromptVariant, values: dict[str, str]) -> tuple[str, list[dict[str, Any]]]:
    """Local rendering of a TEXT or CHAT variant -> (system text, Converse messages).

    Use it to run ANY variant (A/B) with your own guardrails; Converse with a prompt ARN runs only the default.
    Catch: values are inserted verbatim ⇒ fence untrusted text first (01.05 fence_untrusted).
    """
    undeclared = set(values) - set(variant.input_variables)
    if undeclared:
        raise MissingVariableError(f"not declared in variant {variant.name}: {sorted(undeclared)}")
    if variant.template_type == "TEXT":
        return "", [{"role": "user", "content": [{"text": render_text(variant.text, values)}]}]
    messages = [
        {"role": m["role"], "content": [{"text": render_text(b["text"], values)} for b in m["content"] if "text" in b]}
        for m in variant.messages
    ]
    return render_text(variant.system, values), messages
