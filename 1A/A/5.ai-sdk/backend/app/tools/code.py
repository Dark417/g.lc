"""`run_code`: execute Python in a managed sandbox (AgentCore Code Interpreter).

Only offered on the bedrock branch with AGENTCORE_CODE_INTERPRETER=true. There is deliberately
no local fallback: running model-written code on the API host is the one thing this project
refuses to illustrate. See docs/design/03-cloud-branches.md, "Documented gaps".
"""

import asyncio
from typing import Protocol

from app.core.scope import current_scope

MAX_OUTPUT = 4000


class CodeSandbox(Protocol):
    name: str

    async def execute(self, code: str) -> dict: ...


class AgentCoreCodeInterpreter:
    name = "agentcore_code_interpreter"

    def __init__(self, region: str):
        self.region = region

    def _run(self, code: str) -> dict:
        from bedrock_agentcore.tools.code_interpreter_client import code_session

        with code_session(self.region) as client:
            resp = client.execute_code(code, language="python")
            texts, structured = [], {}
            for event in resp["stream"]:
                result = event.get("result", {})
                structured = result.get("structuredContent") or structured
                texts += [
                    c.get("text", "") for c in result.get("content", []) if c.get("type") == "text"
                ]
            return {
                "stdout": structured.get("stdout", "\n".join(texts))[:MAX_OUTPUT],
                "stderr": structured.get("stderr", "")[:MAX_OUTPUT],
                "exit_code": structured.get("exitCode"),
            }

    async def execute(self, code: str) -> dict:
        return await asyncio.to_thread(self._run, code)


async def run_code(code: str) -> dict:
    """Run Python code in an isolated cloud sandbox and return stdout/stderr.

    Use it for data wrangling or calculations too complex for the calculator.

    Args:
        code: A complete Python program; print() what you need to see.
    """
    sandbox = current_scope().provider.code_sandbox
    if sandbox is None:
        return {"status": "unavailable", "error": "no code sandbox on this provider"}
    try:
        return {"status": "ok", "backend": sandbox.name, **(await sandbox.execute(code))}
    except Exception as e:
        return {"status": "error", "error": f"{type(e).__name__}: {e}"[:500]}
