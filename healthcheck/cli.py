#!/usr/bin/env python3
"""CLI entry point for the critical ports health check."""

import argparse
import json
import sys

from healthcheck.checker import (
    DEFAULT_SERVICES,
    ServiceConfig,
    check_services,
    format_report,
    run_healthcheck,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="healthcheck",
        description="Check connectivity to critical infrastructure services.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="Connection timeout in seconds (default: 3.0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--service",
        action="append",
        dest="services",
        metavar="NAME=HOST:PORT",
        help="Override service to check (can be repeated). "
        "E.g. --service oscar=localhost:11434",
    )
    return parser.parse_args(argv)


def parse_service_spec(specs: list[str]) -> list[ServiceConfig]:
    """Parse service specs in NAME=HOST:PORT format."""
    services: list[ServiceConfig] = []
    for spec in specs:
        try:
            name, endpoint = spec.split("=", 1)
            host, port_str = endpoint.rsplit(":", 1)
            port = int(port_str)
            services.append(ServiceConfig(name=name, host=host, port=port))
        except ValueError:
            print(
                f"Error: Invalid service spec '{spec}'. "
                "Expected format: NAME=HOST:PORT",
                file=sys.stderr,
            )
            sys.exit(1)
    return services


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.services:
        services = parse_service_spec(args.services)
    else:
        services = DEFAULT_SERVICES

    results, all_up = run_healthcheck(services, timeout=args.timeout)

    if args.json_output:
        data = {
            "all_up": all_up,
            "services": [
                {
                    "name": r.service,
                    "host": r.host,
                    "port": r.port,
                    "status": r.status,
                    "response_time_ms": r.response_time_ms,
                    "error": r.error or None,
                }
                for r in results
            ],
        }
        print(json.dumps(data, indent=2))
    else:
        report = format_report(results)
        print(report)

    return 0 if all_up else 1


if __name__ == "__main__":
    sys.exit(main())
