/**
 * Service definitions for critical infrastructure ports.
 *
 * Each service entry maps a human-readable name to its expected port
 * and a brief description of what it provides.
 */

const SERVICES = Object.freeze([
  { name: 'oscar',   port: 11434, description: 'AI/LLM service (Ollama-compatible)' },
  { name: 'honcho',  port: 8000,  description: 'API gateway / orchestration service' },
  { name: 'huly',    port: 8087,  description: 'Project management service' },
  { name: 'phantom', port: 3100,  description: 'Headless rendering service' },
]);

module.exports = { SERVICES };
