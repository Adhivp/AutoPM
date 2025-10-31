import React from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  Network, 
  Brain, 
  Shield, 
  MessageSquare, 
  TrendingUp,
  CheckCircle,
  Zap
} from 'lucide-react';

const features = [
  {
    icon: <BarChart3 />,
    title: 'Auto-Generated Dashboards',
    description: 'Consolidate Jira, GitHub, Teams, and Confluence data into unified, real-time dashboards.',
    color: '#3b82f6'
  },
  {
    icon: <Network />,
    title: 'Dependency Graph Intelligence',
    description: 'Build and analyze project dependency graphs using GNNs to highlight cascading delays.',
    color: '#8b5cf6'
  },
  {
    icon: <Brain />,
    title: 'AI Workload Optimizer',
    description: 'Actively suggests task reassignment to prevent overload and balance team capacity.',
    color: '#ec4899'
  },
  {
    icon: <Shield />,
    title: 'Compliance-Aware AI',
    description: 'Flags non-compliance in workflows for ISO 26262 & ASPICE standards automatically.',
    color: '#10b981'
  },
  {
    icon: <MessageSquare />,
    title: 'Conversational PM Agent',
    description: 'Natural language Q&A interface for project managers with context-aware responses.',
    color: '#f59e0b'
  },
  {
    icon: <TrendingUp />,
    title: 'What-if Scenario Generator',
    description: 'Simulate resource changes and delivery impacts with Monte Carlo simulation.',
    color: '#06b6d4'
  },
  {
    icon: <CheckCircle />,
    title: 'Multi-Modal Risk Prediction',
    description: 'Combines data, commits, and sentiment analysis for deeper risk insights.',
    color: '#ef4444'
  },
  {
    icon: <Zap />,
    title: 'Causal AI Explanations',
    description: 'Explains why risks exist, not just what they are, for better decision making.',
    color: '#a855f7'
  }
];

const Features = () => {
  return (
    <section id="features" className="features">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="section-header"
        >
          <h2 className="section-title">
            Unique Features & <span className="gradient-text">Innovations</span>
          </h2>
          <p className="section-subtitle">
            Transform project management from reactive tracking to proactive intelligence
          </p>
        </motion.div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -10 }}
              className="feature-card"
            >
              <div 
                className="feature-icon"
                style={{ '--feature-color': feature.color }}
              >
                {feature.icon}
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
