"""
=============================================================
 Fake News Analyzer — Comprehensive Test Suite
=============================================================
Run: pytest tests/test_suite.py -v
     pytest tests/test_suite.py -v --tb=short   (shorter tracebacks)

Covers:
  - OriginalityAnalyzer
  - CyberThreatAnalyzer  (+ URL analysis)
  - URLhausChecker
  - HybridFakeNewsAnalyzer / FakeNewsAnalyzer
  - FactChecker  (heuristic layer only — no live API calls)
  - WebSearchVerifier  (mocked — no live network calls)
  - FastAPI /analyze endpoint  (integration)
"""

import sys
import os
import re
import pytest
from unittest.mock import patch, MagicMock

# ── ensure backend/ is on the path ──────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════════════════
#  FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def originality_analyzer():
    from originality import OriginalityAnalyzer
    return OriginalityAnalyzer()


@pytest.fixture(scope="module")
def cyber_analyzer():
    from cyber_threat import CyberThreatAnalyzer
    return CyberThreatAnalyzer()


@pytest.fixture(scope="module")
def urlhaus_checker():
    from urlhaus_checker import URLhausChecker
    return URLhausChecker()


@pytest.fixture(scope="module")
def fact_checker():
    """FactChecker with a dummy API key — tests only the heuristic layer."""
    from fact_checker import FactChecker
    return FactChecker(api_key="TEST_KEY_HEURISTIC_ONLY")


@pytest.fixture(scope="module")
def hybrid_analyzer():
    """HybridFakeNewsAnalyzer — ML model loaded from cache if available."""
    from fake_news import HybridFakeNewsAnalyzer
    return HybridFakeNewsAnalyzer()


# ═══════════════════════════════════════════════════════════════════════════
#  1. ORIGINALITY ANALYZER
# ═══════════════════════════════════════════════════════════════════════════

class TestOriginalityAnalyzer:

    def test_returns_required_keys(self, originality_analyzer):
        result = originality_analyzer.analyze("The quick brown fox jumps over the lazy dog.")
        assert "score" in result
        assert "factors" in result

    def test_score_in_range(self, originality_analyzer):
        texts = [
            "Breaking news! Scientists confirm moon is made of cheese! Share before deleted!",
            "According to a peer-reviewed study published in Nature, climate change is accelerating.",
            "They don't want you to know. Wake up people. Do your own research. Connect the dots.",
        ]
        for text in texts:
            result = originality_analyzer.analyze(text)
            assert 0 <= result["score"] <= 100, f"Score out of range for: {text[:40]}"

    def test_template_phrases_lower_score(self, originality_analyzer):
        """Texts with fake-news template phrases should score lower than clean journalism."""
        fake_text = (
            "They dont want you to know the truth. Wake up people and do your own research. "
            "Mainstream media wont tell you what they dont want exposed. Connect the dots!"
        )
        legit_text = (
            "According to a study published in The Lancet, researchers confirmed that the "
            "new vaccine showed 94% efficacy across all demographic groups tested. "
            "The findings were independently verified by three separate institutions."
        )
        fake_score = originality_analyzer.analyze(fake_text)["score"]
        legit_score = originality_analyzer.analyze(legit_text)["score"]
        assert fake_score < legit_score, (
            f"Expected fake score ({fake_score:.1f}) < legit score ({legit_score:.1f})"
        )

    def test_short_text_returns_neutral(self, originality_analyzer):
        """Very short texts should not crash and return a valid score."""
        result = originality_analyzer.analyze("Hello world.")
        assert 0 <= result["score"] <= 100

    def test_rich_vocabulary_detected(self, originality_analyzer):
        rich_text = (
            "Quantum entanglement demonstrates non-local correlations that challenge classical "
            "electrodynamics. Photoelectric phenomena corroborate wave-particle duality through "
            "empirical observation, substantiating Bohr correspondence principles."
        )
        result = originality_analyzer.analyze(rich_text)
        assert result["factors"]["vocabulary_richness"] > 50

    def test_repetitive_text_low_phrase_uniqueness(self, originality_analyzer):
        reps = "the cat sat on the mat " * 20
        result = originality_analyzer.analyze(reps)
        assert result["factors"]["phrase_uniqueness"] < 50

    def test_factors_all_present(self, originality_analyzer):
        result = originality_analyzer.analyze("Some normal news text about the economy today.")
        for key in ["vocabulary_richness", "phrase_uniqueness", "structural_variety",
                    "information_density", "template_penalty", "explanation"]:
            assert key in result["factors"], f"Missing factor: {key}"


