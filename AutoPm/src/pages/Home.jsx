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
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-950 transition-colors duration-300">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-slate-900 via-gray-900 to-slate-950 dark:from-black dark:via-gray-950 dark:to-black text-white overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary-900/20 via-transparent to-transparent"></div>
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-20 left-10 w-96 h-96 bg-primary-500 rounded-full mix-blend-screen filter blur-3xl animate-blob"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-teal-400 rounded-full mix-blend-screen filter blur-3xl animate-blob animation-delay-2000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-emerald-500 rounded-full mix-blend-screen filter blur-3xl animate-blob animation-delay-4000 opacity-50"></div>
        </div>

        {/* Floating Particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 bg-white/20 rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                y: [0, -30, 0],
                opacity: [0.2, 0.8, 0.2],
              }}
              transition={{
                duration: 3 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-36">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-500/20 to-teal-500/20 backdrop-blur-sm border border-primary-400/30 px-5 py-2.5 rounded-full mb-8 shadow-lg shadow-primary-500/20"
            >
              <Sparkles className="w-5 h-5 text-primary-300 animate-pulse" />
              <span className="text-sm font-semibold text-primary-100 tracking-wide">AI-Powered Project Management</span>
            </motion.div>

            <motion.h1 
              className="text-5xl md:text-7xl font-extrabold mb-8 leading-tight"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
            >
              <span className="text-white">Transform Your</span>
              <br />
              <span className="bg-gradient-to-r from-primary-400 via-teal-400 to-emerald-400 bg-clip-text text-transparent animate-gradient">
                Project Management
              </span>
            </motion.h1>
            
            <motion.p 
              className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.5 }}
            >
              AutoPM automates dashboards, predicts risks, and delivers intelligent insights 
              by seamlessly integrating your project data from Jira, GitHub, and MS Teams.
            </motion.p>

            <motion.div 
              className="flex flex-col sm:flex-row justify-center items-center gap-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.7 }}
            >
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link
                  to="/register"
                  className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-gradient-to-r from-primary-500 to-teal-500 rounded-xl overflow-hidden shadow-2xl shadow-primary-500/30 hover:shadow-primary-500/50 transition-all duration-300"
                >
                  <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-primary-600 to-teal-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
                  <span className="relative flex items-center space-x-2">
                    <span>Get Started Free</span>
                    <Sparkles className="w-5 h-5" />
                  </span>
                </Link>
              </motion.div>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link
                  to="/login"
                  className="inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-xl hover:bg-white/20 hover:border-white/30 transition-all duration-300"
                >
                  Sign In
                </Link>
              </motion.div>
            </motion.div>

            {/* Trust Indicators */}
            <motion.div
              className="mt-16 flex flex-wrap justify-center items-center gap-8 opacity-60"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.6 }}
              transition={{ duration: 1, delay: 1 }}
            >
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-300">No credit card required</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-300">14-day free trial</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-300">Cancel anytime</span>
              </div>
            </motion.div>
          </motion.div>
        </div>

        {/* Wave separator */}
        <div className="absolute bottom-0 left-0 right-0 pointer-events-none">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto">
            <path d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" className="fill-white dark:fill-gray-900"/>
          </svg>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={containerVariants}
            className="text-center mb-16"
          >
            <motion.h2 
              variants={itemVariants} 
              className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-4"
            >
              Powerful Features Built for{' '}
              <span className="bg-gradient-to-r from-primary-600 to-teal-500 bg-clip-text text-transparent">
                Project Managers
              </span>
            </motion.h2>
            <motion.p 
              variants={itemVariants} 
              className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto leading-relaxed"
            >
              Everything you need to manage projects efficiently and make data-driven decisions
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={containerVariants}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover={{ y: -10, scale: 1.02 }}
                transition={{ type: "spring", stiffness: 300 }}
                className="group bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-md hover:shadow-2xl dark:shadow-gray-900/50 dark:hover:shadow-primary-500/20 transition-all duration-300 border border-gray-100 dark:border-gray-700 hover:border-primary-200 dark:hover:border-primary-800 relative overflow-hidden"
              >
                {/* Gradient overlay on hover */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-teal-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                
                <div className="relative z-10">
                  <div className={`${feature.color} w-16 h-16 rounded-xl flex items-center justify-center mb-5 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-24 bg-gradient-to-b from-gray-50 to-white dark:from-gray-950 dark:to-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-6 leading-tight">
                Why Choose{' '}
                <span className="bg-gradient-to-r from-primary-600 to-teal-500 bg-clip-text text-transparent">
                  AutoPM?
                </span>
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-400 mb-10 leading-relaxed">
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
                    whileHover={{ x: 10 }}
                    className="group flex items-center space-x-4 p-5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-lg dark:hover:shadow-primary-500/10 transition-all duration-300"
                  >
                    <div className="text-primary-600 dark:text-primary-400 flex-shrink-0 bg-primary-50 dark:bg-primary-900/30 p-3 rounded-lg group-hover:scale-110 transition-transform duration-300">
                      {benefit.icon}
                    </div>
                    <span className="text-gray-800 dark:text-gray-200 font-semibold text-lg">{benefit.text}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              {/* Decorative elements */}
              <div className="absolute -inset-4 bg-gradient-to-r from-primary-500 to-teal-500 rounded-3xl blur-2xl opacity-20"></div>
              
              <div className="relative bg-gradient-to-br from-primary-500 to-teal-500 rounded-3xl p-1 shadow-2xl dark:shadow-primary-500/20">
                <div className="bg-white dark:bg-gray-900 rounded-[22px] p-8">
                  <img 
                    src="/logo.jpeg" 
                    alt="AutoPM Dashboard" 
                    className="w-full rounded-2xl shadow-2xl transform hover:scale-105 transition-transform duration-500"
                  />
                  
                  {/* Floating badge */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.5 }}
                    className="mt-6 inline-flex items-center space-x-2 bg-gradient-to-r from-primary-500 to-teal-500 text-white px-6 py-3 rounded-full text-sm font-semibold shadow-lg"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>Trusted by 1000+ Teams</span>
                  </motion.div>
                </div>
              </div>

              {/* Floating elements */}
              <motion.div
                animate={{ y: [0, -20, 0] }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                className="absolute -top-6 -right-6 w-24 h-24 bg-primary-500/20 dark:bg-primary-500/10 rounded-2xl rotate-12 blur-xl"
              ></motion.div>
              <motion.div
                animate={{ y: [0, 20, 0] }}
                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                className="absolute -bottom-6 -left-6 w-32 h-32 bg-teal-500/20 dark:bg-teal-500/10 rounded-2xl -rotate-12 blur-xl"
              ></motion.div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Integrations Section */}
      <section className="py-24 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={containerVariants}
            className="text-center mb-16"
          >
            <motion.h2 
              variants={itemVariants} 
              className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-4"
            >
              <span className="bg-gradient-to-r from-primary-600 to-teal-500 bg-clip-text text-transparent">
                Seamless
              </span>{' '}
              Integrations
            </motion.h2>
            <motion.p 
              variants={itemVariants} 
              className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto"
            >
              Connect your favorite tools and let AutoPM do the heavy lifting
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={containerVariants}
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
          >
            {integrations.map((integration, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover={{ scale: 1.05, y: -10 }}
                transition={{ type: "spring", stiffness: 300 }}
                className="group bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 p-10 rounded-2xl shadow-lg hover:shadow-2xl dark:shadow-gray-900/50 dark:hover:shadow-primary-500/20 text-center border border-gray-100 dark:border-gray-700 hover:border-primary-200 dark:hover:border-primary-800 transition-all duration-300 relative overflow-hidden"
              >
                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-teal-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                
                <div className="relative z-10">
                  <motion.div 
                    className="flex justify-center mb-6"
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    {integration.logo ? (
                      <div className="w-24 h-24 flex items-center justify-center rounded-2xl overflow-hidden bg-white dark:bg-gray-700 p-4 shadow-md group-hover:shadow-xl transition-shadow duration-300">
                        <img 
                          src={integration.logo} 
                          alt={`${integration.name} Logo`}
                          className="w-full h-full object-contain"
                        />
                      </div>
                    ) : (
                      <span className="text-7xl filter drop-shadow-lg">{integration.icon}</span>
                    )}
                  </motion.div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-300">
                    {integration.name}
                  </h3>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-24 bg-gradient-to-br from-slate-900 via-gray-900 to-slate-950 dark:from-black dark:via-gray-950 dark:to-black text-white overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-0 left-0 w-96 h-96 bg-primary-500 rounded-full mix-blend-screen filter blur-3xl animate-blob"></div>
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-teal-400 rounded-full mix-blend-screen filter blur-3xl animate-blob animation-delay-2000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-emerald-500 rounded-full mix-blend-screen filter blur-3xl animate-blob animation-delay-4000 opacity-50"></div>
        </div>

        {/* Grid pattern overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_at_center,black_50%,transparent_100%)]"></div>
        
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <motion.div
              initial={{ scale: 0 }}
              whileInView={{ scale: 1 }}
              viewport={{ once: true }}
              transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-500/20 to-teal-500/20 backdrop-blur-sm border border-primary-400/30 px-5 py-2.5 rounded-full mb-8"
            >
              <Sparkles className="w-5 h-5 text-primary-300 animate-pulse" />
              <span className="text-sm font-semibold text-primary-100">Limited Time Offer</span>
            </motion.div>

            <h2 className="text-4xl md:text-6xl font-extrabold mb-6 leading-tight">
              Ready to Transform Your
              <br />
              <span className="bg-gradient-to-r from-primary-400 via-teal-400 to-emerald-400 bg-clip-text text-transparent">
                Project Management?
              </span>
            </h2>
            <p className="text-xl md:text-2xl mb-12 text-gray-300 leading-relaxed">
              Join thousands of project managers who trust AutoPM to streamline their workflow
            </p>
            
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Link
                to="/register"
                className="group relative inline-flex items-center justify-center px-10 py-5 text-xl font-bold text-white bg-gradient-to-r from-primary-500 to-teal-500 rounded-xl overflow-hidden shadow-2xl shadow-primary-500/30 hover:shadow-primary-500/50 transition-all duration-300"
              >
                <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-primary-600 to-teal-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
                <span className="relative flex items-center space-x-2">
                  <span>Start Your Free Trial</span>
                  <Sparkles className="w-5 h-5" />
                </span>
              </Link>
            </motion.div>

            <motion.p 
              className="mt-8 text-gray-400 flex flex-wrap justify-center items-center gap-6"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
            >
              <span className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span>No credit card required</span>
              </span>
              <span className="hidden sm:inline text-gray-600">•</span>
              <span className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span>14-day free trial</span>
              </span>
              <span className="hidden sm:inline text-gray-600">•</span>
              <span className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span>Cancel anytime</span>
              </span>
            </motion.p>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Home;
