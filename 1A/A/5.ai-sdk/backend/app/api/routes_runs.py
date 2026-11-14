"""The one entrance: POST /v1/runs (JSON) and POST /v1/runs/stream (SSE). Same body, same events."""

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.deps import get_container
from app.container import Container
from app.core.adapter import AdapterError
from app.schemas import RunRequest, RunResponse
from app.services.run_service import (
    LockUnavailable,
    ProviderUnavailable,
    SessionBusy,
    SessionMismatch,
    UnknownTarget,
)

router = APIRouter(prefix="/v1", tags=["runs"])


async def _preflight(c: Container, req: RunRequest) -> None:
    try:
        await c.runs.preflight(req)
    except UnknownTarget as e:
        raise HTTPException(404, str(e)) from e
    except (ProviderUnavailable, AdapterError) as e:
        raise HTTPException(400, str(e)) from e
    except (SessionBusy, SessionMismatch) as e:
        raise HTTPException(409, str(e)) from e
    except LockUnavailable as e:  # fail closed: never run two loops on one session
        raise HTTPException(503, str(e)) from e
    except Exception as e:  # adapter failed to import/construct
        raise HTTPException(503, f"framework {req.framework!r} unavailable: {e}") from e


@router.post("/runs", response_model=RunResponse, response_model_exclude_none=True)
async def run(req: RunRequest, c: Container = Depends(get_container)) -> RunResponse:
    await _preflight(c, req)
    return await c.runs.run(req)


@router.post("/runs/stream")
async def run_stream(req: RunRequest, c: Container = Depends(get_container)) -> StreamingResponse:
    await _preflight(c, req)

    async def sse():
        async for event in c.runs.stream(req):
            yield f"data: {json.dumps(event.wire(), default=str)}\n\n"

    return StreamingResponse(sse(), media_type="text/event-stream")
