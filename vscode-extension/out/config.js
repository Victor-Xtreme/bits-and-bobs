"use strict";
/**
 * VSCode Extension Configuration
 * Centralized configuration for the RepoSense extension
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.getConfig = exports.defaultConfig = void 0;
/**
 * Default configuration values
 */
exports.defaultConfig = {
    // Backend API URL - update this if your backend runs on a different port
    backendUrl: 'http://localhost:8000',
    // How often to poll for job status updates (in milliseconds)
    pollingIntervalMs: 3000,
    // Request timeout (in milliseconds)
    requestTimeoutMs: 30000
};
/**
 * Get the current configuration
 * In the future, this could read from VSCode settings
 */
function getConfig() {
    return exports.defaultConfig;
}
exports.getConfig = getConfig;
// Made with Bob
//# sourceMappingURL=config.js.map