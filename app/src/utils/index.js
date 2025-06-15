/**
 * Utils Index - Central export for all utility functions
 * Exports all utility functions for easy importing throughout the app
 */

// Export logging utilities
export { logDebug, logError, logWarning, logInfo } from './utils.js';

// Export WebSocket utilities (from parent utils.jsx file)
export { useSocket } from '../utils.jsx';

// Export session utilities
export {
  saveUserCredentials,
  getUserCredentials,
  clearUserCredentials,
  isValidSession,
  refreshSession
} from './sessionUtils.js';

// Export environment utilities
export { default as ENV } from './env.js';

// Export user setup utilities
export {
  setupAdminUser,
  setupTestUsers,
  validateUserSetup
} from './userSetup.js';

// Export credential fix utilities
export {
  fixUserCredentials,
  validateCredentials,
  resetCredentials
} from './fixUserCredentials.js';

// Re-export everything for convenience
export * from './utils.js';
export * from './sessionUtils.js';
export * from './userSetup.js';
export * from './fixUserCredentials.js';
