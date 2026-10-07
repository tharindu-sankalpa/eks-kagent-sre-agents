"""DNS lookup from inside the cluster, so Service and pod names resolve the way workloads see them."""

import socket

from mcp.types import ToolAnnotations

from core.server import mcp


@mcp.tool(annotations=ToolAnnotations(title="DNS lookup", readOnlyHint=True))
def dns_lookup(hostname: str) -> dict:
    """Resolve a hostname with the cluster's DNS (CoreDNS) and return its addresses.

    Works for Kubernetes names such as checkout.demo-broken.svc.cluster.local
    and for public names. A Service with no endpoints still resolves to its
    ClusterIP, so pair this with http_check or tcp_connect.

    Args:
        hostname: Name to resolve, without scheme or port.

    Returns:
        resolved (bool), addresses (list of IPs), canonical_name, and error when it failed.
    """
    try:
        infos = socket.getaddrinfo(hostname, None)
        addresses = sorted({i[4][0] for i in infos})
        canonical = socket.getfqdn(hostname)
        return {"resolved": True, "addresses": addresses, "canonical_name": canonical}
    except socket.gaierror as e:
        return {"resolved": False, "error": str(e)}
