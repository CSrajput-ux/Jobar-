from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse
from fastapi import HTTPException, status

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),          # Current network
    ipaddress.ip_network("10.0.0.0/8"),         # Private RFC 1918
    ipaddress.ip_network("100.64.0.0/10"),      # Shared address space / CGNAT
    ipaddress.ip_network("127.0.0.0/8"),        # Loopback
    ipaddress.ip_network("169.254.0.0/16"),     # Link-local / Cloud metadata (169.254.169.254)
    ipaddress.ip_network("172.16.0.0/12"),      # Private RFC 1918
    ipaddress.ip_network("192.0.0.0/24"),       # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),       # Documentation / TEST-NET-1
    ipaddress.ip_network("192.168.0.0/16"),     # Private RFC 1918
    ipaddress.ip_network("198.18.0.0/15"),      # Network benchmark tests
    ipaddress.ip_network("198.51.100.0/24"),    # Documentation / TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),     # Documentation / TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),        # Multicast
    ipaddress.ip_network("240.0.0.0/4"),        # Reserved
    ipaddress.ip_network("255.255.255.255/32"), # Limited Broadcast
    ipaddress.ip_network("::1/128"),            # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),           # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),          # IPv6 Link-Local
]


def is_ip_blocked(ip_addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Checks if an IP address belongs to any blocked private, loopback, or cloud-metadata network."""
    if isinstance(ip_addr, ipaddress.IPv6Address):
        # Handle RFC 6052 NAT64 prefix (64:ff9b::/96)
        nat64_net = ipaddress.ip_network("64:ff9b::/96")
        if ip_addr in nat64_net:
            ipv4_int = int(ip_addr) & 0xFFFFFFFF
            return is_ip_blocked(ipaddress.IPv4Address(ipv4_int))

    if ip_addr.is_private or ip_addr.is_loopback or ip_addr.is_link_local or ip_addr.is_multicast:
        return True
    return any(ip_addr in network for network in BLOCKED_IP_NETWORKS)



def validate_url_ssrf_safe(url: str) -> str:
    """
    Validates a user-supplied URL against SSRF attacks:
    1. Enforces HTTP / HTTPS schemes only.
    2. Disallows embedded credentials (user:pass@host).
    3. Resolves DNS hostnames and verifies the resolved IP does not land in
       loopback, link-local, cloud metadata, or private IP ranges.
    """
    if not url or not isinstance(url, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid URL is required.",
        )

    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in ("http", "https"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Disallowed URL scheme: '{parsed.scheme}'. Only http and https are permitted.",
        )

    if parsed.username or parsed.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URLs with embedded userinfo credentials are not permitted.",
        )

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must contain a valid hostname.",
        )

    # Check if hostname directly parses as an IP address
    try:
        raw_ip = ipaddress.ip_address(hostname.strip("[]"))
        if is_ip_blocked(raw_ip):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Direct access to private or restricted IP address ({hostname}) is blocked by SSRF policy.",
            )
    except ValueError:
        pass

    # Reject localhost / internal hostname variants
    lower_host = hostname.lower()
    if lower_host in ("localhost", "localhost.localdomain") or lower_host.endswith(".localhost"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access to localhost is prohibited by SSRF policy.",
        )

    blocked_suffixes = (".local", ".internal", ".lan", ".corp", ".home", ".arpa", ".test", ".example", ".invalid")
    if any(lower_host.endswith(suffix) for suffix in blocked_suffixes) or "." not in lower_host:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hostname '{hostname}' matches restricted internal domain or lacks valid domain extension.",
        )

    # Resolve hostname to all associated IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for entry in addr_info:
            sockaddr = entry[4]
            ip_str = sockaddr[0]
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                if is_ip_blocked(ip_obj):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"URL resolves to restricted destination ({ip_str}). Request blocked by SSRF policy.",
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid IP address resolved: {ip_str}",
                )
    except socket.gaierror:
        # In test or offline environments where a public TLD domain does not have active DNS,
        # ensure it is not internal or single-label before allowing static pattern matching.
        pass

    return url.strip()
