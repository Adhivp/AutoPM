import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  GitPullRequest,
  Search,
  Calendar,
  User,
  CheckCircle,
  Clock,
  XCircle,
  Eye,
  ExternalLink,
  GitBranch,
  MessageSquare
} from 'lucide-react';
import { dataAPI } from '../utils/api';

const GitHubPRs = () => {
  const [prs, setPrs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [projectFilter, setProjectFilter] = useState('');
  const [authorFilter, setAuthorFilter] = useState('');
  const [selectedPR, setSelectedPR] = useState(null);
  const [projects, setProjects] = useState([]);
  const [authors, setAuthors] = useState([]);

  const fetchPRs = useCallback(async () => {
    try {
      setLoading(true);
      const params = {};
      if (projectFilter) params.project_id = projectFilter;
      if (authorFilter) params.author_id = authorFilter;
      if (statusFilter) params.status = statusFilter;

      const response = await dataAPI.getPullRequests(params);
      setPrs(response.data);

      // Extract unique authors from PRs
      const uniqueAuthors = [...new Set(response.data.map(pr => pr.author_name).filter(Boolean))];
      setAuthors(uniqueAuthors);
    } catch (err) {
      setError('Failed to fetch pull requests');
      console.error('Error fetching PRs:', err);
    } finally {
      setLoading(false);
    }
  }, [projectFilter, authorFilter, statusFilter]);

  const fetchProjects = async () => {
    try {
      const response = await dataAPI.getProjects();
      setProjects(response.data);
    } catch (err) {
      console.error('Error fetching projects:', err);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    fetchPRs();
  }, [fetchPRs]);

  const filteredPRs = prs.filter(pr => {
    const matchesSearch = pr.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         pr.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         pr.pr_id?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case 'merged': return <CheckCircle className="w-5 h-5 text-purple-500" />;
      case 'open': return <Clock className="w-5 h-5 text-green-500" />;
      case 'closed': return <XCircle className="w-5 h-5 text-red-500" />;
      default: return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'merged': return 'bg-purple-100 text-purple-800';
      case 'open': return 'bg-green-100 text-green-800';
      case 'closed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading pull requests...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">GitHub Pull Requests</h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Track and manage GitHub pull requests</p>
            </div>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow p-6"
        >
          {error && (
            <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 rounded-lg">
              {error}
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search PRs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="closed">Closed</option>
              <option value="merged">Merged</option>
            </select>
            <select
              value={projectFilter}
              onChange={(e) => setProjectFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">All Projects</option>
              {projects.map(project => (
                <option key={project.project_id} value={project.project_id}>
                  {project.project_name}
                </option>
              ))}
            </select>
            <select
              value={authorFilter}
              onChange={(e) => setAuthorFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">All Authors</option>
              {authors.map(author => (
                <option key={author} value={author}>
                  {author}
                </option>
              ))}
            </select>
          </div>
        </motion.div>

        {/* PRs List */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="space-y-4"
        >
          {filteredPRs.map((pr, index) => (
            <motion.div
              key={pr.pr_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <div className="mt-1">
                    {getStatusIcon(pr.status)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-gray-900 dark:text-white">{pr.title || `PR #${pr.pr_number}`}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(pr.status)}`}>
                        {pr.status}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-300 text-sm mb-3 line-clamp-2">
                      {pr.description || 'No description available'}
                    </p>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                      <div className="flex items-center gap-1">
                        <User className="w-4 h-4" />
                        <span>{pr.author_name || 'Unknown'}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <GitBranch className="w-4 h-4" />
                        <span>{pr.source_branch} → {pr.target_branch}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <GitPullRequest className="w-4 h-4" />
                        <span>{pr.project_name || pr.project_id}</span>
                      </div>
                      {pr.created_at && (
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(pr.created_at).toLocaleDateString()}</span>
                        </div>
                      )}
                      {pr.comments_count !== undefined && (
                        <div className="flex items-center gap-1">
                          <MessageSquare className="w-4 h-4" />
                          <span>{pr.comments_count} comments</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  {pr.html_url && (
                    <a
                      href={pr.html_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-1"
                    >
                      <ExternalLink className="w-4 h-4" />
                      View
                    </a>
                  )}
                  <button
                    onClick={() => setSelectedPR(pr)}
                    className="bg-blue-100 dark:bg-blue-900 hover:bg-blue-200 dark:hover:bg-blue-800 text-blue-700 dark:text-blue-300 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-1"
                  >
                    <Eye className="w-4 h-4" />
                    Details
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {filteredPRs.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <GitPullRequest className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No pull requests found</h3>
            <p className="text-gray-600 dark:text-gray-400">Try adjusting your search or filter criteria.</p>
          </motion.div>
        )}

        {/* PR Details Modal */}
        {selectedPR && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex justify-between items-start mb-6">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(selectedPR.status)}
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{selectedPR.title || `PR #${selectedPR.pr_number}`}</h2>
                      <p className="text-gray-600 dark:text-gray-400">#{selectedPR.pr_number} in {selectedPR.project_name || selectedPR.project_id}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedPR.status)}`}>
                      {selectedPR.status}
                    </span>
                    {selectedPR.html_url && (
                      <a
                        href={selectedPR.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-1"
                      >
                        <ExternalLink className="w-4 h-4" />
                        View on GitHub
                      </a>
                    )}
                    <button
                      onClick={() => setSelectedPR(null)}
                      className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 ml-2"
                    >
                      ✕
                    </button>
                  </div>
                </div>

                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Description</h3>
                    <p className="text-gray-600 dark:text-gray-300 whitespace-pre-wrap">
                      {selectedPR.description || 'No description available'}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Pull Request Details</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Author:</span>
                          <span className="text-gray-900 dark:text-white font-medium">{selectedPR.author_name || 'Unknown'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Source Branch:</span>
                          <span className="text-gray-900 dark:text-white font-medium font-mono text-sm">{selectedPR.source_branch}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Target Branch:</span>
                          <span className="text-gray-900 dark:text-white font-medium font-mono text-sm">{selectedPR.target_branch}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Project:</span>
                          <span className="text-gray-900 dark:text-white font-medium">{selectedPR.project_name || selectedPR.project_id}</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Timeline & Stats</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Created:</span>
                          <span className="text-gray-900 dark:text-white font-medium">
                            {selectedPR.created_at ? new Date(selectedPR.created_at).toLocaleString() : 'Unknown'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Updated:</span>
                          <span className="text-gray-900 dark:text-white font-medium">
                            {selectedPR.updated_at ? new Date(selectedPR.updated_at).toLocaleString() : 'Unknown'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Comments:</span>
                          <span className="text-gray-900 dark:text-white font-medium">{selectedPR.comments_count || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Last Synced:</span>
                          <span className="text-gray-900 dark:text-white font-medium">
                            {selectedPR.last_synced_at ? new Date(selectedPR.last_synced_at).toLocaleString() : 'Never'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {selectedPR.labels && selectedPR.labels.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Labels</h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedPR.labels.map((label, index) => (
                          <span
                            key={index}
                            className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-300 rounded-full text-sm"
                          >
                            {label}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedPR.reviews && selectedPR.reviews.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Reviews</h3>
                      <div className="space-y-3">
                        {selectedPR.reviews.map((review, index) => (
                          <div key={index} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                            <div className="flex justify-between items-start mb-2">
                              <span className="font-medium text-gray-900 dark:text-white">{review.reviewer}</span>
                              <span className="text-sm text-gray-500 dark:text-gray-400">
                                {new Date(review.submitted_at).toLocaleString()}
                              </span>
                            </div>
                            <p className="text-gray-600 dark:text-gray-300 mb-2">{review.body || 'No review comment'}</p>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              review.state === 'approved' ? 'bg-green-100 text-green-800' :
                              review.state === 'changes_requested' ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {review.state}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GitHubPRs;