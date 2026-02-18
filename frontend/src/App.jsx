import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyzeContent = async () => {
    if (text.trim().length < 10) {
      setError('Please enter at least 10 characters of text to analyze.');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      // Truncate very long texts to prevent timeout (keep first 15000 chars)
      let analysisText = text.trim();
      if (analysisText.length > 15000) {
        analysisText = analysisText.substring(0, 15000);
      }
      
      const response = await axios.post(`${API_URL}/analyze`, {
        text: analysisText,
        url: url.trim() || null
      }, {
        timeout: 30000 // 30 second timeout
      });
      setResults(response.data);
    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        setError('Analysis timed out. Try with shorter text.');
      } else {
        setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setText('');
    setUrl('');
    setResults(null);
    setError('');
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

      <main className="main-content">
        <section className="input-section">
          <div className="input-group">
            <label htmlFor="text-input">Content to Analyze</label>
            <textarea
              id="text-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste news article, social media post, or suspicious message here..."
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
            <small id="url-help">Enter a URL to analyze for phishing indicators</small>
          </div>

          <div className="button-group">
            <button 
              onClick={analyzeContent} 
              disabled={loading}
              className="btn-primary"
              aria-busy={loading}
            >
              {loading ? 'Analyzing...' : 'Analyze Content'}
            </button>
            <button onClick={clearForm} className="btn-secondary">
              Clear
            </button>
          </div>

          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}
        </section>

        {results && (
          <section className="results-section" aria-live="polite">
            <h2>Analysis Results</h2>
            
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
            </div>

            {/* Web Verification Section - NEW! */}
            {results.analysis_details.fake_news_factors.web_verification && (
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

            {/* Detailed Analysis */}
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
                <FactorCard 
                  title="Cyber Threat Factors"
                  factors={results.analysis_details.cyber_threat_factors}
                />
              </div>
            </div>
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
  return (
    <div className="factor-card">
      <h4>{title}</h4>
      <ul>
        {Object.entries(factors).map(([key, value]) => {
          if (key === 'explanation' || key === 'detected_threats') {
            return (
              <li key={key} className="explanation">
                <strong>{key === 'explanation' ? 'Summary' : 'Threats'}:</strong> {
                  Array.isArray(value) ? value.join(', ') : value
                }
              </li>
            );
          }
          return (
            <li key={key}>
              <span className="factor-name">{key.replace(/_/g, ' ')}:</span>
              <span className="factor-value">{typeof value === 'number' ? `${value}%` : value}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default App;
