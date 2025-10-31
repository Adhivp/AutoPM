import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, GitBranch, Users } from 'lucide-react';

const Hero = () => {
  return (
    <section className="hero">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="hero-content"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="hero-badge"
          >
            <Sparkles size={16} />
            <span>AI-Powered Project Management</span>
          </motion.div>

          <h1 className="hero-title">
            <span className="gradient-text">AutoPM</span>
            <br />
            The AI Copilot for Automotive Project Management
          </h1>

          <p className="hero-subtitle">
            Unify Jira, GitHub, and Teams. Predict risks with dependency graphs. 
            Optimize workloads. Ensure compliance through intelligent automation.
          </p>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="hero-cta"
          >
            <button className="btn btn-primary">
              Explore Features
              <ArrowRight size={20} />
            </button>
            <button className="btn btn-secondary">
              Watch Demo
            </button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="hero-stats"
          >
            <div className="stat">
              <GitBranch className="stat-icon" />
              <div>
                <div className="stat-value">30-40%</div>
                <div className="stat-label">Time Saved</div>
              </div>
            </div>
            <div className="stat">
              <Users className="stat-icon" />
              <div>
                <div className="stat-value">100%</div>
                <div className="stat-label">Compliance Ready</div>
              </div>
            </div>
            <div className="stat">
              <Sparkles className="stat-icon" />
              <div>
                <div className="stat-value">Real-time</div>
                <div className="stat-label">Risk Detection</div>
              </div>
            </div>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 1 }}
          className="hero-visual"
        >
          <div className="floating-card card-1">
            <div className="card-icon">📊</div>
            <div className="card-text">Auto-generated Dashboards</div>
          </div>
          <div className="floating-card card-2">
            <div className="card-icon">🔗</div>
            <div className="card-text">Dependency Graph Analysis</div>
          </div>
          <div className="floating-card card-3">
            <div className="card-icon">🤖</div>
            <div className="card-text">AI Workload Optimizer</div>
          </div>
          <div className="hero-circle"></div>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;
