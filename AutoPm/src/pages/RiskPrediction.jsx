import { useState, useEffect } from 'react';
import { 
  Brain, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  TrendingUp,
  Info,
  ChevronDown,
  ChevronUp,
  Calendar,
  Users,
  GitBranch,
  Clock,
  Target,
  Shield,
  Database,
  Cpu,
  BarChart3,
  Zap,
  MessageSquare,
  AlertCircle,
  Activity,
  Loader2
} from 'lucide-react';
import api from '../utils/api';

export default function RiskPrediction() {
  const [modelStatus, setModelStatus] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [error, setError] = useState(null);
  const [aiSummary, setAiSummary] = useState(null);
  const [generatingAI, setGeneratingAI] = useState(false);
  
  const [expandedSections, setExpandedSections] = useState({
    modelInfo: false,
    trainingData: false,
    features: false,
    dimensions: false,
    howItWorks: false
  });

  useEffect(() => {
    fetchModelStatus();
    fetchPredictions();
  }, []);

  const fetchModelStatus = async () => {
    try {
      const response = await api.get('/api/risk/model/status');
      setModelStatus(response.data);
    } catch {
      setError('Failed to fetch model status');
    }
  };

  const fetchPredictions = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/risk/predict/all');
      setPredictions(response.data.predictions || []);
    } catch (err) {
      setError('Failed to fetch predictions');
    } finally {
      setLoading(false);
    }
  };

  const handleTrainModel = async () => {
    setTraining(true);
    setTrainingProgress(0);
    setError(null);

    const progressInterval = setInterval(() => {
      setTrainingProgress(prev => {
        if (prev >= 95) {
          clearInterval(progressInterval);
          return 95;
        }
        return prev + 5;
      });
    }, 1000);

    try {
      await new Promise(resolve => setTimeout(resolve, 20000));
      
      const response = await api.post('/api/risk/model/train');
      
      if (response.data.status === 'success') {
        setTrainingProgress(100);
        setTimeout(() => {
          setTraining(false);
          setTrainingProgress(0);
          fetchModelStatus();
          fetchPredictions();
        }, 1000);
      } else {
        throw new Error(response.data.message);
      }
    } catch (err) {
      setError(`Training failed: ${err.message}`);
      setTraining(false);
      setTrainingProgress(0);
    } finally {
      clearInterval(progressInterval);
    }
  };

  const handleGenerateAISummary = async (projectId) => {
    setGeneratingAI(true);
    try {
      const response = await api.post('/api/risk/summary/generate', { project_id: projectId });
      setAiSummary(response.data.summary);
    } catch (err) {
      setError('Failed to generate AI summary');
    } finally {
      setGeneratingAI(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getRiskColor = (category) => {
    switch (category) {
      case 'LOW': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      case 'MEDIUM': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
      case 'HIGH': return 'text-orange-400 bg-orange-500/10 border-orange-500/30';
      case 'CRITICAL': return 'text-red-400 bg-red-500/10 border-red-500/30';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/30';
    }
  };

  const getRiskIcon = (category) => {
    switch (category) {
      case 'LOW': return <CheckCircle className="w-6 h-6 text-emerald-400" />;
      case 'MEDIUM': return <AlertCircle className="w-6 h-6 text-yellow-400" />;
      case 'HIGH': return <AlertTriangle className="w-6 h-6 text-orange-400" />;
      case 'CRITICAL': return <XCircle className="w-6 h-6 text-red-400" />;
      default: return <Info className="w-6 h-6 text-gray-400" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-gray-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white flex items-center gap-3">
              <Brain className="w-10 h-10 text-purple-400" />
              AI Risk Prediction Engine
            </h1>
            <p className="text-gray-400 mt-2">ML-powered project risk assessment and forecasting</p>
          </div>
          <div className="flex items-center gap-4">
            {modelStatus?.status === 'ready' && (
              <div className="flex items-center gap-2 px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 rounded-lg">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                <span className="text-emerald-400 text-sm font-medium">Model Ready</span>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-red-400 font-semibold">Error</h3>
              <p className="text-red-300 text-sm mt-1">{error}</p>
            </div>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
              <XCircle className="w-5 h-5" />
            </button>
          </div>
        )}

        {training && (
          <div className="bg-gradient-to-r from-purple-500/10 via-blue-500/10 to-purple-500/10 border border-purple-500/30 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
              <div>
                <h3 className="text-xl font-semibold text-white">Training Model...</h3>
                <p className="text-gray-400 text-sm">Processing historical data and building predictive model</p>
              </div>
            </div>
            <div className="relative w-full h-3 bg-gray-700/50 rounded-full overflow-hidden">
              <div 
                className="absolute top-0 left-0 h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-300 ease-out"
                style={{ width: `${trainingProgress}%` }}
              >
                <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
              </div>
            </div>
            <p className="text-center text-purple-300 text-sm mt-2 font-medium">{trainingProgress}% Complete</p>
          </div>
        )}

        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
                <Cpu className="w-6 h-6 text-blue-400" />
                Model Status
              </h2>
              {modelStatus?.status === 'ready' && modelStatus?.metadata && (
                <div className="mt-3 space-y-1 text-sm">
                  <p className="text-gray-300">
                    <span className="text-gray-400">Trained:</span> {new Date(modelStatus.metadata.trained_at).toLocaleString()}
                  </p>
                  <p className="text-gray-300">
                    <span className="text-gray-400">Accuracy:</span> {(modelStatus.metadata.accuracy * 100).toFixed(1)}%
                  </p>
                  <p className="text-gray-300">
                    <span className="text-gray-400">Samples:</span> {modelStatus.metadata.n_samples} projects
                  </p>
                </div>
              )}
              {modelStatus?.status === 'not_trained' && (
                <p className="text-yellow-400 mt-2">Model needs to be trained before predictions</p>
              )}
            </div>
            <button
              onClick={handleTrainModel}
              disabled={training}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-600 text-white rounded-lg font-semibold transition-all duration-200 flex items-center gap-2 shadow-lg disabled:cursor-not-allowed"
            >
              {training ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Training...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  {modelStatus?.status === 'ready' ? 'Retrain Model' : 'Train Model'}
                </>
              )}
            </button>
          </div>
        </div>

        {loading && !training && (
          <div className="text-center py-12">
            <Loader2 className="w-12 h-12 text-purple-400 animate-spin mx-auto" />
            <p className="text-gray-400 mt-4">Loading predictions...</p>
          </div>
        )}

        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('howItWorks')}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-700/30 transition-colors"
          >
            <div className="flex items-center gap-3">
              <Info className="w-5 h-5 text-blue-400" />
              <h2 className="text-xl font-semibold text-white">How It Works</h2>
            </div>
            {expandedSections.howItWorks ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          
          {expandedSections.howItWorks && (
            <div className="px-6 pb-6 space-y-4 text-gray-300">
              <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  <Target className="w-5 h-5 text-purple-400" />
                  Machine Learning Approach
                </h3>
                <p className="leading-relaxed">
                  Our risk prediction engine uses a <strong className="text-purple-400">Random Forest Classifier</strong>, 
                  an ensemble learning method that combines multiple decision trees to make accurate predictions. 
                  The model analyzes 18 different features across 5 key dimensions of project health.
                </p>
              </div>

              <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  <Database className="w-5 h-5 text-blue-400" />
                  Training Process
                </h3>
                <p className="leading-relaxed mb-3">
                  The model is trained on historical project data that includes both successful projects and those 
                  that faced challenges. The training process involves:
                </p>
                <ul className="space-y-2 ml-4">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-400 mt-1">•</span>
                    <span><strong className="text-white">Data Collection:</strong> Gathering metrics from completed projects</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-400 mt-1">•</span>
                    <span><strong className="text-white">Feature Engineering:</strong> Extracting 18 meaningful features</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-400 mt-1">•</span>
                    <span><strong className="text-white">Model Training:</strong> Using Random Forest with 100 trees</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-400 mt-1">•</span>
                    <span><strong className="text-white">Validation:</strong> Testing accuracy on unseen data</span>
                  </li>
                </ul>
              </div>

              <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-emerald-400" />
                  Risk Categories
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                      <span className="font-semibold text-emerald-400">LOW</span>
                    </div>
                    <p className="text-sm text-gray-400">Project on track, minimal issues</p>
                  </div>
                  <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <AlertCircle className="w-4 h-4 text-yellow-400" />
                      <span className="font-semibold text-yellow-400">MEDIUM</span>
                    </div>
                    <p className="text-sm text-gray-400">Some concerns, needs monitoring</p>
                  </div>
                  <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <AlertTriangle className="w-4 h-4 text-orange-400" />
                      <span className="font-semibold text-orange-400">HIGH</span>
                    </div>
                    <p className="text-sm text-gray-400">Significant risks, action needed</p>
                  </div>
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <XCircle className="w-4 h-4 text-red-400" />
                      <span className="font-semibold text-red-400">CRITICAL</span>
                    </div>
                    <p className="text-sm text-gray-400">Urgent intervention required</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('trainingData')}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-700/30 transition-colors"
          >
            <div className="flex items-center gap-3">
              <Database className="w-5 h-5 text-emerald-400" />
              <h2 className="text-xl font-semibold text-white">Training Data Sources</h2>
            </div>
            {expandedSections.trainingData ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          
          {expandedSections.trainingData && (
            <div className="px-6 pb-6 space-y-4 text-gray-300">
              <p className="text-gray-400 leading-relaxed">
                The ML model is trained using comprehensive data from 7 different database tables, 
                each providing unique insights into project health and risk factors:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-5 h-5 text-blue-400" />
                    <h3 className="font-semibold text-white">Project Metadata</h3>
                  </div>
                  <p className="text-sm text-gray-400">
                    Basic project information including start date, deadline, current status, 
                    and planned vs actual completion dates
                  </p>
                </div>

                <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Target className="w-5 h-5 text-purple-400" />
                    <h3 className="font-semibold text-white">JIRA Tasks</h3>
                  </div>
                  <p className="text-sm text-gray-400">
                    Task status, priorities, story points, completion rates, and time tracking 
                    data from JIRA
                  </p>
                </div>

                <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                  <div className="flex items-center gap-2 mb-2">
                    <GitBranch className="w-5 h-5 text-orange-400" />
                    <h3 className="font-semibold text-white">GitHub Activity</h3>
                  </div>
                  <p className="text-sm text-gray-400">
                    Commit frequency, PR merge rates, code review cycles, and repository activity 
                    patterns
                  </p>
                </div>

                <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="w-5 h-5 text-emerald-400" />
                    <h3 className="font-semibold text-white">Resource Allocation</h3>
                  </div>
                  <p className="text-sm text-gray-400">
                    Team member assignments, allocation percentages, role distributions, and 
                    resource availability
                  </p>
                </div>

                <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="w-5 h-5 text-yellow-400" />
                    <h3 className="font-semibold text-white">Task Dependencies</h3>
                  </div>
                  <p className="text-sm text-gray-400">
                    Dependency relationships, blocking issues, dependency chain lengths, and 
                    critical path analysis
                  </p>
                </div>

                <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30">
                  <div className="flex items-center gap-2 mb-2">
                    <MessageSquare className="w-5 h-5 text-pink-400" />
                    <h3 className="font-semibold text-white">Team Communication</h3>
                  </div>
                  <p className="text-sm text-gray-400">
                    Sentiment analysis of team communications, message frequency, and collaboration 
                    patterns
                  </p>
                </div>

                <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/30 md:col-span-2">
                  <div className="flex items-center gap-2 mb-2">
                    <Shield className="w-5 h-5 text-red-400" />
                    <h3 className="font-semibold text-white">Historical Project Performance</h3>
                  </div>
                  <p className="text-sm text-gray-400">
                    Past project outcomes including actual delay days, defect densities, integration 
                    issues, root cause analyses, and final risk categories. This is the ground truth 
                    data used to train the model.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('features')}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-700/30 transition-colors"
          >
            <div className="flex items-center gap-3">
              <Cpu className="w-5 h-5 text-cyan-400" />
              <h2 className="text-xl font-semibold text-white">18 Features Extracted for ML</h2>
            </div>
            {expandedSections.features ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          
          {expandedSections.features && (
            <div className="px-6 pb-6 space-y-6 text-gray-300">
              <p className="text-gray-400 leading-relaxed">
                Each project is analyzed across 18 numerical features grouped into 5 key dimensions. 
                These features are engineered from raw data to provide meaningful insights:
              </p>

              <div className="space-y-4">
                <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg p-5 border border-blue-500/30">
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <Clock className="w-5 h-5 text-blue-400" />
                    Schedule Dimension (4 features)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-blue-300 mb-1">Days Until Deadline</p>
                      <p className="text-xs text-gray-400">Time remaining to project completion date</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-blue-300 mb-1">Progress Percentage</p>
                      <p className="text-xs text-gray-400">Overall project completion percentage</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-blue-300 mb-1">Schedule Pressure Index</p>
                      <p className="text-xs text-gray-400">Ratio of remaining work to remaining time</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-blue-300 mb-1">Task Completion Rate</p>
                      <p className="text-xs text-gray-400">Percentage of completed vs total tasks</p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-red-500/10 to-orange-500/10 rounded-lg p-5 border border-red-500/30">
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                    Quality Dimension (4 features)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-red-300 mb-1">Bug Count</p>
                      <p className="text-xs text-gray-400">Total number of open bugs</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-red-300 mb-1">Bug Rate</p>
                      <p className="text-xs text-gray-400">Bugs per completed task</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-red-300 mb-1">PR Merge Success Rate</p>
                      <p className="text-xs text-gray-400">Percentage of PRs merged without issues</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-red-300 mb-1">Code Review Cycle Time</p>
                      <p className="text-xs text-gray-400">Average time for code review completion</p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-emerald-500/10 to-teal-500/10 rounded-lg p-5 border border-emerald-500/30">
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <Users className="w-5 h-5 text-emerald-400" />
                    Resource Dimension (4 features)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-emerald-300 mb-1">Team Size</p>
                      <p className="text-xs text-gray-400">Number of team members allocated</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-emerald-300 mb-1">Average Allocation</p>
                      <p className="text-xs text-gray-400">Mean allocation percentage per member</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-emerald-300 mb-1">Allocation Variance</p>
                      <p className="text-xs text-gray-400">Spread of allocation across team</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-emerald-300 mb-1">Commit Activity</p>
                      <p className="text-xs text-gray-400">Average daily commit frequency</p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-yellow-500/10 to-amber-500/10 rounded-lg p-5 border border-yellow-500/30">
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-yellow-400" />
                    Dependency Dimension (3 features)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-yellow-300 mb-1">Dependency Count</p>
                      <p className="text-xs text-gray-400">Total number of task dependencies</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-yellow-300 mb-1">Blocked Tasks</p>
                      <p className="text-xs text-gray-400">Number of tasks blocked by dependencies</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-yellow-300 mb-1">Dependency Chain Length</p>
                      <p className="text-xs text-gray-400">Maximum depth of dependency chains</p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-pink-500/10 to-purple-500/10 rounded-lg p-5 border border-pink-500/30">
                  <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-pink-400" />
                    Team & Sentiment Dimension (3 features)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-pink-300 mb-1">Communication Frequency</p>
                      <p className="text-xs text-gray-400">Average messages per team member per day</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-pink-300 mb-1">Average Sentiment Score</p>
                      <p className="text-xs text-gray-400">Mean sentiment of team communications (-1 to 1)</p>
                    </div>
                    <div className="bg-gray-900/50 rounded p-3">
                      <p className="font-medium text-pink-300 mb-1">Sentiment Volatility</p>
                      <p className="text-xs text-gray-400">Standard deviation of sentiment scores</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 rounded-lg p-5 border border-cyan-500/30">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-cyan-400" />
                  Feature Engineering Process
                </h3>
                <p className="text-gray-300 mb-3">
                  Raw data from the 7 database tables is transformed into these 18 numerical features through:
                </p>
                <ul className="space-y-2 ml-4">
                  <li className="flex items-start gap-2">
                    <span className="text-cyan-400 mt-1">•</span>
                    <span><strong className="text-white">Aggregation:</strong> Counting, averaging, and summing raw values</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-cyan-400 mt-1">•</span>
                    <span><strong className="text-white">Ratio Calculation:</strong> Computing meaningful ratios and percentages</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-cyan-400 mt-1">•</span>
                    <span><strong className="text-white">Statistical Analysis:</strong> Calculating variance and standard deviations</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-cyan-400 mt-1">•</span>
                    <span><strong className="text-white">Normalization:</strong> Scaling features to comparable ranges</span>
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {!loading && !training && predictions.length > 0 && (
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-purple-400" />
              Project Risk Predictions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {predictions.map((pred) => (
                <div
                  key={pred.project_id}
                  className={`rounded-lg p-5 border transition-all duration-200 hover:shadow-lg cursor-pointer ${getRiskColor(pred.risk_category)}`}
                  onClick={() => setSelectedProject(pred)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold text-white text-lg mb-1">{pred.project_name}</h3>
                      <p className="text-xs text-gray-400">ID: {pred.project_id}</p>
                    </div>
                    {getRiskIcon(pred.risk_category)}
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Risk Level</span>
                      <span className="font-bold text-lg">{pred.risk_category}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Confidence</span>
                      <span className="font-semibold">{(pred.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400">Risk Score</span>
                      <span className="font-semibold">{pred.risk_score.toFixed(2)}</span>
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleGenerateAISummary(pred.project_id);
                    }}
                    disabled={generatingAI}
                    className="mt-4 w-full px-4 py-2 bg-white/10 hover:bg-white/20 rounded text-sm font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    {generatingAI ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4" />
                        AI Summary
                      </>
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {aiSummary && (
          <div className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 backdrop-blur-sm border border-purple-500/30 rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
                <Brain className="w-6 h-6 text-purple-400" />
                AI Risk Analysis
              </h2>
              <button onClick={() => setAiSummary(null)} className="text-gray-400 hover:text-white">
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="prose prose-invert max-w-none">
              <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{aiSummary}</p>
            </div>
          </div>
        )}

        {!loading && !training && predictions.length === 0 && modelStatus?.status === 'ready' && (
          <div className="text-center py-12 bg-gray-800/30 rounded-lg border border-gray-700/50">
            <AlertCircle className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No Predictions Available</h3>
            <p className="text-gray-400">No active projects found to generate predictions</p>
          </div>
        )}
      </div>
    </div>
  );
}
