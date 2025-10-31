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

// Data Management API calls
export const dataAPI = {
  // Projects
  getProjects: () => api.get('/api/data/projects'),
  getProject: (projectId) => api.get(`/api/data/projects/${projectId}`),
  createProject: (data) => api.post('/api/data/projects', data),
  
  // Employees
  getEmployees: () => api.get('/api/data/employees'),
  getEmployee: (employeeId) => api.get(`/api/data/employees/${employeeId}`),
  
  // Tasks
  getTasks: (params = {}) => api.get('/api/data/tasks', { params }),
  getTask: (issueId) => api.get(`/api/data/tasks/${issueId}`),
  
  // GitHub PRs
  getPullRequests: (params = {}) => api.get('/api/data/github/prs', { params }),
  getPullRequest: (prId) => api.get(`/api/data/github/prs/${prId}`),
  
  // GitHub Issues
  getGitHubIssues: (params = {}) => api.get('/api/data/github/issues', { params }),
  getGitHubIssue: (issueId) => api.get(`/api/data/github/issues/${issueId}`),
  
  // Resource Allocations
  getAllocations: (params = {}) => api.get('/api/data/allocations', { params }),
  createAllocation: (data) => api.post('/api/data/allocations', data),
  
  // Communications
  getCommunications: (params = {}) => api.get('/api/data/communications', { params }),
  createCommunication: (data) => api.post('/api/data/communications', data),
  
  // Task Dependencies
  getDependencies: (params = {}) => api.get('/api/data/dependencies', { params }),
  createDependency: (data) => api.post('/api/data/dependencies', data),
  
  // Historical Performance
  getHistoricalPerformance: () => api.get('/api/data/historical'),
  
  // Dashboard Stats
  getDashboardStats: () => api.get('/api/data/dashboard/stats'),
};

// Sync API calls
export const syncAPI = {
  triggerSync: () => api.post('/api/sync/trigger'),
  startPeriodicSync: () => api.post('/api/sync/start'),
  stopPeriodicSync: () => api.post('/api/sync/stop'),
  getSyncStatus: () => api.get('/api/sync/status'),
  getSyncHistory: () => api.get('/api/sync/history'),
};

export default api;
