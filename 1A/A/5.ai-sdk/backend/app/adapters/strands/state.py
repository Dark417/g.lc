"""Strands session managers and hooks.

Session managers persist an agent's messages and state between requests:
  raw / vertex  FileSessionManager                  PRODUCTION (vertex): implement SessionRepository
                                                    on Firestore/GCS + RepositorySessionManager
  bedrock       S3SessionManager                    if STRANDS_S3_SESSION_BUCKET is set
                AgentCoreMemorySessionManager       else if AGENTCORE_MEMORY_ID: short-term events +
                                                    long-term extraction
                FileSessionManager                  otherwise
"""

import logging
from typing import Any

from strands.hooks import (
    AfterToolCallEvent,
    BeforeModelCallEvent,
    BeforeToolCallEvent,
    HookProvider,
    HookRegistry,
)

from app.config import Settings

log = logging.getLogger(__name__)


def session_manager(provider: str, s: Settings, session_id: str, user_id: str) -> Any:
    if provider == "bedrock" and s.strands_s3_session_bucket:
        # S3SessionManager: the same file layout as FileSessionManager, in a bucket. Durable and
        # cheap; no extraction (that is what AgentCore Memory adds).
        from strands.session.s3_session_manager import S3SessionManager

        return S3SessionManager(
            session_id=session_id,
            bucket=s.strands_s3_session_bucket,
            prefix="strands/",
            region_name=s.aws_region,
        )
    if provider == "bedrock" and s.agentcore_memory_id:
        from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
        from bedrock_agentcore.memory.integrations.strands.session_manager import (
            AgentCoreMemorySessionManager,
        )

        config = AgentCoreMemoryConfig(
            memory_id=s.agentcore_memory_id, session_id=session_id, actor_id=user_id
        )
        return AgentCoreMemorySessionManager(config, region_name=s.aws_region)
    from strands.session.file_session_manager import FileSessionManager

    return FileSessionManager(
        session_id=session_id, storage_dir=str(s.data_path / "strands_sessions")
    )


class ToolPolicyHooks(HookProvider):
    """Typed lifecycle hooks: count model calls, deny tools by name, time tool calls.

    Setting `event.cancel_tool` stops the tool and returns the message to the model as an error
    result; the agent loop keeps going.
    """

    def __init__(self, deny: set[str] | None = None, max_model_calls: int = 20):
        self.deny = deny or set()
        self.max_model_calls = max_model_calls
        self.model_calls = 0

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        registry.add_callback(BeforeModelCallEvent, self.before_model)
        registry.add_callback(BeforeToolCallEvent, self.before_tool)
        registry.add_callback(AfterToolCallEvent, self.after_tool)

    def before_model(self, event: BeforeModelCallEvent) -> None:
        self.model_calls += 1
        if self.model_calls > self.max_model_calls:
            raise RuntimeError(f"model call limit ({self.max_model_calls}) exceeded")

    def before_tool(self, event: BeforeToolCallEvent) -> None:
        name = event.tool_use["name"]
        if name in self.deny:
            event.cancel_tool = f"tool {name!r} is disabled by policy"

    def after_tool(self, event: AfterToolCallEvent) -> None:
        log.info("strands tool %s took %.2fs", event.tool_use["name"], event.duration or 0.0)
