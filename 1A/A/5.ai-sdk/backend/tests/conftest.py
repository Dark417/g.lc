"""Shared fixtures. No API keys, no cloud: providers are 'configured' with dummy values and every
model is scripted. Cloud SDK clients are replaced with stubs where a test touches them."""

import asyncio
import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.container import build_container
from app.core.adapter import PatternInfo, RunContext
from app.core.scope import RunScope, reset_scope, set_scope
from app.main import create_app
from app.schemas import Event

CHROMIUM = os.environ.get("PLAYWRIGHT_CHROMIUM_PATH", "/opt/pw-browsers/chromium")


@pytest.fixture(scope="session")
def redis_url():
    """A real redis-server on a free port (Valkey/ElastiCache/Memorystore speak the same protocol)."""
    import shutil
    import socket
    import subprocess
    import time

    binary = shutil.which("redis-server") or shutil.which("valkey-server")
    if not binary:
        pytest.skip("redis-server not installed")
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    proc = subprocess.Popen(
        [binary, "--port", str(port), "--save", "", "--appendonly", "no"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(50):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                break
        time.sleep(0.05)
    yield f"redis://127.0.0.1:{port}/0"
    proc.terminate()
    proc.wait(5)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        data_dir=str(tmp_path / "data"),
        anthropic_api_key="test-key",
        google_api_key="test-key",
        aws_region="us-east-1",
        google_cloud_project="test-project",
        playwright_chromium_path=CHROMIUM if Path(CHROMIUM).exists() else "",
        otel_exporter="none",
    )


@pytest.fixture
def container(settings):
    return build_container(settings, adapter_specs={})


@pytest.fixture
def scope(container):
    """Set a RunScope as RunService would, for calling tools directly."""
    token = set_scope(RunScope(user_id="u1", session_id="s1", provider=container.providers["raw"]))
    yield container.providers["raw"]
    reset_scope(token)


class EchoAdapter:
    """A minimal adapter: proves the core contract without any framework."""

    name = "echo"
    description = "test adapter"

    def __init__(self, delay: float = 0.0, tool: str | None = "calculator"):
        self.delay = delay
        self.tool = tool

    def patterns(self) -> list[PatternInfo]:
        return [PatternInfo("single", "echo back", ("none",))]

    def providers(self) -> list[str]:
        return ["raw", "bedrock", "vertex"]

    async def run(self, ctx: RunContext) -> AsyncIterator[Event]:
        from app.tools import ALL_TOOLS

        yield Event(type="agent", agent="echo")
        if self.tool:
            args = {"expression": "2+3"}
            yield Event(type="tool_call", name=self.tool, args=args)
            yield Event(
                type="tool_result", name=self.tool, result=await ALL_TOOLS[self.tool](**args)
            )
        if self.delay:
            await asyncio.sleep(self.delay)
        text = f"echo[{ctx.provider.name}]: {ctx.request.message}"
        yield Event(type="message", agent="echo", text=text)
        yield Event(type="done", output=text)


@pytest.fixture
def client(container):
    container.registry.register(EchoAdapter())
    with TestClient(create_app(container)) as c:
        yield c
