import React from 'react';
import { motion } from 'framer-motion';
import { Moon, Sun, Zap } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const Navbar = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="navbar"
    >
      <div className="container">
        <div className="nav-content">
          <div className="logo">
            <Zap className="logo-icon" />
            <span className="logo-text">Auto<span className="logo-highlight">PM</span></span>
          </div>
          
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#demo">Demo</a>
            <a href="#tech">Tech Stack</a>
            <a href="#team">Team</a>
          </div>

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={toggleTheme}
            className="theme-toggle"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          </motion.button>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
