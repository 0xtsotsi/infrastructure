"""Service configuration for critical port monitoring."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Service:
    """Represents a monitored service."""

    name: str
    port: int
    host: str = "localhost"
    timeout: float = 5.0
    protocol: str = "tcp"


# Critical services that must be running
CRITICAL_SERVICES: list[Service] = [
    Service(name="oscar", port=11434, protocol="tcp"),
    Service(name="honcho", port=8000, protocol="tcp"),
    Service(name="huly", port=8087, protocol="tcp"),
    Service(name="phantom", port=3100, protocol="tcp"),
]
