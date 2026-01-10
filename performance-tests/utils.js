/**
 * Utility functions for K6 tests
 */

/**
 * Safely parses JSON response body
 * @param {object} response - K6 HTTP response object
 * @returns {object|null} - Parsed JSON object or null if parsing fails
 */
export function parseBody(response) {
  try {
    return JSON.parse(response.body);
  } catch {
    return null;
  }
}
