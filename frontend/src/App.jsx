import React, { useState, useEffect, useRef } from 'react';
import {
  Shield,
  Eye,
  Bell,
  Clock,
  Send,
  Play,
  Activity,
  AlertTriangle,
  CheckCircle,
  X,
  RefreshCw,
  Home,
  Moon,
  Target,
  Sparkles,
  Zap,
  Radio,
  DoorClosed,
  Car,
  Footprints,
  Terminal,
} from 'lucide-react';

const API_BASE = '';

export default function App() {
  // State
  const [homeState, setHomeState] = useState({
    occupancy_mode: 'home',
    active_alerts: [],
    devices_count: 0,
    devices: {},
    context_summary: 'Loading HomeMind ambient context...',
    last_event_timestamp: null,
    active_watches_count: 0,
    updated_at: new Date().toISOString(),
  });
  const [events, setEvents] = useState([]);
  const [watches, setWatches] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());
  const [loadingAction, setLoadingAction] = useState(false);

  // Chat conversation
  const [chatMessages, setChatMessages] = useState([
    {
      sender: 'homemind',
      text: "Hello! I'm HomeMind, your context-aware home intelligence agent. You can ask what's happening or set a temporary watch.",
      tool: null,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const chatEndRef = useRef(null);

  // Custom simulation inputs
  const [simLocation, setSimLocation] = useState('front_door');
  const [simType, setSimType] = useState('doorbell_press');

  // Clock tick
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Poll backend state every 1.5s
  const fetchAllData = async () => {
    try {
      const [stateRes, eventsRes, watchesRes, alertsRes] = await Promise.all([
        fetch(`${API_BASE}/state`),
        fetch(`${API_BASE}/events?limit=25`),
        fetch(`${API_BASE}/watches`),
        fetch(`${API_BASE}/alerts`),
      ]);

      if (stateRes.ok) {
        const s = await stateRes.json();
        setHomeState(s);
        setConnected(true);
      } else {
        setConnected(false);
      }
      if (eventsRes.ok) {
        const ev = await eventsRes.json();
        setEvents(ev);
      }
      if (watchesRes.ok) {
        const w = await watchesRes.json();
        setWatches(w);
      }
      if (alertsRes.ok) {
        const al = await alertsRes.json();
        setAlerts(al);
      }
    } catch (err) {
      setConnected(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 1500);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Mode changer
  const handleSetMode = async (mode) => {
    setLoadingAction(true);
    try {
      await fetch(`${API_BASE}/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode }),
      });
      await fetchAllData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingAction(false);
    }
  };

  // Simulate event trigger
  const handleSimulate = async (eventType, location, metadata = {}) => {
    setLoadingAction(true);
    try {
      const res = await fetch(`${API_BASE}/simulate/event`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_type: eventType,
          location: location,
          source: 'ring',
          metadata,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        // Add notification note if action was notify_user
        if (data.action?.decision === 'notify_user') {
          setChatMessages((prev) => [
            ...prev,
            {
              sender: 'homemind',
              text: `🔔 [Voice Notification - ${data.action.target_device.toUpperCase()}]: ${data.action.payload?.message || data.action.reasoning}`,
              tool: 'proactive_decision',
              time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            },
          ]);
        }
      }
      await fetchAllData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingAction(false);
    }
  };

  // Cancel watch
  const handleCancelWatch = async (watchId) => {
    try {
      await fetch(`${API_BASE}/watches/${watchId}`, { method: 'DELETE' });
      await fetchAllData();
    } catch (err) {
      console.error(err);
    }
  };

  // Dismiss alert
  const handleDismissAlert = async (alertId) => {
    try {
      await fetch(`${API_BASE}/alerts/clear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alert_id: alertId }),
      });
      await fetchAllData();
    } catch (err) {
      console.error(err);
    }
  };

  // Chat send
  const handleSendMessage = async (msgText) => {
    const textToSend = msgText || inputMessage;
    if (!textToSend.trim()) return;

    const userMsg = {
      sender: 'user',
      text: textToSend,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setChatMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setLoadingAction(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: textToSend }),
      });
      if (res.ok) {
        const data = await res.json();
        setChatMessages((prev) => [
          ...prev,
          {
            sender: 'homemind',
            text: data.reply,
            tool: data.tool_called,
            toolResult: data.tool_result,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      } else {
        setChatMessages((prev) => [
          ...prev,
          {
            sender: 'homemind',
            text: 'Sorry, I encountered an issue executing that command.',
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
      }
      await fetchAllData();
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        {
          sender: 'homemind',
          text: 'Unable to communicate with HomeMind backend.',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoadingAction(false);
    }
  };

  const modeColors = {
    home: { bg: 'badge-blue', icon: <Home size={14} />, label: 'Home' },
    away: { bg: 'badge-amber', icon: <Shield size={14} />, label: 'Away' },
    sleep: { bg: 'badge-purple', icon: <Moon size={14} />, label: 'Sleep' },
    focus: { bg: 'badge-indigo', icon: <Target size={14} />, label: 'Focus' },
  };

  const getEventIcon = (type) => {
    const t = type.toLowerCase();
    if (t.includes('doorbell') || t.includes('chime')) return <DoorClosed size={16} className="text-amber-400" />;
    if (t.includes('vehicle')) return <Car size={16} className="text-sky-400" />;
    return <Footprints size={16} className="text-emerald-400" />;
  };

  return (
    <div className="app-container">
      {/* SECTION A: HEADER */}
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)'
          }}>
            <Sparkles size={24} color="#fff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ fontSize: '1.45rem', fontWeight: 800, letterSpacing: '-0.02em', margin: 0 }}>HomeMind</h1>
              <span className="badge badge-indigo">Local Agent + MCP</span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
              Context-Aware Multi-Device AI Home Agent · Amazon Build, Ship, Shape
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 12px',
            borderRadius: '10px',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            fontSize: '0.8rem'
          }}>
            <span className="pulse-dot" style={{ backgroundColor: connected ? '#10b981' : '#ef4444', boxShadow: connected ? '0 0 8px #10b981' : '0 0 8px #ef4444' }} />
            <span style={{ color: connected ? '#34d399' : '#f87171', fontWeight: 600 }}>
              {connected ? 'Backend Online (Port 8081)' : 'Connecting...'}
            </span>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 12px',
            borderRadius: '10px',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            fontSize: '0.85rem',
            color: 'var(--text-muted)',
            fontFamily: 'monospace'
          }}>
            <Clock size={14} />
            <span>{currentTime}</span>
          </div>
        </div>
      </header>

      {/* SECTION B: HOME STATE & OCCUPANCY MODE */}
      <section style={{ marginBottom: '24px' }}>
        <div className="card" style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.6) 100%)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '18px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>Occupancy & Context State</span>
                <span className={`badge ${modeColors[homeState.occupancy_mode]?.bg || 'badge-blue'}`}>
                  {modeColors[homeState.occupancy_mode]?.icon}
                  {modeColors[homeState.occupancy_mode]?.label || homeState.occupancy_mode} Mode
                </span>
              </div>
              <p style={{ fontSize: '1.2rem', fontWeight: 600, color: '#f8fafc', lineHeight: 1.4, margin: 0, maxWidth: '850px' }}>
                {homeState.context_summary}
              </p>
            </div>

            {/* Quick Mode Switcher */}
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {['home', 'away', 'sleep', 'focus'].map((modeKey) => (
                <button
                  key={modeKey}
                  onClick={() => handleSetMode(modeKey)}
                  className={`btn btn-sm ${homeState.occupancy_mode === modeKey ? 'btn-primary' : ''}`}
                  style={{
                    borderColor: homeState.occupancy_mode === modeKey ? 'transparent' : 'var(--border-color)',
                    textTransform: 'capitalize'
                  }}
                  disabled={loadingAction}
                >
                  {modeColors[modeKey]?.icon}
                  {modeKey}
                </button>
              ))}
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: '12px',
            paddingTop: '16px',
            borderTop: '1px solid rgba(255, 255, 255, 0.07)'
          }}>
            <div style={{ padding: '10px 14px', borderRadius: '10px', background: 'rgba(0, 0, 0, 0.25)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Active Watches</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: watches.length > 0 ? '#fbbf24' : '#94a3b8' }}>
                {watches.length} Active
              </div>
            </div>

            <div style={{ padding: '10px 14px', borderRadius: '10px', background: 'rgba(0, 0, 0, 0.25)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Active Alerts</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: alerts.length > 0 ? '#f87171' : '#34d399' }}>
                {alerts.length} Alerts
              </div>
            </div>

            <div style={{ padding: '10px 14px', borderRadius: '10px', background: 'rgba(0, 0, 0, 0.25)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Observed Devices</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#38bdf8' }}>
                {homeState.devices_count} Devices
              </div>
            </div>

            <div style={{ padding: '10px 14px', borderRadius: '10px', background: 'rgba(0, 0, 0, 0.25)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Ingested Events</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#a5b4fc' }}>
                {events.length} Events
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION E: ACTIVE ALERTS (If any) */}
      {alerts.length > 0 && (
        <section style={{ marginBottom: '24px' }}>
          <div className="card" style={{ borderColor: 'rgba(239, 68, 68, 0.3)', background: 'rgba(31, 18, 26, 0.85)' }}>
            <div className="card-header">
              <span className="card-title" style={{ color: '#f87171' }}>
                <AlertTriangle size={18} />
                Active HomeMind Alerts ({alerts.length})
              </span>
              <button onClick={() => handleDismissAlert('all')} className="btn btn-sm btn-danger">
                Clear All Alerts
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {alerts.map((alertText, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    borderRadius: '10px',
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <AlertTriangle size={16} className="text-red-400" />
                    <span style={{ fontSize: '0.9rem', color: '#fecaca' }}>{alertText}</span>
                  </div>
                  <button onClick={() => handleDismissAlert(alertText)} className="btn btn-sm" style={{ background: 'transparent' }}>
                    <X size={14} /> Dismiss
                  </button>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* MAIN TWO-COLUMN WORKSPACE */}
      <div className="grid-layout">
        {/* LEFT COLUMN: ACTIVE WATCHES & CONVERSATION */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* SECTION C: ACTIVE WATCHES */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">
                <Eye size={18} style={{ color: '#fbbf24' }} />
                Active Temporary Watches
                <span className="badge badge-amber">{watches.length}</span>
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Targeted intention monitoring
              </span>
            </div>

            {watches.length === 0 ? (
              <div style={{
                padding: '24px',
                textAlign: 'center',
                borderRadius: '12px',
                background: 'rgba(0, 0, 0, 0.2)',
                border: '1px dashed var(--border-color)',
                color: 'var(--text-dim)'
              }}>
                <Eye size={24} style={{ margin: '0 auto 8px', opacity: 0.4 }} />
                <p style={{ margin: '0 0 4px', fontSize: '0.88rem' }}>No temporary watches currently active.</p>
                <p style={{ margin: 0, fontSize: '0.78rem' }}>
                  Ask Alexa+ in the panel below: <em>"Watch the front door for 30 minutes"</em>
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {watches.map((w) => {
                  const mins = Math.floor(w.remaining_seconds / 60);
                  const secs = w.remaining_seconds % 60;
                  return (
                    <div
                      key={w.watch_id}
                      style={{
                        padding: '12px 16px',
                        borderRadius: '12px',
                        background: 'rgba(245, 158, 11, 0.08)',
                        border: '1px solid rgba(245, 158, 11, 0.25)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '12px',
                        flexWrap: 'wrap'
                      }}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#fef08a' }}>
                            📍 {w.location.replace('_', ' ').toUpperCase()}
                          </span>
                          <span className="badge badge-amber" style={{ fontSize: '0.7rem' }}>
                            {mins}m {secs}s remaining
                          </span>
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          Duration: {w.duration_minutes}m · Created at: {new Date(w.created_at).toLocaleTimeString()}
                          {w.event_types && ` · Filters: [${w.event_types.join(', ')}]`}
                        </div>
                      </div>

                      <button
                        onClick={() => handleCancelWatch(w.watch_id)}
                        className="btn btn-sm btn-danger"
                      >
                        <X size={13} /> Cancel Watch
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* SECTION F: HOME MIND CONVERSATION PANEL (ALEXA+ INTERFACE) */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '520px' }}>
            <div className="card-header" style={{ marginBottom: '12px' }}>
              <span className="card-title">
                <Radio size={18} style={{ color: '#a855f7' }} />
                Alexa+ Conversational Interface
              </span>
              <span className="badge badge-purple">MCP Client Sim</span>
            </div>

            {/* Quick Prompts */}
            <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '8px', marginBottom: '10px' }}>
              {[
                'What is happening at home?',
                'What happened at the front door?',
                'Watch the front door for 30 minutes.',
                'Set focus mode.',
                'Set home mode.',
                'Show recent events.',
              ].map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => handleSendMessage(prompt)}
                  disabled={loadingAction}
                  style={{
                    padding: '4px 10px',
                    fontSize: '0.72rem',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    color: '#cbd5e1',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {prompt}
                </button>
              ))}
            </div>

            {/* Messages Scroll Area */}
            <div style={{
              flex: 1,
              overflowY: 'auto',
              padding: '12px',
              borderRadius: '12px',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--border-color)',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              marginBottom: '12px'
            }}>
              {chatMessages.map((msg, index) => (
                <div
                  key={index}
                  style={{
                    alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '85%',
                    padding: '10px 14px',
                    borderRadius: msg.sender === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                    background: msg.sender === 'user'
                      ? 'linear-gradient(135deg, #4338ca 0%, #4f46e5 100%)'
                      : 'rgba(23, 32, 51, 0.9)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', marginBottom: '4px' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, color: msg.sender === 'user' ? '#c7d2fe' : '#c084fc', textTransform: 'uppercase' }}>
                      {msg.sender === 'user' ? 'User' : 'HomeMind Agent (Alexa+)'}
                    </span>
                    <span style={{ fontSize: '0.65rem', color: 'rgba(255, 255, 255, 0.4)' }}>{msg.time}</span>
                  </div>

                  <p style={{ margin: 0, fontSize: '0.88rem', color: '#f8fafc', whiteSpace: 'pre-wrap', lineHeight: 1.45 }}>
                    {msg.text}
                  </p>

                  {msg.tool && (
                    <div style={{ marginTop: '6px', paddingTop: '6px', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                      <span className="badge badge-purple" style={{ fontSize: '0.65rem', textTransform: 'none' }}>
                        <Terminal size={10} /> Tool: {msg.tool}
                      </span>
                    </div>
                  )}
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>

            {/* Chat Input */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              style={{ display: 'flex', gap: '8px' }}
            >
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Say something to HomeMind..."
                disabled={loadingAction}
                style={{
                  flex: 1,
                  padding: '10px 14px',
                  borderRadius: '10px',
                  background: 'var(--bg-card-secondary)',
                  border: '1px solid var(--border-color)',
                  color: '#fff',
                  fontSize: '0.88rem',
                  outline: 'none'
                }}
              />
              <button type="submit" className="btn btn-primary" disabled={loadingAction || !inputMessage.trim()}>
                <Send size={15} /> Send
              </button>
            </form>
          </div>
        </div>

        {/* RIGHT COLUMN: SIMULATION CONTROLS & RECENT EVENTS */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* SECTION G: SIMULATION CONTROLS */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">
                <Zap size={18} style={{ color: '#38bdf8' }} />
                Event & Sensor Simulator
              </span>
              <span className="badge badge-blue">Ring Provider Sim</span>
            </div>

            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
              Dispatch real-world physical events into HomeMind's cognitive loop to test awareness and active watches.
            </p>

            {/* Quick Simulation Buttons */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '8px', marginBottom: '16px' }}>
              <button
                onClick={() => handleSimulate('doorbell_press', 'front_door')}
                disabled={loadingAction}
                className="btn btn-sm"
                style={{ background: 'rgba(245, 158, 11, 0.15)', borderColor: 'rgba(245, 158, 11, 0.3)', color: '#fbbf24' }}
              >
                <DoorClosed size={14} /> Doorbell (Front)
              </button>

              <button
                onClick={() => handleSimulate('motion_detected', 'front_door')}
                disabled={loadingAction}
                className="btn btn-sm"
                style={{ background: 'rgba(16, 185, 129, 0.15)', borderColor: 'rgba(16, 185, 129, 0.3)', color: '#34d399' }}
              >
                <Footprints size={14} /> Motion (Front)
              </button>

              <button
                onClick={() => handleSimulate('vehicle_detected', 'driveway')}
                disabled={loadingAction}
                className="btn btn-sm"
                style={{ background: 'rgba(14, 165, 233, 0.15)', borderColor: 'rgba(14, 165, 233, 0.3)', color: '#38bdf8' }}
              >
                <Car size={14} /> Vehicle (Driveway)
              </button>

              <button
                onClick={() => handleSimulate('motion_detected', 'backyard')}
                disabled={loadingAction}
                className="btn btn-sm"
              >
                <Footprints size={14} /> Motion (Backyard)
              </button>
            </div>

            {/* Custom Event Trigger Form */}
            <div style={{
              padding: '12px',
              borderRadius: '10px',
              background: 'rgba(0, 0, 0, 0.25)',
              border: '1px solid var(--border-color)',
              display: 'flex',
              gap: '8px',
              flexWrap: 'wrap',
              alignItems: 'center'
            }}>
              <select
                value={simType}
                onChange={(e) => setSimType(e.target.value)}
                style={{
                  background: 'var(--bg-card-secondary)',
                  border: '1px solid var(--border-color)',
                  color: '#fff',
                  padding: '6px 10px',
                  borderRadius: '8px',
                  fontSize: '0.8rem',
                  outline: 'none',
                  flex: 1
                }}
              >
                <option value="doorbell_press">doorbell_press</option>
                <option value="motion_detected">motion_detected</option>
                <option value="vehicle_detected">vehicle_detected</option>
                <option value="door_opened">door_opened</option>
                <option value="smoke_alarm_triggered">smoke_alarm_triggered</option>
              </select>

              <select
                value={simLocation}
                onChange={(e) => setSimLocation(e.target.value)}
                style={{
                  background: 'var(--bg-card-secondary)',
                  border: '1px solid var(--border-color)',
                  color: '#fff',
                  padding: '6px 10px',
                  borderRadius: '8px',
                  fontSize: '0.8rem',
                  outline: 'none',
                  flex: 1
                }}
              >
                <option value="front_door">front_door</option>
                <option value="driveway">driveway</option>
                <option value="backyard">backyard</option>
                <option value="living_room">living_room</option>
                <option value="garage">garage</option>
                <option value="kitchen">kitchen</option>
              </select>

              <button
                onClick={() => handleSimulate(simType, simLocation)}
                disabled={loadingAction}
                className="btn btn-sm btn-primary"
              >
                <Play size={13} /> Trigger
              </button>
            </div>
          </div>

          {/* SECTION D: RECENT EVENTS LOG */}
          <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', maxHeight: '420px' }}>
            <div className="card-header">
              <span className="card-title">
                <Activity size={18} style={{ color: '#10b981' }} />
                Real-Time Event Stream
                <span className="badge badge-green">{events.length}</span>
              </span>
              <button onClick={fetchAllData} className="btn btn-sm" style={{ padding: '4px 8px' }}>
                <RefreshCw size={12} />
              </button>
            </div>

            {events.length === 0 ? (
              <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem', textAlign: 'center', padding: '24px 0' }}>
                No events recorded yet. Trigger one above!
              </p>
            ) : (
              <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px', paddingRight: '4px' }}>
                {events.slice(0, 30).map((evt, idx) => (
                  <div
                    key={evt.event_id || idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 12px',
                      borderRadius: '8px',
                      background: 'rgba(255, 255, 255, 0.03)',
                      border: '1px solid rgba(255, 255, 255, 0.05)',
                      fontSize: '0.8rem'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      {getEventIcon(evt.event_type)}
                      <div>
                        <div style={{ fontWeight: 600, color: '#f1f5f9' }}>
                          {evt.event_type.replace('_', ' ')}
                        </div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          📍 {evt.location} · {evt.source}
                        </div>
                      </div>
                    </div>

                    <div style={{ textAlign: 'right', fontSize: '0.7rem', color: 'var(--text-dim)', fontFamily: 'monospace' }}>
                      {new Date(evt.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
