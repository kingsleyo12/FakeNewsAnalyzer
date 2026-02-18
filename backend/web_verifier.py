"""
Web Search Verifier
Verifies news claims by searching credible sources online
"""

from ddgs import DDGS
import re
from typing import Dict, List, Optional
import time

class WebSearchVerifier:
    def __init__(self):
        """Initialize the web search verifier"""
        
        # Trusted news sources (high credibility)
        self.trusted_sources = [
            'reuters.com', 'bbc.com', 'bbc.co.uk', 'apnews.com', 
            'npr.org', 'pbs.org', 'nytimes.com', 'washingtonpost.com',
            'theguardian.com', 'wsj.com', 'economist.com', 'time.com',
            'cnn.com', 'nbcnews.com', 'cbsnews.com', 'abcnews.go.com',
            'usatoday.com', 'latimes.com', 'politico.com', 'thehill.com'
        ]
        
        # Fact-checking sources (highest credibility)
        self.fact_check_sources = [
            'snopes.com', 'factcheck.org', 'politifact.com', 
            'fullfact.org', 'factcheck.afp.com', 'apnews.com/APFactCheck',
            'reuters.com/fact-check', 'usatoday.com/fact-check'
        ]
        
        # Low credibility indicators (suspicious domains)
        self.suspicious_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', 
            '.work', '.click', '.link', '.loan', '.bid', '.win'
        ]
    
    def verify_claims(self, text: str, max_searches: int = 2) -> Dict:
        """
        Verify claims in text by searching the web
        
        Args:
            text: News text to verify
            max_searches: Maximum number of search queries (default 2 to avoid rate limits)
        
        Returns:
            Dictionary with verification results and score adjustment
        """
        # Extract key claims from text
        claims = self._extract_claims(text)
        
        if not claims:
            return {
                'verified': False,
                'credible_sources_found': 0,
                'fact_check_found': False,
                'debunked': False,
                'score_adjustment': 0,
                'explanation': 'No specific claims to verify',
                'sources': []
            }
        
        # Search for the most important claims (limit to avoid rate limits)
        all_results = []
        credible_count = 0
        fact_check_found = False
        debunked = False
        
        for i, claim in enumerate(claims[:max_searches]):
            try:
                # Add small delay to avoid rate limiting
                if i > 0:
                    time.sleep(1)
                
                results = self._search_claim(claim)
                all_results.extend(results)
                
                # Count credible sources
                for result in results:
                    if self._is_credible_source(result['url']):
                        credible_count += 1
                    
                    # Check if it's a fact-check article
                    if self._is_fact_check_source(result['url']):
                        fact_check_found = True
                        
                        # Check if it's marked as false/debunked
                        if self._is_debunked(result['title'], result.get('snippet', '')):
                            debunked = True
                
            except Exception as e:
                print(f"Search error for claim '{claim}': {e}")
                continue
        
        # Calculate score adjustment based on findings
        score_adjustment = self._calculate_adjustment(
            credible_count, fact_check_found, debunked, len(all_results)
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            credible_count, fact_check_found, debunked, len(all_results)
        )
        
        return {
            'verified': credible_count > 0,
            'credible_sources_found': credible_count,
            'fact_check_found': fact_check_found,
            'debunked': debunked,
            'score_adjustment': score_adjustment,
            'explanation': explanation,
            'sources': all_results[:5],  # Return top 5 sources
            'claims_searched': claims[:max_searches]
        }
    
    def _extract_claims(self, text: str) -> List[str]:
        """
        Extract key claims from text for searching
        Focuses on the most important/suspicious statements
        """
        claims = []
        text_lower = text.lower()
        
        # Extract sentences with strong claims
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences[:5]:  # Check first 5 sentences
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
            
            # Prioritize sentences with claim indicators
            claim_indicators = [
                'scientists', 'researchers', 'study', 'discover', 'found',
                'report', 'confirm', 'reveal', 'announce', 'claim',
                'according to', 'breaking', 'new evidence', 'proves'
            ]
            
            if any(indicator in sentence.lower() for indicator in claim_indicators):
                # Clean and shorten for search
                clean_claim = self._clean_claim(sentence)
                if clean_claim:
                    claims.append(clean_claim)
        
        # If no claims found with indicators, use first meaningful sentence
        if not claims and sentences:
            for sentence in sentences[:3]:
                clean = self._clean_claim(sentence)
                if clean and len(clean.split()) > 5:
                    claims.append(clean)
                    break
        
        return claims[:2]  # Return max 2 claims to search
    
    def _clean_claim(self, claim: str) -> str:
        """Clean and shorten claim for searching"""
        # Remove excessive punctuation
        claim = re.sub(r'[!?]{2,}', '', claim)
        
        # Remove all caps words (often clickbait)
        claim = re.sub(r'\b[A-Z]{4,}\b', '', claim)
        
        # Keep first 60 characters (good search query length)
        words = claim.split()[:12]  # ~12 words
        clean = ' '.join(words).strip()
        
        return clean if len(clean) > 10 else ''
    
    def _search_claim(self, claim: str) -> List[Dict]:
        """
        Search DuckDuckGo for a claim
        Returns list of search results
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(claim, max_results=5))
                
                return [
                    {
                        'title': r.get('title', ''),
                        'url': r.get('href', ''),
                        'snippet': r.get('body', '')
                    }
                    for r in results
                ]
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []
    
    def _is_credible_source(self, url: str) -> bool:
        """Check if URL is from a credible news source"""
        url_lower = url.lower()
        return any(source in url_lower for source in self.trusted_sources)
    
    def _is_fact_check_source(self, url: str) -> bool:
        """Check if URL is from a fact-checking site"""
        url_lower = url.lower()
        return any(source in url_lower for source in self.fact_check_sources)
    
    def _is_debunked(self, title: str, snippet: str) -> bool:
        """Check if content indicates the claim was debunked"""
        combined = (title + ' ' + snippet).lower()
        
        debunk_keywords = [
            'false', 'fake', 'debunked', 'not true', 'misleading',
            'hoax', 'myth', 'incorrect', 'wrong', 'misinformation',
            'fact check: false', 'rating: false', 'pants on fire'
        ]
        
        return any(keyword in combined for keyword in debunk_keywords)
    
    def _calculate_adjustment(self, credible_count: int, fact_check_found: bool, 
                             debunked: bool, total_results: int) -> float:
        """
        Calculate score adjustment based on search results
        Positive = increase fake score, Negative = decrease fake score
        """
        adjustment = 0
        
        # If debunked by fact-checkers → strong evidence of fake news
        if debunked:
            adjustment += 40  # Major increase
        
        # If found on fact-check sites but not debunked → might be verified true
        elif fact_check_found:
            adjustment -= 20  # Decrease fake score
        
        # If found on multiple credible sources → likely real news
        if credible_count >= 3:
            adjustment -= 30  # Strong decrease
        elif credible_count >= 1:
            adjustment -= 15  # Moderate decrease
        
        # If no results found at all → suspicious (but could be very new)
        if total_results == 0:
            adjustment += 10  # Slight increase
        
        # If only found on non-credible sources
        elif credible_count == 0 and total_results > 0:
            adjustment += 20  # Moderate increase
        
        return adjustment
    
    def _generate_explanation(self, credible_count: int, fact_check_found: bool,
                             debunked: bool, total_results: int) -> str:
        """Generate human-readable explanation of search results"""
        
        if debunked:
            return f"Debunked by fact-checkers; Found in {credible_count} credible sources"
        
        if credible_count >= 3:
            return f"Verified by {credible_count} credible news sources"
        
        if credible_count >= 1:
            return f"Found in {credible_count} credible source(s)"
        
        if fact_check_found:
            return "Found in fact-checking databases (not marked as false)"
        
        if total_results == 0:
            return "No search results found for claims"
        
        if total_results > 0 and credible_count == 0:
            return f"Only found on non-credible sources ({total_results} results)"
        
        return "Unable to verify claims"


# Test the verifier
if __name__ == "__main__":
    print("="*60)
    print("WEB SEARCH VERIFIER TEST")
    print("="*60)
    
    verifier = WebSearchVerifier()
    
    # Test Case 1: Fake news claim
    test1 = """
    SHOCKING: Scientists discover hand-clapping cures cancer! 
    Researchers at a major university found that clapping your hands 
    200 times daily eliminates cancer cells. Big Pharma doesn't want 
    you to know this!
    """
    
    print("\n📰 Test 1: Fake News Claim")
    print("-" * 60)
    print("Searching web for verification...")
    result1 = verifier.verify_claims(test1)
    print(f"Credible sources found: {result1['credible_sources_found']}")
    print(f"Fact-check found: {result1['fact_check_found']}")
    print(f"Debunked: {result1['debunked']}")
    print(f"Score adjustment: {result1['score_adjustment']:+.1f}")
    print(f"Explanation: {result1['explanation']}")
    
    # Test Case 2: Real news (example - adjust based on current events)
    test2 = """
    According to Reuters, researchers from Harvard University published 
    a new study on climate change impacts. The peer-reviewed research 
    was published in the journal Nature.
    """
    
    print("\n📰 Test 2: Real News with Credible Source")
    print("-" * 60)
    print("Searching web for verification...")
    result2 = verifier.verify_claims(test2)
    print(f"Credible sources found: {result2['credible_sources_found']}")
    print(f"Fact-check found: {result2['fact_check_found']}")
    print(f"Score adjustment: {result2['score_adjustment']:+.1f}")
    print(f"Explanation: {result2['explanation']}")
    
    print("\n" + "="*60)
    print("✅ Test Complete!")
    print("="*60)