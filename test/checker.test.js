'use strict';

const { checkPort, checkAll } = require('../src/checker');
const { SERVICES } = require('../src/services');
const assert = require('node:assert/strict');
const net = require('net');
const { describe, it } = require('node:test');

/**
 * Spin up a temporary TCP server on the given port, returning a promise
 * that resolves to the server handle (call .close() when done).
 */
function createMockServer(port) {
  return new Promise((resolve, reject) => {
    const server = net.createServer((socket) => {
      socket.end();
    });
    server.listen(port, '127.0.0.1', () => resolve(server));
    server.on('error', reject);
  });
}

// ---- checkPort ----

describe('checkPort', () => {
  it('reports "up" when the port is listening', async () => {
    const server = await createMockServer(0); // random free port
    const addr = server.address();
    const service = { name: 'test', port: addr.port, description: 'test service' };

    const result = await checkPort(service, '127.0.0.1', 2000);

    assert.equal(result.name, 'test');
    assert.equal(result.port, addr.port);
    assert.equal(result.status, 'up');
    assert.equal(result.error, null);
    assert.ok(result.responseTime >= 0);

    server.close();
  });

  it('reports "down" when nothing is listening', async () => {
    // Use a port that is extremely unlikely to be in use
    const service = { name: 'ghost', port: 59999, description: 'nope' };

    const result = await checkPort(service, '127.0.0.1', 500);

    assert.equal(result.status, 'down');
    assert.ok(result.error !== null);
  });

  it('times out within the specified window', async () => {
    const service = { name: 'slow', port: 59998, description: 'slow' };
    const start = Date.now();

    const result = await checkPort(service, '127.0.0.1', 300);

    const elapsed = Date.now() - start;
    assert.equal(result.status, 'down');
    assert.ok(elapsed < 2000, `Should have timed out quickly, took ${elapsed}ms`);
  });
});

// ---- checkAll ----

describe('checkAll', () => {
  it('returns correct summary when all services are down', async () => {
    // Use ports that won't be listening
    const testServices = [
      { name: 'svc-a', port: 59991, description: 'a' },
      { name: 'svc-b', port: 59992, description: 'b' },
    ];

    const summary = await checkAll(testServices, '127.0.0.1', 300);

    assert.equal(summary.total, 2);
    assert.equal(summary.healthy, 0);
    assert.equal(summary.unhealthy, 2);
    assert.equal(summary.allUp, false);
    assert.equal(summary.results.length, 2);
  });

  it('returns allUp=true when all services are up', async () => {
    const s1 = await createMockServer(0);
    const s2 = await createMockServer(0);

    const testServices = [
      { name: 'svc-a', port: s1.address().port, description: 'a' },
      { name: 'svc-b', port: s2.address().port, description: 'b' },
    ];

    const summary = await checkAll(testServices, '127.0.0.1', 2000);

    assert.equal(summary.total, 2);
    assert.equal(summary.healthy, 2);
    assert.equal(summary.unhealthy, 0);
    assert.equal(summary.allUp, true);

    s1.close();
    s2.close();
  });

  it('handles mixed up/down services', async () => {
    const s1 = await createMockServer(0);

    const testServices = [
      { name: 'svc-up', port: s1.address().port, description: 'up' },
      { name: 'svc-down', port: 59997, description: 'down' },
    ];

    const summary = await checkAll(testServices, '127.0.0.1', 300);

    assert.equal(summary.total, 2);
    assert.equal(summary.healthy, 1);
    assert.equal(summary.unhealthy, 1);
    assert.equal(summary.allUp, false);

    s1.close();
  });
});

// ---- services config ----

describe('services config', () => {
  it('defines exactly the four expected services', () => {
    const names = SERVICES.map((s) => s.name).sort();
    assert.deepEqual(names, ['honcho', 'huly', 'oscar', 'phantom']);
  });

  it('each service has required fields', () => {
    for (const svc of SERVICES) {
      assert.ok(svc.name, `missing name`);
      assert.ok(typeof svc.port === 'number' && svc.port > 0, `invalid port for ${svc.name}`);
      assert.ok(typeof svc.description === 'string' && svc.description.length > 0, `missing description for ${svc.name}`);
    }
  });

  it('ports match the expected values', () => {
    const byName = Object.fromEntries(SERVICES.map((s) => [s.name, s.port]));
    assert.equal(byName.oscar, 11434);
    assert.equal(byName.honcho, 8000);
    assert.equal(byName.huly, 8087);
    assert.equal(byName.phantom, 3100);
  });
});
