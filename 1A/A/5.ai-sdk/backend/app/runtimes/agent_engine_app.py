"""Deploy the ADK `single` agent to Vertex AI Agent Engine (managed ADK hosting).

Agent Engine hosts *one agent* (not our FastAPI entrance): AdkApp wraps the ADK agent and gives
it managed Sessions and Memory Bank, autoscaling, and query/stream endpoints. This is the GCP
counterpart of agentcore_app.py, but ADK-specific.

  python -m app.runtimes.agent_engine_app --staging-bucket gs://my-bucket            # deploy
  python -m app.runtimes.agent_engine_app --local "What is 17% of 2340?"           # local AdkApp
"""

import argparse
import asyncio

from app.adapters.adk.models import default_model_factory
from app.adapters.adk.patterns import AdkKit, single
from app.config import get_settings
from app.core.scope import RunScope, set_default_scope
from app.providers import build_profiles


def build_adk_app():
    from vertexai import agent_engines

    settings = get_settings()
    profile = build_profiles(settings)["vertex"]
    # Agent Engine calls the agent directly, not through RunService, so tools get a default scope.
    set_default_scope(RunScope(user_id="agent-engine", session_id="agent-engine", provider=profile))
    root = single(
        AdkKit(
            profile=profile,
            settings=settings,
            options={"mcp": False},  # no subprocess MCP servers inside Agent Engine
            model_for=lambda role: default_model_factory(profile, "gemini", role),
        )
    )
    return agent_engines.AdkApp(agent=root, enable_tracing=True)


def deploy(staging_bucket: str) -> str:
    import vertexai

    s = get_settings()
    client = vertexai.Client(project=s.google_cloud_project, location=s.google_cloud_location)
    remote = client.agent_engines.create(
        agent=build_adk_app(),
        config={
            "display_name": "ai-sdk-adk-single",
            "staging_bucket": staging_bucket,
            "requirements": [
                "google-adk[extensions]>=2.9",
                "google-cloud-aiplatform[agent_engines]",
                "pydantic-settings",
                "aiosqlite",
                "pyyaml",
                "boto3",
                "bedrock-agentcore",
                "playwright",
            ],
            "extra_packages": ["app"],
            "env_vars": {"GOOGLE_CLOUD_LOCATION": s.google_cloud_location},
        },
    )
    return remote.api_resource.name


async def local_query(message: str) -> None:
    app = build_adk_app()
    async for event in app.async_stream_query(user_id="local", message=message):
        print(event)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging-bucket")
    parser.add_argument("--local")
    args = parser.parse_args()
    if args.local:
        asyncio.run(local_query(args.local))
    elif args.staging_bucket:
        print("deployed:", deploy(args.staging_bucket))
    else:
        parser.error("pass --staging-bucket gs://... to deploy, or --local 'message'")
