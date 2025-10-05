import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Cpu, Activity, Settings, AlertTriangle, RotateCcw, Send, Zap, Shield, Database, Clock, TrendingUp, Download, Terminal, BarChart3, FileText, Menu, X } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const API_BASE = 'http://localhost:5000';

const THEMES = {
  corporate: { 
    bg: '#fafafa',
    surface: '#ffffff', 
    accent: '#1a1a1a',
    accentHover: '#333333',
    text: '#1a1a1a',
    textLight: '#666666',
    border: '#e5e5e5',
    success: '#16a34a',
    error: '#dc2626',
    warning: '#ea580c'
  },
  executive: {
    bg: '#f5f5f4',
    surface: '#ffffff',
    accent: '#78716c',
    accentHover: '#57534e',
    text: '#1c1917',
    textLight: '#78716c',
    border: '#e7e5e4',
    success: '#15803d',
    error: '#b91c1c',
    warning: '#c2410c'
  },
  minimal: {
    bg: '#ffffff',
    surface: '#f9fafb',
    accent: '#374151',
    accentHover: '#1f2937',
    text: '#111827',
    textLight: '#6b7280',
    border: '#e5e7eb',
    success: '#059669',
    error: '#dc2626',
    warning: '#d97706'
  }
};

const api = {
  async chat(message, history = []) {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history })
    });
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  },
  async getSkills() {
    const res = await fetch(`${API_BASE}/api/skills`);
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  },
  async reloadSkills() {
    const res = await fetch(`${API_BASE}/api/skills/reload`, { method: 'POST' });
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  },
  async getMetrics() {
    const res = await fetch(`${API_BASE}/api/metrics`);
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.text();
  },
  async getHealth() {
    const res = await fetch(`${API_BASE}/api/health`);
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  },
  async getSystemStatus() {
    const res = await fetch(`${API_BASE}/api/system/status`);
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  },
  async resetCircuitBreaker() {
    const res = await fetch(`${API_BASE}/api/system/circuit-breaker/reset`, { method: 'POST' });
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return res.json();
  }
};

const parsePrometheusMetrics = (text) => {
  const lines = text.split('\n');
  const metrics = {};
  lines.forEach(line => {
    if (line.startsWith('#') || !line.trim()) return;
    const match = line.match(/^([a-zA-Z_:][a-zA-Z0-9_:]*(?:{[^}]*})?)\s+([0-9.e+-]+)/);
    if (match) {
      metrics[match[1]] = parseFloat(match[2]);
    }
  });
  return metrics;
};

