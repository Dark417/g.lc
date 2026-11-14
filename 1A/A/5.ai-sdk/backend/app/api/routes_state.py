"""State API: history, checkpoints, fork, long-term memories, forget.

Generic routes; each framework answers from its own store via optional StateOps methods.
See docs/design/07-state-and-memory.md.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_container
from app.container import Container
from app.core.adapter import AdapterError
from app.core.sessions import SessionRecord

router = APIRouter(prefix="/v1", tags=["state"])


class ForkIn(BaseModel):
    checkpoint_id: str


async def _session(c: Container, session_id: str) -> SessionRecord:
    rec = await c.sessions.get(session_id)
    if rec is None:
        raise HTTPException(404, "session not found")
    return rec


def _op(c: Container, framework: str, name: str):
    adapter = c.registry.get(framework)
    fn = getattr(adapter, name, None)
    if fn is None:
        raise HTTPException(501, f"{framework} does not implement {name}")

    async def call(*args):
        try:
            return await fn(*args)
        except AdapterError as e:
            raise HTTPException(400, str(e)) from e

    return call


@router.get("/sessions")
async def list_sessions(user_id: str | None = None, c: Container = Depends(get_container)):
    return [r.summary() for r in await c.sessions.list(user_id)]


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, c: Container = Depends(get_container)):
    rec = await _session(c, session_id)
    return {**rec.summary(), "last_output": rec.last_output}


@router.get("/sessions/{session_id}/history")
async def history(session_id: str, c: Container = Depends(get_container)):
    rec = await _session(c, session_id)
    return await _op(c, rec.framework, "history")(rec, c.providers[rec.provider])


@router.get("/sessions/{session_id}/checkpoints")
async def checkpoints(session_id: str, c: Container = Depends(get_container)):
    rec = await _session(c, session_id)
    return await _op(c, rec.framework, "checkpoints")(rec, c.providers[rec.provider])


@router.post("/sessions/{session_id}/fork")
async def fork(session_id: str, body: ForkIn, c: Container = Depends(get_container)):
    rec = await _session(c, session_id)
    fn = _op(c, rec.framework, "fork")
    new = SessionRecord(
        id=uuid.uuid4().hex,
        user_id=rec.user_id,
        framework=rec.framework,
        pattern=rec.pattern,
        provider=rec.provider,
    )
    await fn(rec, c.providers[rec.provider], body.checkpoint_id, new)
    await c.sessions.save(new)
    return {
        "session_id": new.id,
        "forked_from": {"session_id": rec.id, "checkpoint_id": body.checkpoint_id},
    }


@router.post("/sessions/{session_id}/rewind")
async def rewind(session_id: str, body: ForkIn, c: Container = Depends(get_container)):
    """Roll the session back to before `checkpoint_id`, in place (ADK: Runner.rewind_async)."""
    rec = await _session(c, session_id)
    await _op(c, rec.framework, "rewind")(rec, c.providers[rec.provider], body.checkpoint_id)
    return {"session_id": rec.id, "rewound_before": body.checkpoint_id}


@router.delete("/sessions/{session_id}", status_code=204)
async def forget(session_id: str, c: Container = Depends(get_container)):
    rec = await _session(c, session_id)
    fn = getattr(c.registry.get(rec.framework), "forget", None)
    if fn is not None:
        await fn(rec, c.providers[rec.provider])
    await c.sessions.delete(session_id)


@router.get("/users/{user_id}/memories")
async def memories(
    user_id: str,
    framework: str | None = None,
    provider: str = "raw",
    query: str = "",
    c: Container = Depends(get_container),
):
    """Long-term memories. With `framework`, as that framework stores them; without, the neutral
    memory behind the remember/recall tools (SQLite / AgentCore / Memory Bank)."""
    if provider not in c.providers:
        raise HTTPException(404, f"unknown provider {provider!r}")
    profile = c.providers[provider]
    if framework:
        return await _op(c, framework, "memories")(user_id, profile, query)
    return [m.as_dict() for m in await profile.memory.search(user_id, query, k=20)]
