import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  BarChart3, 
  Users, 
  AlertTriangle, 
  MessageSquare,
  CheckCircle,
  Zap,
  Shield,
  TrendingUp,
  Clock
} from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: 'Auto-Generated Dashboards',
      description: 'Integrate Jira, GitHub, and MS Teams data to create comprehensive project dashboards automatically.',
      color: 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: 'Resource Allocation Insights',
      description: 'Real-time visibility into who is overloaded and who is available for new tasks.',
      color: 'bg-teal-100 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400'
    },
    {
      icon: <AlertTriangle className="w-8 h-8" />,
      title: 'Risk & Delay Prediction',
      description: 'AI-powered predictions using historical patterns and live progress signals.',
      color: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400'
    },
    {
      icon: <MessageSquare className="w-8 h-8" />,
      title: 'Natural Language Summaries',
      description: 'Deliver clear, actionable summaries for managers and stakeholders.',
      color: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400'
    }
  ];

  const benefits = [
    { icon: <Zap />, text: 'Save 10+ hours per week on manual reporting' },
    { icon: <Shield />, text: 'Secure integration with your favorite tools' },
    { icon: <TrendingUp />, text: 'Data-driven insights for better decisions' },
    { icon: <Clock />, text: 'Real-time updates and notifications' }
  ];

  const integrations = [
    { name: 'GitHub', logo: '/github_logo.png', color: 'bg-gray-900 dark:bg-gray-100' },
    { name: 'Jira', logo: '/jira_logo.jpeg', color: 'bg-blue-600' },
    { name: 'MS Teams', icon: '💬', color: 'bg-purple-600' }
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
    <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors duration-300">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900 dark:from-gray-950 dark:via-slate-900 dark:to-gray-950 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="absolute inset-0">
          <div className="absolute top-20 left-10 w-72 h-72 bg-primary-500 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-72 h-72 bg-teal-400 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse animation-delay-2000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-emerald-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="inline-flex items-center space-x-2 bg-primary-500/20 backdrop-blur-sm border border-primary-400/30 px-4 py-2 rounded-full mb-6"
            >
              <Sparkles className="w-5 h-5 text-primary-300" />
              <span className="text-sm font-medium text-primary-200">AI-Powered Project Management</span>
            </motion.div>

            <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
              Transform Your Project
              <br />
              <span className="bg-gradient-to-r from-primary-400 to-teal-400 bg-clip-text text-transparent">
                Management Workflow
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-300 mb-10 max-w-3xl mx-auto">
              AutoPM automates dashboards, predicts risks, and delivers intelligent insights 
              by integrating your project data from Jira, GitHub, and MS Teams.
            </p>

            <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4">
              <Link
                to="/register"
                className="bg-gradient-to-r from-primary-500 to-teal-500 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:from-primary-600 hover:to-teal-600 transition-all duration-200 shadow-xl shadow-primary-500/30 hover:shadow-2xl hover:shadow-primary-500/40 transform hover:-translate-y-1"
              >
                Get Started Free
              </Link>
              <Link
                to="/login"
                className="bg-transparent border-2 border-primary-400 text-primary-300 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-primary-500/10 transition-all duration-200"
              >
                Sign In
              </Link>
            </div>
          </motion.div>
        </div>

        {/* Wave separator */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="dark:opacity-100 opacity-100">
            <path d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" className="fill-white dark:fill-gray-900"/>
          </svg>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={containerVariants}
            className="text-center mb-16"
          >
            <motion.h2 variants={itemVariants} className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Powerful Features Built for Project Managers
            </motion.h2>
            <motion.p variants={itemVariants} className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Everything you need to manage projects efficiently and make data-driven decisions
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={containerVariants}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8"
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover={{ y: -10 }}
                className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg hover:shadow-xl dark:shadow-primary-500/10 dark:hover:shadow-primary-500/20 transition-all duration-300 border border-transparent dark:border-gray-700"
              >
                <div className={`${feature.color} w-16 h-16 rounded-lg flex items-center justify-center mb-4`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-6">
                Why Choose AutoPM?
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
                AutoPM combines the power of AI with seamless integrations to give you 
                unprecedented visibility and control over your projects.
              </p>
              
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className="flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-lg"
                  >
                    <div className="text-primary-600 dark:text-primary-400 flex-shrink-0">
                      {benefit.icon}
                    </div>
                    <span className="text-gray-800 dark:text-gray-200 font-medium">{benefit.text}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              <div className="bg-gradient-to-br from-primary-500 to-teal-500 rounded-2xl p-8 shadow-2xl dark:shadow-primary-500/20">
                <img 
                  src="/logo.jpeg" 
                  alt="AutoPM Dashboard" 
                  className="w-full rounded-lg shadow-lg"
                />
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Integrations Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={containerVariants}
            className="text-center mb-16"
          >
            <motion.h2 variants={itemVariants} className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Seamless Integrations
            </motion.h2>
            <motion.p variants={itemVariants} className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Connect your favorite tools and let AutoPM do the heavy lifting
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={containerVariants}
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
          >
            {integrations.map((integration, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover={{ scale: 1.05 }}
                className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg dark:shadow-primary-500/10 text-center border border-transparent dark:border-gray-700"
              >
                <div className="flex justify-center mb-6">
                  {integration.logo ? (
                    <div className="w-20 h-20 flex items-center justify-center rounded-lg overflow-hidden bg-white dark:bg-gray-700 p-3">
                      <img 
                        src={integration.logo} 
                        alt={`${integration.name} Logo`}
                        className="w-full h-full object-contain"
                      />
                    </div>
                  ) : (
                    <span className="text-6xl">{integration.icon}</span>
                  )}
                </div>
                <h3 className="text-2xl font-semibold text-gray-900 dark:text-white">{integration.name}</h3>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-gray-900 via-slate-800 to-gray-900 dark:from-gray-950 dark:via-slate-900 dark:to-gray-950 text-white relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-0 left-0 w-96 h-96 bg-primary-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-teal-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
        </div>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl md:text-5xl font-bold mb-6">
              Ready to Transform Your Project Management?
            </h2>
            <p className="text-xl mb-10 text-gray-300">
              Join thousands of project managers who trust AutoPM to streamline their workflow
            </p>
            <Link
              to="/register"
              className="inline-block bg-gradient-to-r from-primary-500 to-teal-500 text-white px-10 py-4 rounded-lg font-semibold text-lg hover:from-primary-600 hover:to-teal-600 transition-all duration-200 shadow-xl shadow-primary-500/30 hover:shadow-2xl hover:shadow-primary-500/40 transform hover:-translate-y-1"
            >
              Start Your Free Trial
            </Link>
            <p className="mt-6 text-gray-400">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Home;
