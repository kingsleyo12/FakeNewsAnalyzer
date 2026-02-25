import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [mode, setMode] = useState('fakenews'); // 'fakenews' | 'cyberthreat'
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
      setError('Please enter at least 10 characters of text to analyze.');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);
    setShowSuccessAnimation(false);
    setLoadingStep(0);

    const stepInterval = setInterval(() => {
      setLoadingStep(prev => {
        if (prev < steps.length - 1) return prev + 1;
        return prev;
      });
    }, 2000);

    try {
      let analysisText = text.trim();
      if (analysisText.length > 15000) {
        analysisText = analysisText.substring(0, 15000);
      }

      const response = await axios.post(`${API_URL}/analyze`, {
        text: analysisText,
        url: url.trim() || null
      }, {
        timeout: 45000
      });

      setLoadingStep(steps.length - 1);

      const analysisData = response.data;

      setTimeout(() => {
        setLoading(false);
        setShowSuccessAnimation(true);

        setTimeout(() => {
          setShowSuccessAnimation(false);
          setResults(analysisData);
          setError(null);
        }, 2200);
      }, 500);
    } catch (err) {
      console.error('Analysis error:', err);
      let errorTitle = 'Analysis Aborted';
      let errorMessage = 'The system could not complete the full analysis.';
      let errorReason = 'A technical error occurred while communicating with the analysis engines.';

      if (err.code === 'ECONNABORTED') {
        errorReason = 'The request timed out because the analysis took longer than 45 seconds.';
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
      if (clipboardText) {
        setText(clipboardText);
        setError(null);
      }
    } catch (err) {
      console.error('Failed to read clipboard:', err);
      setError({
        title: 'Clipboard Access Denied',
        message: 'The browser blocked access to your clipboard.',
        reason: 'Please ensure you have granted clipboard permissions to this site.'
      });
    }
  };

  const clearForm = () => {
    setText('');
    setUrl('');
    setResults(null);
    setError(null);
    setShowSuccessAnimation(false);
  };

  const handleModeSwitch = (newMode) => {
    setMode(newMode);
    setResults(null);
    setError(null);
  };

  const getThreatColor = (level) => {
    const colors = {
      'Low': '#22c55e',
      'Medium': '#eab308',
      'High': '#f97316',
      'Critical': '#ef4444'
    };
    return colors[level] || '#6b7280';
  };

  const getScoreColor = (score, inverse = false) => {
    const adjustedScore = inverse ? 100 - score : score;
    if (adjustedScore <= 30) return '#22c55e';
    if (adjustedScore <= 50) return '#eab308';
    if (adjustedScore <= 70) return '#f97316';
    return '#ef4444';
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

          {/* URL field shown for both modes but with context-appropriate help text */}
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
                : mode === 'fakenews'
                  ? '📰 Analyze for Fake News'
                  : '🛡️ Analyze Cyber Threats'}
            </button>
            <button
              id="btn-paste"
              onClick={pasteFromClipboard}
              className="btn-secondary"
              title="Paste from clipboard"
            >
              📋 Paste
            </button>
            <button id="btn-clear" onClick={clearForm} className="btn-secondary">
              Clear
            </button>
          </div>

          {!loading && error && !results && (
            <div className="error-message" role="alert">
              <div className="error-title">
                <span>⚠️</span> {error.title}
              </div>
              <div className="error-detail">{error.message}</div>
              {error.reason && (
                <div className="error-reason">
                  <strong>Technical Cause:</strong> {error.reason}
                </div>
              )}
            </div>
          )}
        </section>

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

        {loading && (
          <div className="loading-overlay">
            <div className="loader-container">
              <div className="loader-outer"></div>
              <div className="loader-inner"></div>
              <div className="loader-icon">
                {mode === 'fakenews' ? '📰' : '🛡️'}
              </div>
            </div>
            <div className="loading-text">
              <h2>
                {mode === 'fakenews' ? 'Fake News Analysis in Progress' : 'Threat Analysis in Progress'}
              </h2>
              <div className="loading-step">{steps[loadingStep].label}</div>
            </div>
            <div className="loading-progress-container">
              <div
                className="loading-progress-bar"
                style={{ width: `${steps[loadingStep].progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {!loading && results && (
          <section className="results-section" aria-live="polite">
            <div className="results-header">
              <h2>
                {mode === 'fakenews' ? '📰 Fake News Analysis Results' : '🛡️ Cyber Threat Analysis Results'}
              </h2>
              {results.analysis_details.is_comprehensive && (
                <span className="comprehensive-badge">
                  🛡️ Full Comprehensive Analysis Successful
                </span>
              )}
            </div>

            {/* ── FAKE NEWS MODE RESULTS ── */}
            {mode === 'fakenews' && (
              <>
                <div className="results-grid">
                  {/* Fake News Score */}
                  <div className="result-card">
                    <h3>📰 Fake News Probability</h3>
                    <div className="score-display">
                      <span
                        className="score-value"
                        style={{ color: getScoreColor(results.fake_news_probability) }}
                      >
                        {results.fake_news_probability}%
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${results.fake_news_probability}%`,
                          backgroundColor: getScoreColor(results.fake_news_probability)
                        }}
                        role="progressbar"
                        aria-valuenow={results.fake_news_probability}
                        aria-valuemin="0"
                        aria-valuemax="100"
                      />
                    </div>
                    <p className="score-label">
                      {results.fake_news_probability > 70 ? 'High likelihood of misinformation' :
                       results.fake_news_probability > 40 ? 'Some suspicious indicators' :
                       'Appears relatively credible'}
                    </p>
                  </div>

                  {/* Authenticity Score */}
                  <div className="result-card">
                    <h3>✅ Authenticity Score</h3>
                    <div className="score-display">
                      <span
                        className="score-value"
                        style={{ color: getScoreColor(results.authenticity_score, true) }}
                      >
                        {results.authenticity_score}%
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${results.authenticity_score}%`,
                          backgroundColor: getScoreColor(results.authenticity_score, true)
                        }}
                        role="progressbar"
                        aria-valuenow={results.authenticity_score}
                        aria-valuemin="0"
                        aria-valuemax="100"
                      />
                    </div>
                    <p className="score-label">
                      {results.authenticity_score > 70 ? 'High credibility indicators' :
                       results.authenticity_score > 40 ? 'Moderate credibility' :
                       'Low credibility markers'}
                    </p>
                  </div>

                  {/* Originality Score */}
                  <div className="result-card">
                    <h3>📝 Originality Score</h3>
                    <div className="score-display">
                      <span
                        className="score-value"
                        style={{ color: getScoreColor(results.originality_score, true) }}
                      >
                        {results.originality_score}%
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${results.originality_score}%`,
                          backgroundColor: getScoreColor(results.originality_score, true)
                        }}
                        role="progressbar"
                        aria-valuenow={results.originality_score}
                        aria-valuemin="0"
                        aria-valuemax="100"
                      />
                    </div>
                    <p className="score-label">
                      {results.originality_score > 70 ? 'Highly original content' :
                       results.originality_score > 40 ? 'Moderate originality' :
                       'Potentially templated content'}
                    </p>
                  </div>
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

                {/* Fake News Detail Cards */}
                <div className="details-section">
                  <h3>📊 Detailed Analysis</h3>
                  <div className="details-grid">
                    <FactorCard
                      title="Fake News Factors"
                      factors={results.analysis_details.fake_news_factors}
                    />
                    <FactorCard
                      title="Originality Factors"
                      factors={results.analysis_details.originality_factors}
                    />
                  </div>
                </div>
              </>
            )}

            {/* ── CYBER THREAT MODE RESULTS ── */}
            {mode === 'cyberthreat' && (
              <>
                <div className="results-grid">
                  {/* Cyber Threat Score */}
                  <div className="result-card threat-card">
                    <h3>🛡️ Cyber Threat Risk</h3>
                    <div className="score-display">
                      <span
                        className="score-value"
                        style={{ color: getThreatColor(results.threat_level) }}
                      >
                        {results.cyber_threat_risk}%
                      </span>
                      <span
                        className="threat-badge"
                        style={{ backgroundColor: getThreatColor(results.threat_level) }}
                      >
                        {results.threat_level}
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${results.cyber_threat_risk}%`,
                          backgroundColor: getThreatColor(results.threat_level)
                        }}
                        role="progressbar"
                        aria-valuenow={results.cyber_threat_risk}
                        aria-valuemin="0"
                        aria-valuemax="100"
                      />
                    </div>
                    <p className="score-label">
                      {results.threat_level === 'Critical' ? 'Immediate security concern!' :
                       results.threat_level === 'High' ? 'Significant threat indicators' :
                       results.threat_level === 'Medium' ? 'Some suspicious patterns' :
                       'Low security risk'}
                    </p>
                  </div>

                  {/* Authenticity Score — also useful for cyber context */}
                  <div className="result-card">
                    <h3>✅ Content Authenticity</h3>
                    <div className="score-display">
                      <span
                        className="score-value"
                        style={{ color: getScoreColor(results.authenticity_score, true) }}
                      >
                        {results.authenticity_score}%
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${results.authenticity_score}%`,
                          backgroundColor: getScoreColor(results.authenticity_score, true)
                        }}
                        role="progressbar"
                        aria-valuenow={results.authenticity_score}
                        aria-valuemin="0"
                        aria-valuemax="100"
                      />
                    </div>
                    <p className="score-label">
                      {results.authenticity_score > 70 ? 'High credibility indicators' :
                       results.authenticity_score > 40 ? 'Moderate credibility' :
                       'Low credibility — possible deception attempt'}
                    </p>
                  </div>
                </div>

                {/* Cyber Threat Detail Card */}
                <div className="details-section">
                  <h3>📊 Threat Intelligence Breakdown</h3>
                  <div className="details-grid">
                    <FactorCard
                      title="Cyber Threat Factors"
                      factors={results.analysis_details.cyber_threat_factors}
                    />
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

    if (typeof value === 'number') {
      return isPercentage ? `${value}%` : value;
    }

    return value;
  };

  return (
    <div className="factor-card">
      <h4>{title}</h4>

      {explanation && (
        <div className="card-summary">
          <strong>Summary:</strong> {explanation}
        </div>
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
