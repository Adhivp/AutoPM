import React from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from './components/Features';
import DashboardDemo from './components/DashboardDemo';
import TechStack from './components/TechStack';
import Team from './components/Team';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <ThemeProvider>
      <div className="app">
        <Navbar />
        <Hero />
        <Features />
        <DashboardDemo />
        <TechStack />
        <Team />
        <Footer />
      </div>
    </ThemeProvider>
  );
}

export default App;
