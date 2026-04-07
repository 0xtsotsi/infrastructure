"""Service definitions for critical infrastructure ports."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Service:
    """Represents an infrastructure service with its health check config."""

    name: str
    port: int
    host: str = "localhost"
    protocol: str = "tcp"
    description: str = ""
    critical: bool = True


# Registry of critical services that must be running.
CRITICAL_SERVICES: list[Service] = [
    Service(
        name="oscar",
        port=11434,
        description="Oscar AI service",
    ),
    Service(
        name="honcho",
        port=8000,
        description="Honcho orchestration service",
    ),
    Service(
        name="huly",
        port=8087,
        description="Huly project management service",
    ),
    Service(
        name="phantom",
        port=3100,
        description="Phantom rendering service",
    ),
]
