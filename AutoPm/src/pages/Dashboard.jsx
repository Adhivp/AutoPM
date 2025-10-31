import { useAuth } from '../contexts/AuthContext';
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

const Dashboard = () => {
  const { user } = useAuth();

  const stats = [
    {
      icon: <LayoutDashboard className="w-8 h-8" />,
      label: 'Active Projects',
      value: '12',
      change: '+3 this month',
      color: 'bg-blue-100 text-blue-600'
    },
    {
      icon: <Users className="w-8 h-8" />,
      label: 'Team Members',
      value: '24',
      change: '4 available',
      color: 'bg-green-100 text-green-600'
    },
    {
      icon: <AlertCircle className="w-8 h-8" />,
      label: 'Risk Alerts',
      value: '3',
      change: '2 high priority',
      color: 'bg-yellow-100 text-yellow-600'
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      label: 'Completion Rate',
      value: '87%',
      change: '+5% this week',
      color: 'bg-purple-100 text-purple-600'
    }
  ];

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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.full_name || user?.email}!
          </h1>
          <p className="text-gray-600 mt-2">
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
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              whileHover={{ y: -5 }}
              className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-all duration-300"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm text-gray-600 mb-2">{stat.label}</p>
                  <h3 className="text-3xl font-bold text-gray-900 mb-1">
                    {stat.value}
                  </h3>
                  <p className="text-xs text-gray-500">{stat.change}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  {stat.icon}
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="lg:col-span-2 bg-white rounded-xl shadow-md p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Recent Activity</h2>
              <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
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
                  className="flex items-start space-x-4 p-4 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <div className="flex-shrink-0 mt-1">
                    {activity.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      {activity.title}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {activity.description}
                    </p>
                    <div className="flex items-center mt-2 text-xs text-gray-500">
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
            className="bg-white rounded-xl shadow-md p-6"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">Quick Actions</h2>
            
            <div className="space-y-3">
              <button className="w-full text-left px-4 py-3 bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100 transition-colors font-medium">
                Generate Report
              </button>
              <button className="w-full text-left px-4 py-3 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors font-medium">
                Create New Project
              </button>
              <button className="w-full text-left px-4 py-3 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors font-medium">
                Invite Team Member
              </button>
              <button className="w-full text-left px-4 py-3 bg-yellow-50 text-yellow-700 rounded-lg hover:bg-yellow-100 transition-colors font-medium">
                Review Risk Alerts
              </button>
            </div>

            {/* AI Insights */}
            <div className="mt-6 p-4 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg text-white">
              <h3 className="font-semibold mb-2">AI Insight</h3>
              <p className="text-sm text-primary-100">
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
          className="mt-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg p-8 text-white text-center"
        >
          <h3 className="text-2xl font-bold mb-2">More Features Coming Soon!</h3>
          <p className="text-blue-100 mb-4">
            We're working on advanced AI predictions, real-time collaboration, and more integrations.
          </p>
          <button className="bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
            Stay Updated
          </button>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
