# Fake News & Cyber Threat Intelligence Analyzer

A production-ready web application that analyzes text content using **Machine Learning + NLP** and outputs **percentage-based confidence scores** across two dedicated analysis interfaces: **Fake News Detection** and **Cyber Threat Intelligence**.

## 🎯 Features

- **Dual-Mode Interface** - Switch between a dedicated Fake News Analysis view and a Cyber Threat Analysis view from a single tab selector.
- **State-of-the-Art ML Model** - Zero-shot classification via `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli`, trained on MNLI + FEVER + ANLI + 30+ NLI datasets.
- **Verified Comprehensive Analysis** - Enforces full verification: ML (DeBERTa) + Google Fact Check + Web verification must all succeed.
- **Fake News Probability (0–100%)** - Hybrid model using deep learning and real-time external verification.
- **Cyber Threat Risk (0–100%)** - Phishing, social engineering, URLhaus malware analysis, and malicious pattern detection.
- **Separated Authenticity Scores** - `news_authenticity_score` (derived from fake news probability) and `cyber_authenticity_score` (derived from cyber threat risk) are computed and displayed independently per mode.
- **Originality Score (0–100%)** - Vocabulary richness, linguistic diversity, and template detection.
- **Animated Donut Charts** - Each score is displayed as an SVG ring chart that animates from 0 on render, with the percentage in the center.
- **Range Markers** - Every score card shows a contextual legend (e.g. 0–30% = Low Risk) with the active range highlighted.
- **Deterministic Result Caching** - MD5-based in-memory caching ensures consistent outcomes for identical inputs within a server session.
- **Google Fact Check API** - Integrated real-time verification against global fact-checking databases.
- **Premium User Experience** - Glassmorphism UI with mode-specific loading steps, "bank-style" success animation, and per-mode color themes (blue/purple for news, orange/red for cyber).

## 🖥️ Interface Modes

The application presents two selectable analysis modes via a tab strip below the header:

| Mode | Tab Color | Scores Shown |
|------|-----------|--------------|
| 📰 **Fake News Analysis** | Blue / Purple | Fake News Probability · News Authenticity · Originality · Web Verification · Detail cards |
| 🛡️ **Cyber Threat Analysis** | Orange / Red | Cyber Threat Risk (with threat-level badge) · Cyber Safety Score · Threat detail card |

Switching modes clears previous results and adapts the placeholder text, URL helper, button label, and loading steps to the selected context.

## 🤖 ML Model

| Property | Value |
|---|---|
| **Model** | `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` |
| **Architecture** | DeBERTa-v3-large (zero-shot NLI) |
| **Training data** | MNLI · FEVER · ANLI · Ling · WaNLI · 30+ NLI datasets |
| **Task** | Zero-shot classification — no domain-specific fake-news bias |
| **Candidate labels** | `"misinformation or fake news"` vs `"credible factual reporting"` |
| **Download size** | ~900 MB (cached locally after first run) |
| **Inference speed** | ~20–40 s on CPU (analysis timeout: 120 s) |

**Why zero-shot NLI?** Fake-news-specific models are trained on narrow datasets (social media clickbait) and develop systematic biases (e.g., flagging real celebrity deaths as fake). A zero-shot NLI model reasons about logical entailment with no domain-specific prior, making it far more robust on real-world news.

## 🏗️ Architecture

```
├── backend/
│   ├── app.py                  # FastAPI main application
│   │                           #   → computes news_authenticity_score & cyber_authenticity_score separately
│   ├── fake_news.py            # HybridFakeNewsAnalyzer (DeBERTa zero-shot + heuristics + NLP)
│   │                           #   + FakeNewsAnalyzer wrapper (web verify + fact check)
│   ├── fact_checker.py         # Google Fact Check API integration
│   ├── web_verifier.py         # Real-time search verification (DuckDuckGo)
│   ├── cyber_threat.py         # Threat intelligence & URLhaus checker
│   ├── originality.py          # Originality & linguistic metrics
│   ├── requirements.txt        # Full dependency list
│   └── .env                    # Environment variables (GOOGLE_FACT_CHECK_KEY)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   │                       #   → ScoreCircle (SVG donut), RangeMarkers, ScoreCard
│   │   │                       #   → Dual-mode tab switcher
│   │   │                       #   → 120 s analysis timeout
│   │   ├── App.css             # Styling (mode tabs, donut charts, range markers)
│   │   └── main.jsx            # Entry point
│   ├── package.json
│   └── vite.config.js
│
└── NLP_ACCURACY_JUSTIFICATION.md
```

