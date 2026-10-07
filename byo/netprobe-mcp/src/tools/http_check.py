"""HTTP check: status, latency and redirect target of a URL, from inside the cluster."""

import time
from urllib.parse import urlparse

import httpx
from mcp.types import ToolAnnotations

from core.server import mcp


@mcp.tool(annotations=ToolAnnotations(title="HTTP check", readOnlyHint=True))
def http_check(url: str, timeout_seconds: float = 5.0) -> dict:
    """Send one GET request to a URL and report what happened, from the server's own network.

    Use it to tell "the service is down" apart from "the service is up but my
    client cannot reach it": the probe runs inside the cluster.

    Args:
        url: Full URL, for example http://checkout.demo-broken.svc:80/ or https://example.com/health
        timeout_seconds: Connect and read timeout.

    Returns:
        ok (bool), status_code, latency_ms, final_url (after redirects),
        server header, content_length, and error (string) when the request failed.
    """
    if urlparse(url).scheme not in ("http", "https"):
        return {"ok": False, "error": "url must start with http:// or https://"}
    started = time.perf_counter()
    try:
        with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
            r = client.get(url)
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        return {
            "ok": r.status_code < 400,
            "status_code": r.status_code,
            "latency_ms": latency_ms,
            "final_url": str(r.url),
            "server": r.headers.get("server"),
            "content_length": len(r.content),
        }
    except httpx.HTTPError as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}", "latency_ms": round((time.perf_counter() - started) * 1000, 1)}
