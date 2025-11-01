import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  Users,
  AlertCircle,
  CheckCircle,
  Clock,
  Activity,
  Code,
  Trophy,
  AlertTriangle,
  Sparkles,
  Heart,
  FileText,
  GitPullRequest,
  MessageSquare
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { dataAPI, insightsAPI } from '../utils/api';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [insights, setInsights] = useState([]);
  const [insightsLoading, setInsightsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
    fetchAIInsights();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      const response = await dataAPI.getDashboardStats();
      const dashboardData = response.data;

      // Transform the data into the format expected by the UI
      const transformedStats = [
        {
          icon: <LayoutDashboard className="w-8 h-8" />,
          label: 'Total Projects',
          value: dashboardData.total_projects?.toString() || '0',
          change: 'Active projects',
          color: 'bg-blue-100 text-blue-600'
        },
        {
          icon: <Users className="w-8 h-8" />,
          label: 'Team Members',
          value: dashboardData.total_employees?.toString() || '0',
          change: 'Active employees',
          color: 'bg-green-100 text-green-600'
        },
        {
          icon: <CheckCircle className="w-8 h-8" />,
          label: 'Total Tasks',
          value: dashboardData.total_tasks?.toString() || '0',
          change: 'Across all projects',
          color: 'bg-purple-100 text-purple-600'
        },
        {
          icon: <Activity className="w-8 h-8" />,
          label: 'Active Projects',
          value: dashboardData.active_projects?.toString() || '0',
          change: 'Currently in progress',
          color: 'bg-yellow-100 text-yellow-600'
        }
      ];

      setStats(transformedStats);
    } catch (err) {
      setError('Failed to fetch dashboard statistics');
      console.error('Error fetching dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAIInsights = async () => {
    try {
      setInsightsLoading(true);
      const response = await insightsAPI.generateInsights();
      
      // Map insights to UI format with icons
      const insightIconMap = {
        project_health: { icon: Activity, color: 'text-blue-500', bgColor: 'bg-blue-50 dark:bg-blue-900/20' },
        team_performance: { icon: Users, color: 'text-green-500', bgColor: 'bg-green-50 dark:bg-green-900/20' },
        code_quality: { icon: Code, color: 'text-purple-500', bgColor: 'bg-purple-50 dark:bg-purple-900/20' },
        blockers: { icon: AlertCircle, color: 'text-red-500', bgColor: 'bg-red-50 dark:bg-red-900/20' },
        upcoming_risks: { icon: AlertTriangle, color: 'text-yellow-500', bgColor: 'bg-yellow-50 dark:bg-yellow-900/20' },
        recent_achievements: { icon: Trophy, color: 'text-teal-500', bgColor: 'bg-teal-50 dark:bg-teal-900/20' }
      };

      const formattedInsights = response.data.map(insight => {
        const config = insightIconMap[insight.insight_type] || insightIconMap.project_health;
        return {
          ...insight,
          iconConfig: config
        };
      });

      setInsights(formattedInsights);
    } catch (err) {
      console.error('Error fetching AI insights:', err);
      // Set empty insights on error
      setInsights([]);
    } finally {
      setInsightsLoading(false);
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
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back, {user?.full_name || user?.email}!
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            Here's what's happening with your projects today
          </p>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {loading ? (
            // Loading skeleton
            Array.from({ length: 4 }).map((_, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md border border-transparent dark:border-gray-700"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2 animate-pulse"></div>
                    <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-1 animate-pulse"></div>
                    <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                  </div>
                  <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
                </div>
              </motion.div>
            ))
          ) : error ? (
            <motion.div
              variants={itemVariants}
              className="col-span-full bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6"
            >
              <div className="text-center">
                <p className="text-red-600 dark:text-red-400 font-medium mb-2">Failed to load dashboard data</p>
                <p className="text-red-500 dark:text-red-500 text-sm">{error}</p>
                <button
                  onClick={fetchDashboardStats}
                  className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Retry
                </button>
              </div>
            </motion.div>
          ) : (
            stats.map((stat, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover={{ y: -5 }}
                className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md hover:shadow-lg dark:shadow-primary-500/10 dark:hover:shadow-primary-500/20 transition-all duration-300 border border-transparent dark:border-gray-700"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{stat.label}</p>
                    <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                      {stat.value}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{stat.change}</p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    {stat.icon}
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* AI Insights */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-md dark:shadow-primary-500/10 p-6 border border-transparent dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-primary-500" />
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">AI Insights</h2>
              </div>
              <button 
                onClick={fetchAIInsights}
                className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-sm font-medium flex items-center gap-1"
              >
                <Activity className="w-4 h-4" />
                Refresh
              </button>
            </div>
            
            <div className="space-y-4">
              {insightsLoading ? (
                // Loading skeleton
                Array.from({ length: 3 }).map((_, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
                  >
                    <div className="w-10 h-10 bg-gray-200 dark:bg-gray-600 rounded-lg animate-pulse"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded animate-pulse w-3/4"></div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded animate-pulse w-full"></div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded animate-pulse w-5/6"></div>
                    </div>
                  </motion.div>
                ))
              ) : insights.length > 0 ? (
                insights.map((insight, index) => {
                  const IconComponent = insight.iconConfig.icon;
                  return (
                    <motion.div
                      key={insight.insight_type}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`flex items-start space-x-4 p-4 ${insight.iconConfig.bgColor} rounded-lg border border-transparent hover:border-gray-200 dark:hover:border-gray-600 transition-all`}
                    >
                      <div className="flex-shrink-0 mt-1">
                        <IconComponent className={`w-5 h-5 ${insight.iconConfig.color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900 dark:text-white capitalize mb-1">
                          {insight.insight_type.replace(/_/g, ' ')}
                        </p>
                        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                          {insight.insight}
                        </p>
                        {insight.context_count > 0 && (
                          <div className="flex items-center mt-2 text-xs text-gray-500 dark:text-gray-400">
                            <Activity className="w-3 h-3 mr-1" />
                            Based on {insight.context_count} data points
                          </div>
                        )}
                      </div>
                    </motion.div>
                  );
                })
              ) : (
                <div className="text-center py-8">
                  <Sparkles className="w-12 h-12 text-gray-400 dark:text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-600 dark:text-gray-400">
                    No insights available. Sync your data to generate insights.
                  </p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md dark:shadow-primary-500/10 p-6 border border-transparent dark:border-gray-700"
          >
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Quick Access</h2>
            
            <div className="space-y-3">
              <button 
                onClick={() => navigate('/sentiment')}
                className="w-full text-left px-4 py-3 bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/30 dark:to-purple-900/30 text-purple-700 dark:text-purple-400 rounded-lg hover:from-pink-100 hover:to-purple-100 dark:hover:from-pink-900/50 dark:hover:to-purple-900/50 transition-all font-medium flex items-center gap-3 group"
              >
                <Heart className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-semibold">Sentiment Analysis</div>
                  <div className="text-xs opacity-75">Team morale & feedback</div>
                </div>
              </button>
              <button 
                onClick={() => navigate('/projects')}
                className="w-full text-left px-4 py-3 bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-400 rounded-lg hover:bg-teal-100 dark:hover:bg-teal-900/50 transition-colors font-medium flex items-center gap-3 group"
              >
                <LayoutDashboard className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-semibold">View Projects</div>
                  <div className="text-xs opacity-75">Manage all projects</div>
                </div>
              </button>
              <button 
                onClick={() => navigate('/tasks')}
                className="w-full text-left px-4 py-3 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors font-medium flex items-center gap-3 group"
              >
                <CheckCircle className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-semibold">View Tasks</div>
                  <div className="text-xs opacity-75">Track Jira issues</div>
                </div>
              </button>
              <button 
                onClick={() => navigate('/github-prs')}
                className="w-full text-left px-4 py-3 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 rounded-lg hover:bg-emerald-100 dark:hover:bg-emerald-900/50 transition-colors font-medium flex items-center gap-3 group"
              >
                <GitPullRequest className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-semibold">Pull Requests</div>
                  <div className="text-xs opacity-75">Code reviews & PRs</div>
                </div>
              </button>
              <button 
                onClick={() => navigate('/ai-chat')}
                className="w-full text-left px-4 py-3 bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 rounded-lg hover:bg-amber-100 dark:hover:bg-amber-900/50 transition-colors font-medium flex items-center gap-3 group"
              >
                <MessageSquare className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-semibold">AI Chat</div>
                  <div className="text-xs opacity-75">Ask questions</div>
                </div>
              </button>
            </div>

            {/* Insight Summary */}
            <div className="mt-6 p-4 bg-gradient-to-br from-primary-500 to-teal-500 rounded-lg text-white shadow-lg">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-5 h-5" />
                <h3 className="font-semibold">AI-Powered Dashboard</h3>
              </div>
              <p className="text-sm text-primary-50">
                {insightsLoading 
                  ? "Generating intelligent insights..."
                  : insights.length > 0 
                    ? `${insights.length} AI-generated insights available above, powered by semantic search and Gemini AI.`
                    : "Sync your projects to enable AI insights."
                }
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
