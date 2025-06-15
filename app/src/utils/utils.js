/**
 * Utility functions for logging and common operations
 */

// Debug logging utility
const DEBUG_ENABLED = true; // Set to false in production

export const logDebug = (component, message, data = null) => {
  if (DEBUG_ENABLED) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [DEBUG] [${component}] ${message}`;
    console.log(logMessage, data || '');
  }
};

export const logError = (component, message, error = null) => {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [ERROR] [${component}] ${message}`;
  console.error(logMessage, error || '');

  // In production, you might want to send errors to a logging service
  if (!DEBUG_ENABLED && window.gtag) {
    window.gtag('event', 'exception', {
      description: `${component}: ${message}`,
      fatal: false
    });
  }
};

export const logWarning = (component, message, data = null) => {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [WARNING] [${component}] ${message}`;
  console.warn(logMessage, data || '');
};

export const logInfo = (component, message, data = null) => {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [INFO] [${component}] ${message}`;
  console.info(logMessage, data || '');
};

// Date utility functions
export const formatDate = (date, options = {}) => {
  if (!date) return '';
  
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  };
  
  return new Date(date).toLocaleDateString('en-US', { ...defaultOptions, ...options });
};

export const formatTime = (time, use24Hour = false) => {
  if (!time) return '';
  
  const [hours, minutes] = time.split(':');
  const hour = parseInt(hours);
  
  if (use24Hour) {
    return `${hour.toString().padStart(2, '0')}:${minutes}`;
  }
  
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
  
  return `${displayHour}:${minutes} ${ampm}`;
};

export const formatDateTime = (dateTime, options = {}) => {
  if (!dateTime) return '';
  
  const date = new Date(dateTime);
  return date.toLocaleString('en-US', options);
};

// Array utility functions
export const groupBy = (array, key) => {
  return array.reduce((groups, item) => {
    const group = item[key];
    if (!groups[group]) {
      groups[group] = [];
    }
    groups[group].push(item);
    return groups;
  }, {});
};

export const sortBy = (array, key, direction = 'asc') => {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (direction === 'desc') {
      return bVal > aVal ? 1 : bVal < aVal ? -1 : 0;
    }
    
    return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
  });
};

// String utility functions
export const capitalize = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

export const truncate = (str, length = 50, suffix = '...') => {
  if (!str || str.length <= length) return str;
  return str.substring(0, length) + suffix;
};

// Validation functions
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidPhone = (phone) => {
  const phoneRegex = /^\+?[\d\s\-\(\)]+$/;
  return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
};

// Local storage utilities
export const getFromStorage = (key, defaultValue = null) => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    logError('utils', `Error reading from localStorage: ${key}`, error);
    return defaultValue;
  }
};

export const setToStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    logError('utils', `Error writing to localStorage: ${key}`, error);
    return false;
  }
};

export const removeFromStorage = (key) => {
  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    logError('utils', `Error removing from localStorage: ${key}`, error);
    return false;
  }
};

// Debounce function
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Throttle function
export const throttle = (func, limit) => {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// Generate unique ID
export const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

// Deep clone object
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (typeof obj === 'object') {
    const clonedObj = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
};

// Check if object is empty
export const isEmpty = (obj) => {
  if (obj == null) return true;
  if (Array.isArray(obj) || typeof obj === 'string') return obj.length === 0;
  return Object.keys(obj).length === 0;
};

// Format currency
export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

// Calculate duration between two times
export const calculateDuration = (startTime, endTime) => {
  if (!startTime || !endTime) return 0;
  
  const [startHour, startMin] = startTime.split(':').map(Number);
  const [endHour, endMin] = endTime.split(':').map(Number);
  
  const startMinutes = startHour * 60 + startMin;
  let endMinutes = endHour * 60 + endMin;
  
  // Handle overnight shifts
  if (endMinutes < startMinutes) {
    endMinutes += 24 * 60;
  }
  
  return (endMinutes - startMinutes) / 60; // Return hours
};

export default {
  logDebug,
  logError,
  logWarning,
  logInfo,
  formatDate,
  formatTime,
  formatDateTime,
  groupBy,
  sortBy,
  capitalize,
  truncate,
  isValidEmail,
  isValidPhone,
  getFromStorage,
  setToStorage,
  removeFromStorage,
  debounce,
  throttle,
  generateId,
  deepClone,
  isEmpty,
  formatCurrency,
  calculateDuration
};
