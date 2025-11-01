import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Heart,
  ThumbsUp,
  ThumbsDown,
  Meh,
  TrendingUp,
  TrendingDown,
  MessageSquare,
  Users,
  BarChart3,
  Activity,
  Calendar,
  Filter,
  Download,
  Sparkles
} from 'lucide-react';
import { sentimentAPI, dataAPI } from '../utils/api';

const SentimentAnalysis = () => {
  const [loading, setLoading] = useState(true);
  const [projectSentiments, setProjectSentiments] = useState([]);
  const [employeeSentiments, setEmployeeSentiments] = useState([]);
  const [summary, setSummary] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [daysBack, setDaysBack] = useState(90);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchData();
    fetchProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [daysBack, selectedProject]);

  const fetchProjects = async () => {
    try {
      const response = await dataAPI.getProjects();
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const params = { days_back: daysBack };
      if (selectedProject) {
        params.project_id = selectedProject;
      }

      const [projectRes, employeeRes, summaryRes] = await Promise.all([
        sentimentAPI.getProjectSentiment(params),
        sentimentAPI.getEmployeeSentiment(params),
        sentimentAPI.getSentimentSummary()
      ]);

      setProjectSentiments(projectRes.data.projects || []);
      setEmployeeSentiments(employeeRes.data.employees || []);
      setSummary(summaryRes.data);
    } catch (error) {
      console.error('Error fetching sentiment data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (label) => {
    switch (label) {
      case 'positive':
        return 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30';
      case 'negative':
        return 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700/30';
    }
  };

  const getSentimentIcon = (label) => {
    switch (label) {
      case 'positive':
        return <ThumbsUp className="w-5 h-5" />;
      case 'negative':
        return <ThumbsDown className="w-5 h-5" />;
      default:
        return <Meh className="w-5 h-5" />;
    }
  };

  const getSentimentEmoji = (label) => {
    switch (label) {
      case 'positive':
        return '😊';
      case 'negative':
        return '😞';
      default:
        return '😐';
    }
  };

  const getTrendIcon = (score) => {
    if (score > 0.15) return <TrendingUp className="w-4 h-4 text-green-500" />;
    if (score < -0.15) return <TrendingDown className="w-4 h-4 text-red-500" />;
    return <Activity className="w-4 h-4 text-gray-500" />;
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-pink-500 to-purple-600 p-3 rounded-xl">
                <Heart className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  Sentiment Analysis
                </h1>
                <p className="text-gray-600 dark:text-gray-300 mt-1">
                  Analyze team sentiment based on comments and interactions
                </p>
              </div>
            </div>
            <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
              <Download className="w-4 h-4" />
              Export Report
            </button>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-6 border border-transparent dark:border-gray-700"
        >
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Filters</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Project
              </label>
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All Projects</option>
                {projects.map((project) => (
                  <option key={project.project_id} value={project.project_id}>
                    {project.project_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Time Period
              </label>
              <select
                value={daysBack}
                onChange={(e) => setDaysBack(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500"
              >
                <option value={30}>Last 30 Days</option>
                <option value={60}>Last 60 Days</option>
                <option value={90}>Last 90 Days</option>
                <option value={180}>Last 6 Months</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={fetchData}
                className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </motion.div>

        {/* Summary Cards */}
        {summary && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
          >
            <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between mb-4">
                <Sparkles className="w-8 h-8" />
                <span className="text-3xl">{getSentimentEmoji(summary.overall_sentiment)}</span>
              </div>
              <h3 className="text-lg font-semibold mb-1">Overall Sentiment</h3>
              <p className="text-2xl font-bold capitalize">{summary.overall_sentiment}</p>
              <p className="text-sm mt-2 opacity-90">Score: {summary.average_score}</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-transparent dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <BarChart3 className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Projects</h3>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{summary.total_projects}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                {summary.projects_with_data} with data
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-transparent dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <MessageSquare className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                <span className="text-2xl">💬</span>
              </div>
              <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Comments</h3>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {summary.total_comments.toLocaleString()}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Analyzed</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-transparent dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <ThumbsUp className="w-8 h-8 text-green-600 dark:text-green-400" />
                <span className="text-2xl">✅</span>
              </div>
              <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-1">Positive Projects</h3>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{summary.positive_projects}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                {summary.negative_projects} negative
              </p>
            </div>
          </motion.div>
        )}

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex gap-4">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-4 py-3 font-medium border-b-2 transition-colors ${
                  activeTab === 'overview'
                    ? 'border-purple-600 text-purple-600 dark:text-purple-400'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Project Overview
                </div>
              </button>
              <button
                onClick={() => setActiveTab('employees')}
                className={`px-4 py-3 font-medium border-b-2 transition-colors ${
                  activeTab === 'employees'
                    ? 'border-purple-600 text-purple-600 dark:text-purple-400'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Team Members
                </div>
              </button>
            </nav>
          </div>
        </div>

        {/* Content based on active tab */}
        {activeTab === 'overview' ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
                <p className="text-gray-600 dark:text-gray-400 mt-4">Analyzing sentiment...</p>
              </div>
            ) : projectSentiments.length === 0 ? (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-12 text-center border border-transparent dark:border-gray-700">
                <Heart className="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  No Data Available
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  No comments found for the selected period. Try syncing your data or selecting a different time range.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-6">
                {projectSentiments.map((project, index) => (
                  <motion.div
                    key={project.project_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-transparent dark:border-gray-700 hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                            {project.project_name}
                          </h3>
                          <span className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(project.sentiment_label)}`}>
                            {getSentimentIcon(project.sentiment_label)}
                            <span className="capitalize">{project.sentiment_label}</span>
                          </span>
                          {getTrendIcon(project.sentiment_score)}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {project.total_comments} comments analyzed
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-gray-900 dark:text-white">
                          {project.sentiment_score > 0 ? '+' : ''}{project.sentiment_score}
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Sentiment Score</p>
                      </div>
                    </div>

                    {/* Sentiment Distribution */}
                    <div className="space-y-3">
                      <div className="flex items-center gap-4">
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm text-green-600 dark:text-green-400 font-medium flex items-center gap-1">
                              <ThumbsUp className="w-4 h-4" />
                              Positive
                            </span>
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                              {project.positive_percentage}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-green-500 h-2 rounded-full transition-all"
                              style={{ width: `${project.positive_percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm text-gray-600 dark:text-gray-400 font-medium flex items-center gap-1">
                              <Meh className="w-4 h-4" />
                              Neutral
                            </span>
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                              {project.neutral_percentage}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-gray-500 h-2 rounded-full transition-all"
                              style={{ width: `${project.neutral_percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm text-red-600 dark:text-red-400 font-medium flex items-center gap-1">
                              <ThumbsDown className="w-4 h-4" />
                              Negative
                            </span>
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                              {project.negative_percentage}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-red-500 h-2 rounded-full transition-all"
                              style={{ width: `${project.negative_percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">
                        <Calendar className="w-4 h-4 inline mr-1" />
                        Last {project.analysis_period_days} days
                      </span>
                      <span className="text-gray-600 dark:text-gray-400">
                        Confidence: {(project.average_confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
                <p className="text-gray-600 dark:text-gray-400 mt-4">Analyzing sentiment...</p>
              </div>
            ) : employeeSentiments.length === 0 ? (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-12 text-center border border-transparent dark:border-gray-700">
                <Users className="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  No Employee Data
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  No employee comments found for the selected period.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {employeeSentiments.map((employee, index) => (
                  <motion.div
                    key={employee.employee_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-transparent dark:border-gray-700 hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                          {employee.employee_name.charAt(0)}
                        </div>
                        <div>
                          <h3 className="font-bold text-gray-900 dark:text-white">
                            {employee.employee_name}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{employee.role}</p>
                        </div>
                      </div>
                      <span className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(employee.sentiment_label)}`}>
                        {getSentimentIcon(employee.sentiment_label)}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-3 mb-4">
                      <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <ThumbsUp className="w-5 h-5 text-green-600 dark:text-green-400 mx-auto mb-1" />
                        <p className="text-lg font-bold text-gray-900 dark:text-white">
                          {employee.positive_count}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Positive</p>
                      </div>
                      <div className="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                        <Meh className="w-5 h-5 text-gray-600 dark:text-gray-400 mx-auto mb-1" />
                        <p className="text-lg font-bold text-gray-900 dark:text-white">
                          {employee.neutral_count}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Neutral</p>
                      </div>
                      <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                        <ThumbsDown className="w-5 h-5 text-red-600 dark:text-red-400 mx-auto mb-1" />
                        <p className="text-lg font-bold text-gray-900 dark:text-white">
                          {employee.negative_count}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Negative</p>
                      </div>
                    </div>

                    <div className="text-center py-3 bg-gray-50 dark:bg-gray-700/30 rounded-lg">
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {employee.sentiment_score > 0 ? '+' : ''}{employee.sentiment_score}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        Based on {employee.total_comments} comments
                      </p>
                    </div>

                    {employee.project_breakdown && employee.project_breakdown.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
                          Project Breakdown:
                        </p>
                        <div className="space-y-1">
                          {employee.project_breakdown.slice(0, 3).map((proj) => (
                            <div key={proj.project_id} className="flex items-center justify-between text-xs">
                              <span className="text-gray-700 dark:text-gray-300 truncate">
                                {proj.project_name}
                              </span>
                              <span className={`font-medium ${proj.avg_sentiment > 0 ? 'text-green-600 dark:text-green-400' : proj.avg_sentiment < 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-600 dark:text-gray-400'}`}>
                                {proj.avg_sentiment > 0 ? '+' : ''}{proj.avg_sentiment}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default SentimentAnalysis;
