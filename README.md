# infra-critical-ports

Critical ports health monitoring for infrastructure services.

## Services

| Service  | Port  | Description                          |
|----------|-------|--------------------------------------|
| oscar    | 11434 | AI/LLM service (Ollama-compatible)   |
| honcho   | 8000  | API gateway / orchestration service  |
| huly     | 8087  | Project management service           |
| phantom  | 3100  | Headless rendering service           |

## Usage

### CLI

```bash
npm run check
```

Set `CHECK_HOST` (default: `localhost`) and `CHECK_TIMEOUT` (default: `3000` ms) via environment variables.

### Programmatic

```js
const { checkAll, SERVICES } = require('./src');

const summary = await checkAll(SERVICES);
console.log(summary.allUp ? 'All clear' : 'Degraded');
```

## Tests

```bash
npm test
```
