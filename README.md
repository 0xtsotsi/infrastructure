# infrastructure
infrastructure

## Critical Ports Health Check

Monitors connectivity to critical infrastructure services:

| Service | Port  | Description                    |
|---------|-------|--------------------------------|
| oscar   | 11434 | Ollama LLM inference service   |
| honcho  | 8000  | Honcho API gateway             |
| huly    | 8087  | Huly project management        |
| phantom | 3100  | Phantom headless rendering     |

### Usage

```bash
# Run health check
npm run check

# Run tests
npm test

# Run with custom host/timeout
CHECK_HOST=192.168.1.10 CHECK_TIMEOUT=5000 npm run check
```

### Configuration

Service definitions are in `config/services.json` and `src/services.js`.
