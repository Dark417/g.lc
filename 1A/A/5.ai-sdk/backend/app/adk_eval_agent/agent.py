from app.adapters.adk.models import default_model_factory
from app.adapters.adk.patterns import AdkKit, single
from app.config import get_settings
from app.core.scope import RunScope, set_default_scope
from app.providers import build_profiles

_settings = get_settings()
_profile = build_profiles(_settings)["raw"]
set_default_scope(RunScope(user_id="adk-eval", session_id="adk-eval", provider=_profile))

root_agent = single(
    AdkKit(
        profile=_profile,
        settings=_settings,
        options={"mcp": False},
        model_for=lambda role: default_model_factory(_profile, None, role),
    )
)
