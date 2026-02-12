"""
ML-Enhanced Fake News Detection with TF-IDF + Logistic Regression
==================================================================
Combines traditional NLP with machine learning for superior accuracy.
"""
import re
import numpy as np
from typing import Dict
import pickle
import os

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from nlp_analyzer import get_nlp_features
    NLP_ENABLED = True
except ImportError:
    NLP_ENABLED = False


class MLFakeNewsDetector:
    """
    Machine Learning-based fake news detector with TF-IDF features.
    """
    
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.scaler = None
        self.model_trained = False
        
        # Try to load pre-trained model
        if os.path.exists('fake_news_model.pkl'):
            self._load_model()
        else:
            self._train_model()
    
    def _train_model(self):
        """Train ML model on sample dataset."""
        if not SKLEARN_AVAILABLE:
            return
        
        # Training data: (text, label) where 1=fake, 0=real
        training_data = [
            # FAKE NEWS (label=1)
            ("SHOCKING scientists EXPOSED the truth about vaccines they dont want you to know share before deleted", 1),
            ("BREAKING government hiding alien technology wake up sheeple mainstream media lies cover up", 1),
            ("You wont believe what happens next doctors hate this one weird trick click here now", 1),
            ("Big pharma doesnt want you to know this simple cure they are suppressing the truth", 1),
            ("Deep state conspiracy exposed new world order plandemic false flag operation", 1),
            ("Share this before they delete it mainstream media wont tell you the real story", 1),
            ("URGENT your account suspended click immediately verify identity or lose access forever", 1),
            ("Scientists confirm Nigerian aunty hand-clapping is quantum communication defies physics", 1),
            ("Government announces plan to replace traffic lights with AI-powered dance battles", 1),
            ("Holographic dancers will control traffic flow via TikTok integration ministry confirms", 1),
            
            # REAL NEWS (label=0)
            ("According to Reuters the World Health Organization reported 500 new cases in the region", 0),
            ("The Minister of Health announced new healthcare policies in a press briefing today", 0),
            ("Research published in the Journal of Medicine shows promising results from clinical trials", 0),
            ("Al Jazeera reported that officials confirmed the new economic policy will take effect next month", 0),
            ("According to the Associated Press government spokesperson said negotiations are ongoing", 0),
            ("The BBC reported that the Prime Minister addressed parliament on climate change legislation", 0),
            ("A peer-reviewed study published in Nature found significant correlation between the variables", 0),
            ("The Federal Reserve announced interest rate changes following economic data analysis", 0),
            ("According to the CDC health officials recommend following standard safety protocols", 0),
            ("The United Nations Security Council met to discuss the humanitarian situation in the region", 0),
            ("Bloomberg reported that stock markets responded to quarterly earnings reports from major companies", 0),
            ("The Guardian published an investigation into government spending based on official documents", 0),
            ("NPR interviewed experts who explained the scientific consensus on the environmental impact", 0),
            ("The New York Times reported that city officials approved the infrastructure development plan", 0),
            ("According to AP News the court ruling was announced following months of legal proceedings", 0),
        ]
        
        texts = [t[0] for t in training_data]
        labels = [t[1] for t in training_data]
        
        # TF-IDF Vectorization
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 3),
            stop_words='english',
            min_df=1
        )
        
        X = self.vectorizer.fit_transform(texts)
        
        # Train Logistic Regression
        self.classifier = LogisticRegression(
            random_state=42,
            max_iter=1000,
            class_weight='balanced'
        )
        self.classifier.fit(X, labels)
        
        self.model_trained = True
        self._save_model()
    
    def _save_model(self):
        """Save trained model to disk."""
        try:
            with open('fake_news_model.pkl', 'wb') as f:
                pickle.dump({
                    'vectorizer': self.vectorizer,
                    'classifier': self.classifier
                }, f)
        except:
            pass
    
    def _load_model(self):
        """Load pre-trained model from disk."""
        try:
            with open('fake_news_model.pkl', 'rb') as f:
                data = pickle.load(f)
                self.vectorizer = data['vectorizer']
                self.classifier = data['classifier']
                self.model_trained = True
        except:
            self._train_model()
    
    def predict_probability(self, text: str) -> float:
        """
        Predict fake news probability using ML model.
        Returns probability between 0-100.
        """
        if not self.model_trained or not SKLEARN_AVAILABLE:
            return 50.0  # Neutral if model unavailable
        
        try:
            X = self.vectorizer.transform([text])
            proba = self.classifier.predict_proba(X)[0]
            # proba[1] is probability of class 1 (fake)
            return proba[1] * 100
        except:
            return 50.0


