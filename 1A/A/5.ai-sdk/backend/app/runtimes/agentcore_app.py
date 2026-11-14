"""Host the whole service on Amazon Bedrock AgentCore Runtime.

AgentCore Runtime runs a container per session (microVM isolation) and calls:
  POST /invocations   payload -> our RunRequest JSON; we stream neutral events back (SSE)
  GET  /ping          health
Every framework in this project becomes one AgentCore agent, because RunService is the entrance.

Run locally:   python -m app.runtimes.agentcore_app        (port 8080)
Deploy:        see infra/aws/README.md (agentcore configure / agentcore launch)
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from app.container import build_container
from app.schemas import RunRequest
from app.telemetry import setup_telemetry

app = BedrockAgentCoreApp()
_container = build_container()
setup_telemetry(_container.settings)


@app.entrypoint
async def invoke(payload: dict, context=None):
    """Async generator entrypoint: AgentCore streams each yielded item to the caller."""
    req = RunRequest(**{"provider": "bedrock", **payload})
    if context is not None and getattr(context, "session_id", None) and not req.session_id:
        # AgentCore's runtime session id doubles as our session id.
        req.session_id = context.session_id.replace("-", "")[:32]
    try:
        await _container.runs.preflight(req)
    except Exception as e:
        yield {"type": "error", "message": str(e)}
        return
    async for event in _container.runs.stream(req):
        yield event.wire()


if __name__ == "__main__":
    app.run()
