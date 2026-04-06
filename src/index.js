'use strict';

/**
 * Public API for the critical-ports health checker.
 *
 * Usage:
 *   const { checkAll, SERVICES } = require('./src');
 */

const { checkPort, checkAll } = require('./checker');
const { SERVICES } = require('./services');

module.exports = { checkPort, checkAll, SERVICES };
