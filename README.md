# Infrastructure

Critical services health check tool for infrastructure monitoring.

## Critical Services

| Service  | Default Port |
|----------|-------------|
| oscar    | 11434       |
| honcho   | 8000        |
| huly     | 8087        |
| phantom  | 3100        |

## Usage

### Text report (default)

```bash
python3 -m healthcheck.cli
```

### JSON output

```bash
python3 -m healthcheck.cli --json
```

### Custom timeout

```bash
python3 -m healthcheck.cli --timeout 5.0
```

### Override services

```bash
python3 -m healthcheck.cli --service oscar=10.0.0.1:11434 --service honcho=10.0.0.2:8000
```

### Exit codes

- `0` — all services are reachable
- `1` — one or more services are unreachable

## Running Tests

```bash
python3 -m pytest tests/ -v
```
