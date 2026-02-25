"""
Hybrid Fake News Analyzer
Combines pre-trained transformer models with heuristic rules and NLP analysis
"""

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("  transformers library not installed - running in heuristics-only mode")

import os
from dotenv import load_dotenv
load_dotenv()

# Disable problematic background threads and network checks in transformers
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_AUTO_CONVERSION"] = "1"

import re
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from web_verifier import WebSearchVerifier
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    print("Warning: Web search not available")

class HybridFakeNewsAnalyzer:
    def __init__(self):
        """
        Initialize the hybrid analyzer with pre-trained model and heuristics
        """
        print("[*] Loading Fake News Analyzer...")
        
        # Try to load pre-trained model
        self.ml_model = None
        self.ml_available = False
        
        if TRANSFORMERS_AVAILABLE:
            try:
                print(" Loading RoBERTa model (using local cache if available)...")
                # Try local loading first to avoid the Thread-auto_conversion crash
                try:
                    self.ml_model = pipeline(
                        "text-classification",
                        model="hamzab/roberta-fake-news-classification",
                        device=-1,
                        local_files_only=True
                    )
                except Exception:
                    # If not in cache, let it download (standard behavior)
                    print("  Model not found in local cache, attempting download...")
                    self.ml_model = pipeline(
                        "text-classification",
                        model="hamzab/roberta-fake-news-classification",
                        device=-1
                    )
                
                self.ml_available = True
                print(" Pre-trained model loaded successfully!")
            except Exception as e:
                print(f"  Pre-trained model loading failed: {e}")
                print(" Falling back to heuristics-only mode")
        else:
            print(" Running in heuristics-only mode (install transformers for ML features)")
        
        # Heuristic patterns
        self._initialize_patterns()
        
        print(" Fake News Analyzer ready!")
    
    def _initialize_patterns(self):
        """Initialize all pattern matching rules"""
        
        # Strong fake news indicators (conspiracy, misinformation)
        self.strong_fake_indicators = [
            'they don\'t want you to know', 'what they\'re hiding', 'the truth they',
            'mainstream media won\'t tell', 'doctors hate', 'big pharma', 'deep state',
            'wake up', 'open your eyes', 'do your own research', 'question everything',
            'government coverup', 'conspiracy', 'illuminati', 'new world order',
            'suppressed information', 'censored', 'banned', 'forbidden knowledge'
        ]
        
        # Absurdity/Satire indicators
        self.absurdity_patterns = [
            'scientists discover', 'study shows', 'researchers find',
            'miracle cure', 'secret revealed', 'this one trick',
            'you won\'t believe', 'shocked', 'stunning', 'incredible',
            'hand clapping', 'telepathy', 'psychic', 'alien',
            'flat earth', 'chemtrails', 'crystal healing'
        ]
        
        # Pseudo-science markers
        self.pseudoscience_keywords = [
            'quantum healing', 'energy frequency', 'vibration',
            'detox', 'cleanse', 'toxins', 'natural remedy',
            'ancient secret', 'chakra', 'aura', 'manifesting'
        ]
        
        # Clickbait patterns
        self.clickbait_patterns = [
            'you won\'t believe', 'what happens next', 'will shock you',
            'doctors hate him', 'this one trick', 'number 7 will',
            'must see', 'going viral', 'breaking',
            'everyone is talking about', 'you need to see'
        ]
        
        # Humor/satire indicators
        self.satire_indicators = [
            'reportedly', 'sources say', 'allegedly', 'claims to',
            'purportedly', 'supposedly', 'is said to', 'appears to',
            'witnesses report', 'insiders claim', 'experts suggest'
        ]
        
        # Credibility boosters (legitimate journalism)
        self.credibility_indicators = [
            'according to', 'study published in', 'research from',
            'peer-reviewed', 'data shows', 'statistics indicate',
            'analysis by', 'reported by', 'confirmed by',
            'spokesperson said', 'official statement', 'press release',
            'academic journal', 'university study'
        ]
        
        # Trusted news sources
        self.trusted_sources = [
            'reuters', 'associated press', 'bbc', 'npr', 'pbs',
            'new york times', 'washington post', 'wall street journal',
            'guardian', 'economist', 'nature', 'science', 'lancet',
            'nejm', 'jama', 'harvard', 'stanford', 'mit'
        ]
    
    def analyze(self, text: str) -> Dict:
        """
        Main analysis method - hybrid approach
        
        Args:
            text: News article or text to analyze
        
        Returns:
            Dictionary with fake news probability and detailed breakdown
        """
        if not text or len(text.strip()) < 10:
            return self._error_response("Text too short for analysis")
        
        # Truncate very long texts (transformer limit is 512 tokens)
        text_for_ml = text[:2000]  # ~500 tokens
        text_lower = text.lower()
        
        # COMPONENT 1: Pre-trained ML Model (50% weight)
        ml_score = self._get_ml_score(text_for_ml)
        
        # COMPONENT 2: Heuristic Analysis (30% weight)
        heuristic_score = self._get_heuristic_score(text_lower)
        
        # COMPONENT 3: NLP Analysis (20% weight)
        nlp_adjustment = self._get_nlp_adjustment(text_lower)
        
        # Combine scores with weights
        if self.ml_available:
            # Full hybrid: ML (50%) + Heuristics (30%) + NLP (20%)
            final_score = (
                ml_score * 0.50 +
                heuristic_score * 0.30 +
                nlp_adjustment * 0.20
            )
        else:
            # Fallback: Heuristics (60%) + NLP (40%)
            final_score = (
                heuristic_score * 0.60 +
                nlp_adjustment * 0.40
            )
        
        # Apply thresholds and constraints
        final_score = self._apply_constraints(final_score, text_lower)
        
        # Generate detailed explanation
        explanation = self._generate_explanation(
            ml_score, heuristic_score, nlp_adjustment, text_lower
        )
        
        return {
            'fake_news_probability': round(final_score, 1),
            'authenticity_score': round(100 - final_score, 1),
            'components': {
                'ml_probability': round(ml_score, 1) if self.ml_available else None,
                'heuristic_score': round(heuristic_score, 1),
                'nlp_adjustment': round(nlp_adjustment, 1),
                'model_used': 'hybrid' if self.ml_available else 'heuristics_only'
            },
            'factors': {
                'strong_fake_indicators': self._count_patterns(text_lower, self.strong_fake_indicators),
                'absurdity_score': self._check_absurdity(text_lower),
                'clickbait_score': self._check_clickbait(text_lower),
                'credibility_indicators': self._count_patterns(text_lower, self.credibility_indicators),
                'satire_detected': self._check_satire(text_lower)
            },
            'explanation': explanation
        }
    
    def _get_ml_score(self, text: str) -> float:
        """
        Get score from pre-trained transformer model
        Returns probability (0-100) that text is fake news
        """
        if not self.ml_available:
            return 50.0  # Neutral score if model unavailable
        
        try:
            result = self.ml_model(text, truncation=True, max_length=512)[0]
            
            # Model returns label and score
            label = result['label'].lower()
            confidence = result['score']
            
            # Convert to fake news probability (0-100)
            if 'fake' in label or 'false' in label:
                # Model says fake with X% confidence
                return confidence * 100
            else:
                # Model says real with X% confidence
                # So fake probability is (1 - confidence)
                return (1 - confidence) * 100
                
        except Exception as e:
            print(f"ML model error: {e}")
            return 50.0  # Neutral fallback
    
    def _get_heuristic_score(self, text: str) -> float:
        """
        Calculate score based on pattern matching heuristics
        Returns fake news probability (0-100)
        """
        score = 0
        
        # 1. Strong fake news indicators (weighted more heavily)
        fake_count = self._count_patterns(text, self.strong_fake_indicators)
        score += min(fake_count * 20, 40)  # Increased from 15 to 20
        
        # 2. Absurdity/implausibility (40% of heuristic weight)
        absurdity = self._check_absurdity(text)
        score += absurdity * 0.50  # Increased from 0.40 to 0.50
        
        # 3. Clickbait (15% of heuristic weight)
        clickbait = self._check_clickbait(text)
        score += clickbait * 0.20  # Increased from 0.15 to 0.20
        
        # 4. Credibility reduction (subtract up to 30 points)
        credibility = self._check_credibility(text)
        score = max(score - credibility, 0)
        
        return min(score, 100)
    
    def _get_nlp_adjustment(self, text: str) -> float:
        """
        NLP-based adjustments (simplified version without spaCy/NLTK for now)
        Returns adjustment score (0-100)
        """
        score = 50  # Start neutral
        
        # Check for excessive punctuation (!!!, ???)
        excessive_punct = len(re.findall(r'[!?]{2,}', text))
        score += min(excessive_punct * 5, 15)
        
        # Check for ALL CAPS words
        caps_words = len(re.findall(r'\b[A-Z]{4,}\b', text))
        score += min(caps_words * 3, 10)
        
        # Check for emotional words
        emotional_words = [
            'shocking', 'amazing', 'unbelievable', 'incredible',
            'outrageous', 'scandal', 'disaster', 'crisis'
        ]
        emotion_count = sum(1 for word in emotional_words if word in text)
        score += min(emotion_count * 5, 15)
        
        # Check sentence length (very short sentences can indicate clickbait)
        sentences = re.split(r'[.!?]+', text)
        avg_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
        if avg_length < 10:
            score += 10
        
        return min(score, 100)
    
    def _count_patterns(self, text: str, patterns: list) -> int:
        """Count how many patterns from list appear in text"""
        count = 0
        for pattern in patterns:
            if pattern in text:
                count += 1
        return count
    
    def _check_absurdity(self, text: str) -> float:
        """
        Check for absurd/implausible claims
        Returns score 0-100
        """
        score = 0
        
        # Count absurd patterns
        absurd_count = self._count_patterns(text, self.absurdity_patterns)
        score += min(absurd_count * 20, 60)
        
        # Check for pseudoscience
        pseudo_count = self._count_patterns(text, self.pseudoscience_keywords)
        score += min(pseudo_count * 15, 40)
        
        # Check for impossible claims (very simplified)
        impossible_patterns = [
            r'\d{3,}%',  # 500% increase
            r'cure.{0,20}cancer',
            r'immortal',
            r'travel back in time',
            r'communicate with dead'
        ]
        for pattern in impossible_patterns:
            if re.search(pattern, text):
                score += 20
        
        return min(score, 100)
    
    def _check_clickbait(self, text: str) -> float:
        """
        Check for clickbait patterns
        Returns score 0-100
        """
        score = 0
        
        # Count clickbait phrases
        clickbait_count = self._count_patterns(text, self.clickbait_patterns)
        score += min(clickbait_count * 20, 60)
        
        # Check for excessive punctuation in first 100 chars (headline)
        headline = text[:100]
        if '!' in headline or '?' in headline:
            score += 15
        
        # Check for numbered lists in headline (e.g., "10 things...")
        if re.search(r'\b\d+\s+(things|ways|reasons|tips|secrets)', headline):
            score += 20
        
        return min(score, 100)
    
    def _check_satire(self, text: str) -> bool:
        """Check if text appears to be satire"""
        satire_count = self._count_patterns(text, self.satire_indicators)
        absurdity = self._check_absurdity(text)
        
        # High absurdity + satire markers = likely satire
        return satire_count >= 3 and absurdity > 70
    
    def _check_credibility(self, text: str) -> float:
        """
        Check for credibility indicators (reduces fake score)
        Returns credibility points (0-30)
        """
        points = 0
        
        # Academic/research indicators
        credibility_count = self._count_patterns(text, self.credibility_indicators)
        points += min(credibility_count * 5, 15)
        
        # Trusted source mentions
        source_count = self._count_patterns(text, self.trusted_sources)
        points += min(source_count * 5, 15)
        
        return min(points, 30)
    
    def _apply_constraints(self, score: float, text: str) -> float:
        """
        Apply final constraints and thresholds
        """
        # If extremely absurd (>80), set minimum of 75% fake
        absurdity = self._check_absurdity(text)
        if absurdity > 80:
            score = max(score, 75)
        
        # If high credibility indicators, cap fake score at 30%
        credibility = self._check_credibility(text)
        if credibility > 20:
            score = min(score, 30)
        
        # Ensure score is in valid range
        return max(0, min(score, 100))
    
    def _generate_explanation(self, ml_score: float, heuristic_score: float, 
                             nlp_score: float, text: str) -> str:
        """Generate human-readable explanation"""
        explanations = []
        
        # ML component
        if self.ml_available:
            if ml_score > 70:
                explanations.append("AI model: High fake probability detected")
            elif ml_score > 50:
                explanations.append("AI model: Moderate fake probability")
            elif ml_score < 30:
                explanations.append("AI model: Low fake probability (likely authentic)")
        
        # Heuristic findings
        fake_indicators = self._count_patterns(text, self.strong_fake_indicators)
        if fake_indicators > 2:
            explanations.append(f"Multiple misinformation patterns ({fake_indicators} indicators)")
        elif fake_indicators > 0:
            explanations.append("Some misinformation indicators present")
        
        absurdity = self._check_absurdity(text)
        if absurdity > 80:
            explanations.append("Highly absurd/implausible claims detected")
        elif absurdity > 60:
            explanations.append("Absurd or implausible claims present")
        elif absurdity > 40:
            explanations.append("Questionable claims detected")
        
        if self._check_satire(text):
            explanations.append("Likely satire or parody content")
        
        clickbait = self._check_clickbait(text)
        if clickbait > 60:
            explanations.append("Strong clickbait patterns detected")
        elif clickbait > 40:
            explanations.append("Clickbait elements present")
        
        credibility = self._check_credibility(text)
        if credibility > 20:
            explanations.append("Multiple credible sources referenced")
        elif credibility > 10:
            explanations.append("Some credible source references")
        
        # NLP findings
        if nlp_score > 65:
            explanations.append("Emotional manipulation detected")
        
        # If no strong signals
        if not explanations:
            if heuristic_score < 30:
                return "Appears mostly authentic with minor concerns"
            elif heuristic_score > 70:
                return "Strong fake news indicators despite lack of specific patterns"
            else:
                return "Mixed signals - inconclusive analysis"
        
        return "; ".join(explanations)
    
    def _error_response(self, message: str) -> Dict:
        """Return error response"""
        return {
            'fake_news_probability': 0,
            'authenticity_score': 0,
            'error': message
        }

