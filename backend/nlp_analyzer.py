"""
Advanced NLP Analyzer - Enhanced Robustness
===========================================
Uses multiple NLP techniques for comprehensive text analysis:
- spaCy: NER, POS tagging, dependency parsing, linguistic features
- NLTK: Sentiment analysis, lexical diversity, readability metrics
- Custom: Fact-checking patterns, source verification, claim analysis
"""
import re
import math
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter

# Try to import NLP libraries
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class AdvancedNLPAnalyzer:
    """
    Robust NLP analyzer with multiple linguistic features.
    """
    
    def __init__(self):
        self.nlp = None
        self.sia = None
        self.stop_words = set()
        self._init_spacy()
        self._init_nltk()
        
        # Fact-checking indicators
        self.verification_phrases = {
            'verified', 'confirmed', 'fact-checked', 'authenticated',
            'corroborated', 'substantiated', 'validated', 'proven'
        }
        
        # Uncertainty markers (hedging language)
        self.hedging_words = {
            'allegedly', 'reportedly', 'supposedly', 'claimed',
            'purportedly', 'apparently', 'seemingly', 'possibly',
            'might', 'could', 'may', 'perhaps', 'probably'
        }
        
        # Authoritative sources
        self.authoritative_entities = {
            'reuters', 'associated press', 'bbc', 'cnn', 'al jazeera',
            'world health organization', 'who', 'cdc', 'fda', 'fbi',
            'united nations', 'european union', 'world bank', 'imf'
        }
    
    def _init_spacy(self):
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("spaCy model not found. Install: python -m spacy download en_core_web_sm")
                self.nlp = None
    
    def _init_nltk(self):
        if NLTK_AVAILABLE:
            try:
                nltk.data.find('vader_lexicon')
            except LookupError:
                try:
                    nltk.download('vader_lexicon', quiet=True)
                except:
                    pass
            try:
                nltk.data.find('punkt')
            except LookupError:
                try:
                    nltk.download('punkt', quiet=True)
                except:
                    pass
            try:
                nltk.data.find('stopwords')
            except LookupError:
                try:
                    nltk.download('stopwords', quiet=True)
                except:
                    pass
            try:
                self.sia = SentimentIntensityAnalyzer()
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at'}
    
    def analyze_entities(self, text: str) -> Dict:
        """Enhanced entity recognition with credibility scoring."""
        if not self.nlp:
            return self._fallback_entity_analysis(text)
        
        doc = self.nlp(text[:10000])
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Categorize entities
        persons = [e for e in entities if e[1] == 'PERSON']
        orgs = [e for e in entities if e[1] == 'ORG']
        locations = [e for e in entities if e[1] in ['GPE', 'LOC']]
        dates = [e for e in entities if e[1] == 'DATE']
        money = [e for e in entities if e[1] == 'MONEY']
        
        # Check for authoritative entities
        text_lower = text.lower()
        auth_count = sum(1 for auth in self.authoritative_entities if auth in text_lower)
        
        # Entity diversity score
        entity_types = set(e[1] for e in entities)
        diversity_score = min(100, len(entity_types) * 15)
        
        # Real entity score (more entities = more credible)
        real_entity_score = min(100, (len(persons) * 8 + len(orgs) * 10 + 
                                     len(locations) * 5 + len(dates) * 7 + 
                                     auth_count * 15))
        
        return {
            "total_entities": len(entities),
            "persons": len(persons),
            "organizations": len(orgs),
            "locations": len(locations),
            "dates": len(dates),
            "money_mentions": len(money),
            "authoritative_sources": auth_count,
            "entity_diversity": diversity_score,
            "real_entity_score": real_entity_score,
            "has_real_entities": len(entities) > 3
        }
    
    def _fallback_entity_analysis(self, text: str) -> Dict:
        """Fallback entity detection without spaCy."""
        # Simple capitalized word detection
        words = text.split()
        capitalized = [w for w in words if w and w[0].isupper() and len(w) > 2]
        
        # Check for authoritative sources
        text_lower = text.lower()
        auth_count = sum(1 for auth in self.authoritative_entities if auth in text_lower)
        
        # Estimate entity score
        entity_score = min(100, len(capitalized) * 3 + auth_count * 15)
        
        return {
            "total_entities": len(capitalized),
            "persons": 0,
            "organizations": 0,
            "locations": 0,
            "dates": 0,
            "money_mentions": 0,
            "authoritative_sources": auth_count,
            "entity_diversity": 30,
            "real_entity_score": entity_score,
            "has_real_entities": len(capitalized) > 5
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Advanced sentiment analysis with bias detection."""
        if not self.sia:
            return self._fallback_sentiment(text)
        
        # Overall sentiment
        scores = self.sia.polarity_scores(text)
        
        # Sentence-level sentiment for consistency check
        sentences = sent_tokenize(text) if NLTK_AVAILABLE else text.split('.')
        sent_scores = [self.sia.polarity_scores(s)['compound'] for s in sentences[:20]]
        
        # Sentiment consistency (low variance = more consistent)
        if sent_scores:
            sentiment_variance = np.var(sent_scores)
            consistency_score = max(0, 100 - sentiment_variance * 200)
        else:
            consistency_score = 50
        
        # Extreme sentiment detection
        is_extreme = abs(scores['compound']) > 0.6
        is_very_extreme = abs(scores['compound']) > 0.8
        
        # Bias indicators (very positive or very negative)
        bias_score = abs(scores['compound']) * 100
        
        return {
            "compound": scores['compound'],
            "positive": scores['pos'],
            "negative": scores['neg'],
            "neutral": scores['neu'],
            "is_extreme": is_extreme,
            "is_very_extreme": is_very_extreme,
            "bias_score": bias_score,
            "consistency_score": consistency_score
        }
    
    def _fallback_sentiment(self, text: str) -> Dict:
        """Fallback sentiment without NLTK."""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'best'}
        negative_words = {'bad', 'terrible', 'awful', 'worst', 'horrible', 'poor'}
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            compound = 0
        else:
            compound = (pos_count - neg_count) / total
        
        return {
            "compound": compound,
            "positive": pos_count / max(total, 1),
            "negative": neg_count / max(total, 1),
            "neutral": 1 - (pos_count + neg_count) / max(total, 1),
            "is_extreme": abs(compound) > 0.6,
            "is_very_extreme": abs(compound) > 0.8,
            "bias_score": abs(compound) * 100,
            "consistency_score": 50
        }
    
    def analyze_pos_tags(self, text: str) -> Dict:
        """Advanced POS tagging with linguistic feature extraction."""
        if not self.nlp:
            return self._fallback_pos_analysis(text)
        
        doc = self.nlp(text[:5000])
        total = len(doc)
        if total == 0:
            return self._fallback_pos_analysis(text)
        
        # Count POS tags
        nouns = sum(1 for t in doc if t.pos_ in ['NOUN', 'PROPN'])
        verbs = sum(1 for t in doc if t.pos_ == 'VERB')
        adjs = sum(1 for t in doc if t.pos_ == 'ADJ')
        advs = sum(1 for t in doc if t.pos_ == 'ADV')
        
        # Sensationalism indicators
        excessive_adjs = (adjs / total) > 0.12
        excessive_advs = (advs / total) > 0.08
        
        # Noun-to-verb ratio (informative vs action-oriented)
        nv_ratio = nouns / max(verbs, 1)
        
        # Lexical density (content words / total words)
        content_words = nouns + verbs + adjs + advs
        lexical_density = content_words / total
        
        return {
            "noun_ratio": nouns / total,
            "verb_ratio": verbs / total,
            "adj_ratio": adjs / total,
            "adv_ratio": advs / total,
            "excessive_adjectives": excessive_adjs,
            "excessive_adverbs": excessive_advs,
            "noun_verb_ratio": nv_ratio,
            "lexical_density": lexical_density,
            "sensationalism_score": (adjs + advs) / total * 100
        }
    
    def _fallback_pos_analysis(self, text: str) -> Dict:
        """Fallback POS analysis without spaCy."""
        return {
            "noun_ratio": 0.3,
            "verb_ratio": 0.2,
            "adj_ratio": 0.1,
            "adv_ratio": 0.05,
            "excessive_adjectives": False,
            "excessive_adverbs": False,
            "noun_verb_ratio": 1.5,
            "lexical_density": 0.65,
            "sensationalism_score": 15
        }
    
    def analyze_linguistic_features(self, text: str) -> Dict:
        """Advanced linguistic analysis."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = text.split()
        
        if not sentences or not words:
            return {"complexity_score": 50, "readability_score": 50}
        
        # Sentence length statistics
        sent_lengths = [len(s.split()) for s in sentences]
        avg_sent_len = np.mean(sent_lengths)
        sent_len_variance = np.var(sent_lengths)
        
        # Vocabulary richness (Type-Token Ratio)
        unique_words = set(w.lower() for w in words if w.isalpha())
        ttr = len(unique_words) / len(words)
        
        # Flesch Reading Ease approximation
        syllables = sum(self._count_syllables(w) for w in words[:200])
        avg_syllables = syllables / min(len(words), 200)
        flesch_score = 206.835 - 1.015 * avg_sent_len - 84.6 * avg_syllables
        flesch_score = max(0, min(100, flesch_score))
        
        # Hedging language (uncertainty)
        hedging_count = sum(1 for h in self.hedging_words if h in text.lower())
        hedging_ratio = hedging_count / len(sentences)
        
        # Verification language
        verification_count = sum(1 for v in self.verification_phrases if v in text.lower())
        
        # Complexity score
        complexity = 50
        if 15 <= avg_sent_len <= 25:
            complexity += 20
        if ttr > 0.5:
            complexity += 15
        if sent_len_variance > 20:
            complexity += 10
        if verification_count > 0:
            complexity += 5
        
        return {
            "avg_sentence_length": round(avg_sent_len, 1),
            "sentence_variance": round(sent_len_variance, 1),
            "vocabulary_richness": round(ttr, 3),
            "flesch_reading_ease": round(flesch_score, 1),
            "hedging_ratio": round(hedging_ratio, 2),
            "verification_count": verification_count,
            "complexity_score": min(100, complexity),
            "readability_score": round(flesch_score, 1)
        }
    
    def _count_syllables(self, word: str) -> int:
        """Approximate syllable count."""
        word = word.lower()
        vowels = 'aeiouy'
        count = 0
        prev_was_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        if word.endswith('e'):
            count -= 1
        return max(1, count)
    
    def get_comprehensive_analysis(self, text: str) -> Dict:
        """Complete NLP analysis with all features."""
        entities = self.analyze_entities(text)
        sentiment = self.analyze_sentiment(text)
        pos_tags = self.analyze_pos_tags(text)
        linguistic = self.analyze_linguistic_features(text)
        
        # Calculate overall credibility score from NLP features
        nlp_credibility = (
            entities.get('real_entity_score', 0) * 0.35 +
            (100 - sentiment.get('bias_score', 50)) * 0.20 +
            linguistic.get('complexity_score', 50) * 0.25 +
            sentiment.get('consistency_score', 50) * 0.20
        )
        
        return {
            "entities": entities,
            "sentiment": sentiment,
            "pos_tags": pos_tags,
            "linguistic": linguistic,
            "nlp_credibility_score": round(nlp_credibility, 1),
            "nlp_available": {
                "spacy": self.nlp is not None,
                "nltk": self.sia is not None
            }
        }


# Global instance
nlp_analyzer = AdvancedNLPAnalyzer()


def get_nlp_features(text: str) -> Dict:
    """Main entry point for NLP analysis."""
    return nlp_analyzer.get_comprehensive_analysis(text)
