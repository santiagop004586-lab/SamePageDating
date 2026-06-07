import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL ?? '';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
  paramsSerializer: {
    indexes: null, // Use repeat format for arrays: status=val1&status=val2 instead of status[]=val1
  },
});

// Attach JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sec8_access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    console.log('[api] Request:', config.method?.toUpperCase(), config.url, 'params:', config.params);
    return config;
  },
  (error) => {
    console.error('[api] Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor — on 401 force logout
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('sec8_access_token');
      localStorage.removeItem('sec8_refresh_token');
      // Let the AuthContext detect the missing token on next render
    }
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;