# ═══════════════════════════════════════════════════════════════════════════
#  2. CYBER THREAT ANALYZER
# ═══════════════════════════════════════════════════════════════════════════

class TestCyberThreatAnalyzer:

    def test_clean_news_low_risk(self, cyber_analyzer):
        text = "The Federal Reserve raised interest rates by 25 basis points today."
        result = cyber_analyzer.analyze(text)
        assert result["risk_score"] < 30
        assert result["threat_level"] in ("Low", "Medium")

    def test_phishing_text_high_risk(self, cyber_analyzer):
        text = (
            "URGENT: Your bank account has been suspended due to unauthorized access. "
            "Verify your account immediately by clicking here and entering your password "
            "and credit card details. Failure to act within 24 hours will result in closure."
        )
        result = cyber_analyzer.analyze(text)
        assert result["risk_score"] >= 50
        assert result["threat_level"] in ("High", "Critical")

    def test_crypto_scam_detected(self, cyber_analyzer):
        text = "Send 1 BTC to this wallet address and get guaranteed returns of 200%! Crypto giveaway!"
        result = cyber_analyzer.analyze(text)
        assert result["risk_score"] > 20
        detected = result["factors"]["detected_threats"]
        assert any("scam" in t.lower() or "malware" in t.lower() for t in detected)

    def test_phishing_indicators_in_factors(self, cyber_analyzer):
        text = "Verify your account now. Click here to update your information. Act now!"
        result = cyber_analyzer.analyze(text)
        assert result["factors"]["phishing_indicators"] > 0

    def test_suspicious_url_raises_score(self, cyber_analyzer):
        text = "Click: http://192.168.1.1/login/verify"
        result = cyber_analyzer.analyze(text, url="http://192.168.1.1/login/verify")
        assert result["factors"]["url_risk_score"] > 30

    def test_trusted_domain_reduces_url_score(self, cyber_analyzer):
        result = cyber_analyzer.analyze("More details at https://microsoft.com",
                                         url="https://microsoft.com")
        assert result["factors"]["url_risk_score"] < 40

    def test_typosquatting_detected(self, cyber_analyzer):
        result = cyber_analyzer.analyze("Visit http://g00gle.com for more info",
                                         url="http://g00gle.com")
        assert result["factors"]["url_risk_score"] > 30

    def test_suspicious_tld_raises_url_score(self, cyber_analyzer):
        result = cyber_analyzer.analyze("Check http://verify-account.xyz",
                                         url="http://verify-account.xyz")
        assert result["factors"]["url_risk_score"] > 20

    def test_dark_web_terms_detected(self, cyber_analyzer):
        text = "The ransomware uses a botnet with a keylogger and rootkit component."
        result = cyber_analyzer.analyze(text)
        assert result["factors"]["malware_patterns"] > 0

    def test_no_url_zero_url_score(self, cyber_analyzer):
        text = "This is a plain text article with no links."
        result = cyber_analyzer.analyze(text)
        assert result["factors"]["url_risk_score"] == 0

    def test_threat_level_thresholds(self, cyber_analyzer):
        """Confirm threat_level labels match score thresholds."""
        from cyber_threat import CyberThreatAnalyzer
        ct = CyberThreatAnalyzer()
        assert ct._get_threat_level(10) == "Low"
        assert ct._get_threat_level(30) == "Medium"
        assert ct._get_threat_level(60) == "High"
        assert ct._get_threat_level(80) == "Critical"

    def test_multiple_threats_bonus(self, cyber_analyzer):
        """Multiple active threat types should compound the final score."""
        single_text = "Verify your account immediately."
        multi_text = (
            "URGENT: Your bank account is suspended. Verify your account immediately! "
            "Enter your password and credit card now. Click here: http://fake-bank.xyz "
            "Failure to respond within 24 hours will delete your account."
        )
        single_score = cyber_analyzer.analyze(single_text)["risk_score"]
        multi_score = cyber_analyzer.analyze(multi_text)["risk_score"]
        assert multi_score >= single_score

    def test_result_schema(self, cyber_analyzer):
        result = cyber_analyzer.analyze("Normal article text.")
        assert "risk_score" in result
        assert "threat_level" in result
        assert "factors" in result
        for key in ["phishing_indicators", "social_engineering_score", "urgency_pressure_score",
                    "credential_harvesting_risk", "url_risk_score", "malware_patterns",
                    "detected_threats", "explanation"]:
            assert key in result["factors"], f"Missing factor key: {key}"


