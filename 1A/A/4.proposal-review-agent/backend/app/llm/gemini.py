"""Single-shot structured calls to Gemini (no agent loop): assess, summarize, extract rules.

Uses google-genai, the same client ADK uses, so it runs on a Gemini API key locally and on
Vertex AI in GCP with no code change. Tests substitute a scripted fake.
"""

from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLM(Protocol):
    model: str

    async def generate_json(self, *, system: str, prompt: str, schema: type[T]) -> T: ...


class GeminiLLM:
    def __init__(self, model: str) -> None:
        self.model = model
        self._client = None

    def _c(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client()  # credentials from env (see Settings.export_model_env)
        return self._client

    async def generate_json(self, *, system: str, prompt: str, schema: type[T]) -> T:
        from google.genai import types

        res = await self._c().aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.0,
            ),
        )
        if isinstance(res.parsed, schema):
            return res.parsed
        return schema.model_validate_json(res.text or "{}")