# Global ML detector
ml_detector = MLFakeNewsDetector() if SKLEARN_AVAILABLE else None


class FakeNewsAnalyzer:
    def __init__(self):
        # STRONG fake news indicators
        self.strong_fake_patterns = [
            r'they\s+(?:dont|don\'t)\s+want\s+you\s+to\s+know',
            r'mainstream\s+media\s+(?:lies|wont|won\'t\s+tell)',
            r'wake\s+up\s+(?:sheeple|people)',
            r'share\s+(?:this\s+)?before\s+(?:they\s+)?(?:delete|remove)',
            r'exposed?\s+the\s+truth',
            r'big\s+(?:pharma|tech|government)',
            r'deep\s+state',
            r'new\s+world\s+order',
            r'plandemic',
            r'false\s+flag',
        ]
        
        # Satire/absurdity patterns
        self.absurdity_patterns = [
            r'quantum.*(?:clap|hand|aunty|food|garri|jollof)',
            r'(?:clap|hand).*quantum',
            r'defies?\s+(?:classical\s+)?physics',
            r'weaponized?\s+against\s+(?:husband|wife)',
            r'(?:cern|nasa|mit).*(?:via\s+)?zoom',
            r'instantaneous\s+compulsion',
            r'previously\s+undetected\s+form',
            r'\d+\s+meters?\s+(?:away|through).*(?:concrete|walls?)',
            r'observed.*\d{3,}.*(?:clap|sequence|pattern)',
            r'(?:garri|jollof|wrapper|gele).*(?:amplif|enhanc|research)',
            r'dance\s+battle.*(?:traffic|government)',
            r'holographic.*(?:dancer|projection)',
            r'tiktok.*(?:government|ministry|policy)',
        ]
        
        # Satire markers
        self.satire_markers = [
            r'told\s+journalists.*(?:clap|quantum|dance)',
            r'lead\s+(?:physicist|scientist).*(?:dr\.|prof\.)',
            r'joint\s+research.*zoom',
            r'we\s+(?:are\s+)?calling\s+it\s+["\']?\w+yon',
            r'experience.*(?:instantaneous|immediate)\s+compulsion',
            r'observed.*over\s+\d{3,}',
            r'across\s+\d+\s+states',
            r'paper\s+suggests.*amplified\s+by',
            r'follow.?up\s+experiment.*weaponiz',
            r'ministry.?s\s+response',
            r'backup.*(?:play|blast).*(?:loop|until)',
            r'too\s+busy.*(?:recording|filming|watching)',
        ]
        
        # Clickbait patterns
        self.clickbait_patterns = [
            r'you\s+(?:wont|won\'t)\s+believe',
            r'what\s+happens\s+next',
            r'number\s+\d+\s+will\s+(?:shock|surprise)',
            r'doctors\s+(?:hate|don\'t\s+want)',
            r'one\s+(?:weird|simple)\s+trick',
            r'this\s+(?:simple|easy)\s+(?:trick|hack)',
        ]
        
        # STRONG credibility indicators
        self.strong_credibility = {
            'reuters reported', 'associated press reported', 'ap news reported',
            'afp reported', 'according to reuters', 'according to ap',
            'peer-reviewed study', 'published in the journal of',
            'research published in', 'study published in',
            'according to the world health organization',
            'according to the cdc', 'according to who',
        }
        
        # Moderate credibility
        self.moderate_credibility = {
            'according to', 'sources say', 'officials said',
            'spokesperson said', 'in a statement', 'press release',
            'ministry of', 'department of', 'government official',
        }
        
        # Trusted sources
        self.trusted_sources = {
            'bbc', 'cnn', 'reuters', 'associated press', 'ap news',
            'al jazeera', 'the guardian', 'new york times', 'washington post',
            'bloomberg', 'financial times', 'the economist', 'npr',
        }

    def analyze(self, text: str) -> Dict:
        text_lower = text.lower()
        word_count = len(text.split())
        
        # ML-based prediction (most important)
        ml_probability = 50.0
        if ml_detector:
            ml_probability = ml_detector.predict_probability(text)
        
        # Get NLP features
        nlp_features = get_nlp_features(text) if NLP_ENABLED else None
        
        # Calculate heuristic scores
        strong_fake = self._calc_strong_fake(text_lower)
        absurdity = self._calc_absurdity(text_lower)
        satire = self._calc_satire(text_lower)
        clickbait = self._calc_clickbait(text_lower)
        credibility = self._calc_credibility(text_lower, word_count)
        structure = self._calc_structure(text, word_count)
        
        # NLP enhancements
        nlp_credibility = 0
        nlp_adjustment = 0
        sentiment_extreme = False
        has_entities = False
        
        if nlp_features:
            nlp_credibility = nlp_features.get('nlp_credibility_score', 0)
            
            sentiment = nlp_features.get('sentiment', {})
            if sentiment.get('is_very_extreme', False):
                nlp_adjustment += 15
                sentiment_extreme = True
            elif sentiment.get('is_extreme', False):
                nlp_adjustment += 8
            
            entities = nlp_features.get('entities', {})
            entity_score = entities.get('real_entity_score', 0)
            if entity_score > 50:
                credibility += 20
                has_entities = True
            elif entity_score > 30:
                credibility += 10
            
            pos_tags = nlp_features.get('pos_tags', {})
            if pos_tags.get('excessive_adjectives', False):
                nlp_adjustment += 10
            
            linguistic = nlp_features.get('linguistic', {})
            if linguistic.get('complexity_score', 50) > 70:
                credibility += 10
        
        # HYBRID SCORING: ML (50%) + Heuristics (30%) + NLP (20%)
        
        # Heuristic score
        combined_absurd = max(absurdity, satire) + (absurdity + satire) * 0.25
        
        heuristic_score = (
            strong_fake * 0.35 +
            combined_absurd * 0.40 +
            clickbait * 0.15 +
            nlp_adjustment * 0.10
        )
        
        # Credibility reduction
        total_credibility = credibility + nlp_credibility * 0.5
        
        if combined_absurd > 40 or strong_fake > 20:
            cred_reduction = total_credibility * 0.10
        elif combined_absurd > 20:
            cred_reduction = total_credibility * 0.25
        else:
            cred_reduction = total_credibility * 0.45
        
        # Structure bonus
        if combined_absurd < 25 and strong_fake < 15:
            structure_bonus = max(0, (structure - 50) * 0.15)
        else:
            structure_bonus = 0
        
        heuristic_final = 30 + heuristic_score - cred_reduction - structure_bonus
        
        # COMBINE: ML (50%) + Heuristics (50%)
        if SKLEARN_AVAILABLE and ml_detector and ml_detector.model_trained:
            base_prob = ml_probability * 0.50 + heuristic_final * 0.50
        else:
            base_prob = heuristic_final
        
        # Force minimum scores for high absurdity/satire
        if absurdity > 70 or satire > 70:
            base_prob = max(base_prob, 80)
        elif absurdity > 50 or satire > 50:
            base_prob = max(base_prob, 70)
        elif absurdity > 35 or satire > 35:
            base_prob = max(base_prob, 60)
        elif strong_fake > 40:
            base_prob = max(base_prob, 70)
        
        # Cap for high credibility + low fake indicators
        if total_credibility > 80 and strong_fake < 10 and absurdity < 20 and satire < 20:
            base_prob = min(base_prob, 25)
        elif total_credibility > 60 and strong_fake < 15 and absurdity < 25:
            base_prob = min(base_prob, 35)
        
        prob = max(5, min(95, base_prob))
        
        return {
            "probability": prob,
            "factors": {
                "ml_probability": round(ml_probability, 1),
                "strong_fake_indicators": round(strong_fake, 1),
                "absurdity_score": round(absurdity, 1),
                "satire_indicators": round(satire, 1),
                "clickbait_score": round(clickbait, 1),
                "credibility_score": round(credibility, 1),
                "nlp_credibility": round(nlp_credibility, 1),
                "structure_quality": round(structure, 1),
                "explanation": self._explain(ml_probability, strong_fake, absurdity, satire, 
                                            clickbait, credibility, sentiment_extreme, has_entities)
            }
        }

    def _calc_strong_fake(self, text: str) -> float:
        matches = sum(1 for p in self.strong_fake_patterns if re.search(p, text, re.IGNORECASE))
        return min(100, matches * 30)

    def _calc_absurdity(self, text: str) -> float:
        matches = sum(1 for p in self.absurdity_patterns if re.search(p, text, re.IGNORECASE))
        
        science = ['quantum', 'physics', 'entanglement', 'cern', 'nasa', 'experiment', 'defies']
        absurd = ['aunty', 'uncle', 'clapping', 'garri', 'jollof', 'wrapper', 'gele', 
                 'husband', 'wife', 'dance', 'tiktok']
        
        sci_count = sum(1 for t in science if t in text)
        abs_count = sum(1 for t in absurd if t in text)
        
        if sci_count >= 3 and abs_count >= 2:
            matches += 5
        elif sci_count >= 2 and abs_count >= 2:
            matches += 3
        elif sci_count >= 1 and abs_count >= 1:
            matches += 1
        
        made_up = re.findall(r'\b[A-Za-z]{4,}yon\b', text, re.IGNORECASE)
        real = ['canyon', 'crayon', 'rayon', 'halcyon']
        fake = [w for w in made_up if w.lower() not in real]
        matches += len(fake) * 3
        
        return min(100, matches * 10)

    def _calc_satire(self, text: str) -> float:
        matches = sum(1 for p in self.satire_markers if re.search(p, text, re.IGNORECASE))
        
        humor = ['reportedly', 'apparently', 'somehow', 'mysteriously', 
                'ironically', 'curiously', 'conveniently', 'surprisingly']
        h_count = sum(1 for w in humor if w in text)
        
        followup = [r'follow.?up.*experiment', r'weaponiz', r'same\s+effect.*against']
        f_count = sum(1 for p in followup if re.search(p, text, re.IGNORECASE))
        
        return min(100, matches * 12 + h_count * 8 + f_count * 15)

    def _calc_clickbait(self, text: str) -> float:
        matches = sum(1 for p in self.clickbait_patterns if re.search(p, text, re.IGNORECASE))
        
        exclaim = text.count('!')
        if exclaim > 5:
            matches += 1
        if exclaim > 10:
            matches += 1
        
        caps = re.findall(r'\b[A-Z]{4,}\b', text)
        if len(caps) > 5:
            matches += 1
        
        return min(100, matches * 20)

    def _calc_credibility(self, text: str, wc: int) -> float:
        score = 0
        
        strong = sum(1 for i in self.strong_credibility if i in text)
        score += strong * 12
        
        trusted = sum(1 for s in self.trusted_sources if s in text)
        score += trusted * 10
        
        moderate = sum(1 for i in self.moderate_credibility if i in text)
        score += moderate * 4
        
        quotes = len(re.findall(r'"[^"]{15,}"', text))
        score += min(15, quotes * 5)
        
        stats = len(re.findall(r'\b\d+(?:\.\d+)?%', text))
        score += min(10, stats * 3)
        
        dates = len(re.findall(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?', text, re.IGNORECASE))
        score += min(10, dates * 5)
        
        if wc > 300:
            score += 8
        if wc > 600:
            score += 7
        
        return min(100, score)

    def _calc_structure(self, text: str, wc: int) -> float:
        sents = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sents) < 2:
            return 25
        
        score = 50
        lens = [len(s.split()) for s in sents]
        
        avg = np.mean(lens)
        if 12 <= avg <= 28:
            score += 20
        elif avg < 8 or avg > 40:
            score -= 10
        
        caps = sum(1 for s in sents if s and s[0].isupper())
        if caps / len(sents) > 0.75:
            score += 15
        
        if '\n' in text:
            score += 10
        
        if len(set(lens)) > len(lens) * 0.4:
            score += 5
        
        return min(100, max(0, score))

    def _explain(self, ml_prob, strong, absurd, satire, click, cred, sent_extreme, has_ent) -> str:
        exp = []
        
        if ml_prob > 70:
            exp.append("ML model: High fake probability")
        elif ml_prob > 50:
            exp.append("ML model: Moderate fake probability")
        
        if strong > 25:
            exp.append("Strong misinformation patterns")
        if absurd > 35:
            exp.append("Absurd/implausible claims")
        if satire > 35:
            exp.append("Satire/humor indicators")
        if click > 30:
            exp.append("Clickbait patterns")
        
        if cred > 60 and strong < 15 and absurd < 25 and satire < 25:
            exp.append("Strong credibility indicators")
        elif cred > 35 and strong < 10 and absurd < 20:
            exp.append("Some credibility markers")
        
        if sent_extreme:
            exp.append("Extreme sentiment (NLP)")
        if has_ent:
            exp.append("Real entities found (NLP)")
        
        return "; ".join(exp) if exp else "Content appears balanced"