# ═══════════════════════════════════════════════════════════════════════════
#  3. URLHAUS CHECKER
# ═══════════════════════════════════════════════════════════════════════════

class TestURLhausChecker:

    def test_no_urls_in_text(self, urlhaus_checker):
        result = urlhaus_checker.extract_and_check("This text has no links at all.")
        assert result["urls_found"] == 0
        assert result["risk_score"] == 0

    def test_url_extraction_from_text(self, urlhaus_checker):
        text = "Check https://example.com and http://test.org for details."
        result = urlhaus_checker.extract_and_check(text)
        assert result["urls_found"] == 2

    @patch("urlhaus_checker.requests.post")
    def test_malicious_url_detected(self, mock_post, urlhaus_checker):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"query_status": "is_malware", "threat": "malware_download", "tags": ["trojan"]}
        )
        result = urlhaus_checker.check_url("http://evil-malware-site.tk/payload.exe")
        assert result["is_malicious"] is True
        assert result["risk_score"] == 95

    @patch("urlhaus_checker.requests.post")
    def test_clean_url_no_results(self, mock_post, urlhaus_checker):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"query_status": "no_results"}
        )
        result = urlhaus_checker.check_url("https://reuters.com")
        assert result["is_malicious"] is False
        assert result["risk_score"] == 0

    @patch("urlhaus_checker.requests.post", side_effect=Exception("Network error"))
    def test_network_failure_graceful(self, mock_post, urlhaus_checker):
        result = urlhaus_checker.check_url("https://example.com")
        assert result["is_malicious"] is False
        assert result["risk_score"] == 0

    @patch("urlhaus_checker.requests.post")
    def test_extract_and_check_malicious(self, mock_post, urlhaus_checker):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"query_status": "is_malware", "threat": "phishing", "tags": []}
        )
        result = urlhaus_checker.extract_and_check(
            "Download the update: http://malware-host.xyz/update.exe"
        )
        assert result["malicious_urls"] >= 1
        assert result["risk_score"] == 95


# ═══════════════════════════════════════════════════════════════════════════
#  4. HYBRID FAKE NEWS ANALYZER (heuristic layer — no ML needed)
# ═══════════════════════════════════════════════════════════════════════════

class TestHybridFakeNewsAnalyzer:

    def test_returns_required_keys(self, hybrid_analyzer):
        result = hybrid_analyzer.analyze("Scientists have found new evidence about climate change.")
        for key in ["fake_news_probability", "authenticity_score", "components", "factors", "explanation"]:
            assert key in result, f"Missing key: {key}"

    def test_score_in_range(self, hybrid_analyzer):
        texts = [
            "According to Reuters, the economy grew by 2.5% this quarter.",
            "SHOCKING! Big Pharma doesn't want you to know this miracle cure!",
            "Scientists discover hand-clapping cures cancer! Share before deleted!",
            "The President signed a new executive order on climate policy today.",
        ]
        for text in texts:
            result = hybrid_analyzer.analyze(text)
            assert 0 <= result["fake_news_probability"] <= 100
            assert 0 <= result["authenticity_score"] <= 100

    def test_fake_indicators_raise_score(self, hybrid_analyzer):
        """Strong conspiracy text should score higher than credible journalism."""
        fake_text = (
            "They don't want you to know! Big Pharma is hiding the cure! "
            "Deep state conspiracy! Wake up! Government coverup! Illuminati exposed!"
        )
        real_text = (
            "According to a peer-reviewed study published in Nature, researchers from "
            "Harvard University confirmed the findings through independent replication."
        )
        fake_score = hybrid_analyzer.analyze(fake_text)["fake_news_probability"]
        real_score = hybrid_analyzer.analyze(real_text)["fake_news_probability"]
        assert fake_score > real_score, (
            f"Expected fake ({fake_score:.1f}) > real ({real_score:.1f})"
        )

    def test_credible_sources_reduce_score(self, hybrid_analyzer):
        text = (
            "According to Reuters, peer-reviewed research from Harvard confirmed "
            "through official statement and press release that data shows positive results."
        )
        result = hybrid_analyzer.analyze(text)
        assert result["fake_news_probability"] < 70

    def test_authenticity_is_complement(self, hybrid_analyzer):
        text = "Breaking news from the BBC about the latest economic figures."
        result = hybrid_analyzer.analyze(text)
        expected = round(100 - result["fake_news_probability"], 1)
        assert abs(result["authenticity_score"] - expected) < 0.2

    def test_short_text_returns_error(self, hybrid_analyzer):
        result = hybrid_analyzer.analyze("Hi")
        assert "error" in result

    def test_pseudoscience_detected(self, hybrid_analyzer):
        text = "Quantum healing through chakra energy vibration and crystal aura detox."
        result = hybrid_analyzer.analyze(text)
        assert result["factors"]["absurdity_score"] > 0

    def test_clickbait_detected(self, hybrid_analyzer):
        text = "You won't believe what happens next! This one trick will shock you! Going viral!"
        result = hybrid_analyzer.analyze(text)
        assert result["factors"]["clickbait_score"] > 0

    def test_explanation_is_string(self, hybrid_analyzer):
        result = hybrid_analyzer.analyze("The government announced new trade policies.")
        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 0


