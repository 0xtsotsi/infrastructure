'use strict';

const net = require('net');

/**
 * Check whether a single port is reachable on the given host.
 *
 * @param {object} service - Service descriptor { name, port, description }
 * @param {string} [host='localhost'] - Hostname or IP to check
 * @param {number} [timeoutMs=3000] - Connection timeout in milliseconds
 * @returns {Promise<object>} Result with name, port, status, responseTime
 */
function checkPort(service, host = 'localhost', timeoutMs = 3000) {
  const start = Date.now();

  return new Promise((resolve) => {
    const socket = new net.Socket();

    const result = {
      name: service.name,
      port: service.port,
      description: service.description,
      status: 'down',
      responseTime: null,
      error: null,
    };

    socket.setTimeout(timeoutMs);

    socket.on('connect', () => {
      result.status = 'up';
      result.responseTime = Date.now() - start;
      socket.destroy();
      resolve(result);
    });

    socket.on('timeout', () => {
      result.error = 'Connection timed out';
      socket.destroy();
      resolve(result);
    });

    socket.on('error', (err) => {
      result.error = err.message;
      socket.destroy();
      resolve(result);
    });

    socket.connect(service.port, host);
  });
}

/**
 * Check all provided services in parallel.
 *
 * @param {Array<object>} services - Array of service descriptors
 * @param {string} [host='localhost'] - Hostname or IP to check
 * @param {number} [timeoutMs=3000] - Connection timeout in milliseconds
 * @returns {Promise<object>} Summary with individual results and overall health
 */
async function checkAll(services, host = 'localhost', timeoutMs = 3000) {
  const results = await Promise.all(
    services.map((svc) => checkPort(svc, host, timeoutMs))
  );

  const healthy = results.filter((r) => r.status === 'up');
  const unhealthy = results.filter((r) => r.status === 'down');

  return {
    healthy: healthy.length,
    unhealthy: unhealthy.length,
    total: results.length,
    allUp: unhealthy.length === 0,
    results,
  };
}

module.exports = { checkPort, checkAll };
