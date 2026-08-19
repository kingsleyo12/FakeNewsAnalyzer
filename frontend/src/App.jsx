import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/* ═══════════════════════════════════════════════════════════════════════════════
   SVG ICONS
   ═══════════════════════════════════════════════════════════════════════════════ */

const iconStyle = { width: '1em', height: '1em', verticalAlign: '-0.125em', flexShrink: 0 };

function IconSearch({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function IconNewspaper({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2" />
      <path d="M18 14h-8" />
      <path d="M15 18h-5" />
      <path d="M10 6h8v4h-8V6Z" />
    </svg>
  );
}

function IconShield({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
    </svg>
  );
}

function IconShieldCheck({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}

function IconCheckCircle({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="12" cy="12" r="10" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}

function IconXCircle({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="12" cy="12" r="10" />
      <path d="m15 9-6 6" />
      <path d="m9 9 6 6" />
    </svg>
  );
}

function IconFileText({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
      <path d="M14 2v4a2 2 0 0 0 2 2h4" />
      <path d="M10 9H8" />
      <path d="M16 13H8" />
      <path d="M16 17H8" />
    </svg>
  );
}

function IconBarChart({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="12" x2="12" y1="20" y2="10" />
      <line x1="18" x2="18" y1="20" y2="4" />
      <line x1="6" x2="6" y1="20" y2="14" />
    </svg>
  );
}

function IconBrain({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z" />
      <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z" />
      <path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4" />
      <path d="M17.599 6.5a3 3 0 0 0 .399-1.375" />
      <path d="M6.003 5.125A3 3 0 0 0 6.401 6.5" />
      <path d="M3.477 10.896a4 4 0 0 1 .585-.396" />
      <path d="M19.938 10.5a4 4 0 0 1 .585.396" />
      <path d="M6 18a4 4 0 0 1-1.967-.516" />
      <path d="M19.967 17.484A4 4 0 0 1 18 18" />
    </svg>
  );
}

function IconGlobe({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="12" cy="12" r="10" />
      <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" />
      <path d="M2 12h20" />
    </svg>
  );
}

function IconAlertTriangle({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3" />
      <path d="M12 9v4" />
      <path d="M12 17h.01" />
    </svg>
  );
}

function IconClipboard({ size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect width="8" height="4" x="8" y="2" rx="1" ry="1" />
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
      <path d="M9 14h6" />
      <path d="M9 18h6" />
      <path d="M9 10h6" />
    </svg>
  );
}

function IconCheckBig({ size = 48, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════════
   HOOKS
   ═══════════════════════════════════════════════════════════════════════════════ */

/** Animated count-up from 0 → target value */
function useCountUp(target, duration = 1000, enabled = true) {
  const [value, setValue] = useState(0);
  const frameRef = useRef(null);

  useEffect(() => {
    if (!enabled || target === 0) {
      setValue(target);
      return;
    }
    const start = performance.now();
    const animate = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * target * 10) / 10);
      if (progress < 1) {
        frameRef.current = requestAnimationFrame(animate);
      }
    };
    frameRef.current = requestAnimationFrame(animate);
    return () => { if (frameRef.current) cancelAnimationFrame(frameRef.current); };
  }, [target, duration, enabled]);

  return value;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   PARTICLE FIELD
   ═══════════════════════════════════════════════════════════════════════════════ */

function ParticleField() {
  const canvasRef = useRef(null);
  const animRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let w, h;
    const particles = [];
    const COUNT = 28; // reduced from 60
    const CONNECT_DIST_SQ = 120 * 120; // squared distance, no sqrt needed
    const CONNECT_DIST = 120;
    let frameCount = 0;

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + 'px';
      canvas.style.height = h + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener('resize', resize);

    for (let i = 0; i < COUNT; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.25,
        vy: (Math.random() - 0.5) * 0.25,
        r: Math.random() * 1.2 + 0.4,
        opacity: Math.random() * 0.25 + 0.08,
      });
    }

    const draw = () => {
      // Throttle to every 2nd frame for perf
      frameCount++;
      if (frameCount % 2 === 0) {
        animRef.current = requestAnimationFrame(draw);
        return;
      }

      ctx.clearRect(0, 0, w, h);
      const len = particles.length;

      // Batch strokes: draw all lines in one path
      ctx.strokeStyle = 'rgba(108, 140, 255, 0.05)';
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      for (let i = 0; i < len; i++) {
        const a = particles[i];
        for (let j = i + 1; j < len; j++) {
          const b = particles[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          if (Math.abs(dx) < CONNECT_DIST && Math.abs(dy) < CONNECT_DIST) {
            const distSq = dx * dx + dy * dy;
            if (distSq < CONNECT_DIST_SQ) {
              ctx.moveTo(a.x, a.y);
              ctx.lineTo(b.x, b.y);
            }
          }
        }
      }
      ctx.stroke();

      // Draw particles (batch by opacity since they're all similar)
      ctx.fillStyle = 'rgba(167, 139, 250, 0.15)';
      ctx.beginPath();
      for (const p of particles) {
        ctx.moveTo(p.x + p.r, p.y);
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        // Move
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < -10) p.x = w + 10;
        if (p.x > w + 10) p.x = -10;
        if (p.y < -10) p.y = h + 10;
        if (p.y > h + 10) p.y = -10;
      }
      ctx.fill();

      animRef.current = requestAnimationFrame(draw);
    };

    animRef.current = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener('resize', resize);
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, []);

  return <canvas ref={canvasRef} className="particle-canvas" />;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   SVG DONUT CHART (with count-up)
   ═══════════════════════════════════════════════════════════════════════════════ */

function ScoreCircle({ value, color, size = 150, animate = false }) {
  const displayValue = useCountUp(value, 1200, animate);
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (displayValue / 100) * circumference;

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      className="score-circle"
      aria-label={`Score: ${value}%`}
    >
      <circle
        cx="60" cy="60" r={radius}
        fill="none"
        stroke="rgba(255,255,255,0.05)"
        strokeWidth="10"
      />
      <circle
        cx="60" cy="60" r={radius}
        fill="none"
        stroke={color}
        strokeWidth="10"
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        transform="rotate(-90 60 60)"
        style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)' }}
      />
      <text
        x="60" y="55"
        textAnchor="middle"
        dominantBaseline="middle"
        fill="#ffffff"
        fontSize="20"
        fontWeight="700"
        style={{ fontFamily: 'inherit' }}
      >
        {typeof displayValue === 'number' ? (displayValue % 1 === 0 ? displayValue : displayValue.toFixed(1)) : displayValue}%
      </text>
    </svg>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════════
   RANGE MARKERS
   ═══════════════════════════════════════════════════════════════════════════════ */

function RangeMarkers({ ranges, value }) {
  const active = ranges.findIndex(r => value >= r.min && value <= r.max);

  return (
    <div className="range-markers">
      {ranges.map((r, i) => (
        <div
          key={i}
          className={`range-item ${i === active ? 'range-item--active' : ''}`}
        >
          <span className="range-bar" style={{ backgroundColor: r.color }} />
          <div className="range-text">
            <span className="range-label" style={{ color: i === active ? r.color : undefined }}>
              {r.min}–{r.max}% · {r.label}
            </span>
            <span className="range-desc">{r.desc}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════════
   RANGE DEFINITIONS
   ═══════════════════════════════════════════════════════════════════════════════ */

const FAKE_NEWS_RANGES = [
  { min: 0, max: 30, label: 'Low Risk', desc: 'Content appears credible', color: '#22c55e' },
  { min: 31, max: 60, label: 'Moderate', desc: 'Some suspicious indicators', color: '#eab308' },
  { min: 61, max: 80, label: 'High Risk', desc: 'Likely misinformation', color: '#f97316' },
  { min: 81, max: 100, label: 'Critical', desc: 'Strong misinformation signals', color: '#ef4444' },
];

const NEWS_AUTH_RANGES = [
  { min: 0, max: 30, label: 'Very Low', desc: 'Content is highly unreliable', color: '#ef4444' },
  { min: 31, max: 60, label: 'Low', desc: 'Treat with caution', color: '#f97316' },
  { min: 61, max: 80, label: 'Moderate', desc: 'Generally credible', color: '#eab308' },
  { min: 81, max: 100, label: 'High', desc: 'Strong authenticity indicators', color: '#22c55e' },
];

const ORIGINALITY_RANGES = [
  { min: 0, max: 30, label: 'Templated', desc: 'Likely copied or generated', color: '#ef4444' },
  { min: 31, max: 60, label: 'Low', desc: 'Moderate reuse detected', color: '#f97316' },
  { min: 61, max: 80, label: 'Moderate', desc: 'Mostly original content', color: '#eab308' },
  { min: 81, max: 100, label: 'Highly Original', desc: 'Unique vocabulary & style', color: '#22c55e' },
];

const CYBER_THREAT_RANGES = [
  { min: 0, max: 25, label: 'Low', desc: 'No significant threat detected', color: '#22c55e' },
  { min: 26, max: 50, label: 'Medium', desc: 'Some suspicious patterns', color: '#eab308' },
  { min: 51, max: 75, label: 'High', desc: 'Multiple threat indicators', color: '#f97316' },
  { min: 76, max: 100, label: 'Critical', desc: 'Immediate security concern', color: '#ef4444' },
];

const CYBER_AUTH_RANGES = [
  { min: 0, max: 25, label: 'Critical Risk', desc: 'Highly dangerous content', color: '#ef4444' },
  { min: 26, max: 50, label: 'High Risk', desc: 'Significant threat present', color: '#f97316' },
  { min: 51, max: 75, label: 'Moderate', desc: 'Some suspicious signals', color: '#eab308' },
  { min: 76, max: 100, label: 'Safe', desc: 'No significant threat found', color: '#22c55e' },
];

/* ═══════════════════════════════════════════════════════════════════════════════
   COLOR HELPERS
   ═══════════════════════════════════════════════════════════════════════════════ */

const getThreatColor = (level) => ({
  Low: '#22c55e', Medium: '#eab308', High: '#f97316', Critical: '#ef4444'
}[level] || '#6b7280');

const getScoreColor = (score, inverse = false) => {
  const s = inverse ? 100 - score : score;
  if (s <= 30) return '#22c55e';
  if (s <= 50) return '#eab308';
  if (s <= 70) return '#f97316';
  return '#ef4444';
};

/* ═══════════════════════════════════════════════════════════════════════════════
   SCORE CARD
   ═══════════════════════════════════════════════════════════════════════════════ */

function ScoreCard({ title, value, color, ranges, badge, badgeColor, animate = false }) {
  return (
    <div className="result-card">
      <h3>{title}</h3>
      <div className="score-circle-wrap">
        <ScoreCircle value={value} color={color} animate={animate} />
        {badge && (
          <span className="threat-badge" style={{ backgroundColor: badgeColor }}>
            {badge}
          </span>
        )}
      </div>
      <RangeMarkers ranges={ranges} value={value} />
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════════
   MAIN APP
   ═══════════════════════════════════════════════════════════════════════════════ */

function App() {
  const [mode, setMode] = useState('fakenews');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSuccessAnimation, setShowSuccessAnimation] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [showDetails, setShowDetails] = useState(false);
  const [animateScores, setAnimateScores] = useState(false);

  const fakeNewsSteps = [
    { label: 'Initializing deep analysis engine...', progress: 5 },
    { label: 'Running ML Transformer analysis (DeBERTa)...', progress: 25 },
    { label: 'Consulting Groq Fact Check API...', progress: 50 },
    { label: 'Performing real-time Web verification...', progress: 75 },
    { label: 'Generating comprehensive report...', progress: 95 },
  ];

  const cyberThreatSteps = [
    { label: 'Initializing threat intelligence engine...', progress: 5 },
    { label: 'Scanning for phishing indicators...', progress: 30 },
    { label: 'Assessing malware & social engineering patterns...', progress: 60 },
    { label: 'Cross-referencing threat databases...', progress: 85 },
    { label: 'Generating security report...', progress: 95 },
  ];

  const steps = mode === 'cyberthreat' ? cyberThreatSteps : fakeNewsSteps;

  const analyzeContent = async () => {
    if (text.trim().length < 10) {
      toast.error('Input Too Short: Please enter at least 10 characters of text to analyze.');
      return;
    }
    if (text.trim().length > 1996) {
      toast.error('Input Too Long: Please enter at most 1996 characters of text to analyze.');
      return;
    }

    setLoading(true);
    setResults(null);
    setShowSuccessAnimation(false);
    setLoadingStep(0);
    setShowDetails(false);
    setAnimateScores(false);

    const stepInterval = setInterval(() => {
      setLoadingStep(prev => prev < steps.length - 1 ? prev + 1 : prev);
    }, 2000);

    try {
      let analysisText = text.trim();
      if (analysisText.length > 1996) analysisText = analysisText.substring(0, 1996);

      const response = await axios.post(`${API_URL}/analyze`, {
        text: analysisText,
        url: url.trim() || null
      }, { timeout: 120000 });

      setLoadingStep(steps.length - 1);

      setTimeout(() => {
        setLoading(false);
        setShowSuccessAnimation(true);
        setTimeout(() => {
          setShowSuccessAnimation(false);
          setResults(response.data);
          // Trigger count-up animation
          setTimeout(() => setAnimateScores(true), 50);
        }, 2200);
      }, 500);
    } catch (err) {
      console.error('Analysis error:', err);
      let errorTitle = 'Analysis Aborted';
      let errorMessage = 'The system could not complete the full analysis.';
      let errorReason = 'A technical error occurred while communicating with the analysis engines.';

      if (err.code === 'ECONNABORTED') {
        errorReason = 'The request timed out because the analysis took longer than 120 seconds.';
      } else if (err.response) {
        errorReason = err.response.data?.detail || 'The server returned an internal error state.';
      } else if (!navigator.onLine) {
        errorTitle = 'No Internet Connection';
        errorMessage = 'Analysis cannot proceed without a network connection.';
        errorReason = 'Your device appears to be offline.';
      }

      toast.error(`${errorTitle}: ${errorMessage} - ${errorReason}`);
      setResults(null);
      setLoading(false);
    } finally {
      clearInterval(stepInterval);
    }
  };

  const pasteFromClipboard = async () => {
    try {
      const clipboardText = await navigator.clipboard.readText();
      if (clipboardText) {
        setText(clipboardText.substring(0, 1996));
      }
    } catch (err) {
      toast.error('Clipboard Access Denied: The browser blocked access to your clipboard.');
    }
  };

  const clearForm = () => {
    setText(''); setUrl(''); setResults(null); setShowSuccessAnimation(false); setAnimateScores(false);
  };

  const handleModeSwitch = (newMode) => {
    setMode(newMode); setResults(null); setAnimateScores(false);
  };

  return (
    <div className="app">
      {/* Animated particle field */}
      <ParticleField />

      {/* Floating background orbs */}
      <div className="orb-container">
        <div className="orb orb--1" />
        <div className="orb orb--2" />
        <div className="orb orb--3" />
        <div className="orb orb--4" />
      </div>

      <ToastContainer position="top-right" theme="dark" />
      <header className="header">
        <div className="header-brand">
          <IconShieldCheck size={32} className="header-logo" />
          <h1>Sentinel NLP</h1>
        </div>
        <p>Fake News & Cyber Threat Intelligence Analyzer</p>
      </header>

      {/* Mode Selector Tabs */}
      <div className="mode-selector">
        <button
          id="tab-fakenews"
          className={`mode-tab ${mode === 'fakenews' ? 'mode-tab--active mode-tab--news' : ''}`}
          onClick={() => handleModeSwitch('fakenews')}
          aria-pressed={mode === 'fakenews'}
        >
          <IconNewspaper size={18} className="mode-tab-icon" />
          <span className="mode-tab-label">Fake News Analysis</span>
        </button>
        <button
          id="tab-cyberthreat"
          className={`mode-tab ${mode === 'cyberthreat' ? 'mode-tab--active mode-tab--cyber' : ''}`}
          onClick={() => handleModeSwitch('cyberthreat')}
          aria-pressed={mode === 'cyberthreat'}
        >
          <IconShield size={18} className="mode-tab-icon" />
          <span className="mode-tab-label">Cyber Threat Analysis</span>
        </button>
      </div>

      <main className="main-content">
        <section className="input-section">
          <div className="input-group">
            <label htmlFor="text-input">
              {mode === 'fakenews' ? 'Article / Post to Analyze' : 'Suspicious Content to Inspect'}
            </label>
            <textarea
              id="text-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={
                mode === 'fakenews'
                  ? 'Paste a news article, social media post, or headline here...'
                  : 'Paste a suspicious email, message, URL description, or any potentially malicious content...'
              }
              rows={8}
              maxLength={1996}
              aria-describedby="text-help"
            />
            <div className="input-meta">
              <small id="text-help">Minimum 10 characters required</small>
              <small className="input-count">{text.length} / 1996</small>
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="url-input">URL (Optional)</label>
            <input
              id="url-input"
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/article"
              aria-describedby="url-help"
            />
            <small id="url-help">
              {mode === 'fakenews'
                ? 'Enter the source URL to cross-check article origin'
                : 'Enter a suspicious URL to analyze for phishing indicators'}
            </small>
          </div>

          <div className="button-group">
            <button
              id="btn-analyze"
              onClick={analyzeContent}
              disabled={loading || showSuccessAnimation}
              className={`btn-primary ${mode === 'cyberthreat' ? 'btn-primary--cyber' : ''}`}
              aria-busy={loading}
            >
              {loading
                ? 'Analyzing...'
                : mode === 'fakenews' ? <><IconSearch size={16} /> Analyze for Fake News</> : <><IconShieldCheck size={16} /> Analyze Cyber Threats</>}
            </button>
            <button id="btn-paste" onClick={pasteFromClipboard} className="btn-secondary" title="Paste from clipboard">
              <IconClipboard size={16} /> Paste
            </button>
            <button id="btn-clear" onClick={clearForm} className="btn-secondary">Clear</button>
          </div>
        </section>

        {/* Success overlay */}
        {showSuccessAnimation && (
          <div className="success-overlay">
            <div className="checkmark-circle">
              <div className="circle"></div>
              <div className="checkmark-icon">
                <IconCheckBig size={56} />
              </div>
            </div>
            <div className="success-message-text">
              <h2>Analysis Completed</h2>
              <p>Security & Verification Passed</p>
            </div>
          </div>
        )}

        {/* Loading overlay */}
        {loading && (
          <div className="loading-overlay">
            <div className="loader-container">
              <div className="loader-outer"></div>
              <div className="loader-inner"></div>
              <div className="loader-icon">
                {mode === 'fakenews' ? <IconNewspaper size={28} /> : <IconShield size={28} />}
              </div>
            </div>
            <div className="loading-text">
              <h2>{mode === 'fakenews' ? 'Fake News Analysis in Progress' : 'Threat Analysis in Progress'}</h2>
              <div className="loading-step">{steps[loadingStep].label}</div>
            </div>
            <div className="loading-progress-container">
              <div className="loading-progress-bar" style={{ width: `${steps[loadingStep].progress}%` }} />
            </div>
          </div>
        )}

        {/* ── Results ── */}
        {!loading && results && (
          <section className="results-section" aria-live="polite">
            <div className="results-header">
              <h2>
                {mode === 'fakenews' ? <><IconNewspaper size={22} /> Fake News Analysis Results</> : <><IconShield size={22} /> Cyber Threat Analysis Results</>}
              </h2>
            </div>

            {/* ── FAKE NEWS MODE ── */}
            {mode === 'fakenews' && (
              <>
                <div className="results-grid">
                  <ScoreCard
                    title="Fake News Probability"
                    value={results.fake_news_probability}
                    color={getScoreColor(results.fake_news_probability)}
                    ranges={FAKE_NEWS_RANGES}
                    animate={animateScores}
                  />
                  <ScoreCard
                    title="News Authenticity"
                    value={results.news_authenticity_score}
                    color={getScoreColor(results.news_authenticity_score, true)}
                    ranges={NEWS_AUTH_RANGES}
                    animate={animateScores}
                  />
                  <ScoreCard
                    title="Originality Score"
                    value={results.originality_score}
                    color={getScoreColor(results.originality_score, true)}
                    ranges={ORIGINALITY_RANGES}
                    animate={animateScores}
                  />
                </div>

                <div className="details-section" onClick={() => setShowDetails(!showDetails)}>
                  <div className="details-toggle">
                    <h3><IconBarChart size={18} /> Detailed Analysis</h3>
                    <span className="details-arrow" data-open={showDetails}>▼</span>
                  </div>

                  {showDetails && (
                    <div className="details-grid">
                      <FactorCard title="Fake News Factors" factors={results.analysis_details.fake_news_factors} />
                      <FactorCard title="Originality Factors" factors={results.analysis_details.originality_factors} />
                    </div>
                  )}
                </div>
              </>
            )}

            {/* ── CYBER THREAT MODE ── */}
            {mode === 'cyberthreat' && (
              <>
                <div className="results-grid">
                  <ScoreCard
                    title="Cyber Threat Risk"
                    value={results.cyber_threat_risk}
                    color={getThreatColor(results.threat_level)}
                    ranges={CYBER_THREAT_RANGES}
                    badge={results.threat_level}
                    badgeColor={getThreatColor(results.threat_level)}
                    animate={animateScores}
                  />
                </div>

                <div className="details-section" onClick={() => setShowDetails(!showDetails)}>
                  <div className="details-toggle">
                    <h3><IconBarChart size={18} /> Threat Intelligence Breakdown</h3>
                    <span className="details-arrow" data-open={showDetails}>▼</span>
                  </div>

                  {showDetails && (
                    <div className="details-grid">
                      <FactorCard title="Cyber Threat Factors" factors={results.analysis_details.cyber_threat_factors} />
                    </div>
                  )}
                </div>
              </>
            )}
          </section>
        )}
      </main>

      <footer className="footer">
        <p>Sentinel NLP — Fake News & Cyber Threat Intelligence System</p>
        <p>Percentage-based confidence scoring for interpretable results</p>
      </footer>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════════
   FACTOR CARD
   ═══════════════════════════════════════════════════════════════════════════════ */

function FactorCard({ title, factors }) {
  const { explanation, detected_threats, ai_analysis, web_sources, ...otherFactors } = factors;
  const [isSourcesExpanded, setIsSourcesExpanded] = useState(false);

  const formatValue = (key, value) => {
    if (typeof value === 'boolean') return value ? <><IconCheckCircle size={14} className="icon-yes" /> Yes</> : <><IconXCircle size={14} className="icon-no" /> No</>;
    if (value === null || value === undefined) return 'N/A';
    if (Array.isArray(value)) return value.length > 0 ? value.join(', ') : 'None';
    if (typeof value === 'object') return JSON.stringify(value);
    const percentageKeys = [
      'probability', 'score', 'ml_probability', 'heuristic_score',
      'nlp_adjustment', 'absurdity_score', 'clickbait_score',
      'fact_check_confidence', 'risk_score'
    ];
    const isPercentage = percentageKeys.some(p => key.includes(p));
    if (typeof value === 'number') return isPercentage ? `${value}%` : value;
    return String(value);
  };

  return (
    <div className="factor-card">
      <h4>{title}</h4>
      {explanation && (
        <div className="card-summary"><strong>Summary:</strong> {explanation}</div>
      )}
      {detected_threats && (
        <div className="card-summary threats">
          <strong>Detected Threats:</strong>{' '}
          {Array.isArray(detected_threats) ? detected_threats.join(', ') : String(detected_threats)}
        </div>
      )}
      {/* AI Verifier Analysis */}
      {ai_analysis && ai_analysis.reasoning && (
        <div className="card-summary card-summary--ai">
          <strong><IconBrain size={14} /> Explainable AI:</strong>
          <div className="card-summary__body">
            {ai_analysis.reasoning}
          </div>
        </div>
      )}
      {/* Web Sources */}
      {web_sources && web_sources.length > 0 && (
        <div className="card-summary card-summary--sources">
          <div
            className="sources-toggle"
            onClick={() => setIsSourcesExpanded(!isSourcesExpanded)}
          >
            <strong><IconGlobe size={14} /> Searched Sources ({web_sources.length})</strong>
            <span className="details-arrow" data-open={isSourcesExpanded}>▼</span>
          </div>

          {isSourcesExpanded && (
            <ul className="sources-list">
              {web_sources.map((source, idx) => {
                let domain = source.url;
                try { domain = new URL(source.url).hostname.replace('www.', ''); } catch (e) { }

                return (
                  <li key={idx} className="source-item">
                    <a href={source.url} target="_blank" rel="noopener noreferrer"
                      className={`source-link ${source.is_credible ? 'source-link--credible' : 'source-link--warning'}`}>
                      {source.is_credible ? <IconCheckCircle size={13} /> : <IconAlertTriangle size={13} />}
                      {domain}
                    </a>
                    {source.title && (
                      <div className="source-title">{source.title}</div>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
      <ul>
        {Object.entries(otherFactors).map(([key, value]) => (
          <li key={key}>
            <span className="factor-name">{key.replace(/_/g, ' ')}:</span>
            <span className="factor-value">{formatValue(key, value)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
