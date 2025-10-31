import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Issue, User, Calendar, Tag, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { dataAPI } from '../utils/api';

const GitHubIssues = () => {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    project_id: '',
    author_id: '',
    status: '',
    issue_type: '',
    priority: ''
  });
  const [projects, setProjects] = useState([]);
  const [employees, setEmployees] = useState([]);

  const fetchIssues = useCallback(async () => {
    try {
      setLoading(true);
      const params = { ...filters };
      // Remove empty filters
      Object.keys(params).forEach(key => {
        if (!params[key]) delete params[key];
      });

      const response = await dataAPI.getGitHubIssues(params);
      setIssues(response.data || []);
    } catch (err) {
      setError('Failed to fetch GitHub issues');
      console.error('Error fetching GitHub issues:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const fetchProjects = async () => {
    try {
      const response = await dataAPI.getProjects();
      setProjects(response.data || []);
    } catch (err) {
      console.error('Error fetching projects:', err);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await dataAPI.getEmployees();
      setEmployees(response.data || []);
    } catch (err) {
      console.error('Error fetching employees:', err);
    }
  };

  useEffect(() => {
    fetchIssues();
    fetchProjects();
    fetchEmployees();
  }, [fetchIssues]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const filteredIssues = issues.filter(issue =>
    issue.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    issue.author_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    issue.issue_id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Open':
        return <AlertCircle className="w-4 h-4 text-green-500" />;
      case 'Closed':
        return <CheckCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'Critical':
        return 'bg-red-100 text-red-800';
      case 'High':
        return 'bg-orange-100 text-orange-800';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'Low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'Bug':
        return 'bg-red-100 text-red-800';
      case 'Feature':
        return 'bg-blue-100 text-blue-800';
      case 'Enhancement':
        return 'bg-purple-100 text-purple-800';
      case 'Question':
        return 'bg-yellow-100 text-yellow-800';
      case 'Documentation':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          GitHub Issues
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Track and manage GitHub issues across all projects
        </p>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-md dark:shadow-primary-500/10 p-6 mb-6 border border-transparent dark:border-gray-700"
      >
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search issues..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          {/* Project Filter */}
          <div className="w-full lg:w-48">
            <select
              value={filters.project_id}
              onChange={(e) => handleFilterChange('project_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">All Projects</option>
              {projects.map(project => (
                <option key={project.project_id} value={project.project_id}>
                  {project.project_name}
                </option>
              ))}
            </select>
          </div>

          {/* Author Filter */}
          <div className="w-full lg:w-48">
            <select
              value={filters.author_id}
              onChange={(e) => handleFilterChange('author_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">All Authors</option>
              {employees.map(employee => (
                <option key={employee.employee_id} value={employee.employee_id}>
                  {employee.name}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div className="w-full lg:w-32">
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">All Status</option>
              <option value="Open">Open</option>
              <option value="Closed">Closed</option>
            </select>
          </div>

          {/* Type Filter */}
          <div className="w-full lg:w-40">
            <select
              value={filters.issue_type}
              onChange={(e) => handleFilterChange('issue_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">All Types</option>
              <option value="Bug">Bug</option>
              <option value="Feature">Feature</option>
              <option value="Enhancement">Enhancement</option>
              <option value="Question">Question</option>
              <option value="Documentation">Documentation</option>
            </select>
          </div>

          {/* Priority Filter */}
          <div className="w-full lg:w-32">
            <select
              value={filters.priority}
              onChange={(e) => handleFilterChange('priority', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">All Priority</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Issues List */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-4"
      >
        {loading ? (
          // Loading skeleton
          Array.from({ length: 5 }).map((_, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md border border-transparent dark:border-gray-700"
            >
              <div className="animate-pulse">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                  </div>
                  <div className="w-20 h-6 bg-gray-200 dark:bg-gray-700 rounded"></div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
                </div>
              </div>
            </motion.div>
          ))
        ) : error ? (
          <motion.div
            variants={itemVariants}
            className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6"
          >
            <div className="text-center">
              <p className="text-red-600 dark:text-red-400 font-medium mb-2">Failed to load GitHub issues</p>
              <p className="text-red-500 dark:text-red-500 text-sm">{error}</p>
              <button
                onClick={fetchIssues}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Retry
              </button>
            </div>
          </motion.div>
        ) : filteredIssues.length === 0 ? (
          <motion.div
            variants={itemVariants}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md dark:shadow-primary-500/10 p-12 text-center border border-transparent dark:border-gray-700"
          >
            <Issue className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No GitHub issues found</h3>
            <p className="text-gray-600 dark:text-gray-300">
              {searchTerm || Object.values(filters).some(v => v) ?
                'Try adjusting your search or filters' :
                'GitHub issues will appear here once synced'
              }
            </p>
          </motion.div>
        ) : (
          filteredIssues.map((issue) => (
            <motion.div
              key={issue.issue_id}
              variants={itemVariants}
              whileHover={{ y: -2 }}
              className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md hover:shadow-lg dark:shadow-primary-500/10 dark:hover:shadow-primary-500/20 transition-all duration-300 border border-transparent dark:border-gray-700"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    {getStatusIcon(issue.status)}
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {issue.title}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(issue.issue_type)}`}>
                      {issue.issue_type}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(issue.priority)}`}>
                      {issue.priority}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
                    {issue.issue_id}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    issue.status === 'Open'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                      : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                  }`}>
                    {issue.status}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6 text-sm text-gray-500 dark:text-gray-400">
                  <div className="flex items-center space-x-1">
                    <User className="w-4 h-4" />
                    <span>{issue.author_name || 'Unknown'}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>{issue.created_at ? new Date(issue.created_at).toLocaleDateString() : 'Unknown'}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Tag className="w-4 h-4" />
                    <span>{issue.project_name || 'Unknown Project'}</span>
                  </div>
                  {issue.comments_count > 0 && (
                    <div className="flex items-center space-x-1">
                      <span>💬 {issue.comments_count}</span>
                    </div>
                  )}
                </div>

                {issue.labels && issue.labels.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {issue.labels.slice(0, 3).map((label, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs"
                      >
                        {label}
                      </span>
                    ))}
                    {issue.labels.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs">
                        +{issue.labels.length - 3}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          ))
        )}
      </motion.div>
    </div>
  );
};

export default GitHubIssues;