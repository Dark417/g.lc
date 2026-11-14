"""Build the three provider profiles. Managed services are used only when configured; otherwise
the local implementation stands in, so you can adopt AWS or GCP one service at a time."""

from app.config import Settings
from app.guardrails.base import Guardrail, NoGuardrail
from app.guardrails.local import LocalGuardrail
from app.memory.local import SqliteMemory
from app.providers.profile import ProviderProfile
from app.rag.local import LocalRetriever
from app.tools.browser import LocalBrowser

PROVIDERS = ("raw", "bedrock", "vertex")


def build_profiles(settings: Settings) -> dict[str, ProviderProfile]:
    local_rag = LocalRetriever(settings.corpus_path)
    local_memory = SqliteMemory(settings.data_path / "memory.db")
    local_browser = LocalBrowser(settings.playwright_chromium_path)
    local_guard: Guardrail = LocalGuardrail() if settings.guardrails_enabled else NoGuardrail()

    raw = ProviderProfile(
        name="raw",
        settings=settings,
        retriever=local_rag,
        memory=local_memory,
        browser=local_browser,
        guardrail=local_guard,
    )
    return {"raw": raw, "bedrock": _bedrock(settings, raw), "vertex": _vertex(settings, raw)}


def _bedrock(s: Settings, local: ProviderProfile) -> ProviderProfile:
    region = s.aws_region or "us-east-1"
    retriever, memory, browser, guard, sandbox = (
        local.retriever, local.memory, local.browser, local.guardrail, None,
    )  # fmt: skip
    if s.bedrock_kb_id:
        from app.rag.bedrock_kb import BedrockKbRetriever

        retriever = BedrockKbRetriever(s.bedrock_kb_id, region)
    if s.agentcore_memory_id:
        from app.memory.agentcore import AgentCoreMemory

        memory = AgentCoreMemory(s.agentcore_memory_id, region)
    if s.agentcore_browser:
        from app.tools.browser import AgentCoreBrowser

        browser = AgentCoreBrowser(region)
    if s.agentcore_code_interpreter:
        from app.tools.code import AgentCoreCodeInterpreter

        sandbox = AgentCoreCodeInterpreter(region)
    if s.bedrock_guardrail_id and s.guardrails_enabled:
        from app.guardrails.bedrock import BedrockGuardrail

        guard = BedrockGuardrail(s.bedrock_guardrail_id, s.bedrock_guardrail_version, region)
    return ProviderProfile(
        name="bedrock",
        settings=s,
        retriever=retriever,
        memory=memory,
        browser=browser,
        guardrail=guard,
        code_sandbox=sandbox,
        notes={"model": "bedrock converse", "region": region},
    )


def _vertex(s: Settings, local: ProviderProfile) -> ProviderProfile:
    retriever, memory, guard = local.retriever, local.memory, local.guardrail
    if s.vertex_rag_corpus:
        from app.rag.vertex_rag import VertexRagRetriever

        retriever = VertexRagRetriever(
            s.vertex_rag_corpus, s.google_cloud_project, s.google_cloud_location
        )
    if s.agent_engine_id:
        from app.memory.vertex_bank import VertexMemoryBank

        memory = VertexMemoryBank(
            s.agent_engine_name, s.google_cloud_project, s.google_cloud_location
        )
    if s.model_armor_template and s.guardrails_enabled:
        from app.guardrails.model_armor import ModelArmorGuardrail

        guard = ModelArmorGuardrail(s.model_armor_template)
    return ProviderProfile(
        name="vertex",
        settings=s,
        retriever=retriever,
        memory=memory,
        browser=local.browser,  # GCP has no managed browser; see docs/design/03
        guardrail=guard,
        notes={"model": "vertex ai", "location": s.google_cloud_location},
    )
