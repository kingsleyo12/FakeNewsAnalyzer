# Fake News & CyberThreats Analyzer Changelog

All notable changes to this project will be documented in this file.

## [2026-03-12]
### Added & Improved
- **Adversarial Robustness**: Implemented chunking in `fake_news.py` to evaluate the text against Zero-Shot models incrementally, defending against Dilution Evasion.
- **Input Sanitization**: Added strict input validation in `backend/app.py` `AnalysisRequest` model to block basic Cross-Site Scripting (XSS) and script injection vectors.
- **Performance Metrics**: Exposed the total processing latency as an explicit factor rendered in the newly integrated "Performance Evaluation Terminal" user interface (`frontend/src/App.css`, `frontend/src/App.jsx`).
- **Threat Intelligence**: Significantly expanded domain regex, cyber threat pattern matching, and suspicious TLD lists in `cyber_threat.py` for increased accuracy.
- **Simplified Logging**: Cleaned up system logs by extracting verbose network exceptions (`backend/app.py`, `backend/urlhaus_checker.py`). Simplified the test suite console printouts to use `[SYSTEM]`/`[OK]` tags instead of UTF-8 emojis (`backend/system_test_suite.py`) preventing rendering errors.
### Fixed & Improved
- **Service Resilience**: Implemented specific exception handling for `NameResolutionError` and `getaddrinfo` failures across `urlhaus_checker.py`, `artificial_verifier.py`, and `fact_checker.py`. The system now fails gracefully with diagnostic messages instead of crashing when external APIs are unreachable.
- **`backend/urlhaus_checker.py`**: Added explicit blocks for `requests.exceptions.ConnectionError` and `Timeout` to provide cleaner UI feedback.
- **`backend/cyber_threat.py`**: Cleaned up redundant error logging to prevent console pollution.
- **`backend/system_test_suite.py`**: Resolved `UnicodeEncodeError` on Windows by stripping emojis and explicitly setting UTF-8 encoding for the test runner.
- **`backend/fact_checker.py`**: Truncated raw exception strings in the UI to prevent overwhelming the user with technical details during API failures.
- **`backend/app.py`**: Configured `logging.FileHandler` to ensure all API transactions and errors are persisted to `backend_service.log` for debugging and audit purposes.
- **`frontend/src/App.css`**: Restricted the `textarea` element by setting `resize: none;` to lock its dimensions and maintain the interface layout.
- **`backend/cyber_threat.py`**: Massively expanded the heuristic dictionaries for all categories (Phishing, Social Engineering, Urgency, Credentials, Malware, and Dark Web) with over 150+ new keywords and regex patterns to significantly increase threat detection sensitivity. Renamed the `ai_threat_analysis` factor to `explainable_ai` to align with project terminology.

## [2026-03-05] (Update 1)
### Changed
- **`frontend/src/App.jsx`**: (Lines 161-165, 193-196, 434-475) Redesigned the "Detailed Analysis" and "Threat Intelligence Breakdown" UI sections into collapsible accordions to massively reduce vertical footprint. Defaults to closed state on new analysis.
- **`backend/fact_checker.py`**: (Lines 1-85) Completely rewrote the fact checker module. Deprecated the brittle Google Fact Check API and replaced it with a Zero-Shot LLM Agent using Groq and the `llama-3.3-70b-versatile` model. Enforced strict JSON response format to extract TRUE/FALSE/UNVERIFIED verdicts directly from the LLM's vast pre-training data.
- **`backend/fake_news.py`**: (Lines 532-547) Reconfigured the AI initialization block to mount the new `FactChecker` using `GROQ_API_KEY` rather than `GOOGLE_FACT_CHECK_KEY`.
- **`backend/fake_news.py`**: (Lines 652-669) Combined the new AI reasoning outputs with the zero-shot fact-checker explanations inside the main analysis loop so both text blocks render natively inside the frontend's "Explainable AI" card. Removed the redundant `fact_check_explanation` from the JSON return map.
- **`backend/fake_news.py`**: (Lines 96-146) Massively expanded the rules-based string matching dictionaries inside `_initialize_patterns`. Added over 75+ modern terms related to absurd sci-fi plots, dark-web conspiracy theories (e.g., adrenochrome, QAnon), health pseudoscience, and clickbait to greatly improve baseline heuristic accuracy when the AI models are unsure.
- **`backend/cyber_threat.py`**: (Lines 83-176) Implemented approach #1: integrated a Zero-Shot Contextual AI Threat Engine using Groq (llama-3.1-8b-instant). If the AI detects sophisticated social engineering that bypasses legacy regex filters, it now dynamically boosts the total risk_score and populates the ai_threat_analysis factor with a detailed reasoning string for the UI.
- **`backend/requirements.txt`**: Added dependencies to support the new Contextual NLP verifier and Zero-Shot fact checker modules. Marked google-generativeai as deprecated.
