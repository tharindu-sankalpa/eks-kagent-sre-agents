"""TCP connect test: is anything listening on host:port, and how fast does it answer."""

import socket
import time

from mcp.types import ToolAnnotations

from core.server import mcp


@mcp.tool(annotations=ToolAnnotations(title="TCP connect", readOnlyHint=True))
def tcp_connect(host: str, port: int, timeout_seconds: float = 3.0) -> dict:
    """Open a TCP connection to host:port and close it again.

    Tells you whether a port is reachable at the network level, independent of
    the protocol spoken on it. A ClusterIP Service whose selector matches no pod
    refuses or times out here even though its name resolves.

    Args:
        host: Hostname or IP.
        port: TCP port, 1 to 65535.
        timeout_seconds: Connect timeout.

    Returns:
        connected (bool), connect_ms, peer (ip, port), and error when it failed.
    """
    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds) as s:
            peer = s.getpeername()
        return {"connected": True, "connect_ms": round((time.perf_counter() - started) * 1000, 1), "peer": list(peer[:2])}
    except OSError as e:
        return {"connected": False, "error": str(e), "connect_ms": round((time.perf_counter() - started) * 1000, 1)}
