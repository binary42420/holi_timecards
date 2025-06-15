/**
 * Session utilities for handling secure authentication
 */

/**
 * Get current session data for authenticated requests
 * @returns {Object|null} Session data with sessionId and csrfToken, or null if not available
 */
export const getSessionData = () => {
  try {
    const sessionData = sessionStorage.getItem('holi_session');
    if (sessionData) {
      return JSON.parse(sessionData);
    }
  } catch (error) {
    console.error('Error getting session data:', error);
    // Clear invalid session data
    sessionStorage.removeItem('holi_session');
  }
  return null;
};

/**
 * Get headers for authenticated WebSocket or HTTP requests
 * @returns {Object} Headers object with session and CSRF tokens
 */
export const getAuthHeaders = () => {
  const sessionData = getSessionData();
  if (sessionData) {
    return {
      'X-Session-ID': sessionData.sessionId,
      'X-CSRF-Token': sessionData.csrfToken
    };
  }
  return {};
};

/**
 * Check if user has a valid session
 * @returns {boolean} True if session exists and appears valid
 */
export const hasValidSession = () => {
  const sessionData = getSessionData();
  return sessionData && sessionData.sessionId && sessionData.csrfToken;
};

/**
 * Clear all session data (for logout)
 */
export const clearSessionData = () => {
  sessionStorage.removeItem('holi_session');
  localStorage.removeItem('holi_user');
};

/**
 * Create authenticated WebSocket request with session data
 * @param {number} requestId - The request ID
 * @param {Object} data - The request data
 * @returns {Object} Complete request object with authentication
 */
export const createAuthenticatedRequest = (requestId, data = {}) => {
  const sessionData = getSessionData();
  
  const request = {
    request_id: requestId,
    data: data
  };

  // Add session data if available
  if (sessionData) {
    request.session_id = sessionData.sessionId;
    request.csrf_token = sessionData.csrfToken;
  }

  return request;
};

/**
 * Validate session response and handle session errors
 * @param {Object} response - Server response
 * @returns {boolean} True if session is valid, false if session error
 */
export const validateSessionResponse = (response) => {
  // Check for session-related errors
  if (response.error) {
    const errorMessage = response.error.toLowerCase();
    if (errorMessage.includes('session') || 
        errorMessage.includes('csrf') || 
        errorMessage.includes('unauthorized') ||
        errorMessage.includes('authentication')) {
      // Clear invalid session
      clearSessionData();
      return false;
    }
  }
  
  return true;
};

export default {
  getSessionData,
  getAuthHeaders,
  hasValidSession,
  clearSessionData,
  createAuthenticatedRequest,
  validateSessionResponse
};