# ═══════════════════════════════════════════════════════════════════════════
#  5. FACT CHECKER (heuristic + mocked API)
# ═══════════════════════════════════════════════════════════════════════════

class TestFactChecker:

    def test_known_false_claim_vaccines_autism(self, fact_checker):
        result = fact_checker.check_claims("Vaccines cause autism in children, proven fact.")
        assert result["verdict"] == "FALSE"
        assert result["confidence"] >= 90

    def test_known_false_claim_flat_earth(self, fact_checker):
        result = fact_checker.check_claims("The flat earth society has proven the earth is flat.")
        assert result["verdict"] == "FALSE"

    def test_known_false_claim_5g_covid(self, fact_checker):
        result = fact_checker.check_claims("5G towers cause COVID-19 disease in people.")
        assert result["verdict"] == "FALSE"

    def test_known_false_claim_moon_landing(self, fact_checker):
        result = fact_checker.check_claims("The moon landing was faked by NASA in a studio.")
        assert result["verdict"] == "FALSE"

    def test_known_false_microchip_vaccines(self, fact_checker):
        result = fact_checker.check_claims("Bill Gates puts microchips in vaccines to track people.")
        assert result["verdict"] == "FALSE"

    @patch("fact_checker.requests.get")
    def test_api_returns_false_verdict(self, mock_get, fact_checker):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "claims": [{
                    "text": "test claim",
                    "claimReview": [{
                        "textualRating": "FALSE",
                        "publisher": {"name": "PolitiFact"},
                        "title": "This is false",
                        "url": "https://politifact.com/test"
                    }]
                }]
            }
        )
        result = fact_checker.check_claims(
            "Scientists discovered that drinking water is harmful to health."
        )
        assert result["verdict"] == "FALSE"
        assert result["fact_checks_found"] >= 1

    @patch("fact_checker.requests.get")
    def test_api_returns_true_verdict(self, mock_get, fact_checker):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "claims": [{
                    "text": "test claim",
                    "claimReview": [{
                        "textualRating": "TRUE",
                        "publisher": {"name": "Snopes"},
                        "title": "This is true",
                        "url": "https://snopes.com/test"
                    }]
                }]
            }
        )
        result = fact_checker.check_claims(
            "According to researchers, the Earth orbits the Sun."
        )
        assert result["verdict"] == "TRUE"

    @patch("fact_checker.requests.get")
    def test_api_no_results_returns_unverified(self, mock_get, fact_checker):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"claims": []}
        )
        result = fact_checker.check_claims(
            "The Bayelsa State Police Command arrested five suspects today."
        )
        assert result["verdict"] == "UNVERIFIED"

    @patch("fact_checker.requests.get")
    def test_api_403_handled_gracefully(self, mock_get, fact_checker):
        mock_get.return_value = MagicMock(status_code=403)
        # Should not raise — should return UNVERIFIED
        result = fact_checker.check_claims("Some claim that might not be in the database.")
        assert result["verdict"] in ("UNVERIFIED", "FALSE", "TRUE", "MIXED")

    def test_extract_claims_short_query(self, fact_checker):
        """_clean_claim should produce ≤ 8 words."""
        claim = fact_checker._clean_claim(
            "According to scientists at Harvard researchers have discovered new evidence for climate"
        )
        assert claim is not None
        assert len(claim.split()) <= 8

    def test_no_claim_in_text(self, fact_checker):
        result = fact_checker.check_claims("OK.")  # too short for any claim
        assert result["verdict"] in ("UNVERIFIED",)

    def test_decimal_not_split(self, fact_checker):
        """Sentences like '5.25%' should not be split into two claims."""
        claims = fact_checker._extract_claims(
            "The Bank of England raised interest rates to 5.25% to combat inflation today."
        )
        # "5" alone should NOT appear as a standalone claim
        for c in claims:
            assert c.strip() != "5", f"Decimal was split incorrectly, got claim: '{c}'"


