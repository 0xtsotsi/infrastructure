'use strict';

const { SERVICES } = require('./services');
const { checkAll } = require('./checker');

/**
 * Format a single result for CLI output.
 */
function formatResult(r) {
  const icon = r.status === 'up' ? '✓' : '✗';
  const time = r.responseTime !== null ? ` (${r.responseTime}ms)` : '';
  const err = r.error ? ` — ${r.error}` : '';
  return `  ${icon} ${r.name} (${r.port}): ${r.status.toUpperCase()}${time}${err}`;
}

/**
 * Print a human-readable report to stdout.
 */
function printReport(summary) {
  console.log('\n=== Critical Ports Health Check ===\n');

  for (const r of summary.results) {
    console.log(formatResult(r));
  }

  console.log(
    `\nSummary: ${summary.healthy}/${summary.total} services up, ` +
    `${summary.unhealthy} down`
  );

  if (summary.allUp) {
    console.log('Status: ALL CLEAR ✓\n');
  } else {
    console.log('Status: DEGRADED — check unhealthy services ✗\n');
  }

  return summary;
}

/**
 * Main entry point for CLI usage.
 */
async function main() {
  const host = process.env.CHECK_HOST || 'localhost';
  const timeout = parseInt(process.env.CHECK_TIMEOUT || '3000', 10);

  const summary = await checkAll(SERVICES, host, timeout);
  printReport(summary);

  // Exit with non-zero if any service is down (useful for CI)
  process.exit(summary.allUp ? 0 : 1);
}

// Allow importing without auto-running
if (require.main === module) {
  main().catch((err) => {
    console.error('Fatal error:', err.message);
    process.exit(2);
  });
}

module.exports = { main, printReport, formatResult };