class FakeNewsAnalyzer:
    """Wrapper to make HybridFakeNewsAnalyzer compatible with existing API"""
    
    def __init__(self):
        self.analyzer = HybridFakeNewsAnalyzer()
        
        # Web search
        if WEB_SEARCH_AVAILABLE:
            self.web_verifier = WebSearchVerifier()
            self.use_web_search = True
            print(" Web search verification enabled")
        else:
            self.web_verifier = None
            self.use_web_search = False

        # Fact checker
        try:
            from fact_checker import FactChecker
            api_key = os.environ.get('GOOGLE_FACT_CHECK_KEY')
            if api_key:
                self.fact_checker = FactChecker(api_key)
                print(" Google Fact Check API enabled")
            else:
                self.fact_checker = None
                print("  No API key found in .env")
        except ImportError as e:
            self.fact_checker = None
            print(f"  Fact checker module not found: {e}")
        except Exception as e:
            self.fact_checker = None
            print(f"  Fact checker error: {e}")

    def analyze(self, text: str):
        result = self.analyzer.analyze(text)
        base_score = result['fake_news_probability']
        
        # Track which components succeeded
        ml_success = result['components']['ml_probability'] is not None
        web_success = False
        fact_check_success = False

        # Web search layer - Ensure it runs for ALL scores to meet "full analysis" requirement
        web_search_result = None
        if self.use_web_search:
            try:
                web_search_result = self.web_verifier.verify_claims(text, max_searches=2)
                base_score += web_search_result['score_adjustment']
                base_score = max(0, min(base_score, 100))
                web_success = True
            except Exception as e:
                print(f" Web search error: {e}")

        # Fact check layer
        fact_check_result = None
        if self.fact_checker:
            try:
                fact_check_result = self.fact_checker.check_claims(text)
                if fact_check_result['verdict'] == 'FALSE':
                    base_score = min(base_score + 20, 100)
                elif fact_check_result['verdict'] == 'TRUE':
                    base_score = max(base_score - 20, 0)
                print(f" Fact check: {fact_check_result['verdict']} ({fact_check_result['confidence']}% confidence)")
                fact_check_success = True
            except Exception as e:
                print(f" Fact check error: {e}")

        # Check if all modules gave results
        is_full = ml_success and web_success and fact_check_success

        return {
            "probability": round(base_score, 1),
            "is_full_analysis": is_full,
            "factors": {
                "ml_probability": result['components']['ml_probability'],
                "heuristic_score": result['components']['heuristic_score'],
                "nlp_adjustment": result['components']['nlp_adjustment'],
                "model_used": result['components']['model_used'],
                "web_verification": web_search_result['explanation'] if web_search_result else None,
                "credible_sources_found": web_search_result['credible_sources_found'] if web_search_result else 0,
                "fact_check_verdict": fact_check_result['verdict'] if fact_check_result else None,
                "fact_check_confidence": fact_check_result['confidence'] if fact_check_result else None,
                "fact_check_explanation": fact_check_result['explanation'] if fact_check_result else None,
                "explanation": result['explanation'],
                "strong_fake_indicators": result['factors']['strong_fake_indicators'],
                "absurdity_score": result['factors']['absurdity_score'],
                "clickbait_score": result['factors']['clickbait_score'],
                "credibility_indicators": result['factors']['credibility_indicators'],
                "satire_detected": result['factors']['satire_detected'],
                "full_analysis_completed": is_full
            }
        }

        
