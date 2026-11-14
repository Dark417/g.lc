"""Build the ADK agent and App from the container. Used by the API runner and by ADK's dev UI."""

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.plugins.save_files_as_artifacts_plugin import SaveFilesAsArtifactsPlugin
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.agents.callbacks import make_before_agent, make_before_tool, save_to_memory
from app.agents.prompts import INSTRUCTION
from app.agents.tools import build_tools
from app.agents.toolsets import RoleGatedToolset


def build_agent(c, *, model=None) -> LlmAgent:
    user_tools, admin_tools = build_tools(c)
    admin_toolset = RoleGatedToolset(admin_tools)
    return LlmAgent(
        name="compliance_agent",
        model=model or c.settings.model,
        description="Reviews proposals against compliance rules and documents.",
        instruction=INSTRUCTION,
        tools=[PreloadMemoryTool(), *user_tools, admin_toolset],
        generate_content_config=types.GenerateContentConfig(temperature=0.2),
        before_agent_callback=make_before_agent(c.settings.admins),
        before_tool_callback=make_before_tool(admin_toolset.names),
        after_agent_callback=save_to_memory,
    )


def build_app(c, *, model=None) -> App:
    return App(
        name=c.settings.app_name,
        root_agent=build_agent(c, model=model),
        # Files attached to a chat message become session artifacts that tools can load.
        # attach_file_reference=False: our tools load artifacts explicitly.
        plugins=[SaveFilesAsArtifactsPlugin(attach_file_reference=False)],
    )
