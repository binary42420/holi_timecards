// Runtime environment configuration for HOLI Timesheets
const isLocalDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const forceLocalMode = false;

window._env_ = {
  REACT_APP_GOOGLE_CLIENT_ID: "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com",
  REACT_APP_API_URL: (isLocalDevelopment || forceLocalMode)
    ? "ws://localhost:8080/ws"
    : "wss://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/ws",
  REACT_APP_ENV: (isLocalDevelopment || forceLocalMode) ? "development" : "production"
};

console.log('env-config.js loaded:', window._env_);
