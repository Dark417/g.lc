"""Composition root: the only place that wires settings -> providers -> registry -> service."""

from dataclasses import dataclass

from app.config import Settings, get_settings
from app.core.registry import AdapterRegistry
from app.core.sessions import InMemorySessionRegistry, RedisSessionRegistry, SessionRegistry
from app.providers import build_profiles
from app.providers.profile import ProviderProfile
from app.services.run_service import RunService


@dataclass
class Container:
    settings: Settings
    providers: dict[str, ProviderProfile]
    registry: AdapterRegistry
    sessions: SessionRegistry
    runs: RunService


def build_container(
    settings: Settings | None = None, *, adapter_specs: dict[str, str] | None = None
) -> Container:
    settings = settings or get_settings()
    providers = build_profiles(settings)
    registry = AdapterRegistry(settings, adapter_specs)
    sessions: SessionRegistry
    if settings.redis_url:
        from app.state.cache import redis_client

        sessions = RedisSessionRegistry(
            redis_client(settings.redis_url), settings.session_lock_ttl_s
        )
    else:
        sessions = InMemorySessionRegistry()
    runs = RunService(registry, providers, sessions, settings)
    return Container(settings, providers, registry, sessions, runs)
