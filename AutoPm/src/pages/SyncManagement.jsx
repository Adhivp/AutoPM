import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  RefreshCw,
  Play,
  Square,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Activity,
  Calendar,
  GitBranch,
  ExternalLink
} from 'lucide-react';
import { syncAPI } from '../utils/api';

const SyncManagement = () => {
  const [syncStatus, setSyncStatus] = useState(null);
  const [syncHistory, setSyncHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [triggeringSync, setTriggeringSync] = useState(false);
  const [stoppingSync, setStoppingSync] = useState(false);

  useEffect(() => {
    fetchSyncStatus();
    fetchSyncHistory();
  }, []);

  const fetchSyncStatus = async () => {
    try {
      const response = await syncAPI.getSyncStatus();
      setSyncStatus(response.data);
    } catch (err) {
      setError('Failed to fetch sync status');
      console.error('Error fetching sync status:', err);
    }
  };

  const fetchSyncHistory = async () => {
    try {
      const response = await syncAPI.getSyncHistory();
      setSyncHistory(response.data);
    } catch (err) {
      console.error('Error fetching sync history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerSync = async () => {
    try {
      setTriggeringSync(true);
      setError(null);
      await syncAPI.triggerSync();
      // Refresh status after a short delay
      setTimeout(() => {
        fetchSyncStatus();
        fetchSyncHistory();
      }, 2000);
    } catch (err) {
      setError('Failed to trigger sync');
      console.error('Error triggering sync:', err);
    } finally {
      setTriggeringSync(false);
    }
  };

  const handleStopSync = async () => {
    try {
      setStoppingSync(true);
      setError(null);
      await syncAPI.stopSync();
      // Refresh status
      setTimeout(() => {
        fetchSyncStatus();
      }, 1000);
    } catch (err) {
      setError('Failed to stop sync');
      console.error('Error stopping sync:', err);
    } finally {
      setStoppingSync(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running': return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'idle': return <Clock className="w-5 h-5 text-gray-500" />;
      default: return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'bg-blue-100 text-blue-800';
      case 'success': return 'bg-green-100 text-green-800';
      case 'error': return 'bg-red-100 text-red-800';
      case 'idle': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading sync management...</p>
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
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Sync Management</h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Monitor and control GitHub/Jira synchronization</p>
            </div>
          </div>
        </motion.div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 rounded-lg"
          >
            {error}
          </motion.div>
        )}

        {/* Current Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Current Sync Status</h2>

          {syncStatus && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  {getStatusIcon(syncStatus.github_sync_status)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">GitHub Sync</div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(syncStatus.github_sync_status)}`}>
                  {syncStatus.github_sync_status}
                </span>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  {getStatusIcon(syncStatus.jira_sync_status)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Jira Sync</div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(syncStatus.jira_sync_status)}`}>
                  {syncStatus.jira_sync_status}
                </span>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <Activity className="w-5 h-5 text-blue-500" />
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">GitHub Items</div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">{syncStatus.github_synced_items || 0}</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <Activity className="w-5 h-5 text-green-500" />
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Jira Items</div>
                <div className="text-lg font-semibold text-gray-900 dark:text-white">{syncStatus.jira_synced_items || 0}</div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Last Sync Times</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">GitHub:</span>
                  <span className="text-gray-900 dark:text-white font-medium">
                    {formatDateTime(syncStatus?.last_github_sync)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Jira:</span>
                  <span className="text-gray-900 dark:text-white font-medium">
                    {formatDateTime(syncStatus?.last_jira_sync)}
                  </span>
                </div>
              </div>
            </div>

            {syncStatus?.errors && syncStatus.errors.length > 0 && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Recent Errors</h3>
                <div className="space-y-2">
                  {syncStatus.errors.slice(0, 3).map((error, index) => (
                    <div key={index} className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900 p-2 rounded">
                      {error}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Control Buttons */}
          <div className="flex flex-wrap gap-4">
            <button
              onClick={handleTriggerSync}
              disabled={triggeringSync || syncStatus?.github_sync_status === 'running' || syncStatus?.jira_sync_status === 'running'}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
            >
              {triggeringSync ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {triggeringSync ? 'Triggering Sync...' : 'Trigger Manual Sync'}
            </button>

            <button
              onClick={handleStopSync}
              disabled={stoppingSync || (syncStatus?.github_sync_status !== 'running' && syncStatus?.jira_sync_status !== 'running')}
              className="bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
            >
              {stoppingSync ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Square className="w-4 h-4" />
              )}
              {stoppingSync ? 'Stopping...' : 'Stop Sync'}
            </button>
          </div>
        </motion.div>

        {/* Sync History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Sync History by Project</h2>

          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3">Project</th>
                  <th className="px-6 py-3">Jira Project Key</th>
                  <th className="px-6 py-3">GitHub Repo</th>
                  <th className="px-6 py-3">Last Jira Sync</th>
                  <th className="px-6 py-3">Last GitHub Sync</th>
                </tr>
              </thead>
              <tbody>
                {syncHistory.map((item, index) => (
                  <tr key={index} className="bg-white dark:bg-gray-800 border-b dark:border-gray-700">
                    <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">
                      {item.project_name}
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      {item.jira_project_key || 'Not configured'}
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      {item.github_repo_name || 'Not configured'}
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      {formatDateTime(item.last_jira_sync)}
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      {formatDateTime(item.last_github_sync)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {syncHistory.length === 0 && (
            <div className="text-center py-8">
              <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No sync history available</h3>
              <p className="text-gray-600 dark:text-gray-400">Sync history will appear here after the first synchronization.</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default SyncManagement;