# Fake News & CyberThreats Analyzer Changelog

All notable changes to this project will be documented in this file.

## [2026-03-05]
### Changed
- **`frontend/src/App.jsx`**: (Lines 161-165, 193-196, 434-475) Redesigned the "Detailed Analysis" and "Threat Intelligence Breakdown" UI sections into collapsible accordions to massively reduce vertical footprint. Defaults to closed state on new analysis.
- **`backend/fact_checker.py`**: (Lines 1-85) Completely rewrote the fact checker module. Deprecated the brittle Google Fact Check API and replaced it with a Zero-Shot LLM Agent using Groq and the `llama-3.3-70b-versatile` model. Enforced strict JSON response format to extract TRUE/FALSE/UNVERIFIED verdicts directly from the LLM's vast pre-training data.
- **`backend/fake_news.py`**: (Lines 532-547) Reconfigured the AI initialization block to mount the new `FactChecker` using `GROQ_API_KEY` rather than `GOOGLE_FACT_CHECK_KEY`.
- **`backend/fake_news.py`**: (Lines 652-669) Combined the new AI reasoning outputs with the zero-shot fact-checker explanations inside the main analysis loop so both text blocks render natively inside the frontend's "Explainable AI" card. Removed the redundant `fact_check_explanation` from the JSON return map.
- **`backend/fake_news.py`**: (Lines 96-146) Massively expanded the rules-based string matching dictionaries inside `_initialize_patterns`. Added over 75+ modern terms related to absurd sci-fi plots, dark-web conspiracy theories (e.g., adrenochrome, QAnon), health pseudoscience, and clickbait to greatly improve baseline heuristic accuracy when the AI models are unsure.

- **`backend/cyber_threat.py`**: (Lines 83-176) Implemented approach #1: integrated a Zero-Shot Contextual AI Threat Engine using Groq (llama-3.1-8b-instant). If the AI detects sophisticated social engineering that bypasses legacy regex filters, it now dynamically boosts the total isk_score and populates the i_threat_analysis factor with a detailed reasoning string for the UI.

- **\ackend/requirements.txt\**: Added \groq\ and \openai\ dependencies to support the new Contextual NLP verifier and Zero-Shot fact checker modules. Marked \google-generativeai\ as deprecated.
