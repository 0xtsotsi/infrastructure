"""Tests for the infrastructure health check system."""

import socket
import threading
import time
from unittest.mock import patch

import pytest

# Make the healthcheck package importable
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "healthcheck"))

from checker import CheckResult, check_all_services, check_port, format_report
from services import CRITICAL_SERVICES, Service


# ---------------------------------------------------------------------------
# Service registry tests
# ---------------------------------------------------------------------------

class TestServiceRegistry:
    """Ensure the service registry is correctly configured."""

    def test_critical_services_exist(self):
        assert len(CRITICAL_SERVICES) >= 4

    def test_expected_ports(self):
        ports = {svc.name: svc.port for svc in CRITICAL_SERVICES}
        assert ports["oscar"] == 11434
        assert ports["honcho"] == 8000
        assert ports["huly"] == 8087
        assert ports["phantom"] == 3100

    def test_all_services_are_critical(self):
        assert all(svc.critical for svc in CRITICAL_SERVICES)

    def test_services_have_descriptions(self):
        for svc in CRITICAL_SERVICES:
            assert svc.description, f"{svc.name} is missing a description"

    def test_service_is_frozen(self):
        svc = CRITICAL_SERVICES[0]
        with pytest.raises(AttributeError):
            svc.name = "changed"


# ---------------------------------------------------------------------------
# Port checker tests
# ---------------------------------------------------------------------------

class TestCheckPort:
    """Test the TCP port check logic."""

    def _start_dummy_server(self, port: int) -> socket.socket:
        """Start a TCP server that accepts one connection on the given port."""
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", port))
        srv.listen(1)
        return srv

    def test_reachable_port(self):
        """A listening port should be reported as reachable."""
        test_port = 19876
        srv = self._start_dummy_server(test_port)
        svc = Service(name="test", port=test_port, host="127.0.0.1")
        try:
            result = check_port(svc, timeout=2.0)
            assert result.reachable is True
            assert result.latency_ms > 0
            assert result.error == ""
        finally:
            srv.close()

    def test_unreachable_port(self):
        """A port with no listener should be reported as unreachable."""
        # Use a port that's almost certainly unused
        svc = Service(name="test", port=19999, host="127.0.0.1")
        result = check_port(svc, timeout=1.0)
        assert result.reachable is False
        assert result.error != ""

    def test_result_status_icon(self):
        svc = Service(name="test", port=19999, host="127.0.0.1")
        result_ok = CheckResult(service=svc, reachable=True, latency_ms=1.0)
        result_fail = CheckResult(service=svc, reachable=False, latency_ms=1.0)
        assert result_ok.status_icon == "✅"
        assert result_fail.status_icon == "❌"


# ---------------------------------------------------------------------------
# Report formatting tests
# ---------------------------------------------------------------------------

class TestFormatReport:
    """Test the human-readable report generation."""

    def test_report_contains_service_names(self):
        svc = Service(name="unittest_svc", port=12345, description="Test service")
        results = [CheckResult(service=svc, reachable=True, latency_ms=5.0)]
        report = format_report(results)
        assert "unittest_svc" in report
        assert "✅" in report

    def test_report_shows_unreachable(self):
        svc = Service(name="dead_svc", port=12345, description="Dead service")
        results = [CheckResult(service=svc, reachable=False, latency_ms=5.0, error="Connection refused")]
        report = format_report(results)
        assert "❌" in report
        assert "UNREACHABLE" in report
        assert "Action required" in report

    def test_all_healthy_report(self):
        results = [
            CheckResult(
                service=Service(name=f"svc_{i}", port=10000 + i, description=f"Svc {i}"),
                reachable=True,
                latency_ms=1.0,
            )
            for i in range(4)
        ]
        report = format_report(results)
        assert "Services healthy: 4/4" in report
        assert "Action required" not in report


# ---------------------------------------------------------------------------
# Integration: check_all_services
# ---------------------------------------------------------------------------

class TestCheckAllServices:
    """Integration test for checking all registered services."""

    def test_returns_result_per_service(self):
        results = check_all_services(timeout=0.5)
        assert len(results) == len(CRITICAL_SERVICES)

    def test_each_result_has_service(self):
        results = check_all_services(timeout=0.5)
        names = {r.service.name for r in results}
        expected = {svc.name for svc in CRITICAL_SERVICES}
        assert names == expected
