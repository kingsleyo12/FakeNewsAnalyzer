"""
Originality Analysis Module
===========================
Analyzes text content for originality and uniqueness indicators.

Academic Justification:
- Originality correlates inversely with fake news likelihood
- Repetitive, templated content often indicates misinformation
- Linguistic diversity metrics measure content quality
- N-gram analysis detects copied/templated phrases

Percentage Calculation:
- Vocabulary richness (Type-Token Ratio)
- Phrase uniqueness (N-gram diversity)
- Structural originality (sentence variation)
- Content depth (information density)
"""

import re
import math
from typing import Dict, List, Set
from collections import Counter


class OriginalityAnalyzer:
    """
    Analyzes text originality using linguistic metrics.
    Higher originality score suggests more authentic content.
    """
    
    def __init__(self):
        # Common filler phrases that reduce originality
        self.filler_phrases = {
            'in order to', 'due to the fact', 'at the end of the day',
            'it goes without saying', 'needless to say', 'as a matter of fact',
            'for all intents and purposes', 'at this point in time',
            'in the event that', 'in light of the fact'
        }
        
        # Template phrases often found in fake news (not legitimate journalism)
        self.template_phrases = {
            'share this before', 'they dont want you to know',
            'mainstream media wont tell you', 'wake up people', 
            'open your eyes', 'do your own research',
            'connect the dots', 'follow the money', 'exposed the truth',
            'what they dont want', 'exposed', 'exposed'
        }
        
        # Legitimate journalism phrases (should NOT reduce originality)
        self.journalism_phrases = {
            'according to', 'sources say', 'officials said', 'reported',
            'in a statement', 'press release', 'spokesperson', 'confirmed',
            'investigation', 'analysis', 'review', 'study', 'research'
        }
        
        # Stop words to exclude from vocabulary analysis
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them',
            'their', 'we', 'us', 'our', 'you', 'your', 'he', 'she', 'him', 'her'
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze text originality and return score with detailed factors.
        
        Returns:
            dict: {
                "score": float (0-100),
                "factors": dict with detailed breakdown
            }
        """
        text_lower = text.lower()
        
        # Calculate individual metrics
        vocabulary_richness = self._calculate_vocabulary_richness(text_lower)
        phrase_uniqueness = self._calculate_phrase_uniqueness(text_lower)
        structural_variety = self._calculate_structural_variety(text)
        information_density = self._calculate_information_density(text_lower)
        template_penalty = self._calculate_template_penalty(text_lower)
        
        # Weighted combination
        # Academic note: Weights based on linguistic research on text quality
        weights = {
            'vocabulary': 0.25,
            'phrase': 0.25,
            'structure': 0.20,
            'density': 0.20,
            'template': 0.10  # Penalty factor
        }
        
        base_score = (
            vocabulary_richness * weights['vocabulary'] +
            phrase_uniqueness * weights['phrase'] +
            structural_variety * weights['structure'] +
            information_density * weights['density']
        )
        
        # Apply template penalty
        final_score = base_score * (1 - template_penalty * weights['template'] / 100)
        
        # Normalize to 0-100
        originality_score = max(0, min(100, final_score))
        
        return {
            "score": originality_score,
            "factors": {
                "vocabulary_richness": round(vocabulary_richness, 1),
                "phrase_uniqueness": round(phrase_uniqueness, 1),
                "structural_variety": round(structural_variety, 1),
                "information_density": round(information_density, 1),
                "template_penalty": round(template_penalty, 1),
                "explanation": self._generate_explanation(
                    vocabulary_richness, phrase_uniqueness,
                    structural_variety, information_density, template_penalty
                )
            }
        }
    
    def _calculate_vocabulary_richness(self, text: str) -> float:
        """
        Calculate Type-Token Ratio (TTR) for vocabulary diversity.
        
        TTR = unique words / total words
        Higher TTR indicates richer vocabulary and more original content.
        
        Academic note: TTR is a standard measure in computational linguistics
        for lexical diversity assessment.
        """
        # Tokenize and clean
        words = re.findall(r'\b[a-z]+\b', text)
        
        if len(words) < 10:
            return 50  # Neutral for very short texts
        
        # Remove stop words for content word analysis
        content_words = [w for w in words if w not in self.stop_words]
        
        if not content_words:
            return 30
        
        # Calculate TTR
        unique_words = set(content_words)
        ttr = len(unique_words) / len(content_words)
        
        # For longer texts, use root TTR (more stable)
        if len(content_words) > 100:
            ttr = len(unique_words) / math.sqrt(len(content_words))
            # Normalize root TTR to 0-1 range (typical values 5-15)
            ttr = min(1, ttr / 15)
        
        # Scale to 0-100
        score = ttr * 100
        return score
    
    def _calculate_phrase_uniqueness(self, text: str) -> float:
        """
        Analyze n-gram diversity to detect repetitive patterns.
        
        Method:
        - Extract 3-grams (trigrams)
        - Calculate ratio of unique trigrams to total
        - Penalize repeated phrases
        """
        words = re.findall(r'\b[a-z]+\b', text)
        
        if len(words) < 10:
            return 50
        
        # Generate trigrams
        trigrams = []
        for i in range(len(words) - 2):
            trigram = ' '.join(words[i:i+3])
            trigrams.append(trigram)
        
        if not trigrams:
            return 50
        
        # Calculate uniqueness ratio
        unique_trigrams = set(trigrams)
        uniqueness_ratio = len(unique_trigrams) / len(trigrams)
        
        # Check for filler phrases
        filler_count = sum(1 for phrase in self.filler_phrases if phrase in text)
        filler_penalty = min(30, filler_count * 10)
        
        score = uniqueness_ratio * 100 - filler_penalty
        return max(0, score)
    
    def _calculate_structural_variety(self, text: str) -> float:
        """
        Measure sentence structure diversity.
        
        Indicators:
        - Sentence length variation
        - Punctuation variety
        - Paragraph structure
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 3:
            return 50
        
        # Calculate sentence length variance
        lengths = [len(s.split()) for s in sentences]
        mean_length = sum(lengths) / len(lengths)
        variance = sum((l - mean_length) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        
        # Good variety: std_dev between 3-10
        if 3 <= std_dev <= 10:
            length_score = 100
        elif std_dev < 3:
            length_score = std_dev * 33  # Too uniform
        else:
            length_score = max(50, 100 - (std_dev - 10) * 5)  # Too varied
        
        # Check sentence starters diversity
        starters = [s.split()[0].lower() if s.split() else '' for s in sentences]
        starter_diversity = len(set(starters)) / len(starters) * 100
        
        # Combine scores
        score = (length_score * 0.6 + starter_diversity * 0.4)
        return score
    
    def _calculate_information_density(self, text: str) -> float:
        """
        Measure information content density.
        
        Higher density indicates more substantive content.
        Based on:
        - Named entity-like patterns (capitalized words)
        - Numeric data presence
        - Specific details vs vague statements
        """
        words = text.split()
        
        if len(words) < 20:
            return 50
        
        # Count potential named entities (capitalized words not at sentence start)
        sentences = re.split(r'[.!?]+', text)
        entity_count = 0
        for sentence in sentences:
            words_in_sent = sentence.split()
            for i, word in enumerate(words_in_sent[1:], 1):
                if word and word[0].isupper():
                    entity_count += 1
        
        # Count numbers and statistics
        numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', text)
        number_density = len(numbers) / len(words) * 100
        
        # Count specific indicators (dates, locations, names)
        specific_patterns = [
            r'\b\d{4}\b',  # Years
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b',
            r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
        ]
        specific_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in specific_patterns)
        
        # Calculate density score
        entity_score = min(40, entity_count * 2)
        number_score = min(30, number_density * 10)
        specific_score = min(30, specific_count * 5)
        
        score = entity_score + number_score + specific_score
        return min(100, score)
    
    def _calculate_template_penalty(self, text: str) -> float:
        """
        Detect template/boilerplate phrases common in fake news.
        Does NOT penalize legitimate journalism phrases.
        
        Returns penalty score (higher = more templated = less original)
        """
        # Only count actual fake news templates
        template_count = sum(1 for phrase in self.template_phrases if phrase in text)
        
        # Reduce penalty if journalism phrases are present (legitimate content)
        journalism_count = sum(1 for phrase in self.journalism_phrases if phrase in text)
        
        # Each template phrase adds 20% penalty, but journalism reduces it
        penalty = max(0, template_count * 20 - journalism_count * 5)
        return min(100, penalty)
    
    def _generate_explanation(self, vocab: float, phrase: float,
                             struct: float, density: float, template: float) -> str:
        """Generate human-readable explanation."""
        explanations = []
        
        if vocab > 70:
            explanations.append("Rich vocabulary diversity")
        elif vocab < 40:
            explanations.append("Limited vocabulary range")
        
        if phrase > 70:
            explanations.append("Unique phrasing patterns")
        elif phrase < 40:
            explanations.append("Repetitive phrase patterns detected")
        
        if struct > 70:
            explanations.append("Good structural variety")
        elif struct < 40:
            explanations.append("Monotonous sentence structure")
        
        if density > 60:
            explanations.append("High information density")
        elif density < 30:
            explanations.append("Low specific information content")
        
        if template > 30:
            explanations.append("Template phrases detected")
        
        if not explanations:
            explanations.append("Average originality indicators")
        
        return "; ".join(explanations)
