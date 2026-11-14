"""Shared fixtures. No test here calls a real model or the network.

- FakeLLM: scripted structured outputs for summaries, rule extraction, and findings.
- ScriptedModel: an ADK BaseLlm that replays a script of parts (text or function calls), so the
  real agent loop, callbacks, toolsets, sessions, and memory run end to end offline.
"""

import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from google.adk.models import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from pydantic import Field

from app.config import Settings
from app.container import build_container
from app.domain.models import DocSummary, ProposedRule, ProposedRules
from app.domain.verdicts import LlmFindings

SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"
ADMIN = {"X-User-Email": "admin@example.com"}
ALICE = {"X-User-Email": "alice@example.com"}
BOB = {"X-User-Email": "bob@example.com"}


class FakeLLM:
    model = "fake-llm"

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.findings: Callable[[str], LlmFindings] | None = None

    async def generate_json(self, *, system: str, prompt: str, schema):
        self.calls.append((schema.__name__, prompt))
        if schema is DocSummary:
            return DocSummary(
                summary="Test summary.", key_points=["point one"], suggested_category="testing"
            )
        if schema is ProposedRules:
            return ProposedRules(
                rules=[
                    ProposedRule(
                        code="TEST-001",
                        title="Everything must be tested",
                        statement="Every feature must have tests.",
                        severity="hard",
                        category="testing",
                        rationale="",
                        exception_process="",
                        source_ref="§1",
                    )
                ]
            )
        if schema is LlmFindings:
            if self.findings:
                return self.findings(prompt)
            return LlmFindings(findings=[], missing_information=[], summary="No findings.")
        raise AssertionError(f"unexpected schema {schema}")


def call(name: str, **args) -> types.Part:
    return types.Part(function_call=types.FunctionCall(name=name, args=args))


def say(text: str) -> types.Part:
    return types.Part(text=text)


class ScriptedModel(BaseLlm):
    """Replays `script` one part per model call; records every request (tools offered, etc.)."""

    model: str = "scripted"
    script: list[Any] = Field(default_factory=list)
    requests: list[Any] = Field(default_factory=list)

    async def generate_content_async(self, llm_request, stream: bool = False):
        self.requests.append(llm_request)
        part = self.script.pop(0) if self.script else say("(end of script)")
        yield LlmResponse(content=types.Content(role="model", parts=[part]))

    def offered_tools(self, i: int = -1) -> set[str]:
        return set(self.requests[i].tools_dict)


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        _env_file=None,
        database_url=f"sqlite+aiosqlite:///{tmp_path}/app.db",
        doc_store_path=str(tmp_path / "documents.json"),
        blob_dir=str(tmp_path / "blobs"),
        artifact_dir=str(tmp_path / "artifacts"),
        admin_users="admin@example.com",
        service_tokens="svc-token",
        enable_adk_web=False,
        embedder="hashing",
        vector_store="sql",
        doc_store="file",
    )


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
async def container(settings, fake_llm):
    c = build_container(settings, llm=fake_llm)
    await c.init()
    yield c
    await c.close()


async def seed_rules(c) -> None:
    from app.services.rule_extraction import parse_rules_file

    data = (SAMPLES / "rules" / "seed-rules.json").read_bytes()
    await c.rule_service.create_many(parse_rules_file(data, "seed-rules.json"), "test")


def findings_from(statuses: dict[str, str]) -> Callable[[str], LlmFindings]:
    """Make a FakeLLM.findings function that returns the given status per rule code."""

    def fn(prompt: str) -> LlmFindings:
        return LlmFindings.model_validate(
            {
                "findings": [
                    {
                        "rule_code": code,
                        "status": status,
                        "reasoning": f"{code} is {status}",
                        "evidence": [{"source": f"rule {code}", "quote": "quoted text"}],
                        "remediation": "fix it" if status in ("violated", "unclear") else "",
                    }
                    for code, status in statuses.items()
                ],
                "missing_information": [],
                "summary": json.dumps(statuses),
            }
        )

    return fn


def integration_url(name: str) -> str:
    url = os.getenv(name, "")
    if not url:
        pytest.skip(f"set {name} to run")
    return url


# every hard rule in seed-rules.json marked satisfied: lets a test isolate flexible-rule behaviour
HARD_OK = {
    c: "satisfied"
    for c in [
        "PRIV-001",
        "PRIV-002",
        "PRIV-003",
        "MKT-001",
        "LAUNCH-001",
        "SEC-001",
        "AI-002",
        "FIN-001",
    ]
}
