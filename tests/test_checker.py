"""Tests for the critical ports health checker."""

import json
import socket
import threading
import time
from unittest.mock import patch

import pytest

from healthcheck.checker import (
    DEFAULT_SERVICES,
    CheckResult,
    ServiceConfig,
    check_port,
    check_services,
    format_report,
    run_healthcheck,
)
from healthcheck.cli import main, parse_service_spec


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _free_port() -> int:
    """Find a free TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _start_echo_server(port: int) -> tuple[threading.Thread, socket.socket]:
    """Start a simple TCP server listening on *port*. Returns (thread, server_socket)."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(1)
    srv.settimeout(2.0)

    def _accept():
        try:
            conn, _ = srv.accept()
            conn.close()
        except socket.timeout:
            pass

    t = threading.Thread(target=_accept, daemon=True)
    t.start()
    # Give the server a moment to start listening
    time.sleep(0.05)
    return t, srv


# ---------------------------------------------------------------------------
# Unit tests — check_port
# ---------------------------------------------------------------------------


class TestCheckPort:
    def test_reachable_port(self):
        port = _free_port()
        _thread, srv = _start_echo_server(port)
        try:
            result = check_port("127.0.0.1", port, timeout=2.0)
            assert result.reachable is True
            assert result.response_time_ms > 0
            assert result.error == ""
        finally:
            srv.close()

    def test_unreachable_port(self):
        port = _free_port()
        # Nothing listening on this port
        result = check_port("127.0.0.1", port, timeout=1.0)
        assert result.reachable is False
        assert result.error != ""

    def test_result_fields(self):
        result = CheckResult(
            service="test", host="localhost", port=1234,
            reachable=True, response_time_ms=1.5,
        )
        assert result.status == "UP"
        result.reachable = False
        assert result.status == "DOWN"


# ---------------------------------------------------------------------------
# Unit tests — check_services
# ---------------------------------------------------------------------------


class TestCheckServices:
    def test_default_services(self):
        """Default services list should match expected names and ports."""
        assert len(DEFAULT_SERVICES) == 4
        by_name = {s.name: s for s in DEFAULT_SERVICES}
        assert by_name["oscar"].port == 11434
        assert by_name["honcho"].port == 8000
        assert by_name["huly"].port == 8087
        assert by_name["phantom"].port == 3100

    def test_custom_services(self):
        port = _free_port()
        _thread, srv = _start_echo_server(port)
        try:
            services = [
                ServiceConfig(name="test-svc", host="127.0.0.1", port=port),
            ]
            results = check_services(services, timeout=2.0)
            assert len(results) == 1
            assert results[0].service == "test-svc"
            assert results[0].reachable is True
        finally:
            srv.close()


# ---------------------------------------------------------------------------
# Unit tests — format_report
# ---------------------------------------------------------------------------


class TestFormatReport:
    def test_report_contains_service_names(self):
        results = [
            CheckResult(service="oscar", host="localhost", port=11434,
                        reachable=False, error="Connection refused"),
            CheckResult(service="honcho", host="localhost", port=8000,
                        reachable=True, response_time_ms=2.3),
        ]
        report = format_report(results)
        assert "oscar" in report
        assert "honcho" in report
        assert "DOWN" in report
        assert "UP" in report
        assert "SOME SERVICES DOWN" in report

    def test_all_up_summary(self):
        results = [
            CheckResult(service="svc", host="localhost", port=1,
                        reachable=True, response_time_ms=1.0),
        ]
        report = format_report(results)
        assert "ALL SERVICES UP" in report


# ---------------------------------------------------------------------------
# Unit tests — run_healthcheck
# ---------------------------------------------------------------------------


class TestRunHealthcheck:
    def test_returns_all_up_flag(self):
        port = _free_port()
        _thread, srv = _start_echo_server(port)
        try:
            services = [ServiceConfig(name="up-svc", host="127.0.0.1", port=port)]
            results, all_up = run_healthcheck(services, timeout=2.0)
            assert all_up is True
        finally:
            srv.close()

    def test_returns_not_all_up_flag(self):
        services = [
            ServiceConfig(name="down-svc", host="127.0.0.1", port=_free_port()),
        ]
        results, all_up = run_healthcheck(services, timeout=1.0)
        assert all_up is False


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestCLI:
    def test_json_output(self, capsys):
        # With default services (all likely down on a dev machine)
        exit_code = main(["--json"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "all_up" in data
        assert "services" in data
        assert len(data["services"]) == 4

    def test_custom_service_json(self, capsys):
        port = _free_port()
        _thread, srv = _start_echo_server(port)
        try:
            exit_code = main([
                "--json",
                "--service", f"my-svc=127.0.0.1:{port}",
            ])
            captured = capsys.readouterr()
            data = json.loads(captured.out)
            assert data["all_up"] is True
            assert data["services"][0]["name"] == "my-svc"
            assert data["services"][0]["status"] == "UP"
            assert exit_code == 0
        finally:
            srv.close()

    def test_exit_code_1_when_down(self):
        exit_code = main([
            "--json",
            "--service", f"missing=127.0.0.1:{_free_port()}",
        ])
        assert exit_code == 1

    def test_parse_service_spec_valid(self):
        services = parse_service_spec(["oscar=10.0.0.1:11434"])
        assert services[0].name == "oscar"
        assert services[0].host == "10.0.0.1"
        assert services[0].port == 11434

    def test_parse_service_spec_invalid(self):
        with pytest.raises(SystemExit):
            parse_service_spec(["bad-spec"])

    def test_text_report_output(self, capsys):
        port = _free_port()
        _thread, srv = _start_echo_server(port)
        try:
            main(["--service", f"testsvc=127.0.0.1:{port}"])
            captured = capsys.readouterr()
            assert "testsvc" in captured.out
            assert "UP" in captured.out
            assert "ALL SERVICES UP" in captured.out
        finally:
            srv.close()