## 📋 Prerequisites

### API Access
1. **Google Fact Check API**: Obtain a free API key from the [Google Cloud Console](https://console.cloud.google.com/).
2. **Environment Configuration**: Create a `.env` file in the `backend/` directory:
   ```env
   GOOGLE_FACT_CHECK_KEY=your_api_key_here
   ```

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher
- **npm**: 8.x or higher
- **RAM**: 6 GB recommended (DeBERTa-v3-large is larger than the previous RoBERTa model)
- **Storage**: ~2 GB for dependencies + ML models (model alone ≈ 900 MB)
- **First-run internet**: Required to download the DeBERTa model (~900 MB); cached locally after that

### Operating Systems
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian, etc.)

## 🚀 Installation & Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd fake-news-analyzer
```

### Step 2: Backend Setup

#### 2.1 Create Virtual Environment

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

#### 2.2 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Key dependencies:**
- `fastapi` — Web framework
- `uvicorn` — ASGI server
- `transformers` — DeBERTa-v3-large zero-shot pipeline
- `torch` — PyTorch runtime (CPU)
- `scikit-learn` — Heuristic ML utilities
- `spacy` — NLP (entity recognition, POS tagging)
- `nltk` — Sentiment analysis (VADER)
- `pydantic` — Data validation

#### 2.3 Download NLP Models (Optional but Recommended)

**spaCy English Model:**
```bash
python -m spacy download en_core_web_sm
```

**NLTK Data (auto-downloads on first run, or manually):**
```bash
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('stopwords')"
```

#### 2.4 DuckDuckGo Web Search (Optional)

```bash
pip install duckduckgo-search
```

#### 2.5 Start Backend Server

```bash
python app.py
```

**On first run**, the DeBERTa model (~900 MB) will download automatically and cache locally. Subsequent starts load from cache in ~2 seconds. You will see:

```
[*] Loading Fake News Analyzer...
 Loading MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli...
  Note: first-time download is ~1.4 GB — this may take a few minutes.
model.safetensors: 100%|███| 870M/870M
 DeBERTa-v3-large zero-shot model loaded successfully!
 Web search verification enabled
 Google Fact Check API enabled
 URLhaus malware database connected
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Frontend Setup

Open a **new terminal** (keep backend running):

```bash
cd frontend
npm install
npm run dev
```

### Step 4: Verify Installation

1. Open browser: `http://localhost:3000` (or `http://localhost:5173`)
2. Select a mode using the **tab strip** at the top
3. Paste some text and click **Analyze**
4. Results appear as animated donut charts with range markers

> ⚠️ **First analysis is slow (~40–80 s on CPU)** — the DeBERTa model needs a warm-up pass. Subsequent analyses are faster. The UI timeout is set to **120 seconds**.

### Health Check

```bash
curl http://localhost:8000/health
```

## 📊 Scoring Methodology

### Full Modular Enforcement
The system only returns results when **all three verification modules** succeed:
- ✅ ML (DeBERTa zero-shot)
- ✅ Google Fact Check API
- ✅ DuckDuckGo Web Verifier

If any module fails, the API returns `503 Service Unavailable`.

### Fake News Detection Pipeline
```
Final Score = (DeBERTa × 0.50) + (Heuristics × 0.30) + (NLP × 0.20) ± External Adjustments
```

