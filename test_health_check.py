"""Tests for health_check module (INFRA-340)."""

import socket
import threading
import time
from unittest.mock import patch

import pytest

from config import CRITICAL_SERVICES, Service
from health_check import check_port, run_checks, print_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _start_dummy_server(port: int, stop_event: threading.Event) -> None:
    """Start a TCP server that accepts connections until told to stop."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("localhost", port))
    srv.listen(1)
    srv.settimeout(0.5)
    while not stop_event.is_set():
        try:
            conn, _ = srv.accept()
            conn.close()
        except socket.timeout:
            continue
    srv.close()


@pytest.fixture()
def dummy_server():
    """Fixture that runs a real TCP server on a random port for one test."""
    port = 19876  # high port unlikely to conflict
    stop = threading.Event()
    t = threading.Thread(target=_start_dummy_server, args=(port, stop), daemon=True)
    t.start()
    time.sleep(0.1)  # let the server bind
    yield port
    stop.set()
    t.join(timeout=2)


# ---------------------------------------------------------------------------
# Tests — config
# ---------------------------------------------------------------------------

class TestConfig:
    def test_critical_services_defined(self):
        assert len(CRITICAL_SERVICES) == 4

    def test_expected_service_names(self):
        names = {s.name for s in CRITICAL_SERVICES}
        assert names == {"oscar", "honcho", "huly", "phantom"}

    def test_expected_ports(self):
        ports = {s.name: s.port for s in CRITICAL_SERVICES}
        assert ports == {
            "oscar": 11434,
            "honcho": 8000,
            "huly": 8087,
            "phantom": 3100,
        }


# ---------------------------------------------------------------------------
# Tests — check_port
# ---------------------------------------------------------------------------

class TestCheckPort:
    def test_healthy_when_port_open(self, dummy_server):
        port = dummy_server  # fixture returns the port number
        svc = Service(name="test-svc", port=port)
        result = check_port(svc)
        assert result["status"] == "healthy"
        assert result["latency_ms"] >= 0
        assert result["error"] is None

    def test_unhealthy_when_port_closed(self):
        # Use a port that's almost certainly not listening
        svc = Service(name="test-svc", port=19999, timeout=0.5)
        result = check_port(svc)
        assert result["status"] == "unhealthy"
        assert result["error"] is not None

    def test_result_includes_service_fields(self, dummy_server):
        svc = Service(name="test-svc", port=dummy_server, host="localhost", timeout=2.0)
        result = check_port(svc)
        assert result["name"] == "test-svc"
        assert result["port"] == dummy_server
        assert result["host"] == "localhost"


# ---------------------------------------------------------------------------
# Tests — run_checks
# ---------------------------------------------------------------------------

class TestRunChecks:
    def test_runs_all_critical_services(self):
        results = run_checks()
        assert len(results) == len(CRITICAL_SERVICES)

    def test_custom_service_list(self, dummy_server):
        custom = [Service(name="custom", port=dummy_server)]
        results = run_checks(custom)
        assert len(results) == 1
        assert results[0]["name"] == "custom"


# ---------------------------------------------------------------------------
# Tests — print_report
# ---------------------------------------------------------------------------

class TestPrintReport:
    def test_text_report_output(self, capsys):
        results = [
            {
                "name": "oscar",
                "port": 11434,
                "host": "localhost",
                "timeout": 5.0,
                "protocol": "tcp",
                "status": "healthy",
                "latency_ms": 1.2,
                "error": None,
            },
            {
                "name": "honcho",
                "port": 8000,
                "host": "localhost",
                "timeout": 5.0,
                "protocol": "tcp",
                "status": "unhealthy",
                "latency_ms": 5000.0,
                "error": "Connection refused",
            },
        ]
        print_report(results, output_format="text")
        captured = capsys.readouterr()
        assert "✓" in captured.out
        assert "✗" in captured.out
        assert "1/2 services healthy" in captured.out

    def test_json_report_output(self, capsys):
        results = [
            {
                "name": "oscar",
                "port": 11434,
                "host": "localhost",
                "timeout": 5.0,
                "protocol": "tcp",
                "status": "healthy",
                "latency_ms": 1.2,
                "error": None,
            },
        ]
        print_report(results, output_format="json")
        captured = capsys.readouterr()
        import json

        parsed = json.loads(captured.out)
        assert parsed[0]["name"] == "oscar"
        assert parsed[0]["status"] == "healthy"
