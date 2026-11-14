"""ADK provider wiring: which model class and which session/memory service each branch gets."""

from google.adk.events import Event
from google.adk.sessions import DatabaseSessionService, Session

from app.adapters.adk.models import default_model_factory
from app.adapters.adk.services import AgentCoreMemoryService, memory_service, session_service
from app.memory.base import MemoryRecord
from app.providers import build_profiles


def test_model_class_per_branch(settings):
    p = build_profiles(settings)
    raw_claude = default_model_factory(p["raw"], "anthropic", "assistant")
    raw_gemini = default_model_factory(p["raw"], "gemini", "assistant")
    bedrock = default_model_factory(p["bedrock"], None, "assistant")
    assert (
        type(raw_claude).__name__ == "AnthropicLlm" and raw_claude.model == settings.anthropic_model
    )
    assert type(raw_gemini).__name__ == "Gemini" and raw_gemini.model == settings.gemini_model
    assert (
        type(bedrock).__name__ == "LiteLlm"
        and bedrock.model == f"bedrock/converse/{settings.bedrock_model_id}"
    )


def test_services_per_branch(settings):
    p = build_profiles(settings)
    assert isinstance(session_service("raw", settings), DatabaseSessionService)
    assert (
        type(memory_service("raw", settings, p["raw"].memory)).__name__ == "InMemoryMemoryService"
    )
    settings.agentcore_memory_id = "mem-1"
    assert isinstance(
        memory_service("bedrock", settings, p["bedrock"].memory), AgentCoreMemoryService
    )
    settings.agent_engine_id = "123"
    assert type(session_service("vertex", settings)).__name__ == "VertexAiSessionService"
    assert type(memory_service("vertex", settings, None)).__name__ == "VertexAiMemoryBankService"


async def test_agentcore_memory_service_bridges_adk():
    calls = {}

    class FakeAgentCore:
        async def add_turns(self, user_id, session_id, turns):
            calls["turns"] = (user_id, session_id, turns)

        async def search(self, user_id, query, k=5):
            return [MemoryRecord("User deploys to us-east-1", 0.9, "agentcore")]

    from google.genai import types

    svc = AgentCoreMemoryService(FakeAgentCore())
    session = Session(
        id="s1",
        app_name="ai_sdk",
        user_id="u1",
        events=[
            Event(
                author="user",
                content=types.Content(
                    role="user", parts=[types.Part(text="I deploy to us-east-1")]
                ),
            ),
            Event(
                author="assistant",
                content=types.Content(role="model", parts=[types.Part(text="Noted.")]),
            ),
        ],
    )
    await svc.add_session_to_memory(session)
    assert calls["turns"] == (
        "u1",
        "s1",
        [("I deploy to us-east-1", "USER"), ("Noted.", "ASSISTANT")],
    )
    found = await svc.search_memory(app_name="ai_sdk", user_id="u1", query="region")
    assert found.memories[0].content.parts[0].text == "User deploys to us-east-1"
