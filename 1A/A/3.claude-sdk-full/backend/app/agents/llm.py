"""Single-shot calls to the Messages API (no agent loop). Used by the writer loop and the judge.

Everything that needs "one prompt in, one answer out" goes through here, so the rest of the
code can inject a fake in tests.
"""

from typing import Protocol, TypeVar

from anthropic import AsyncAnthropic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class TextLLM(Protocol):
    async def __call__(self, *, system: str, prompt: str) -> str: ...


class ClaudeText:
    def __init__(self, model: str, api_key: str | None = None, max_tokens: int = 4000) -> None:
        self._client = AsyncAnthropic(api_key=api_key or None)
        self._model = model
        self._max_tokens = max_tokens

    async def __call__(self, *, system: str, prompt: str) -> str:
        # Adaptive thinking is the default on this model; omit `thinking` and steer with effort.
        res = await self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            output_config={"effort": "medium"},
        )
        if res.stop_reason == "refusal":
            return "(the model declined this request)"
        return "".join(b.text for b in res.content if b.type == "text").strip()


async def parse_structured(
    client: AsyncAnthropic, *, model: str, system: str, prompt: str, schema: type[T]
) -> T:
    """Ask for a validated Pydantic object back (structured outputs)."""
    res = await client.messages.parse(
        model=model,
        max_tokens=4000,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        output_format=schema,
    )
    return res.parsed_output
