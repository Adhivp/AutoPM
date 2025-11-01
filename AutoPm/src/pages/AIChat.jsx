import { useState, useEffect, useRef } from 'react';
import api from '../utils/api';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const AIChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState([]);
  const [selectedProjects, setSelectedProjects] = useState([]);
  const [selectedContentTypes, setSelectedContentTypes] = useState(['pr', 'issue', 'jira_task', 'comment']);
  const [suggestions, setSuggestions] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  const [stats, setStats] = useState(null);
  const messagesEndRef = useRef(null);

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  const contentTypeOptions = [
    { value: 'pr', label: 'Pull Requests', icon: '🔀', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' },
    { value: 'issue', label: 'GitHub Issues', icon: '🐛', color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' },
    { value: 'jira_task', label: 'Jira Tasks', icon: '📋', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' },
    { value: 'comment', label: 'Comments', icon: '💬', color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' }
  ];

  useEffect(() => {
    fetchProjects();
    fetchSuggestions();
    fetchStats();
    scrollToBottom();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Update input with transcript
  useEffect(() => {
    if (transcript) {
      setInputMessage(transcript);
      console.log('Transcript updated:', transcript);
    }
  }, [transcript]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchProjects = async () => {
    try {
      const response = await api.get('/api/data/projects');
      setProjects(response.data || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const response = await api.get('/api/ai/chat/suggestions');
      setSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/ai/embeddings/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleSendMessage = async (messageText = null) => {
    const textToSend = messageText || inputMessage;
    if (!textToSend.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: textToSend,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await api.post('/api/ai/chat', {
        message: textToSend,
        project_ids: selectedProjects.length > 0 ? selectedProjects : null,
        content_types: selectedContentTypes.length > 0 ? selectedContentTypes : null,
        conversation_history: messages.slice(-4).map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      });

      const aiMessage = {
        role: 'assistant',
        content: response.data.response,
        context_items: response.data.context_items || [],
        context_count: response.data.context_count || 0,
        timestamp: response.data.timestamp
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        error: true,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startListening = async () => {
    try {
      // Check internet connectivity
      if (!navigator.onLine) {
        alert('No internet connection detected. Voice recognition requires an internet connection to work.');
        return;
      }

      resetTranscript();
      setInputMessage('');
      
      await SpeechRecognition.startListening({ 
        continuous: true,
        language: 'en-US'
      });
      
      console.log('🎤 Voice recognition started');
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      alert('Could not start voice input. Please ensure:\n1. Microphone permissions are granted\n2. You have an internet connection\n3. You\'re using a supported browser (Chrome, Edge, Safari)');
    }
  };

  const stopListening = () => {
    SpeechRecognition.stopListening();
    console.log('🎤 Voice recognition stopped');
  };

  const handleVoiceSend = () => {
    stopListening();
    if (inputMessage.trim()) {
      setTimeout(() => {
        handleSendMessage();
        resetTranscript();
      }, 100);
    }
  };

  const toggleContentType = (type) => {
    setSelectedContentTypes(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  const toggleProject = (projectId) => {
    setSelectedProjects(prev =>
      prev.includes(projectId)
        ? prev.filter(id => id !== projectId)
        : [...prev, projectId]
    );
  };

  const clearFilters = () => {
    setSelectedProjects([]);
    setSelectedContentTypes(['pr', 'issue', 'jira_task', 'comment']);
  };

  const renderContextItem = (item) => {
    const getContextColor = (type) => {
      switch (type) {
        case 'pr': return 'border-l-purple-500 bg-purple-50 dark:bg-purple-900/20';
        case 'issue': return 'border-l-red-500 bg-red-50 dark:bg-red-900/20';
        case 'jira_task': return 'border-l-blue-500 bg-blue-50 dark:bg-blue-900/20';
        case 'comment': return 'border-l-green-500 bg-green-50 dark:bg-green-900/20';
        default: return 'border-l-gray-500 bg-gray-50 dark:bg-gray-900/20';
      }
    };

    return (
      <div key={item.id} className={`border-l-4 ${getContextColor(item.content_type)} p-3 rounded-r-lg mb-2`}>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">
            {item.content_type.replace('_', ' ')}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            Relevance: {(item.similarity_score * 100).toFixed(1)}%
          </span>
        </div>
        <p className="text-xs text-gray-600 dark:text-gray-400 font-mono">ID: {item.id}</p>
        <p className="text-sm text-gray-800 dark:text-gray-200 mt-1 line-clamp-3">{item.document}</p>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                🤖 AI Assistant
              </h1>
              <p className="mt-2 text-lg text-gray-600 dark:text-gray-300">
                Ask questions about your projects, PRs, issues, and tasks
              </p>
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <span>🔍</span>
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </button>
          </div>

          {/* Stats Bar */}
          {stats && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Embeddings</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total_embeddings || 0}</p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-600 dark:text-gray-400">Pull Requests</p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{stats.by_type?.pr || 0}</p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-600 dark:text-gray-400">Issues</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">{stats.by_type?.issue || 0}</p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-600 dark:text-gray-400">Jira Tasks</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.by_type?.jira_task || 0}</p>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          {showFilters && (
            <div className="lg:col-span-1 space-y-4">
              {/* Content Type Filter */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Content Types</h3>
                  <span className="text-sm text-gray-500 dark:text-gray-400">{selectedContentTypes.length} selected</span>
                </div>
                <div className="space-y-2">
                  {contentTypeOptions.map(option => (
                    <button
                      key={option.value}
                      onClick={() => toggleContentType(option.value)}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                        selectedContentTypes.includes(option.value)
                          ? option.color + ' ring-2 ring-offset-2 ring-blue-500'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      <span className="text-xl">{option.icon}</span>
                      <span className="text-sm font-medium">{option.label}</span>
                      {selectedContentTypes.includes(option.value) && <span className="ml-auto">✓</span>}
                    </button>
                  ))}
                </div>
              </div>

              {/* Project Filter */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Projects</h3>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {selectedProjects.length > 0 ? `${selectedProjects.length} selected` : 'All'}
                  </span>
                </div>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {projects.length > 0 ? (
                    projects.map(project => (
                      <button
                        key={project.project_id}
                        onClick={() => toggleProject(project.project_id)}
                        className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                          selectedProjects.includes(project.project_id)
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100 ring-2 ring-blue-500'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }`}
                      >
                        <p className="text-sm font-medium truncate">{project.project_name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{project.project_id}</p>
                      </button>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">No projects found</p>
                  )}
                </div>
              </div>

              {/* Clear Filters */}
              <button
                onClick={clearFilters}
                className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Clear All Filters
              </button>
            </div>
          )}

          {/* Chat Area */}
          <div className={`${showFilters ? 'lg:col-span-3' : 'lg:col-span-4'}`}>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 flex flex-col" style={{ height: '70vh' }}>
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center">
                    <div className="text-6xl mb-4">🤖</div>
                    <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                      Welcome to AI Assistant!
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300 mb-6">
                      Ask me anything about your projects, PRs, issues, or tasks
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
                      {suggestions.slice(0, 4).map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => handleSendMessage(suggestion)}
                          className="px-4 py-3 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors text-sm text-left"
                        >
                          💡 {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <>
                    {messages.map((message, index) => (
                      <div
                        key={index}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`max-w-3xl ${message.role === 'user' ? 'w-auto' : 'w-full'}`}>
                          <div className={`rounded-lg p-4 ${
                            message.role === 'user'
                              ? 'bg-blue-600 text-white'
                              : message.error
                              ? 'bg-red-100 dark:bg-red-900/20 text-red-900 dark:text-red-200'
                              : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                          }`}>
                            <div className="flex items-start gap-3">
                              <span className="text-2xl">
                                {message.role === 'user' ? '👤' : '🤖'}
                              </span>
                              <div className="flex-1">
                                <p className="whitespace-pre-wrap">{message.content}</p>
                                <p className="text-xs mt-2 opacity-70">
                                  {new Date(message.timestamp).toLocaleTimeString()}
                                </p>
                              </div>
                            </div>
                          </div>

                          {/* Context Items */}
                          {message.context_items && message.context_items.length > 0 && (
                            <div className="mt-3 pl-11">
                              <details className="group">
                                <summary className="cursor-pointer text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 flex items-center gap-2">
                                  <span className="transform group-open:rotate-90 transition-transform">▶</span>
                                  View {message.context_count} context items used
                                </summary>
                                <div className="mt-2 space-y-2">
                                  {message.context_items.map(renderContextItem)}
                                </div>
                              </details>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}

                    {loading && (
                      <div className="flex justify-start">
                        <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
                          <div className="flex items-center gap-3">
                            <span className="text-2xl">🤖</span>
                            <div className="flex gap-1">
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </div>

              {/* Input Area */}
              <div className="border-t border-gray-200 dark:border-gray-700 p-4">
                {!browserSupportsSpeechRecognition ? (
                  <div className="mb-3 p-2 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded text-sm">
                    ⚠️ Voice input is not supported in your browser. Try Chrome, Edge, or Safari.
                  </div>
                ) : (
                  <div className="mb-2 p-2 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-xs">
                    💡 Voice recognition requires an active internet connection and microphone permissions.
                  </div>
                )}
                {listening && (
                  <div className="mb-2 p-2 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-sm font-medium">
                    🎤 Listening: "{transcript || 'Start speaking...'}"
                  </div>
                )}
                <div className="flex gap-3">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={listening ? "Listening... speak now" : "Ask me anything about your projects or click the microphone to speak..."}
                    className={`flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none ${
                      listening 
                        ? 'border-red-500 dark:border-red-500 ring-2 ring-red-300' 
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                    rows="2"
                    disabled={loading}
                  />
                  <div className="flex flex-col gap-2">
                    {browserSupportsSpeechRecognition && (
                      <button
                        onClick={listening ? stopListening : startListening}
                        disabled={loading}
                        className={`px-4 py-2 rounded-lg transition-all font-medium ${
                          listening
                            ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse'
                            : 'bg-green-600 hover:bg-green-700 text-white'
                        } disabled:bg-gray-400 disabled:cursor-not-allowed`}
                        title={listening ? "Stop recording" : "Start voice input"}
                      >
                        {listening ? '🎤 Stop' : '🎤 Voice'}
                      </button>
                    )}
                    {listening && (
                      <button
                        onClick={handleVoiceSend}
                        disabled={!inputMessage.trim() || loading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
                        title="Send voice message"
                      >
                        📤 Send
                      </button>
                    )}
                    {!listening && (
                      <button
                        onClick={() => handleSendMessage()}
                        disabled={!inputMessage.trim() || loading}
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
                      >
                        {loading ? '⏳' : '📤'} Send
                      </button>
                    )}
                  </div>
                </div>
                <div className="mt-2 flex flex-wrap gap-2 items-center">
                  {listening && (
                    <span className="text-xs px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded animate-pulse flex items-center gap-1">
                      <span className="inline-block w-2 h-2 bg-red-600 rounded-full"></span>
                      Recording...
                    </span>
                  )}
                  {selectedContentTypes.length > 0 && (
                    <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                      Searching in: {selectedContentTypes.join(', ')}
                    </span>
                  )}
                  {selectedProjects.length > 0 && (
                    <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded">
                      {selectedProjects.length} project(s) selected
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIChat;
