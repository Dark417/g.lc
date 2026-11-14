"""`run_cli`: let an agent run a few harmless shell programs, safely.

Defense in depth (docs/design/04-tools-mcp-rag-state.md, "CLI tool safety"):
  1. Reject shell metacharacters outright, even though no shell is used.
  2. shlex.split -> argv; exec directly (no shell); allowlisted programs, each with an argument
     validator; file arguments must resolve inside the corpus directory.
  3. Timeout, output truncated.
  4. Framework-level approval on top: LangGraph `hitl` interrupts before it runs; the Claude
     adapter checks it in `can_use_tool`; the ADK adapter in `before_tool_callback`.
"""

import asyncio
import shlex
from collections.abc import Callable
from pathlib import Path

from app.core.scope import current_scope

MAX_OUTPUT = 4000
_FORBIDDEN = set(";|&`$<>(){}\n\\")


def _flags_only(allowed: set[str]) -> Callable[[list[str], Path], None]:
    def check(args: list[str], root: Path) -> None:
        bad = [a for a in args if a not in allowed]
        if bad:
            raise ValueError(f"arguments not allowed: {bad}; allowed: {sorted(allowed)}")

    return check


def _files(flags: set[str]) -> Callable[[list[str], Path], None]:
    def check(args: list[str], root: Path) -> None:
        for a in args:
            if a.startswith("-"):
                if a not in flags:
                    raise ValueError(f"flag {a!r} not allowed; allowed: {sorted(flags)}")
                continue
            p = (root / a).resolve()
            if not p.is_relative_to(root.resolve()):
                raise ValueError(f"path {a!r} is outside the corpus directory")

    return check


def _date(args: list[str], root: Path) -> None:
    for a in args:
        if not (a.startswith("+") or a in {"-u", "-I", "-R"}):
            raise ValueError("date accepts only -u, -I, -R and +FORMAT (never -s)")


def _any(args: list[str], root: Path) -> None:
    return None


ALLOWED: dict[str, Callable[[list[str], Path], None]] = {
    "date": _date,
    "uname": _flags_only({"-a", "-s", "-r", "-m", "-n"}),
    "whoami": _flags_only(set()),
    "pwd": _flags_only(set()),
    "echo": _any,
    "ls": _files({"-l", "-a", "-la", "-1", "-lh"}),
    "cat": _files(set()),
    "head": _files({"-n", "-5", "-10", "-20"}),
    "wc": _files({"-l", "-w", "-c"}),
    "python": _flags_only({"--version"}),
}


def parse_command(command: str, root: Path) -> list[str]:
    if any(c in _FORBIDDEN for c in command):
        raise ValueError("shell metacharacters are not allowed (no pipes, redirects, or chaining)")
    argv = shlex.split(command)
    if not argv:
        raise ValueError("empty command")
    program, args = argv[0], argv[1:]
    if program not in ALLOWED:
        raise ValueError(f"program {program!r} is not allowed; allowed: {sorted(ALLOWED)}")
    if program == "head":  # `head -n 5 file`: let the count through as a value of -n
        args = [
            a for i, a in enumerate(args) if not (i > 0 and args[i - 1] == "-n" and a.isdigit())
        ]
    ALLOWED[program](args, root)
    return argv


async def run_cli(command: str) -> dict:
    """Run one allowlisted command-line program and return its output.

    Allowed: date, uname, whoami, pwd, echo, ls, cat, head, wc, python --version.
    File arguments are relative to the knowledge-base directory (e.g. `ls`, `wc -l adk.md`).
    No pipes, redirects, or chaining.

    Args:
        command: The command line, e.g. "date -u" or "wc -w langgraph.md".
    """
    settings = current_scope().provider.settings
    root = settings.corpus_path
    try:
        argv = parse_command(command, root)
    except ValueError as e:
        return {"status": "rejected", "error": str(e)}
    proc = await asyncio.create_subprocess_exec(
        *argv,
        cwd=root,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=settings.subprocess_env(),
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=settings.cli_timeout_s)
    except TimeoutError:
        proc.kill()
        return {"status": "timeout", "command": command}
    text = out.decode(errors="replace")
    return {
        "status": "ok" if proc.returncode == 0 else "error",
        "exit_code": proc.returncode,
        "output": text[:MAX_OUTPUT] + ("…[truncated]" if len(text) > MAX_OUTPUT else ""),
    }
