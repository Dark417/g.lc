"""Strands model providers per branch.

raw     AnthropicModel | GeminiModel
bedrock BedrockModel (Converse; Strands' default provider) + optional native Guardrail config
vertex  GeminiModel(client=genai.Client(vertexai=True)) | AnthropicModel with an
        AsyncAnthropicVertex client swapped in (same Messages API surface)
"""

from collections.abc import Callable

from strands.models import Model

from app.providers.profile import ProviderProfile

StrandsModelFactory = Callable[[ProviderProfile, str | None, str], Model]


def default_strands_model(profile: ProviderProfile, vendor: str | None, role: str) -> Model:
    s = profile.settings
    v = profile.vendor(vendor)
    model_id = profile.model_id(v)
    if v == "converse":
        from strands.models.bedrock import BedrockModel

        guardrail = (
            {
                "guardrail_id": s.bedrock_guardrail_id,
                "guardrail_version": s.bedrock_guardrail_version,
                "guardrail_trace": "enabled",
            }
            if s.bedrock_guardrail_id and s.guardrails_enabled
            else {}
        )
        return BedrockModel(model_id=model_id, region_name=s.aws_region, **guardrail)
    if v == "anthropic":
        from strands.models.anthropic import AnthropicModel

        if profile.name == "vertex":
            from anthropic import AsyncAnthropicVertex

            model = AnthropicModel(
                client_args={"api_key": "unused"}, model_id=model_id, max_tokens=4096
            )
            model.client = AsyncAnthropicVertex(
                project_id=s.google_cloud_project, region=s.vertex_claude_region
            )
            return model
        return AnthropicModel(
            client_args={"api_key": s.anthropic_api_key}, model_id=model_id, max_tokens=4096
        )
    from google import genai
    from strands.models.gemini import GeminiModel

    if profile.name == "vertex":
        client = genai.Client(
            vertexai=True, project=s.google_cloud_project, location=s.google_cloud_location
        )
    else:
        client = genai.Client(api_key=s.google_api_key)
    return GeminiModel(client=client, model_id=model_id)
