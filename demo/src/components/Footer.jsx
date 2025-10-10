import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="footer-content"
        >
          <div className="footer-brand">
            <div className="logo">
              <Zap className="logo-icon" />
              <span className="logo-text">Auto<span className="logo-highlight">PM</span></span>
            </div>
            <p className="footer-tagline">
              The AI Copilot for Automotive Project Management
            </p>
          </div>

          <div className="footer-links">
            <div className="footer-column">
              <h4 className="footer-title">Product</h4>
              <a href="#features">Features</a>
              <a href="#demo">Dashboard</a>
              <a href="#tech">Technology</a>
            </div>
            <div className="footer-column">
              <h4 className="footer-title">Team</h4>
              <a href="#team">About Us</a>
              <a href="#team">Contact</a>
            </div>
            <div className="footer-column">
              <h4 className="footer-title">Project</h4>
              <a href="#">Problem Statement</a>
              <a href="#">Documentation</a>
            </div>
          </div>
        </motion.div>

        <div className="footer-bottom">
          <p>
            Made with <Heart size={16} className="heart-icon" /> by Porotta Pythoners
          </p>
          <p className="footer-copy">
            © 2025 AutoPM. Demo project for AH2025/PS02
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
