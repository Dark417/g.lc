"""Thin inbound adapter: GET /principles/ lists demos, GET /principles/{name} runs one.

- Names match the Java PrinciplesCatalog so both apps answer the same URLs (Part C names are Java only).
- No I/O, no cloud: every demo is in-memory.
- Catch: demos are pure functions of fresh objects, so repeated calls return the same output.
"""

from collections.abc import Callable

from fastapi import APIRouter, HTTPException

from app.x02_01_principles import general, solid

router = APIRouter()

# Doc order: Part A, then Part B.
DEMOS: dict[str, Callable[[], str]] = {
    "srp": solid.srp_demo,
    "ocp": solid.ocp_demo,
    "lsp": solid.lsp_demo,
    "isp": solid.isp_demo,
    "dip": solid.dip_demo,
    "dry": general.dry_demo,
    "kiss": general.kiss_demo,
    "yagni": general.yagni_demo,
    "soc": general.soc_demo,
    "cohesion": general.cohesion_demo,
    "composition": general.composition_demo,
    "interface": general.interface_demo,
    "encapsulate": general.encapsulate_demo,
    "demeter": general.lod_demo,
    "tell": general.tda_demo,
    "cqs": general.cqs_demo,
    "failfast": general.failfast_demo,
    "pola": general.pola_demo,
}

JAVA_ONLY: frozenset[str] = frozenset({"ioc", "di", "aop", "autoconfig", "pojo", "config", "template"})


@router.get("/")
def list_demos() -> list[str]:
    # Lists demo names in doc order.
    # Use to discover valid {name} values.
    # Catch: Part C (Spring) names are served by the Java app only.
    return list(DEMOS)


@router.get("/{name}")
def show(name: str) -> dict[str, str]:
    # Runs one principle's demo and returns its trace.
    # Use: curl localhost:8000/principles/lsp
    # Catch: unknown names are a 404 with the valid list (fail fast with a clear message).
    if name in JAVA_ONLY:
        raise HTTPException(status_code=404, detail=f"'{name}' is a Spring principle; see the Java app")
    demo = DEMOS.get(name)
    if demo is None:
        raise HTTPException(status_code=404, detail=f"unknown principle '{name}'; try {list(DEMOS)}")
    return {"principle": name, "output": demo()}
