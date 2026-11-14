"""LangChain chat model classes per provider branch.

raw     ChatAnthropic | ChatGoogleGenerativeAI
bedrock ChatBedrockConverse            (langchain-aws, Converse API, any Bedrock model)
vertex  ChatVertexAI | ChatAnthropicVertex (langchain-google-vertexai; Claude via Model Garden)
"""

from collections.abc import Callable

from langchain_core.language_models import BaseChatModel

from app.providers.profile import ProviderProfile

ChatModelFactory = Callable[[ProviderProfile, str | None, str], BaseChatModel]


def default_chat_model(profile: ProviderProfile, vendor: str | None, role: str) -> BaseChatModel:
    s = profile.settings
    v = profile.vendor(vendor)
    model_id = profile.model_id(v)
    if v == "converse":
        from langchain_aws import ChatBedrockConverse

        return ChatBedrockConverse(model=model_id, region_name=s.aws_region)
    if profile.name == "vertex":
        if v == "anthropic":
            from langchain_google_vertexai.model_garden import ChatAnthropicVertex

            return ChatAnthropicVertex(
                model_name=model_id, project=s.google_cloud_project, location=s.vertex_claude_region
            )
        from langchain_google_vertexai import ChatVertexAI

        return ChatVertexAI(
            model=model_id, project=s.google_cloud_project, location=s.google_cloud_location
        )
    if v == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=model_id, api_key=s.anthropic_api_key, max_tokens=4096)
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(model=model_id, google_api_key=s.google_api_key)
