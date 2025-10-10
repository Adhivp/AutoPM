import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  TrendingUp,
  Users,
  GitCommit,
  Target
} from 'lucide-react';

const DashboardDemo = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Activity size={18} /> },
    { id: 'risks', label: 'Risks', icon: <AlertTriangle size={18} /> },
    { id: 'workload', label: 'Workload', icon: <Users size={18} /> },
  ];

  const overviewData = [
    { label: 'Active Tasks', value: '47', icon: <Target />, trend: '+12%', color: '#3b82f6' },
    { label: 'Team Members', value: '8', icon: <Users />, trend: '+2', color: '#8b5cf6' },
    { label: 'Commits Today', value: '23', icon: <GitCommit />, trend: '+8', color: '#10b981' },
    { label: 'Sprint Progress', value: '68%', icon: <TrendingUp />, trend: '+15%', color: '#f59e0b' },
  ];

  const riskData = [
    { 
      title: 'High Priority: Authentication Module', 
      severity: 'high', 
      impact: 'Cascading delay detected in 4 dependent modules',
      assignee: 'Sreya S.'
    },
    { 
      title: 'Medium Priority: Database Migration', 
      severity: 'medium', 
      impact: 'Resource bottleneck - Reassignment suggested',
      assignee: 'Adhithyan VP'
    },
    { 
      title: 'Low Priority: Documentation Gap', 
      severity: 'low', 
      impact: 'ISO 26262 compliance check flagged',
      assignee: 'Team Lead'
    },
  ];

  const workloadData = [
    { name: 'Adhithyan VP', tasks: 12, capacity: 85, status: 'optimal' },
    { name: 'Sreya Suresh', tasks: 10, capacity: 75, status: 'optimal' },
    { name: 'Developer 1', tasks: 15, capacity: 95, status: 'high' },
    { name: 'Developer 2', tasks: 8, capacity: 60, status: 'low' },
  ];

  return (
    <section id="demo" className="dashboard-demo">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="section-header"
        >
          <h2 className="section-title">
            Interactive <span className="gradient-text">Dashboard</span> Preview
          </h2>
          <p className="section-subtitle">
            Experience the power of AI-driven project insights in real-time
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="dashboard-container"
        >
          <div className="dashboard-tabs">
            {tabs.map((tab) => (
              <motion.button
                key={tab.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setActiveTab(tab.id)}
                className={`dashboard-tab ${activeTab === tab.id ? 'active' : ''}`}
              >
                {tab.icon}
                {tab.label}
              </motion.button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            {activeTab === 'overview' && (
              <motion.div
                key="overview"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="dashboard-content"
              >
                <div className="metrics-grid">
                  {overviewData.map((metric, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.1 }}
                      className="metric-card"
                    >
                      <div 
                        className="metric-icon"
                        style={{ '--metric-color': metric.color }}
                      >
                        {metric.icon}
                      </div>
                      <div className="metric-info">
                        <div className="metric-label">{metric.label}</div>
                        <div className="metric-value">{metric.value}</div>
                        <div className="metric-trend">{metric.trend}</div>
                      </div>
                    </motion.div>
                  ))}
                </div>

                <div className="activity-feed">
                  <h3 className="feed-title">Recent Activity</h3>
                  <div className="feed-items">
                    <div className="feed-item">
                      <CheckCircle2 className="feed-icon success" />
                      <div className="feed-content">
                        <div className="feed-text">Authentication module tests passed</div>
                        <div className="feed-time">2 minutes ago</div>
                      </div>
                    </div>
                    <div className="feed-item">
                      <AlertTriangle className="feed-icon warning" />
                      <div className="feed-content">
                        <div className="feed-text">Risk detected in payment integration</div>
                        <div className="feed-time">15 minutes ago</div>
                      </div>
                    </div>
                    <div className="feed-item">
                      <Clock className="feed-icon info" />
                      <div className="feed-content">
                        <div className="feed-text">Sprint review scheduled for tomorrow</div>
                        <div className="feed-time">1 hour ago</div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'risks' && (
              <motion.div
                key="risks"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="dashboard-content"
              >
                <div className="risks-list">
                  {riskData.map((risk, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`risk-card severity-${risk.severity}`}
                    >
                      <div className="risk-header">
                        <div className="risk-severity">{risk.severity.toUpperCase()}</div>
                        <div className="risk-assignee">{risk.assignee}</div>
                      </div>
                      <h4 className="risk-title">{risk.title}</h4>
                      <p className="risk-impact">{risk.impact}</p>
                      <button className="risk-action">View Details →</button>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'workload' && (
              <motion.div
                key="workload"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="dashboard-content"
              >
                <div className="workload-list">
                  {workloadData.map((member, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="workload-card"
                    >
                      <div className="workload-header">
                        <div className="workload-name">{member.name}</div>
                        <div className={`workload-status status-${member.status}`}>
                          {member.status}
                        </div>
                      </div>
                      <div className="workload-stats">
                        <div className="workload-stat">
                          <span className="stat-label">Tasks</span>
                          <span className="stat-value">{member.tasks}</span>
                        </div>
                        <div className="workload-stat">
                          <span className="stat-label">Capacity</span>
                          <span className="stat-value">{member.capacity}%</span>
                        </div>
                      </div>
                      <div className="capacity-bar">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${member.capacity}%` }}
                          transition={{ delay: 0.5 + index * 0.1, duration: 0.8 }}
                          className={`capacity-fill capacity-${member.status}`}
                        />
                      </div>
                    </motion.div>
                  ))}
                </div>

                <div className="ai-suggestion">
                  <div className="suggestion-icon">🤖</div>
                  <div className="suggestion-content">
                    <h4>AI Recommendation</h4>
                    <p>Consider reassigning 2 tasks from Developer 1 to Developer 2 to optimize team capacity and reduce burnout risk.</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </section>
  );
};

export default DashboardDemo;