export default function JarvisAIHub() {
  const [activeView, setActiveView] = useState('chat');
  const [theme, setTheme] = useState('corporate');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [skills, setSkills] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [errors, setErrors] = useState([]);
  const [time, setTime] = useState(new Date());
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const messagesEndRef = useRef(null);

  const colors = THEMES[theme];

  useEffect(() => {
    const saved = localStorage.getItem('jarvis_data');
    if (saved) {
      const data = JSON.parse(saved);
      setMessages(data.messages || []);
      setMetricsHistory(data.metricsHistory || []);
      setTheme(data.theme || 'corporate');
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('jarvis_data', JSON.stringify({ messages, metricsHistory, theme }));
  }, [messages, metricsHistory, theme]);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        await api.getHealth();
        setConnectionStatus('connected');
      } catch {
        setConnectionStatus('disconnected');
      }
    };
    checkConnection();
    const interval = setInterval(checkConnection, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeView === 'skills') loadSkills();
    if (activeView === 'metrics') loadMetrics();
    if (activeView === 'status') loadSystemStatus();
  }, [activeView]);

  const loadSkills = async () => {
    try {
      const data = await api.getSkills();
      setSkills(data.skills || []);
    } catch (err) {
      addError('Failed to load skills', err);
    }
  };

  const loadMetrics = async () => {
    try {
      const text = await api.getMetrics();
      const parsed = parsePrometheusMetrics(text);
      setMetrics(parsed);
      
      const newHistory = [...metricsHistory, {
        time: Date.now(),
        requests: parsed['flask_http_request_total'] || 0,
        memory: (parsed['process_resident_memory_bytes'] || 0) / 1024 / 1024
      }].slice(-30);
      setMetricsHistory(newHistory);
    } catch (err) {
      addError('Failed to load metrics', err);
    }
  };

  const loadSystemStatus = async () => {
    try {
      const status = await api.getSystemStatus();
      setSystemStatus(status);
    } catch (err) {
      addError('Failed to load system status', err);
    }
  };

  const addError = (message, error) => {
    const newError = {
      id: Date.now(),
      message,
      details: error.toString(),
      timestamp: new Date().toISOString()
    };
    setErrors(prev => [newError, ...prev].slice(0, 50));
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMsg = { role: 'user', content: inputMessage, time: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate typing delay
    setTimeout(() => {
      setIsTyping(false);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "I've turned on the living room lights for you. Is there anything else you need?",
        time: Date.now()
      }]);
    }, 1500);
  };

  const MetricCard = ({ icon: Icon, label, value, sublabel }) => (
    <div style={{ background: colors.surface, border: `1px solid ${colors.border}` }} className="p-6 rounded">
      <div className="flex items-start justify-between mb-3">
        <Icon size={20} style={{ color: colors.textLight }} />
        <span style={{ color: colors.textLight }} className="text-xs font-medium uppercase tracking-wide">{label}</span>
      </div>
      <div style={{ color: colors.text }} className="text-3xl font-semibold mb-1">{value}</div>
      {sublabel && <div style={{ color: colors.textLight }} className="text-sm">{sublabel}</div>}
    </div>
  );

  return (
    <div style={{ background: colors.bg, color: colors.text }} className="h-screen flex flex-col font-sans">
      {/* Header */}
      <div style={{ background: colors.surface, borderBottom: `1px solid ${colors.border}` }} className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-gray-100 rounded lg:hidden"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          
          <div className="flex items-center gap-3">
            <div style={{ background: colors.accent }} className="w-8 h-8 rounded flex items-center justify-center">
              <Terminal size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-base font-semibold tracking-tight">JARVIS AI Hub</h1>
              <div className="flex items-center gap-2 text-xs" style={{ color: colors.textLight }}>
                <div className={`w-1.5 h-1.5 rounded-full ${connectionStatus === 'connected' ? 'bg-green-600' : 'bg-red-600'}`} />
                <span className="uppercase tracking-wide">{connectionStatus}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div style={{ color: colors.textLight }} className="text-sm hidden md:block font-medium">
            {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        {sidebarOpen && (
          <div style={{ background: colors.surface, borderRight: `1px solid ${colors.border}` }} className="w-64 flex-shrink-0 p-4">
            <nav className="space-y-1">
              {[
                { id: 'chat', icon: MessageSquare, label: 'Chat', count: messages.length },
                { id: 'skills', icon: Zap, label: 'Skills', count: skills.length },
                { id: 'metrics', icon: BarChart3, label: 'Metrics' },
                { id: 'status', icon: Activity, label: 'System Status' },
                { id: 'logs', icon: FileText, label: 'Error Logs', count: errors.length },
                { id: 'settings', icon: Settings, label: 'Settings' }
              ].map(item => (
                <button
                  key={item.id}
                  onClick={() => setActiveView(item.id)}
                  style={{
                    background: activeView === item.id ? colors.accent : 'transparent',
                    color: activeView === item.id ? '#ffffff' : colors.textLight
                  }}
                  className="w-full flex items-center justify-between px-4 py-2.5 rounded text-sm font-medium transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <item.icon size={18} />
                    <span>{item.label}</span>
                  </div>
                  {item.count > 0 && (
                    <span style={{ background: activeView === item.id ? 'rgba(255,255,255,0.2)' : colors.border }} className="text-xs px-2 py-0.5 rounded font-semibold">
                      {item.count}
                    </span>
                  )}
                </button>
              ))}
            </nav>

            <div className="mt-6 pt-6" style={{ borderTop: `1px solid ${colors.border}` }}>
              <div className="mb-3 px-4">
                <label className="text-xs font-semibold uppercase tracking-wide" style={{ color: colors.textLight }}>
                  Theme
                </label>
              </div>
              <select 
                value={theme} 
                onChange={e => setTheme(e.target.value)}
                style={{ background: colors.bg, border: `1px solid ${colors.border}`, color: colors.text }}
                className="w-full px-3 py-2 rounded text-sm outline-none font-medium"
              >
                <option value="corporate">Corporate</option>
                <option value="executive">Executive</option>
                <option value="minimal">Minimal</option>
              </select>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="flex-1 overflow-auto">
          {/* Chat View */}
          {activeView === 'chat' && (
            <div className="h-full flex flex-col max-w-6xl mx-auto p-6">
              <div className="mb-6">
                <h2 className="text-2xl font-semibold mb-2">Chat Interface</h2>
                <p style={{ color: colors.textLight }} className="text-sm">Communicate with the AI orchestration system</p>
              </div>

              <div style={{ background: colors.surface, border: `1px solid ${colors.border}` }} className="flex-1 rounded overflow-y-auto p-6 mb-4 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center py-16" style={{ color: colors.textLight }}>
                    <MessageSquare size={48} className="mx-auto mb-4 opacity-40" />
                    <p className="font-medium">No messages yet</p>
                    <p className="text-sm mt-1">Start a conversation with the AI system</p>
                  </div>
                )}

                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div
                      style={{
                        background: msg.role === 'user' ? colors.accent : colors.bg,
                        color: msg.role === 'user' ? '#ffffff' : colors.text,
                        border: msg.isError ? `1px solid ${colors.error}` : msg.role === 'user' ? 'none' : `1px solid ${colors.border}`,
                        maxWidth: '65%'
                      }}
                      className="px-5 py-3 rounded"
                    >
                      <div className="text-xs mb-2 font-semibold uppercase tracking-wide opacity-70">
                        {msg.role === 'user' ? 'You' : 'System'}
                      </div>
                      <div className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</div>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex justify-start">
                    <div style={{ background: colors.bg, border: `1px solid ${colors.border}` }} className="px-5 py-3 rounded">
                      <div className="flex gap-1.5">
                        <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: colors.textLight, animationDelay: '0ms' }} />
                        <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: colors.textLight, animationDelay: '150ms' }} />
                        <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: colors.textLight, animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="flex gap-3">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={e => setInputMessage(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && sendMessage()}
                  placeholder="Type your message..."
                  style={{ background: colors.surface, border: `1px solid ${colors.border}`, color: colors.text }}
                  className="flex-1 px-4 py-3 rounded outline-none text-sm"
                />
                <button
                  onClick={sendMessage}
                  disabled={!inputMessage.trim() || isTyping}
                  style={{ background: colors.accent }}
                  className="px-8 py-3 rounded text-white font-medium hover:opacity-90 disabled:opacity-40 transition-opacity"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          )}

          {/* Skills View */}
          {activeView === 'skills' && (
            <div className="p-6 max-w-7xl mx-auto">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-semibold mb-2">Skills Registry</h2>
                  <p style={{ color: colors.textLight }} className="text-sm">Available AI capabilities and functions</p>
                </div>
                <button 
                  onClick={loadSkills}
                  style={{ background: colors.accent }}
                  className="px-5 py-2.5 rounded text-sm text-white font-medium flex items-center gap-2 hover:opacity-90"
                >
                  <RotateCcw size={16} />
                  Reload
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {skills.map((skill, idx) => (
                  <div key={idx} style={{ background: colors.surface, border: `1px solid ${colors.border}` }} className="p-5 rounded">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-base mb-1">{skill.name}</h3>
                        <p className="text-xs font-medium" style={{ color: colors.textLight }}>Version {skill.version || '1.0.0'}</p>
                      </div>
                      {skill.circuit_breaker_open && (
                        <AlertTriangle size={18} style={{ color: colors.error }} />
                      )}
                    </div>
                    <p className="text-sm mb-4" style={{ color: colors.textLight }}>
                      {skill.description || 'No description available'}
                    </p>
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${skill.status === 'active' ? 'bg-green-600' : 'bg-red-600'}`} />
                      <span className="text-xs font-medium uppercase tracking-wide" style={{ color: colors.textLight }}>
                        {skill.status || 'active'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {skills.length === 0 && (
                <div className="text-center py-16" style={{ color: colors.textLight }}>
                  <Zap size={48} className="mx-auto mb-4 opacity-40" />
                  <p className="font-medium">No skills registered</p>
                  <p className="text-sm mt-1">Click reload to fetch available skills</p>
                </div>
              )}
            </div>
          )}

          {/* Metrics View */}
          {activeView === 'metrics' && (
            <div className="p-6 max-w-7xl mx-auto">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-semibold mb-2">Performance Metrics</h2>
                  <p style={{ color: colors.textLight }} className="text-sm">Real-time system performance monitoring</p>
                </div>
                <button 
                  onClick={loadMetrics}
                  style={{ background: colors.accent }}
                  className="px-5 py-2.5 rounded text-sm text-white font-medium flex items-center gap-2 hover:opacity-90"
                >
                  <RotateCcw size={16} />
                  Refresh
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <MetricCard 
                  icon={Activity} 
                  label="Total Requests" 
                  value={metrics['flask_http_request_total'] || 0}
                />
                <MetricCard 
                  icon={MessageSquare} 
                  label="Chat Requests" 
                  value={metrics['jarvis_chat_requests_total'] || 0}
                />
                <MetricCard 
                  icon={TrendingUp} 
                  label="GPT Fallbacks" 
                  value={metrics['jarvis_gpt_fallback_total'] || 0}
                />
                <MetricCard 
                  icon={Cpu} 
                  label="Memory Usage" 
                  value={((metrics['process_resident_memory_bytes'] || 0) / 1024 / 1024).toFixed(1)}
                  sublabel="MB"
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div style={{ background: colors.surface, border: `1px solid ${colors.border}` }} className="p-6 rounded">
                  <h3 className="font-semibold mb-4 text-sm uppercase tracking-wide" style={{ color: colors.textLight }}>Request Volume</h3>
                  <ResponsiveContainer width="100%" height={240}>
                    <AreaChart data={metricsHistory}>
                      <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                      <XAxis dataKey="time" hide />
                      <YAxis stroke={colors.textLight} style={{ fontSize: '12px' }} />
                      <Tooltip 
                        contentStyle={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: '4px', fontSize: '12px' }}
                      />
                      <Area type="monotone" dataKey="requests" stroke={colors.accent} fill={colors.accent} fillOpacity={0.1} strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                <div style={{ background: colors.surface, border: `1px solid ${colors.border}` }} className="p-6 rounded">
                  <h3 className="font-semibold mb-4 text-sm uppercase tracking-wide" style={{ color: colors.textLight }}>Memory Consumption</h3>
                  <ResponsiveContainer width="100%" height={240}>
                    <LineChart data={metricsHistory}>
                      <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                      <XAxis dataKey="time" hide />
                      <YAxis stroke={colors.textLight} style={{ fontSize: '12px' }} />
                      <Tooltip 
                        contentStyle={{ background: colors.surface, border: `1px solid ${colors.border}`, borderRadius: '4px', fontSize: '12px' }}
                      />
                      <Line type="monotone" dataKey="memory" stroke={colors.success} strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {/* Status View */}
          {activeView === 'status' && (
            <div className="p-6 max-w-6xl mx-auto">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-semibold mb-2">System Status</h2>
                  <p style={{ color: colors.textLight }} className="text-sm">Health monitoring and uptime tracking</p>
                </div>
                <div className="flex gap-3">
                  <button 
                    onClick={() => api.resetCircuitBreaker()}
                    style={{ border: `1px solid ${colors.border}`, color: colors.text }}
                    className="px-4 py-2 rounded text-sm font-medium hover:bg-gray-50"
                  >
                    Reset Circuit Breaker
                  </button>
                  <button 
                    onClick={loadSystemStatus}
                    style={{ background: colors.accent }}
                    className="px-5 py-2 rounded text-sm text-white font-medium hover:opacity-90"
                  >
                    <RotateCcw size={16} />
                  </button>
                </div>
              </div>

              {systemStatus ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div style={{ background: colors.surface, border: `1px solid ${colors.border}` }} className="p-6 rounded">
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-3 h-3 rounded-full ${systemStatus.status === 'healthy' ? 'bg-green-600' : 'bg-red-600'}`} />
                      <span style={{ color: colors.textLight }} className="text-xs font-semibold uppercase tracking-wide">System Health</span>
                    </div>
                    <div className="text-3xl font-semibold capitalize">{systemStatus.status || 'Unknown'}</div>
                  </div>

                  <div style={{ background: colors.surface, border: `1px solid ${colors.border}` }} className="p-6 rounded">
                    <div className="flex items-center gap-3 mb-4">
                      <Zap size={16} style={{ color: colors.textLight }} />
                      <span style={{ color: colors.textLight }} className="text-xs font-semibold uppercase tracking-wide">Active Skills</span>
                    </div>
                    <div className="text-3xl font-semibold">{systemStatus.skills_loaded || 0}</div>
                  </div>

                  <div style={{ background: colors.surface, border: `1px solid ${colors.border}` }} className="p-6 rounded">
                    <div className="flex items-center gap-3 mb-4">
                      <Clock size={16} style={{ color: colors.textLight }} />
                      <span style={{ color: colors.textLight }} className="text-xs font-semibold uppercase tracking-wide">Uptime</span>
                    </div>
                    <div className="text-3xl font-semibold">{systemStatus.uptime || 'N/A'}</div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-16" style={{ color: colors.textLight }}>
                  <Database size={48} className="mx-auto mb-4 opacity-40" />
                  <p className="font-medium">Loading system status...</p>
                </div>
              )}
            </div>
          )}

          {/* Logs View */}
          {activeView === 'logs' && (
            <div className="p-6 max-w-7xl mx-auto">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-semibold mb-2">Error Logs</h2>
                  <p style={{ color: colors.textLight }} className="text-sm">System errors and diagnostic information</p>
                </div>
                <div className="flex gap-3">
                  <button 
                    onClick={() => {
                      const data = JSON.stringify(errors, null, 2);
                      const blob = new Blob([data], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `error-logs-${Date.now()}.json`;
                      a.click();
                    }}
                    style={{ border: `1px solid ${colors.border}`, color: colors.text }}
                    className="px-4 py-2 rounded text-sm font-medium flex items-center gap-2 hover:bg-gray-50"
                  >
                    <Download size={16} />
                    Export
                  </button>
                  <button 
                    onClick={() => setErrors([])}
                    style={{ background: colors.accent }}
                    className="px-5 py-2 rounded text-sm text-white font-medium hover:opacity-90"
                  >
                    Clear All
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                {errors.map(err => (
                  <div key={err.id} style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderLeftWidth: '3px', borderLeftColor: colors.error }} className="p-5 rounded">
                    <div className="flex items-start justify-between mb-2">
                      <span className="font-semibold">{err.message}</span>
                      <span className="text-xs font-medium" style={{ color: colors.textLight }}>
                        {new Date(err.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <pre className="text-xs overflow-x-auto p-3 rounded mt-2" style={{ background: colors.bg, color: colors.textLight }}>{err.details}</pre>
                  </div>
                ))}

                {errors.length === 0 && (
                  <div className="text-center py-16" style={{ color: colors.textLight }}>
                    <FileText size={48} className="mx-auto mb-4 opacity-40" />
                    <p className="font-medium">No errors logged</p>
                    <p className="text-sm mt-1">System is operating normally</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Settings View */}
          {activeView === 'settings' && (
            <div className="p-6 max-w-4xl mx-auto">
              <div className="mb-6">
                <h2 className="text-2xl font-semibold mb-2">Settings</h2>
                <p style={{ color: colors.textLight }} className="text-sm">Configure application preferences</p>
              </div>

              <div style={{ background: colors.surface, border: `1px solid ${colors.border}` }} className="p-6 rounded mb-4">
                <h3 className="font-semibold mb-4 text-sm uppercase tracking-wide" style={{ color: colors.textLight }}>Appearance</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-3" style={{ borderBottom: `1px solid ${colors.border}` }}>
                    <div>
                      <div className="font-medium">Color Theme</div>
                      <div className="text-sm mt-1" style={{ color: colors.textLight }}>Choose your preferred interface theme</div>
                    </div>
                    <select 
                      value={theme} 
                      onChange={e => setTheme(e.target.value)}
                      style={{ background: colors.bg, border: `1px solid ${colors.border}`, color: colors.text }}
                      className="px-4 py-2 rounded outline-none text-sm font-medium"
                    >
                      <option value="corporate">Corporate</option>
                      <option value="executive">Executive</option>
                      <option value="minimal">Minimal</option>
                    </select>
                  </div>

                  <div className="flex items-center justify-between py-3" style={{ borderBottom: `1px solid ${colors.border}` }}>
                    <div>
                      <div className="font-medium">Sidebar Visibility</div>
                      <div className="text-sm mt-1" style={{ color: colors.textLight }}>Toggle navigation sidebar display</div>
                    </div>
                    <button
                      onClick={() => setSidebarOpen(!sidebarOpen)}
                      style={{ 
                        background: sidebarOpen ? colors.accent : colors.bg,
                        color: sidebarOpen ? '#ffffff' : colors.text,
                        border: `1px solid ${colors.border}`
                      }}
                      className="px-5 py-2 rounded text-sm font-medium"
                    >
                      {sidebarOpen ? 'Visible' : 'Hidden'}
                    </button>
                  </div>
                </div>
              </div>

              <div style={{ background: colors.surface, border: `1px solid ${colors.border}` }} className="p-6 rounded mb-4">
                <h3 className="font-semibold mb-4 text-sm uppercase tracking-wide" style={{ color: colors.textLight }}>Data Management</h3>
                <div className="flex items-center justify-between py-3">
                  <div>
                    <div className="font-medium">Clear All Data</div>
                    <div className="text-sm mt-1" style={{ color: colors.textLight }}>Remove all stored messages, metrics, and error logs</div>
                  </div>
                  <button
                    onClick={() => {
                      if (window.confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
                        setMessages([]);
                        setMetricsHistory([]);
                        setErrors([]);
                        localStorage.removeItem('jarvis_data');
                      }
                    }}
                    style={{ background: colors.error }}
                    className="px-5 py-2 rounded text-sm text-white font-medium hover:opacity-90"
                  >
                    Clear Data
                  </button>
                </div>
              </div>

              <div style={{ background: colors.surface, border: `1px solid ${colors.border}` }} className="p-6 rounded">
                <h3 className="font-semibold mb-4 text-sm uppercase tracking-wide" style={{ color: colors.textLight }}>System Information</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between py-2" style={{ borderBottom: `1px solid ${colors.border}` }}>
                    <span style={{ color: colors.textLight }}>Backend Endpoint</span>
                    <span className="font-mono font-medium">{API_BASE}</span>
                  </div>
                  <div className="flex justify-between py-2" style={{ borderBottom: `1px solid ${colors.border}` }}>
                    <span style={{ color: colors.textLight }}>Connection Status</span>
                    <span className="font-medium capitalize">{connectionStatus}</span>
                  </div>
                  <div className="flex justify-between py-2" style={{ borderBottom: `1px solid ${colors.border}` }}>
                    <span style={{ color: colors.textLight }}>Registered Skills</span>
                    <span className="font-medium">{skills.length}</span>
                  </div>
                  <div className="flex justify-between py-2" style={{ borderBottom: `1px solid ${colors.border}` }}>
                    <span style={{ color: colors.textLight }}>Total Messages</span>
                    <span className="font-medium">{messages.length}</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span style={{ color: colors.textLight }}>Error Count</span>
                    <span className="font-medium">{errors.length}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}