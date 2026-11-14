"""`python -m app.evals.run`: run the eval suite against the real agent and print a report."""

import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from app.agents.factory import build_options
from app.config import get_settings
from app.db.database import init_db
from app.evals.harness import build_claude_judge, format_report, load_cases, run_suite
from app.rag.factory import build_retriever
from app.services.chat_service import ClaudeChatService

CASES = Path(__file__).resolve().parents[2] / "evals" / "cases.json"


async def main() -> int:
    settings = get_settings()
    Path(settings.workdir).mkdir(parents=True, exist_ok=True)
    init_db(settings.db_path)
    service = ClaudeChatService(
        options=build_options(settings, retriever=build_retriever(settings))
    )

    async def runner(message: str):
        # fresh session per case: no cross-talk between cases
        return await service.chat(user_id="eval", session_id=None, message=message)

    judge = build_claude_judge(settings.judge_model, settings.anthropic_api_key)
    results = await run_suite(load_cases(CASES), runner, judge)
    print(format_report(results))

    out = Path(settings.workdir).parent / "eval-report.json"
    out.write_text(json.dumps([asdict(r) for r in results], indent=2, default=str))
    print(f"\nreport: {out}")
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
