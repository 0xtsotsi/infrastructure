# infrastructure

## Critical Ports Monitor (INFRA-109)

Monitors the health of critical infrastructure services by checking TCP port reachability.

### Monitored Services

| Service  | Port  | Description                        |
| -------- | ----- | ---------------------------------- |
| oscar    | 11434 | AI/LLM service (Ollama-compatible) |
| honcho   | 8000  | API gateway / orchestration        |
| huly     | 8087  | Project management service         |
| phantom  | 3100  | Headless rendering service         |

### Usage

```bash
# Run a health check against localhost
npm run check

# Check a different host
CHECK_HOST=10.0.1.5 npm run check

# Custom timeout (ms)
CHECK_TIMEOUT=5000 npm run check
```

The command exits `0` if all services are up, `1` if any are down — suitable for CI pipelines.

### Programmatic API

```js
const { checkAll, SERVICES } = require('./src');

const summary = await checkAll(SERVICES, 'localhost', 3000);
console.log(summary.allUp ? 'All clear' : 'Degraded');
```

### Tests

```bash
npm test
```
