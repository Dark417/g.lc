"""CLI: score targets on the eval cases and print a matrix.

  uv run python -m app.evals.run --targets adk:single:raw,langgraph:react:raw,strands:single:raw,claude:messages_api:raw
  uv run python -m app.evals.run --targets strands:single:bedrock --judge
  uv run python -m app.evals.run --targets adk:single:vertex --vertex   # + Vertex Gen AI eval

Needs real credentials for the providers in --targets. Writes evals/out/<timestamp>.json.
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

from app.config import BACKEND_DIR, Settings, get_settings
from app.container import build_container
from app.evals.harness import evaluate, load_cases, summary_table

DEFAULT_TARGETS = "adk:single:raw,langgraph:react:raw,strands:single:raw,claude:messages_api:raw"


def claude_judge(settings: Settings):
    """An LLM-as-judge on the Claude API. Swap the client for Bedrock or Vertex the same way the
    messages_api pattern does."""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def judge(prompt: str) -> str:
        msg = await client.messages.create(
            model=settings.judge_model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in msg.content if b.type == "text")

    return judge


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", default=DEFAULT_TARGETS)
    parser.add_argument("--cases", default=str(BACKEND_DIR / "evals" / "cases.yaml"))
    parser.add_argument(
        "--judge", action="store_true", help="add an LLM-as-judge score (Claude API)"
    )
    parser.add_argument("--vertex", action="store_true", help="also score with Vertex Gen AI eval")
    args = parser.parse_args()

    settings = get_settings()
    container = build_container(settings)
    cases = load_cases(Path(args.cases))
    judge = claude_judge(settings) if args.judge else None
    rows = await evaluate(container.runs, args.targets.split(","), cases, judge)

    print(summary_table(rows))
    for r in rows:
        if r["error"]:
            print(f"  ! {r['target']} {r['case']}: {r['error'][:200]}")
    out = BACKEND_DIR / "evals" / "out"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{time.strftime('%Y%m%d-%H%M%S')}.json"
    path.write_text(json.dumps(rows, indent=2, default=str))
    print(f"\nwrote {path}")
    if args.vertex:
        from app.evals.vertex_eval import run_vertex_eval

        print(run_vertex_eval(rows, cases, settings))


if __name__ == "__main__":
    asyncio.run(main())
