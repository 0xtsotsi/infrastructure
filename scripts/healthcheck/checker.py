"""Port health checker for critical infrastructure services."""

import socket
import sys
import time
from dataclasses import dataclass

from services import CRITICAL_SERVICES, Service


@dataclass
class CheckResult:
    """Result of a single service health check."""

    service: Service
    reachable: bool
    latency_ms: float
    error: str = ""

    @property
    def status_icon(self) -> str:
        return "✅" if self.reachable else "❌"


def check_port(service: Service, timeout: float = 2.0) -> CheckResult:
    """Attempt a TCP connection to a service port and measure latency."""
    addr = (service.host, service.port)
    start = time.monotonic()
    try:
        with socket.create_connection(addr, timeout=timeout):
            latency = (time.monotonic() - start) * 1000
            return CheckResult(service=service, reachable=True, latency_ms=latency)
    except (ConnectionRefusedError, OSError, TimeoutError) as exc:
        latency = (time.monotonic() - start) * 1000
        return CheckResult(
            service=service,
            reachable=False,
            latency_ms=latency,
            error=str(exc),
        )


def check_all_services(timeout: float = 2.0) -> list[CheckResult]:
    """Run health checks for every registered critical service."""
    return [check_port(svc, timeout=timeout) for svc in CRITICAL_SERVICES]


def format_report(results: list[CheckResult]) -> str:
    """Build a human-readable status report."""
    lines = ["=" * 60, "Infrastructure Health Check Report", "=" * 60, ""]

    for result in results:
        svc = result.service
        if result.reachable:
            lines.append(
                f"  {result.status_icon}  {svc.name:<12} "
                f"({svc.host}:{svc.port})  "
                f"{result.latency_ms:.1f}ms"
            )
        else:
            lines.append(
                f"  {result.status_icon}  {svc.name:<12} "
                f"({svc.host}:{svc.port})  "
                f"UNREACHABLE — {result.error}"
            )

    reachable = sum(1 for r in results if r.reachable)
    total = len(results)

    lines.append("")
    lines.append("-" * 60)
    lines.append(f"  Services healthy: {reachable}/{total}")

    if reachable < total:
        failed = [r for r in results if not r.reachable]
        lines.append("")
        lines.append("  Action required for:")
        for r in failed:
            lines.append(f"    • {r.service.name} (port {r.service.port}): "
                         f"{r.service.description}")

    lines.append("=" * 60)
    return "\n".join(lines)


def main() -> int:
    """CLI entry point. Returns 0 if all services are healthy, 1 otherwise."""
    results = check_all_services()
    print(format_report(results))

    all_healthy = all(r.reachable for r in results)
    return 0 if all_healthy else 1


if __name__ == "__main__":
    sys.exit(main())
