"""Discovery: which frameworks, patterns, providers, tools, and MCP servers exist right now."""

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.container import Container
from app.mcp.clients import server_specs
from app.schemas import CatalogOut, FrameworkOut, PatternOut, ProviderOut
from app.tools import describe

router = APIRouter(prefix="/v1", tags=["catalog"])


@router.get("/catalog", response_model=CatalogOut)
async def catalog(c: Container = Depends(get_container)) -> CatalogOut:
    frameworks = []
    for name in c.registry.names():
        try:
            a = c.registry.get(name)
        except Exception as e:
            frameworks.append(
                FrameworkOut(
                    name=name,
                    description="",
                    providers=[],
                    patterns=[],
                    available=False,
                    error=f"{type(e).__name__}: {e}"[:300],
                )
            )
            continue
        frameworks.append(
            FrameworkOut(
                name=a.name,
                description=a.description,
                providers=a.providers(),
                patterns=[
                    PatternOut(
                        name=p.name, description=p.description, components=list(p.components)
                    )
                    for p in a.patterns()
                ],
            )
        )
    providers = [
        ProviderOut(name=p.name, available=p.available, missing=p.missing(), services=p.services())
        for p in c.providers.values()
    ]
    return CatalogOut(
        frameworks=frameworks,
        providers=providers,
        tools=describe(),
        mcp_servers=[s.name for s in server_specs(c.settings)],
    )