| Module | Weight | Function |
|--------|--------|----------|
| **DeBERTa-v3-large (zero-shot)** | 50% | NLI-based logical credibility assessment |
| **Heuristics** | 30% | Pattern-based misinformation indicators |
| **NLP** | 20% | Sentiment, punctuation, CAPS analysis |
| **Google Fact Check** | ±20% | Verdict from global fact-checker databases |
| **Web Search** | ±15% | Real-time cross-reference against credible news |

### Authenticity Scores (Separated by Mode)

```
news_authenticity_score  = 100 − fake_news_probability
cyber_authenticity_score = 100 − cyber_threat_risk
```

Each mode shows only its relevant authenticity score:
- 📰 Fake News tab → **News Authenticity** (how credible the content is journalistically)
- 🛡️ Cyber Threat tab → **Cyber Safety Score** (how safe the content is from a threat perspective)

### Score Range Markers

Each score card displays a contextual range legend:

**Fake News Probability**
| Range | Label |
|---|---|
| 0–30% | 🟢 Low Risk — Content appears credible |
| 31–60% | 🟡 Moderate — Some suspicious indicators |
| 61–80% | 🟠 High Risk — Likely misinformation |
| 81–100% | 🔴 Critical — Strong misinformation signals |

**Cyber Threat Risk**
| Range | Label |
|---|---|
| 0–25% | 🟢 Low — No significant threat detected |
| 26–50% | 🟡 Medium — Some suspicious patterns |
| 51–75% | 🟠 High — Multiple threat indicators |
| 76–100% | 🔴 Critical — Immediate security concern |

### Cyber Threat Detection
- URL inspection (suspicious TLDs, IP-literal hosts, redirect chains)
- URLhaus malware domain cross-reference
- Social engineering phrase detection (urgency, credential harvesting)
- Threat level: **Low → Medium → High → Critical**

## 🎓 Academic Justification

### Why DeBERTa over RoBERTa?

| | RoBERTa (previous) | DeBERTa-v3-large (current) |
|---|---|---|
| Task | Text classification | Zero-shot NLI |
| Training data | Narrow clickbait dataset | MNLI + FEVER + ANLI + 30+ datasets |
| Celebrity news bias | High (false flags real events) | None (evaluates logical structure) |
| FEVER (fact verification) | ❌ | ✅ |
| Size | ~500 MB | ~900 MB |

### Performance & Consistency
1. **Zero-shot reasoning** evaluates *how the text is structured logically*, not whether it pattern-matches a training distribution.
2. **Result caching**: MD5-based — same input always returns the same result within a session.
3. **Graceful failures**: Any module timeout returns a detailed error card, never a partial/misleading result.
4. **Temporal coverage**: DeBERTa handles linguistic credibility; Google Fact Check + web search handle current-events verification.

### What the System Can Do

✅ Detect misinformation across politics, health, science, and entertainment  
✅ Identify satire and parody  
✅ Recognize legitimate journalism  
✅ Detect phishing and social engineering patterns  
✅ Provide explainable, mode-specific results  
✅ Handle real-world factual statements (celebrity deaths, historical events, etc.)

### What the System Cannot Do

❌ Real-time knowledge beyond its training cutoff (mitigated by Fact Check + Web APIs)  
❌ Detect sophisticated deepfakes (requires multimedia analysis)  
❌ Guarantee 100% accuracy on highly ambiguous content  

## 🔌 API Documentation

### POST /analyze

```json
// Request
{
  "text": "Article or message content to analyze",
  "url": "https://optional-url-to-check.com"
}

// Response
{
  "fake_news_probability": 12.5,
  "news_authenticity_score": 87.5,
  "cyber_authenticity_score": 95.0,
  "originality_score": 92.0,
  "cyber_threat_risk": 5.0,
  "threat_level": "Low",
  "analysis_details": {
    "fake_news_factors": {
      "ml_probability": 10.2,
      "heuristic_score": 15.0,
      "fact_check_verdict": "TRUE",
      "fact_check_confidence": 95,
      "web_verification": "Verified by 4 credible sources",
      "credible_sources_found": 4
    },
    "originality_factors": { "...": "..." },
    "cyber_threat_factors": { "...": "..." },
    "cached": false,
    "is_comprehensive": true
  }
}
```

