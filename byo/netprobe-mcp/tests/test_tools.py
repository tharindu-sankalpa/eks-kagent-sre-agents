"""Tests for the netprobe tools. They call public hosts, so they need network access."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tools.dns_lookup import dns_lookup  # noqa: E402
from tools.http_check import http_check  # noqa: E402
from tools.tcp_connect import tcp_connect  # noqa: E402
from tools.tls_cert_expiry import tls_cert_expiry  # noqa: E402


def test_dns_lookup_resolves_public_name():
    r = dns_lookup("example.com")
    assert r["resolved"] and r["addresses"]


def test_dns_lookup_reports_failure():
    assert dns_lookup("no-such-host.invalid")["resolved"] is False


def test_http_check_ok():
    r = http_check("https://example.com/")
    assert r["ok"] and r["status_code"] == 200


def test_http_check_rejects_bad_scheme():
    assert http_check("ftp://example.com")["ok"] is False


def test_tcp_connect_and_refusal():
    assert tcp_connect("example.com", 443)["connected"]
    assert tcp_connect("127.0.0.1", 9)["connected"] is False


def test_tls_cert_expiry():
    r = tls_cert_expiry("example.com")
    assert r["valid_now"] and r["days_remaining"] > 0