# ═══════════════════════════════════════════════════════════════════════════
#  6. WEB SEARCH VERIFIER (fully mocked — no network calls)
# ═══════════════════════════════════════════════════════════════════════════

class TestWebSearchVerifier:

    @pytest.fixture(autouse=True)
    def verifier(self):
        from web_verifier import WebSearchVerifier
        self.v = WebSearchVerifier()

    def _mock_results(self, urls):
        return [{"title": "Test", "url": u, "snippet": "test snippet"} for u in urls]

    def test_no_claims_returns_neutral(self):
        """Empty/un-claimable text should return score_adjustment = 0."""
        result = self.v.verify_claims("Ok.")
        assert result["score_adjustment"] == 0

    @patch.object(__import__('web_verifier', fromlist=['WebSearchVerifier']).WebSearchVerifier,
                  '_search_claim')
    def test_credible_sources_reduce_fake_score(self, mock_search):
        mock_search.return_value = self._mock_results([
            "https://reuters.com/article/1",
            "https://bbc.com/news/2",
            "https://apnews.com/3",
        ])
        result = self.v.verify_claims(
            "According to Reuters, researchers confirmed new climate findings."
        )
        assert result["score_adjustment"] < 0  # credible sources → lower fake score
        assert result["credible_sources_found"] >= 3

    @patch.object(__import__('web_verifier', fromlist=['WebSearchVerifier']).WebSearchVerifier,
                  '_search_claim')
    def test_no_results_slight_increase(self, mock_search):
        mock_search.return_value = []
        result = self.v.verify_claims(
            "Scientists confirm that blinking causes climate change."
        )
        assert result["score_adjustment"] >= 0

    @patch.object(__import__('web_verifier', fromlist=['WebSearchVerifier']).WebSearchVerifier,
                  '_search_claim')
    def test_debunked_article_raises_score(self, mock_search):
        mock_search.return_value = self._mock_results(["https://snopes.com/fact-check/xyz"])
        # Make the snippet contain debunk keywords
        mock_search.return_value[0]["title"] = "FALSE: This claim is debunked misinformation"
        result = self.v.verify_claims("Vaccines cause autism confirmed by new study.")
        assert result["score_adjustment"] > 0

    def test_is_credible_source(self):
        assert self.v._is_credible_source("https://reuters.com/article")
        assert self.v._is_credible_source("https://bbc.co.uk/news")
        assert not self.v._is_credible_source("https://random-blog.xyz/article")

    def test_is_fact_check_source(self):
        assert self.v._is_fact_check_source("https://snopes.com/fact-check/something")
        assert self.v._is_fact_check_source("https://politifact.com/truth-o-meter")
        assert not self.v._is_fact_check_source("https://cnn.com/news")

    def test_is_debunked_keywords(self):
        assert self.v._is_debunked("FACT CHECK: FALSE claim about vaccines", "")
        assert self.v._is_debunked("", "This story is debunked misinformation")
        assert not self.v._is_debunked("Scientists make new discovery", "Positive results confirmed")

    def test_ddg_rate_limit_retry(self):
        """DuckDuckGo fallback should retry then give up, not crash."""
        with patch.object(self.v, 'serper_api_key', ''), \
             patch.object(self.v, 'brave_api_key', ''):
            with patch('web_verifier.DDGS') as MockDDGS:
                instance = MockDDGS.return_value.__enter__.return_value
                instance.text.side_effect = Exception("Ratelimit")
                results = self.v._search_duckduckgo("test claim", retries=2)
                assert results == []