### Error Handling
- **503 Service Unavailable** — One or more verification modules (ML, Fact Check, Web Verifier) failed. Ensures only fully-verified results are shown.
- **400 Bad Request** — Text too short (< 10 characters).

### GET /health

```json
{
  "status": "healthy",
  "services": {
    "fake_news_analyzer": "ready",
    "originality_analyzer": "ready",
    "cyber_threat_analyzer": "ready"
  }
}
```

## 🔒 Security Considerations

- ✅ Input sanitization on all endpoints
- ✅ CORS configured for frontend origin only
- ✅ No sensitive data storage
- ✅ URL validation before analysis
- ✅ Rate limiting ready (can be enabled)
- ✅ Error handling prevents information leakage

## 🗺️ Roadmap

- [x] Deep learning models — DeBERTa-v3-large (MNLI + FEVER + ANLI)
- [x] Zero-shot NLI — no domain-specific training bias
- [x] Dual-mode interface (Fake News & Cyber Threat tabs)
- [x] Separated authenticity scores per mode
- [x] Animated SVG donut charts with percentage in center
- [x] Range marker legends (active range highlighted)
- [x] MD5 deterministic caching
- [x] "Bank-style" success animation & per-mode color themes
- [x] Detailed "Why It Failed" error reporting
- [ ] GPU acceleration support (CUDA)
- [ ] External fact-checking (Snopes, PolitiFact)
- [ ] Multi-language support (Spanish, French, Arabic)
- [ ] Real-time social media monitoring
- [ ] Browser extension for on-the-fly analysis
- [ ] Analysis history and trends dashboard
- [ ] API rate limiting and authentication

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Analysis times out every time  
**Solution**: The DeBERTa-v3-large model is slow on CPU. The UI timeout is 120 seconds. If it still times out:
- Submit shorter text (system auto-truncates to 15,000 chars; ML uses first 512 chars)
- Ensure no other heavy processes are consuming CPU
- Consider switching to the base model (faster, ~200 MB)

**Problem**: `ModuleNotFoundError: No module named 'transformers'` or `torch`  
**Solution**:
```bash
pip install transformers torch
```

**Problem**: `ModuleNotFoundError: No module named 'ddgs'`  
**Solution**:
```bash
pip install duckduckgo-search
```

**Problem**: Model download stalls at 0%  
**Solution**: Hugging Face can throttle unauthenticated downloads. Options:
1. Wait — `?B/s` at t=0 is normal; speed appears after ~20 seconds
2. Set a HuggingFace token for higher rate limits: `$env:HF_TOKEN="your_token"`
3. Pre-download manually: `huggingface-cli download MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli`

**Problem**: `deberta.embeddings.position_ids | UNEXPECTED` warning  
**Solution**: Safe to ignore. This is an architectural mismatch warning when loading a sequence-classification checkpoint into a zero-shot pipeline. It does not affect accuracy.

**Problem**: Backend won't start on port 8000  
**Solution**: Change port in `app.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Frontend Issues

**Problem**: `npm install` fails  
**Solution**:
```bash
npm cache clean --force
npm install
```

**Problem**: CORS errors in browser console  
**Solution**: Ensure backend is running and CORS is configured in `app.py`

**Problem**: Results show `undefined` for authenticity scores  
**Solution**: The backend was not restarted after the score fields were renamed. Restart `python app.py` and clear the browser cache.

### NLP Model Issues

**Problem**: "spaCy model not found" warning  
**Solution**: Optional — system works without it:
```bash
python -m spacy download en_core_web_sm
```

**Problem**: Slow analysis (> 60 seconds)  
**Solution**:
- Normal on first analysis (model warm-up)
- Reduce text length
- Ensure venv is active and no conflicting torch versions are installed
