import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  TrendingUp,
  Users,
  AlertCircle,
  CheckCircle,
  Clock,
  Activity
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { dataAPI } from '../utils/api';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardStats();
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

  const recentActivities = [
    {
      icon: <CheckCircle className="w-5 h-5 text-green-500" />,
      title: 'Task completed',
      description: 'API integration finished by John Doe',
      time: '5 minutes ago'
    },
    {
      icon: <AlertCircle className="w-5 h-5 text-yellow-500" />,
      title: 'Risk detected',
      description: 'Project deadline approaching for Mobile App',
      time: '1 hour ago'
    },
    {
      icon: <Users className="w-5 h-5 text-blue-500" />,
      title: 'Team update',
      description: 'Sarah joined the Design team',
      time: '2 hours ago'
    },
    {
      icon: <Activity className="w-5 h-5 text-purple-500" />,
      title: 'Dashboard updated',
      description: 'New metrics available for Q4',
      time: '1 day ago'
    }
  ];

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
          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-md dark:shadow-primary-500/10 p-6 border border-transparent dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Recent Activity</h2>
              <button className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-sm font-medium">
                View All
              </button>
            </div>
            
            <div className="space-y-4">
              {recentActivities.map((activity, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start space-x-4 p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg transition-colors"
                >
                  <div className="flex-shrink-0 mt-1">
                    {activity.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {activity.title}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                      {activity.description}
                    </p>
                    <div className="flex items-center mt-2 text-xs text-gray-500 dark:text-gray-400">
                      <Clock className="w-3 h-3 mr-1" />
                      {activity.time}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-md dark:shadow-primary-500/10 p-6 border border-transparent dark:border-gray-700"
          >
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Quick Actions</h2>
            
            <div className="space-y-3">
              <button className="w-full text-left px-4 py-3 bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/50 transition-colors font-medium">
                Generate Report
              </button>
              <button className="w-full text-left px-4 py-3 bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-400 rounded-lg hover:bg-teal-100 dark:hover:bg-teal-900/50 transition-colors font-medium">
                Create New Project
              </button>
              <button className="w-full text-left px-4 py-3 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 rounded-lg hover:bg-emerald-100 dark:hover:bg-emerald-900/50 transition-colors font-medium">
                Invite Team Member
              </button>
              <button className="w-full text-left px-4 py-3 bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 rounded-lg hover:bg-amber-100 dark:hover:bg-amber-900/50 transition-colors font-medium">
                Review Risk Alerts
              </button>
            </div>

            {/* AI Insights */}
            <div className="mt-6 p-4 bg-gradient-to-br from-primary-500 to-teal-500 rounded-lg text-white shadow-lg">
              <h3 className="font-semibold mb-2">AI Insight</h3>
              <p className="text-sm text-primary-50">
                Based on current velocity, 2 projects may miss their deadlines. 
                Consider reallocating resources from Team B.
              </p>
            </div>
          </motion.div>
        </div>

        {/* Coming Soon Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-8 bg-gradient-to-r from-primary-500 to-teal-500 rounded-xl shadow-lg dark:shadow-primary-500/20 p-8 text-white text-center"
        >
          <h3 className="text-2xl font-bold mb-2">More Features Coming Soon!</h3>
          <p className="text-primary-50 mb-4">
            We're working on advanced AI predictions, real-time collaboration, and more integrations.
          </p>
          <button className="bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors shadow-md">
            Stay Updated
          </button>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