# ═══════════════════════════════════════════════════════════════════════════
#  7. FASTAPI INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestAPIEndpoints:

    @pytest.fixture(scope="class")
    def client(self):
        from fastapi.testclient import TestClient
        from app import app
        return TestClient(app)

    def test_root_health_check(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data

    def test_analyze_returns_200_for_valid_text(self, client):
        response = client.post("/analyze", json={
            "text": "According to BBC, the Bank of England raised interest rates today."
        })
        assert response.status_code == 200

    def test_analyze_response_schema(self, client):
        response = client.post("/analyze", json={
            "text": "The president signed a new trade deal with several countries this week."
        })
        assert response.status_code == 200
        data = response.json()
        for field in ["fake_news_probability", "news_authenticity_score",
                       "cyber_authenticity_score", "originality_score",
                       "cyber_threat_risk", "threat_level", "analysis_details"]:
            assert field in data, f"Missing field: {field}"

    def test_scores_in_valid_range(self, client):
        response = client.post("/analyze", json={
            "text": "Reuters reports that global markets experienced volatility amid economic uncertainty."
        })
        data = response.json()
        assert 0 <= data["fake_news_probability"] <= 100
        assert 0 <= data["news_authenticity_score"] <= 100
        assert 0 <= data["cyber_authenticity_score"] <= 100
        assert 0 <= data["originality_score"] <= 100
        assert 0 <= data["cyber_threat_risk"] <= 100

    def test_authenticity_complements_fake_prob(self, client):
        response = client.post("/analyze", json={
            "text": "Scientists at MIT published new findings on renewable energy storage solutions."
        })
        data = response.json()
        expected = round(100 - data["fake_news_probability"], 1)
        assert abs(data["news_authenticity_score"] - expected) < 0.5

    def test_cyber_authenticity_complements_threat(self, client):
        response = client.post("/analyze", json={
            "text": "Visit our website for the latest technology news and updates."
        })
        data = response.json()
        expected = round(100 - data["cyber_threat_risk"], 1)
        assert abs(data["cyber_authenticity_score"] - expected) < 0.5

    def test_phishing_text_high_threat(self, client):
        response = client.post("/analyze", json={
            "text": (
                "URGENT: Your account is suspended! Verify your credentials immediately. "
                "Click here: http://fake-bank-login.xyz and enter your password and credit card."
            )
        })
        data = response.json()
        assert data["cyber_threat_risk"] >= 50
        assert data["threat_level"] in ("High", "Critical")

    def test_text_too_short_returns_422(self, client):
        response = client.post("/analyze", json={"text": "Hi"})
        assert response.status_code == 422  # Pydantic validation

    def test_missing_text_field_returns_422(self, client):
        response = client.post("/analyze", json={})
        assert response.status_code == 422

    def test_with_url_parameter(self, client):
        response = client.post("/analyze", json={
            "text": "Visit this site for more information about the product.",
            "url": "http://suspicious-site.xyz/login"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["cyber_threat_risk"] > 0

    def test_caching_returns_same_result(self, client):
        payload = {"text": "The Federal Reserve announced a pause in interest rate hikes this quarter."}
        r1 = client.post("/analyze", json=payload)
        r2 = client.post("/analyze", json=payload)
        assert r1.status_code == 200
        assert r2.status_code == 200
        d1, d2 = r1.json(), r2.json()
        assert d1["fake_news_probability"] == d2["fake_news_probability"]
        # Second call should be cached
        assert d2["analysis_details"].get("cached") is True

    def test_threat_level_label_valid(self, client):
        response = client.post("/analyze", json={
            "text": "Normal news article from a reputable publication about world events."
        })
        data = response.json()
        assert data["threat_level"] in ("Low", "Medium", "High", "Critical")

    def test_analysis_mode_field_present(self, client):
        response = client.post("/analyze", json={
            "text": "Breaking news: parliament passed a new budget bill with bipartisan support."
        })
        data = response.json()
        assert "analysis_mode" in data["analysis_details"]
        assert data["analysis_details"]["analysis_mode"] in ("full", "partial")
