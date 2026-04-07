# Infrastructure

Central infrastructure tooling and health monitoring for critical services.

## Critical Services

| Service  | Port  | Description                    |
|----------|-------|--------------------------------|
| oscar    | 11434 | Oscar AI service               |
| honcho   | 8000  | Honcho orchestration service   |
| huly     | 8087  | Huly project management service|
| phantom  | 3100  | Phantom rendering service      |

## Health Check

Run a quick port-reachability scan across all critical services:

```bash
make healthcheck
```

Or directly:

```bash
python3 scripts/healthcheck/checker.py
```

The check exits with code **0** if all services are healthy, or **1** if any are unreachable.

## Tests

```bash
make test
```

## Project Structure

```
scripts/healthcheck/
  services.py   — Service registry (name, port, description)
  checker.py    — TCP port health checker with report generation
tests/
  test_checker.py — Unit and integration tests
```
