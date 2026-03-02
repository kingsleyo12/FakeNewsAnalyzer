import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

// ─── SVG Donut Chart ────────────────────────────────────────────────────────
function ScoreCircle({ value, color, size = 150 }) {
  const [animated, setAnimated] = useState(0);
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animated / 100) * circumference;

  useEffect(() => {
    const t = setTimeout(() => setAnimated(value), 80);
    return () => clearTimeout(t);
  }, [value]);

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      className="score-circle"
      aria-label={`Score: ${value}%`}
    >
      {/* Background track */}
      <circle
        cx="60" cy="60" r={radius}
        fill="none"
        stroke="rgba(255,255,255,0.07)"
        strokeWidth="10"
      />
      {/* Coloured arc */}
      <circle
        cx="60" cy="60" r={radius}
        fill="none"
        stroke={color}
        strokeWidth="10"
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        transform="rotate(-90 60 60)"
        style={{ transition: 'stroke-dashoffset 1s ease-out' }}
      />
      {/* Percentage text */}
      <text
        x="60" y="55"
        textAnchor="middle"
        dominantBaseline="middle"
        fill="#ffffff"
        fontSize="20"
        fontWeight="700"
        style={{ fontFamily: 'inherit' }}
      >
        {value}%
      </text>
    </svg>
  );
}

// ─── Range Markers ───────────────────────────────────────────────────────────
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

// ─── Range definitions ───────────────────────────────────────────────────────
const FAKE_NEWS_RANGES = [
  { min: 0,  max: 30,  label: 'Low Risk',  desc: 'Content appears credible',        color: '#22c55e' },
  { min: 31, max: 60,  label: 'Moderate',  desc: 'Some suspicious indicators',       color: '#eab308' },
  { min: 61, max: 80,  label: 'High Risk', desc: 'Likely misinformation',            color: '#f97316' },
  { min: 81, max: 100, label: 'Critical',  desc: 'Strong misinformation signals',    color: '#ef4444' },
];

const NEWS_AUTH_RANGES = [
  { min: 0,  max: 30,  label: 'Very Low',  desc: 'Content is highly unreliable',    color: '#ef4444' },
  { min: 31, max: 60,  label: 'Low',       desc: 'Treat with caution',              color: '#f97316' },
  { min: 61, max: 80,  label: 'Moderate',  desc: 'Generally credible',              color: '#eab308' },
  { min: 81, max: 100, label: 'High',      desc: 'Strong authenticity indicators',  color: '#22c55e' },
];

const ORIGINALITY_RANGES = [
  { min: 0,  max: 30,  label: 'Templated',    desc: 'Likely copied or generated',   color: '#ef4444' },
  { min: 31, max: 60,  label: 'Low',          desc: 'Moderate reuse detected',       color: '#f97316' },
  { min: 61, max: 80,  label: 'Moderate',     desc: 'Mostly original content',       color: '#eab308' },
  { min: 81, max: 100, label: 'Highly Original', desc: 'Unique vocabulary & style',  color: '#22c55e' },
];

const CYBER_THREAT_RANGES = [
  { min: 0,  max: 25,  label: 'Low',      desc: 'No significant threat detected',   color: '#22c55e' },
  { min: 26, max: 50,  label: 'Medium',   desc: 'Some suspicious patterns',         color: '#eab308' },
  { min: 51, max: 75,  label: 'High',     desc: 'Multiple threat indicators',       color: '#f97316' },
  { min: 76, max: 100, label: 'Critical', desc: 'Immediate security concern',       color: '#ef4444' },
];

const CYBER_AUTH_RANGES = [
  { min: 0,  max: 25,  label: 'Critical Risk', desc: 'Highly dangerous content',    color: '#ef4444' },
  { min: 26, max: 50,  label: 'High Risk',     desc: 'Significant threat present',  color: '#f97316' },
  { min: 51, max: 75,  label: 'Moderate',      desc: 'Some suspicious signals',     color: '#eab308' },
  { min: 76, max: 100, label: 'Safe',          desc: 'No significant threat found', color: '#22c55e' },
];

// ─── Colour helpers ──────────────────────────────────────────────────────────
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

