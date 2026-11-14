"""RunService: the single use case behind the single entrance.

  resolve target -> session lock -> guardrail(in) -> RunScope -> adapter.run() -> guardrail(out)

Validation that can fail with an HTTP status (unknown target, provider not configured, session
busy or bound elsewhere) happens in `preflight`, before a stream starts.
"""

import logging
import time
from collections.abc import AsyncIterator

from opentelemetry.trace import Status, StatusCode

from app.config import Settings
from app.core.adapter import AdapterError, RunContext
from app.core.registry import AdapterRegistry, UnknownTarget
from app.core.scope import RunScope, reset_scope, set_scope
from app.core.sessions import LockUnavailable, SessionBusy, SessionMismatch, SessionRegistry
from app.providers.profile import ProviderProfile
from app.schemas import Event, RunRequest, RunResponse
from app.telemetry import run_duration, runs_counter, tracer

log = logging.getLogger(__name__)


class ProviderUnavailable(ValueError):
    pass


__all__ = [
    "LockUnavailable", "ProviderUnavailable", "RunService", "SessionBusy", "SessionMismatch",
    "UnknownTarget",
]  # fmt: skip


class RunService:
    def __init__(
        self,
        registry: AdapterRegistry,
        providers: dict[str, ProviderProfile],
        sessions: SessionRegistry,
        settings: Settings,
    ):
        self.registry = registry
        self.providers = providers
        self.sessions = sessions
        self.settings = settings

    async def preflight(self, req: RunRequest) -> None:
        if req.provider not in self.providers:
            raise UnknownTarget(
                f"unknown provider {req.provider!r}; known: {', '.join(self.providers)}"
            )
        self.registry.resolve(req.framework, req.pattern, req.provider)
        missing = self.providers[req.provider].missing()
        if missing:
            raise ProviderUnavailable(
                f"provider {req.provider!r} is not configured: set {', '.join(missing)}"
            )
        if not req.message and not req.resume:
            raise AdapterError("message is required (or resume, to continue a paused run)")
        await self.sessions.check(req)

    async def stream(self, req: RunRequest) -> AsyncIterator[Event]:
        """Yield the run's events. Call `preflight` first to turn errors into HTTP statuses."""
        adapter = self.registry.resolve(req.framework, req.pattern, req.provider)
        profile = self.providers[req.provider]
        target = {"framework": req.framework, "pattern": req.pattern, "provider": req.provider}
        started, outcome = time.perf_counter(), "ok"
        try:
            async with self.sessions.acquire(req) as record:
                yield Event(type="session", data={"session_id": record.id, **target})
                with tracer.start_as_current_span("agent.run") as span:
                    span.set_attributes(
                        {
                            "agent.framework": req.framework,
                            "agent.pattern": req.pattern,
                            "agent.provider": req.provider,
                            "session.id": record.id,
                            "enduser.id": req.user_id,
                        }
                    )
                    async for event in self._guarded_run(adapter, req, profile, record):
                        if event.type == "error":
                            outcome = "error"
                            span.set_status(Status(StatusCode.ERROR, event.message or ""))
                        elif event.type == "interrupt":
                            outcome = "interrupted"
                        yield event
        except (SessionBusy, SessionMismatch, LockUnavailable) as e:
            outcome = "rejected"
            yield Event(type="error", message=str(e))
        finally:
            attrs = {**target, "outcome": outcome}
            runs_counter.add(1, attrs)
            run_duration.record(time.perf_counter() - started, attrs)

    async def _guarded_run(self, adapter, req, profile, record) -> AsyncIterator[Event]:
        guard = profile.guardrail
        if req.message:
            verdict = await guard.check(req.message, "INPUT")
            if not verdict.allowed:
                yield Event(
                    type="error", message=f"blocked by {guard.name}: {', '.join(verdict.reasons)}"
                )
                return
        ctx = RunContext(request=req, provider=profile, session=record, settings=self.settings)
        token = set_scope(RunScope(user_id=req.user_id, session_id=record.id, provider=profile))
        try:
            async for event in adapter.run(ctx):
                if event.type == "done":
                    event = await self._screen_output(guard, event)
                    record.turns += 1
                    record.last_output = event.output
                yield event
        except AdapterError as e:
            yield Event(type="error", message=str(e))
        except Exception as e:  # the stream must end with a readable error, not a dropped socket
            log.exception("run failed: %s", req.model_dump(exclude={"message"}))
            yield Event(type="error", message=f"{type(e).__name__}: {e}"[:1000])
        finally:
            reset_scope(token)

    async def _screen_output(self, guard, event: Event) -> Event:
        if not isinstance(event.output, str) or not event.output:
            return event
        verdict = await guard.check(event.output, "OUTPUT")
        if not verdict.allowed:
            return Event(
                type="done",
                output="[answer withheld by guardrail]",
                data={"guardrail": verdict.reasons},
            )
        if verdict.text != event.output:
            return event.model_copy(
                update={"output": verdict.text, "data": {"guardrail": verdict.reasons}}
            )
        return event

    async def run(self, req: RunRequest) -> RunResponse:
        events = [e async for e in self.stream(req)]
        session_id = next(
            (e.data["session_id"] for e in events if e.type == "session"), req.session_id or ""
        )
        output = next((e.output for e in reversed(events) if e.type == "done"), None)
        return RunResponse(session_id=session_id, output=output, events=[e.wire() for e in events])
