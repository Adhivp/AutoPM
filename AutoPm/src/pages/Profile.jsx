import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { integrationAPI } from '../utils/api';
import { motion } from 'framer-motion';
import { 
  User, 
  Mail, 
  Shield, 
  Github, 
  CheckCircle, 
  XCircle,
  Loader,
  ExternalLink,
  AlertCircle
} from 'lucide-react';

const Profile = () => {
  const { user } = useAuth();
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connectingProvider, setConnectingProvider] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadIntegrations();
    // Handle OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const provider = urlParams.get('provider');
    
    if (code && provider) {
      handleOAuthCallback(code, provider);
    }
  }, []);

  const loadIntegrations = async () => {
    try {
      const response = await integrationAPI.getStatus();
      setIntegrations(response.data);
    } catch (err) {
      console.error('Failed to load integrations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (provider) => {
    try {
      setError('');
      setConnectingProvider(provider);
      
      let response;
      if (provider === 'github') {
        response = await integrationAPI.getGithubUrl();
      } else if (provider === 'jira') {
        response = await integrationAPI.getJiraUrl();
      }
      
      // Redirect to OAuth provider
      window.location.href = response.data.url;
    } catch (err) {
      setError(`Failed to connect ${provider}. Please try again.`);
      setConnectingProvider(null);
    }
  };

  const handleOAuthCallback = async (code, provider) => {
    try {
      setConnectingProvider(provider);
      
      if (provider === 'github') {
        await integrationAPI.connectGithub(code);
      } else if (provider === 'jira') {
        await integrationAPI.connectJira(code);
      }
      
      setSuccess(`Successfully connected ${provider}!`);
      
      // Clean URL and reload integrations
      window.history.replaceState({}, document.title, '/profile');
      await loadIntegrations();
    } catch (err) {
      setError(`Failed to complete ${provider} connection. Please try again.`);
    } finally {
      setConnectingProvider(null);
      setTimeout(() => {
        setSuccess('');
        setError('');
      }, 5000);
    }
  };

  const handleDisconnect = async (provider) => {
    if (!window.confirm(`Are you sure you want to disconnect ${provider}?`)) {
      return;
    }

    try {
      setError('');
      await integrationAPI.disconnect(provider);
      setSuccess(`Successfully disconnected ${provider}!`);
      await loadIntegrations();
    } catch (err) {
      setError(`Failed to disconnect ${provider}. Please try again.`);
    } finally {
      setTimeout(() => {
        setSuccess('');
        setError('');
      }, 5000);
    }
  };

  const getIntegrationConfig = (provider) => {
    const configs = {
      github: {
        name: 'GitHub',
        icon: 'logo',
        logoSrc: '/github_logo.png',
        color: 'bg-gray-900 dark:bg-gray-800',
        hoverColor: 'hover:bg-gray-800 dark:hover:bg-gray-700',
        description: 'Connect to sync repositories, issues, and pull requests',
        features: ['Repository access', 'Issue tracking', 'PR monitoring', 'Commit history']
      },
      jira: {
        name: 'Jira',
        icon: 'logo',
        logoSrc: '/jira_logo.jpeg',
        color: 'bg-blue-600 dark:bg-blue-700',
        hoverColor: 'hover:bg-blue-700 dark:hover:bg-blue-600',
        description: 'Connect to sync projects, issues, and sprints',
        features: ['Project tracking', 'Sprint planning', 'Issue management', 'Workflow automation']
      }
    };
    return configs[provider];
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
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Profile Settings</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage your account and integrations
          </p>
        </motion.div>

        {/* Alerts */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg flex items-center space-x-2"
          >
            <AlertCircle size={20} />
            <span>{error}</span>
          </motion.div>
        )}

        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 px-4 py-3 rounded-lg flex items-center space-x-2"
          >
            <CheckCircle size={20} />
            <span>{success}</span>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* User Info Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1 bg-white dark:bg-gray-800 rounded-xl shadow-md dark:shadow-primary-500/10 p-6 border border-transparent dark:border-gray-700"
          >
            <div className="text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-teal-500 rounded-full mx-auto mb-4 flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                {user?.full_name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase()}
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                {user?.full_name || 'User'}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 mb-4">{user?.email}</p>
              
              <div className="space-y-3 text-left">
                <div className="flex items-center space-x-3 text-sm">
                  <User className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                  <span className="text-gray-600 dark:text-gray-300">Member since {new Date().getFullYear()}</span>
                </div>
                <div className="flex items-center space-x-3 text-sm">
                  <Shield className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                  <span className="text-gray-600 dark:text-gray-300 capitalize">Role: {user?.role}</span>
                </div>
                <div className="flex items-center space-x-3 text-sm">
                  <Mail className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                  <span className="text-gray-600 dark:text-gray-300">Email verified</span>
                </div>
              </div>

              <button className="w-full mt-6 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium">
                Edit Profile
              </button>
            </div>
          </motion.div>

          {/* Integrations */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-2"
          >
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md dark:shadow-primary-500/10 p-6 border border-transparent dark:border-gray-700">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Integrations</h2>
                <p className="text-gray-600 dark:text-gray-300">
                  Connect your tools to unlock the full power of AutoPM
                </p>
              </div>

              {loading ? (
                <div className="flex justify-center py-12">
                  <Loader className="w-8 h-8 text-primary-600 dark:text-primary-400 animate-spin" />
                </div>
              ) : (
                <motion.div
                  initial="hidden"
                  animate="visible"
                  variants={containerVariants}
                  className="space-y-4"
                >
                  {integrations.map((integration) => {
                    const config = getIntegrationConfig(integration.provider);
                    if (!config) return null;

                    return (
                      <motion.div
                        key={integration.provider}
                        variants={itemVariants}
                        className="border border-gray-200 dark:border-gray-700 rounded-xl p-6 hover:shadow-md dark:hover:shadow-primary-500/20 transition-all duration-300 integration-card bg-gray-50 dark:bg-gray-900/50"
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center space-x-4">
                            <div className="bg-white dark:bg-gray-700 p-3 rounded-lg flex items-center justify-center w-16 h-16">
                              <img 
                                src={config.logoSrc} 
                                alt={`${config.name} Logo`}
                                className="w-full h-full object-contain"
                              />
                            </div>
                            <div>
                              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                                {config.name}
                              </h3>
                              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                                {config.description}
                              </p>
                            </div>
                          </div>

                          {integration.connected ? (
                            <div className="flex items-center space-x-2 text-green-600 dark:text-green-400">
                              <CheckCircle className="w-5 h-5" />
                              <span className="text-sm font-medium">Connected</span>
                            </div>
                          ) : (
                            <div className="flex items-center space-x-2 text-gray-400 dark:text-gray-500">
                              <XCircle className="w-5 h-5" />
                              <span className="text-sm font-medium">Not Connected</span>
                            </div>
                          )}
                        </div>

                        {integration.connected && (
                          <div className="mb-4 p-3 bg-gray-100 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                            <p className="text-sm text-gray-600 dark:text-gray-300">
                              <strong>User ID:</strong> {integration.provider_user_id || 'N/A'}
                            </p>
                            {integration.provider_email && (
                              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                                <strong>Email:</strong> {integration.provider_email}
                              </p>
                            )}
                          </div>
                        )}

                        <div className="mb-4">
                          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Features:</p>
                          <div className="grid grid-cols-2 gap-2">
                            {config.features.map((feature, idx) => (
                              <div key={idx} className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300">
                                <CheckCircle className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                                <span>{feature}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="flex space-x-3">
                          {integration.connected ? (
                            <>
                              <button
                                onClick={() => handleDisconnect(integration.provider)}
                                className="flex-1 px-4 py-2 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/50 transition-colors font-medium"
                              >
                                Disconnect
                              </button>
                              <button className="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium flex items-center justify-center space-x-2">
                                <ExternalLink className="w-4 h-4" />
                                <span>View Settings</span>
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={() => handleConnect(integration.provider)}
                              disabled={connectingProvider === integration.provider}
                              className="flex-1 px-4 py-2 bg-gradient-to-r from-primary-500 to-teal-500 hover:from-primary-600 hover:to-teal-600 text-white rounded-lg transition-colors font-medium flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                            >
                              {connectingProvider === integration.provider ? (
                                <>
                                  <Loader className="w-4 h-4 animate-spin" />
                                  <span>Connecting...</span>
                                </>
                              ) : (
                                <>
                                  <ExternalLink className="w-4 h-4" />
                                  <span>Connect {config.name}</span>
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </motion.div>
              )}

              {/* Coming Soon */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="mt-6 p-4 bg-gradient-to-r from-primary-500/10 to-teal-500/10 dark:from-primary-500/20 dark:to-teal-500/20 border border-primary-500/30 dark:border-primary-500/40 rounded-lg text-center"
              >
                <p className="text-gray-700 dark:text-gray-200 font-medium">
                  🚀 More integrations coming soon: MS Teams, Slack, Trello, and more!
                </p>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
