"""Wire contract: one request shape and one event stream for every framework.

See docs/design/01-architecture.md, "Event model".
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

Framework = Literal["adk", "langgraph", "strands", "claude"]
Provider = Literal["raw", "bedrock", "vertex"]
EventType = Literal[
    "session", "agent", "tool_call", "tool_result", "delta", "message", "state", "interrupt",
    "done", "error",
]  # fmt: skip


class RunRequest(BaseModel):
    framework: str = Field(examples=["adk"])
    pattern: str = Field(examples=["single"])
    provider: str = Field(default="raw", examples=["raw"])
    message: str = Field(default="", examples=["What is 17% of 2340?"])
    session_id: str | None = None
    user_id: str = "demo-user"
    vendor: Literal["anthropic", "gemini"] | None = Field(
        default=None, description="Model vendor override where the provider offers both"
    )
    resume: dict[str, Any] | None = Field(
        default=None, description='Resume a paused run, e.g. LangGraph hitl: {"approve": true}'
    )
    options: dict[str, Any] = Field(default_factory=dict)


class Event(BaseModel):
    type: EventType
    agent: str | None = None
    name: str | None = None
    id: str | None = None
    args: Any = None
    result: Any = None
    text: str | None = None
    data: Any = None
    output: Any = None
    message: str | None = None

    def wire(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


class RunResponse(BaseModel):
    session_id: str
    output: Any = None
    events: list[dict[str, Any]]


class PatternOut(BaseModel):
    name: str
    description: str
    components: list[str]


class FrameworkOut(BaseModel):
    name: str
    description: str
    providers: list[str]
    patterns: list[PatternOut]
    available: bool = True
    error: str | None = None


class ProviderOut(BaseModel):
    name: str
    available: bool
    missing: list[str]
    services: dict[str, str]


class CatalogOut(BaseModel):
    frameworks: list[FrameworkOut]
    providers: list[ProviderOut]
    tools: list[dict[str, str]]
    mcp_servers: list[str]
