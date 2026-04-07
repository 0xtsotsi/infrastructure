"""Port connectivity checker for critical infrastructure services."""

import socket
import time
from dataclasses import dataclass, field


@dataclass
class ServiceConfig:
    """Configuration for a service to check."""

    name: str
    host: str
    port: int
    timeout: float = 3.0


@dataclass
class CheckResult:
    """Result of a single port check."""

    service: str
    host: str
    port: int
    reachable: bool
    response_time_ms: float = 0.0
    error: str = ""

    @property
    def status(self) -> str:
        return "UP" if self.reachable else "DOWN"


# Default critical services
DEFAULT_SERVICES: list[ServiceConfig] = [
    ServiceConfig(name="oscar", host="localhost", port=11434),
    ServiceConfig(name="honcho", host="localhost", port=8000),
    ServiceConfig(name="huly", host="localhost", port=8087),
    ServiceConfig(name="phantom", host="localhost", port=3100),
]


def check_port(host: str, port: int, timeout: float = 3.0) -> CheckResult:
    """Check if a TCP port is accepting connections.

    Args:
        host: Hostname or IP address.
        port: Port number to check.
        timeout: Connection timeout in seconds.

    Returns:
        CheckResult with connection details.
    """
    start = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            elapsed_ms = (time.monotonic() - start) * 1000
            return CheckResult(
                service=f"{host}:{port}",
                host=host,
                port=port,
                reachable=True,
                response_time_ms=round(elapsed_ms, 2),
            )
    except OSError as exc:
        elapsed_ms = (time.monotonic() - start) * 1000
        return CheckResult(
            service=f"{host}:{port}",
            host=host,
            port=port,
            reachable=False,
            response_time_ms=round(elapsed_ms, 2),
            error=str(exc),
        )


def check_services(
    services: list[ServiceConfig] | None = None,
    timeout: float = 3.0,
) -> list[CheckResult]:
    """Check a list of services and return results.

    Args:
        services: List of ServiceConfig objects. Uses DEFAULT_SERVICES if None.
        timeout: Connection timeout in seconds.

    Returns:
        List of CheckResult objects, one per service.
    """
    if services is None:
        services = DEFAULT_SERVICES

    results: list[CheckResult] = []
    for svc in services:
        result = check_port(svc.host, svc.port, timeout=timeout or svc.timeout)
        result.service = svc.name
        results.append(result)

    return results


def format_report(results: list[CheckResult]) -> str:
    """Format check results into a human-readable report.

    Args:
        results: List of CheckResult objects.

    Returns:
        Formatted report string.
    """
    lines: list[str] = []
    lines.append("=" * 56)
    lines.append("  Critical Ports Health Check Report")
    lines.append("=" * 56)

    all_up = True
    for r in results:
        status_icon = "✓" if r.reachable else "✗"
        line = f"  [{status_icon}] {r.service:<12} {r.host}:{r.port:<6} {r.status}"
        if r.reachable:
            line += f"  ({r.response_time_ms:.1f}ms)"
        else:
            all_up = False
            line += f"  ({r.error})"
        lines.append(line)

    lines.append("-" * 56)
    summary = "ALL SERVICES UP" if all_up else "SOME SERVICES DOWN"
    lines.append(f"  Summary: {summary}")
    lines.append("=" * 56)

    return "\n".join(lines)


def run_healthcheck(
    services: list[ServiceConfig] | None = None,
    timeout: float = 3.0,
) -> tuple[list[CheckResult], bool]:
    """Run a full health check and return results with overall status.

    Args:
        services: List of ServiceConfig objects. Uses DEFAULT_SERVICES if None.
        timeout: Connection timeout in seconds.

    Returns:
        Tuple of (results list, boolean indicating if all services are up).
    """
    results = check_services(services, timeout=timeout)
    all_up = all(r.reachable for r in results)
    return results, all_up