// ─── Score Card ──────────────────────────────────────────────────────────────
function ScoreCard({ title, value, color, ranges, badge, badgeColor }) {
  return (
    <div className="result-card">
      <h3>{title}</h3>
      <div className="score-circle-wrap">
        <ScoreCircle value={value} color={color} />
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

// ─── Main App ────────────────────────────────────────────────────────────────
function App() {
  const [mode, setMode] = useState('fakenews');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSuccessAnimation, setShowSuccessAnimation] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);

  const fakeNewsSteps = [
    { label: 'Initializing deep analysis engine...', progress: 5 },
    { label: 'Running ML Transformer analysis (RoBERTa)...', progress: 25 },
    { label: 'Consulting Google Fact Check API...', progress: 50 },
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
      setError({ title: 'Input Too Short', message: 'Please enter at least 10 characters of text to analyze.', reason: null });
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    setShowSuccessAnimation(false);
    setLoadingStep(0);

    const stepInterval = setInterval(() => {
      setLoadingStep(prev => prev < steps.length - 1 ? prev + 1 : prev);
    }, 2000);

    try {
      let analysisText = text.trim();
      if (analysisText.length > 15000) analysisText = analysisText.substring(0, 15000);

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
          setError(null);
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

      setError({ title: errorTitle, message: errorMessage, reason: errorReason });
      setResults(null);
      setLoading(false);
    } finally {
      clearInterval(stepInterval);
    }
  };

  const pasteFromClipboard = async () => {
    try {
      const clipboardText = await navigator.clipboard.readText();
      if (clipboardText) { setText(clipboardText); setError(null); }
    } catch (err) {
      setError({
        title: 'Clipboard Access Denied',
        message: 'The browser blocked access to your clipboard.',
        reason: 'Please ensure you have granted clipboard permissions to this site.'
      });
    }
  };

  const clearForm = () => {
    setText(''); setUrl(''); setResults(null); setError(null); setShowSuccessAnimation(false);
  };

  const handleModeSwitch = (newMode) => {
    setMode(newMode); setResults(null); setError(null);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🔍 Fake News & Cyber Threat Intelligence Analyzer</h1>
        <p>Percentage-based analysis for content authenticity and security threats</p>
      </header>

      {/* Mode Selector Tabs */}
      <div className="mode-selector">
        <button
          id="tab-fakenews"
          className={`mode-tab ${mode === 'fakenews' ? 'mode-tab--active mode-tab--news' : ''}`}
          onClick={() => handleModeSwitch('fakenews')}
          aria-pressed={mode === 'fakenews'}
        >
          <span className="mode-tab-icon">📰</span>
          <span className="mode-tab-label">Fake News Analysis</span>
        </button>
        <button
          id="tab-cyberthreat"
          className={`mode-tab ${mode === 'cyberthreat' ? 'mode-tab--active mode-tab--cyber' : ''}`}
          onClick={() => handleModeSwitch('cyberthreat')}
          aria-pressed={mode === 'cyberthreat'}
        >
          <span className="mode-tab-icon">🛡️</span>
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
              aria-describedby="text-help"
            />
            <small id="text-help">Minimum 10 characters required</small>
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
                : mode === 'fakenews' ? '📰 Analyze for Fake News' : '🛡️ Analyze Cyber Threats'}
            </button>
            <button id="btn-paste" onClick={pasteFromClipboard} className="btn-secondary" title="Paste from clipboard">
              📋 Paste
            </button>
            <button id="btn-clear" onClick={clearForm} className="btn-secondary">Clear</button>
          </div>

          {!loading && error && !results && (
            <div className="error-message" role="alert">
              <div className="error-title"><span>⚠️</span> {error.title}</div>
              <div className="error-detail">{error.message}</div>
              {error.reason && (
                <div className="error-reason"><strong>Technical Cause:</strong> {error.reason}</div>
              )}
            </div>
          )}
        </section>

        {/* Success overlay */}
        {showSuccessAnimation && (
          <div className="success-overlay">
            <div className="checkmark-circle">
              <div className="circle"></div>
              <div className="checkmark-icon">✓</div>
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
              <div className="loader-icon">{mode === 'fakenews' ? '📰' : '🛡️'}</div>
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
              <h2>{mode === 'fakenews' ? '📰 Fake News Analysis Results' : '🛡️ Cyber Threat Analysis Results'}</h2>
            </div>

            {/* ── FAKE NEWS MODE ── */}
            {mode === 'fakenews' && (
              <>
                <div className="results-grid">
                  <ScoreCard
                    title="📰 Fake News Probability"
                    value={results.fake_news_probability}
                    color={getScoreColor(results.fake_news_probability)}
                    ranges={FAKE_NEWS_RANGES}
                  />
                  <ScoreCard
                    title="✅ News Authenticity"
                    value={results.news_authenticity_score}
                    color={getScoreColor(results.news_authenticity_score, true)}
                    ranges={NEWS_AUTH_RANGES}
                  />
                  <ScoreCard
                    title="📝 Originality Score"
                    value={results.originality_score}
                    color={getScoreColor(results.originality_score, true)}
                    ranges={ORIGINALITY_RANGES}
                  />
                </div>

                {/* Web Verification */}
                {results.analysis_details.fake_news_factors.web_verification && results.cyber_threat_risk < 40 && (
                  <div className="web-verification-section">
                    <h3>🔍 Web Verification Results</h3>
                    <div className="verification-card">
                      <p className="verification-status">
                        {results.analysis_details.fake_news_factors.web_verification}
                      </p>
                      <p className="credible-sources">
                        📰 Credible sources found: {results.analysis_details.fake_news_factors.credible_sources_found || 0}
                      </p>
                      <p className="verification-note">
                        {results.analysis_details.fake_news_factors.credible_sources_found > 0
                          ? '✅ Claims verified by credible news sources'
                          : '⚠️ No verification from credible sources found'}
                      </p>
                    </div>
                  </div>
                )}

                <div className="details-section">
                  <h3>📊 Detailed Analysis</h3>
                  <div className="details-grid">
                    <FactorCard title="Fake News Factors" factors={results.analysis_details.fake_news_factors} />
                    <FactorCard title="Originality Factors" factors={results.analysis_details.originality_factors} />
                  </div>
                </div>
              </>
            )}

            {/* ── CYBER THREAT MODE ── */}
            {mode === 'cyberthreat' && (
              <>
                <div className="results-grid">
                  <ScoreCard
                    title="🛡️ Cyber Threat Risk"
                    value={results.cyber_threat_risk}
                    color={getThreatColor(results.threat_level)}
                    ranges={CYBER_THREAT_RANGES}
                    badge={results.threat_level}
                    badgeColor={getThreatColor(results.threat_level)}
                  />
                  {/* <ScoreCard
                    title="🔒 Cyber Safety Score"
                    value={results.cyber_authenticity_score}
                    color={getScoreColor(results.cyber_authenticity_score, true)}
                    ranges={CYBER_AUTH_RANGES}
                  /> */}
                </div>

                <div className="details-section">
                  <h3>📊 Threat Intelligence Breakdown</h3>
                  <div className="details-grid">
                    <FactorCard title="Cyber Threat Factors" factors={results.analysis_details.cyber_threat_factors} />
                  </div>
                </div>
              </>
            )}
          </section>
        )}
      </main>

      <footer className="footer">
        <p>Academic Project - Fake News & Cyber Threat Intelligence System</p>
        <p>Percentage-based confidence scoring for interpretable results</p>
      </footer>
    </div>
  );
}

// ─── Factor Card ─────────────────────────────────────────────────────────────
function FactorCard({ title, factors }) {
  const { explanation, detected_threats, ...otherFactors } = factors;

  const formatValue = (key, value) => {
    if (typeof value === 'boolean') return value ? '✅ Yes' : '❌ No';
    if (value === null || value === undefined) return 'N/A';
    const percentageKeys = [
      'probability', 'score', 'ml_probability', 'heuristic_score',
      'nlp_adjustment', 'absurdity_score', 'clickbait_score',
      'fact_check_confidence', 'risk_score'
    ];
    const isPercentage = percentageKeys.some(p => key.includes(p));
    if (typeof value === 'number') return isPercentage ? `${value}%` : value;
    return value;
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
          {Array.isArray(detected_threats) ? detected_threats.join(', ') : detected_threats}
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
