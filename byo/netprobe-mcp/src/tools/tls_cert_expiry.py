"""TLS certificate check: who issued it, which names it covers, and how many days are left."""

import socket
import ssl

import certifi
from datetime import datetime, timezone

from mcp.types import ToolAnnotations

from core.server import mcp


@mcp.tool(annotations=ToolAnnotations(title="TLS certificate expiry", readOnlyHint=True))
def tls_cert_expiry(host: str, port: int = 443, timeout_seconds: float = 5.0) -> dict:
    """Connect with TLS and read the server certificate.

    Args:
        host: Hostname (also used for SNI and name verification).
        port: TLS port, default 443.
        timeout_seconds: Connect timeout.

    Returns:
        valid_now (bool), days_remaining, not_after (ISO 8601), issuer, subject,
        san (list of DNS names), tls_version, and error when the handshake failed.
    """
    # certifi's bundle, so the result does not depend on the host's CA store
    ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as tls:
                cert = tls.getpeercert()
                version = tls.version()
    except (OSError, ssl.SSLError) as e:
        return {"valid_now": False, "error": f"{type(e).__name__}: {e}"}
    not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    return {
        "valid_now": now < not_after,
        "days_remaining": (not_after - now).days,
        "not_after": not_after.isoformat(),
        "issuer": dict(x[0] for x in cert.get("issuer", ())),
        "subject": dict(x[0] for x in cert.get("subject", ())),
        "san": [v for k, v in cert.get("subjectAltName", ()) if k == "DNS"],
        "tls_version": version,
    }