# Test the analyzer
if __name__ == "__main__":
    print("="*60)
    print("HYBRID FAKE NEWS ANALYZER TEST")
    print("="*60)
    
    analyzer = HybridFakeNewsAnalyzer()
    
    # Test Case 1: Obvious fake news
    test1 = """
    SHOCKING: Scientists discover that hand-clapping can cure cancer! 
    Doctors don't want you to know this secret! Big Pharma is trying to 
    hide this miracle cure. Share before they delete this!
    """
    
    print("\n Test 1: Obvious Fake News")
    print("-" * 60)
    result1 = analyzer.analyze(test1)
    print(f"Fake Probability: {result1['fake_news_probability']}%")
    print(f"Authenticity: {result1['authenticity_score']}%")
    print(f"Explanation: {result1['explanation']}")
    
    # Test Case 2: Legitimate news
    test2 = """
    According to a study published in Nature, researchers from Harvard 
    University have found new evidence about climate patterns. The 
    peer-reviewed research, conducted over five years, analyzed data 
    from multiple sources and was confirmed by independent experts.
    """
    
    print("\n Test 2: Legitimate News")
    print("-" * 60)
    result2 = analyzer.analyze(test2)
    print(f"Fake Probability: {result2['fake_news_probability']}%")
    print(f"Authenticity: {result2['authenticity_score']}%")
    print(f"Explanation: {result2['explanation']}")
    
    # Test Case 3: Satire
    test3 = """
    Local man reportedly discovers time travel by staring at microwave. 
    Sources say he claims to have visited the year 3000. Witnesses report 
    seeing him disappear in a flash of light. Scientists allegedly baffled.
    """
    
    print("\n Test 3: Satire/Humor")
    print("-" * 60)
    result3 = analyzer.analyze(test3)
    print(f"Fake Probability: {result3['fake_news_probability']}%")
    print(f"Authenticity: {result3['authenticity_score']}%")
    print(f"Explanation: {result3['explanation']}")
    
    print("\n" + "="*60)
    print(" Tests Complete!")
    print("="*60)