"""The backend's REST API, as the MCP server sees it. HTTP only; no database access."""

import httpx

from app.config import Settings


class BackendError(RuntimeError):
    pass


class BackendClient:
    def __init__(
        self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=settings.backend_url.rstrip("/"),
            headers={"X-Service-Token": settings.service_token},
            timeout=settings.timeout_s,
            transport=transport,
        )

    async def _get(self, path: str, **params):
        res = await self._http.get(
            path, params={k: v for k, v in params.items() if v not in ("", None)}
        )
        return self._json(res)

    async def _post(self, path: str, body: dict):
        return self._json(await self._http.post(path, json=body))

    @staticmethod
    def _json(res: httpx.Response):
        if res.status_code == 404:
            return None
        if res.status_code >= 400:
            raise BackendError(f"backend {res.status_code}: {res.text[:300]}")
        return res.json()

    async def list_rules(self, category: str = "", severity: str = "") -> list[dict]:
        return await self._get("/api/v1/rules", category=category, severity=severity)

    async def get_rule(self, code: str) -> dict | None:
        return await self._get(f"/api/v1/rules/{code}")

    async def search_rules(self, query: str) -> list[dict]:
        return await self._get("/api/v1/search/rules", q=query)

    async def list_documents(self, category: str = "") -> list[dict]:
        return await self._get("/api/v1/documents", category=category)

    async def get_document(self, doc_id: str) -> dict | None:
        return await self._get(f"/api/v1/documents/{doc_id}")

    async def search_documents(self, query: str) -> list[dict]:
        return await self._get("/api/v1/search/documents", q=query)

    async def assess(self, proposal: str, context: str = "") -> dict:
        return await self._post("/api/v1/assess", {"proposal": proposal, "context": context})

    async def close(self) -> None:
        await self._http.aclose()
