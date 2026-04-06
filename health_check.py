#!/usr/bin/env python3
"""Critical ports health check for INFRA-199.

Checks that required services are listening on their expected ports
and reports a summary. Exits with code 0 if all services are healthy,
or 1 if any are unreachable.
"""

import argparse
import json
import socket
import sys
import time
from dataclasses import asdict

from config import CRITICAL_SERVICES, Service


def check_port(service: Service) -> dict:
    """Attempt a TCP connection to a service port.

    Returns a result dict with name, port, status, and latency_ms.
    """
    start = time.monotonic()
    try:
        with socket.create_connection(
            (service.host, service.port), timeout=service.timeout
        ):
            latency_ms = (time.monotonic() - start) * 1000
            return {
                **asdict(service),
                "status": "healthy",
                "latency_ms": round(latency_ms, 1),
                "error": None,
            }
    except (ConnectionRefusedError, OSError) as exc:
        latency_ms = (time.monotonic() - start) * 1000
        return {
            **asdict(service),
            "status": "unhealthy",
            "latency_ms": round(latency_ms, 1),
            "error": str(exc),
        }


def run_checks(services: list[Service] | None = None) -> list[dict]:
    """Run health checks against all critical services."""
    services = services or CRITICAL_SERVICES
    return [check_port(svc) for svc in services]


def print_report(results: list[dict], output_format: str = "text") -> None:
    """Print a human-readable or JSON report of check results."""
    if output_format == "json":
        print(json.dumps(results, indent=2))
        return

    width = max(len(r["name"]) for r in results)
    all_healthy = True

    for r in results:
        icon = "✓" if r["status"] == "healthy" else "✗"
        latency = f'{r["latency_ms"]:.1f}ms' if r["status"] == "healthy" else "N/A"
        error = f' — {r["error"]}' if r["error"] else ""
        print(f"  [{icon}] {r['name']:<{width}}  :{r['port']}  {latency}{error}")
        if r["status"] != "healthy":
            all_healthy = False

    healthy = sum(1 for r in results if r["status"] == "healthy")
    total = len(results)
    print(f"\n  {healthy}/{total} services healthy")

    if not all_healthy:
        names = [r["name"] for r in results if r["status"] != "healthy"]
        print(f"  Failed services: {', '.join(names)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check critical service ports (INFRA-199)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Connection timeout in seconds (default: 5)",
    )
    args = parser.parse_args()

    # Apply custom timeout
    services = [
        Service(
            name=s.name,
            port=s.port,
            host=s.host,
            timeout=args.timeout,
            protocol=s.protocol,
        )
        for s in CRITICAL_SERVICES
    ]

    print("Critical Ports Health Check\n")
    results = run_checks(services)
    print_report(results, output_format=args.format)

    if any(r["status"] != "healthy" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
