"""ADK model classes per provider branch.

  raw     Gemini(client=genai.Client(api_key))          or AnthropicLlm(client=AsyncAnthropic)
  bedrock LiteLlm("bedrock/converse/<id>")              (ADK has no native Bedrock class)
  vertex  Gemini(client=genai.Client(vertexai=True))    or Claude(client=AsyncAnthropicVertex)

Clients are passed explicitly instead of via GOOGLE_GENAI_USE_VERTEXAI / ANTHROPIC_API_KEY env
vars, so raw and vertex can run side by side in one process.
"""

from collections.abc import Callable

from google.adk.models import BaseLlm

from app.providers.profile import ProviderProfile

# (profile, vendor override, agent role) -> model. Tests inject scripted models per role.
ModelFactory = Callable[[ProviderProfile, str | None, str], BaseLlm]


def default_model_factory(profile: ProviderProfile, vendor: str | None, role: str) -> BaseLlm:
    s = profile.settings
    v = profile.vendor(vendor)
    model_id = profile.model_id(v)
    if v == "converse":
        from google.adk.models.lite_llm import LiteLlm

        return LiteLlm(model=f"bedrock/converse/{model_id}", aws_region_name=s.aws_region)
    if v == "anthropic":
        if profile.name == "vertex":
            from anthropic import AsyncAnthropicVertex
            from google.adk.models.anthropic_llm import Claude

            client = AsyncAnthropicVertex(
                project_id=s.google_cloud_project, region=s.vertex_claude_region
            )
            return Claude(model=model_id, client=client)
        from anthropic import AsyncAnthropic
        from google.adk.models.anthropic_llm import AnthropicLlm

        return AnthropicLlm(model=model_id, client=AsyncAnthropic(api_key=s.anthropic_api_key))
    from google.adk.models.google_llm import Gemini
    from google.genai import Client

    if profile.name == "vertex":
        client = Client(
            vertexai=True, project=s.google_cloud_project, location=s.google_cloud_location
        )
    else:
        client = Client(api_key=s.google_api_key)
    return Gemini(model=model_id, client=client)
