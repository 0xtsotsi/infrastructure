/**
 * Service definitions for critical infrastructure ports.
 *
 * Each service entry maps a human-readable name to its expected port,
 * host, health endpoint, and a brief description of what it provides.
 */

'use strict';

const SERVICES = Object.freeze([
  { name: 'oscar',   port: 11434, host: 'localhost', description: 'Ollama LLM inference service' },
  { name: 'honcho',  port: 8000,  host: 'localhost', description: 'Honcho API gateway / orchestration service' },
  { name: 'huly',    port: 8087,  host: 'localhost', description: 'Huly project management platform' },
  { name: 'phantom', port: 3100,  host: 'localhost', description: 'Phantom headless rendering service' },
]);

module.exports = { SERVICES };
