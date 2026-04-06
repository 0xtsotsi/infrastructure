# infrastructure

Critical service port monitoring for **INFRA-199**.

## Usage

```bash
# Run health check (text output)
python3 health_check.py

# JSON output
python3 health_check.py --format json

# Custom timeout
python3 health_check.py --timeout 3
```

Exit code is `0` if all services are healthy, `1` if any are unreachable.

## Monitored Services

| Service | Port  |
|---------|-------|
| oscar   | 11434 |
| honcho  | 8000  |
| huly    | 8087  |
| phantom | 3100  |

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
python -m pytest test_health_check.py -v
```
