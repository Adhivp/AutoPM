import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  verifyToken: () => api.get('/auth/verify'),
};

// Integration API calls
export const integrationAPI = {
  getStatus: () => api.get('/integrations/status'),
  listIntegrations: () => api.get('/integrations/list'),
  
  // GitHub
  getGithubUrl: () => api.get('/integrations/github/url'),
  connectGithub: (code) => api.post('/integrations/connect/github', { code }),
  
  // Jira
  getJiraUrl: () => api.get('/integrations/jira/url'),
  connectJira: (code) => api.post('/integrations/connect/jira', { code }),
  
  // Disconnect
  disconnect: (provider) => api.delete(`/integrations/disconnect/${provider}`),
};

export default api;
