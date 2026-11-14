"""`browse`: Playwright, on a local Chromium or on Amazon Bedrock AgentCore Browser.

Same Playwright code both ways. AgentCore Browser is a managed, isolated Chromium you reach over
CDP: start a session, get a signed websocket URL + headers, `connect_over_cdp`. That is the
whole migration from local to managed.
"""

import asyncio
import ipaddress
import logging
import socket
from typing import Protocol
from urllib.parse import urlparse

from app.core.scope import current_scope

log = logging.getLogger(__name__)
MAX_TEXT = 4000


class BlockedUrl(ValueError):
    pass


async def check_url(url: str, allowed_hosts: list[str], allow_private: bool = False) -> None:
    """SSRF guard: http(s) only; refuse hosts resolving to private/loopback/link-local ranges."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise BlockedUrl("only http(s) URLs are allowed")
    host = parsed.hostname.lower()
    if allowed_hosts and not any(host == h or host.endswith("." + h) for h in allowed_hosts):
        raise BlockedUrl(f"host {host!r} is not in BROWSER_ALLOWED_HOSTS")
    if allow_private:
        return
    infos = await asyncio.to_thread(socket.getaddrinfo, host, None)
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise BlockedUrl(f"host {host!r} resolves to a non-public address")


async def _extract(page, url: str) -> dict:
    await page.goto(url, timeout=20_000, wait_until="domcontentloaded")
    title = await page.title()
    text = " ".join((await page.inner_text("body")).split())
    links = await page.eval_on_selector_all(
        "a[href]",
        "els => els.slice(0, 20).map(e => ({text: e.innerText.trim().slice(0, 80), href: e.href}))",
    )
    return {"url": page.url, "title": title, "text": text[:MAX_TEXT], "links": links}


class Browser(Protocol):
    name: str
    allow_private: bool

    async def fetch(self, url: str) -> dict: ...


class LocalBrowser:
    name = "local_playwright"

    def __init__(self, executable_path: str = "", allow_private: bool = False):
        self.executable_path = executable_path or None
        self.allow_private = allow_private

    async def fetch(self, url: str) -> dict:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(executable_path=self.executable_path, headless=True)
            try:
                page = await browser.new_page()
                return await _extract(page, url)
            finally:
                await browser.close()


class AgentCoreBrowser:
    name = "agentcore_browser"
    allow_private = False

    def __init__(self, region: str):
        self.region = region

    async def fetch(self, url: str) -> dict:
        from bedrock_agentcore.tools.browser_client import BrowserClient
        from playwright.async_api import async_playwright

        client = BrowserClient(self.region)
        await asyncio.to_thread(client.start)
        try:
            ws_url, headers = client.generate_ws_headers()
            try:
                log.info("AgentCore live view: %s", client.generate_live_view_url())
            except Exception:  # live view is a nicety; never fail the fetch for it
                pass
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(ws_url, headers=headers)
                try:
                    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
                    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
                    result = await _extract(page, url)
                    result["session_id"] = client.session_id
                    return result
                finally:
                    await browser.close()
        finally:
            await asyncio.to_thread(client.stop)


async def browse(url: str) -> dict:
    """Open a public web page in a real browser and return its title, visible text, and links.

    Args:
        url: Full http(s) URL, e.g. "https://example.com".
    """
    scope = current_scope()
    browser = scope.provider.browser
    try:
        await check_url(url, scope.provider.settings.allowed_hosts, browser.allow_private)
        result = await browser.fetch(url)
    except BlockedUrl as e:
        return {"status": "blocked", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": f"{type(e).__name__}: {e}"[:500]}
    return {"status": "ok", "backend": browser.name, **result}
