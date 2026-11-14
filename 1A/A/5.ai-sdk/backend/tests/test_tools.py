"""Neutral tools, called directly inside a RunScope."""

from pathlib import Path

import pytest

from app.rag.local import LocalRetriever
from app.tools import tools_for
from app.tools.basic import calculator, current_time, evaluate
from app.tools.browser import BlockedUrl, browse, check_url
from app.tools.cli import parse_command, run_cli
from app.tools.code import run_code
from app.tools.knowledge import recall, remember, search_docs


async def test_calculator():
    assert (await calculator("0.17 * 2340"))["result"] == 397.8
    assert evaluate("sqrt(16) + 2^3") == 12
    assert (await calculator("__import__('os')"))["status"] == "error"
    assert (await calculator("9 ** 999999"))["status"] == "error"


async def test_current_time():
    assert (await current_time("UTC"))["iso"].endswith("+00:00")
    assert (await current_time("Mars/Olympus"))["status"] == "error"


@pytest.mark.parametrize(
    "cmd",
    [
        "rm -rf /",
        "date -s 2020-01-01",
        "ls; whoami",
        "cat ../../etc/passwd",
        "echo $(id)",
        "python -c 1",
    ],
)
def test_cli_rejects(cmd, settings):
    with pytest.raises(ValueError):
        parse_command(cmd, settings.corpus_path)


def test_cli_allows(settings):
    assert parse_command("wc -l adk.md", settings.corpus_path) == ["wc", "-l", "adk.md"]
    assert parse_command("head -n 3 mcp.md", settings.corpus_path)[0] == "head"


async def test_run_cli_executes(scope):
    out = await run_cli("ls")
    assert out["status"] == "ok" and "adk.md" in out["output"]
    assert (await run_cli("rm x"))["status"] == "rejected"


async def test_search_docs_local(scope):
    out = await search_docs("AgentCore Memory long-term strategies namespaces")
    assert out["backend"] == "local"
    assert out["passages"][0]["source"].startswith("agentcore.md")


def test_local_retriever_chunks_corpus(settings):
    r = LocalRetriever(settings.corpus_path)
    assert len(r) > 20  # split by heading


async def test_memory_roundtrip(scope):
    await remember("User deploys to us-east-1")
    await remember("User prefers Strands")
    out = await recall("which region do they deploy to")
    assert out["memories"][0]["text"] == "User deploys to us-east-1"


async def test_browse_blocks_private_and_non_http(scope):
    for url in ["file:///etc/passwd", "http://127.0.0.1:8000/", "http://169.254.169.254/latest/"]:
        assert (await browse(url))["status"] == "blocked"


async def test_allowlist():
    with pytest.raises(BlockedUrl):
        await check_url("https://evil.test/", ["example.com"], allow_private=True)
    await check_url("https://docs.example.com/", ["example.com"], allow_private=True)


async def test_run_code_unavailable_on_raw(scope):
    assert (await run_code("print(1)"))["status"] == "unavailable"
    assert "run_code" not in [f.__name__ for f in tools_for(scope)]


@pytest.mark.browser
async def test_browse_local_chromium(scope, tmp_path: Path):
    """Real Chromium against a local page (private address allowed for this test only)."""
    import threading
    from functools import partial
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    if not scope.settings.playwright_chromium_path:
        pytest.skip("no Chromium available")
    (tmp_path / "index.html").write_text("<title>Hello Agents</title><a href='/x'>x</a>Body text")
    server = HTTPServer(
        ("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(tmp_path))
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    scope.browser.allow_private = True
    try:
        out = await browse(f"http://127.0.0.1:{server.server_port}/")
    finally:
        scope.browser.allow_private = False
        server.shutdown()
    assert out["status"] == "ok", out
    assert out["title"] == "Hello Agents" and "Body text" in out["text"]
