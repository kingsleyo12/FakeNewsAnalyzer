"""
Fact Checker Module
Uses Google Fact Check Tools API
"""

import requests
import re
from typing import Dict, List, Optional

class FactChecker:
    def __init__(self, api_key: str):
        """
        Initialize fact checker with Google Fact Check API
        
        Args:
            api_key: Google Fact Check Tools API key
        """
        self.api_key = api_key
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        
        # Known false claims database (backup)
        self.known_false_claims = [
            'hand clapping cures cancer',
            'clapping hands cures cancer',
            '5g causes covid',
            '5g towers cause covid',
            'bill gates microchip',
            'microchips in vaccines',
            'vaccines cause autism',
            'flat earth',
            'moon landing fake',
            'moon landing was faked',
            'chemtrails control',
            'drinking bleach cures',
            'covid is a hoax',
            'covid-19 is a hoax',
            'stolen election',
            'election was rigged',
            'water is turning frogs gay'
        ]
    
    def check_claims(self, text: str) -> Dict:
        """
        Check claims using Google Fact Check API
        
        Args:
            text: Text to fact-check
            
        Returns:
            Dictionary with fact-check results
        """
        # Extract key claims from text
        claims = self._extract_claims(text)
        
        if not claims:
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 30,
                'fact_checks_found': 0,
                'explanation': 'No specific claims found to fact-check'
            }
        
        # Check against known false claims first (fast)
        known_false = self._check_known_false(text.lower())
        if known_false:
            return {
                'verdict': 'FALSE',
                'confidence': 95,
                'fact_checks_found': 1,
                'explanation': 'Contains known debunked claim',
                'matched_claim': known_false
            }
        
        # Query Google Fact Check API
        fact_check_results = []
        for claim in claims[:3]:  # Check top 3 claims
            try:
                # Log for debugging - helps see what the API is actually searching
                print(f"[*] Querying API for: {claim}")
                results = self._query_google_factcheck(claim)
                if results:
                    fact_check_results.extend(results)
            except Exception as e:
                print(f"Fact check API error: {e}")
        
        # Calculate verdict based on results
        verdict = self._calculate_verdict(fact_check_results)
        
        return verdict
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract potential factual claims from text"""
        # Split on sentence boundaries — but NOT on decimal points like 5.25 or 3.14
        # Negative lookbehind: don't split when period is preceded by a digit
        # Negative lookahead:  don't split when period is followed by a digit
        sentences = re.split(r'(?<![\d])([.!?]+)(?![\d])', text)
        # re.split with a capturing group interleaves delimiters; filter them out
        sentences = [s.strip() for s in sentences if s and not re.fullmatch(r'[.!?]+', s.strip())]

        claims = []
        for sentence in sentences[:10]:  # Check first 10 sentences
            sentence = sentence.strip()

            # Skip very short sentences
            if len(sentence) < 20:
                continue

            # Look for claim indicators
            claim_indicators = [
                'according to', 'scientists', 'researchers', 'study shows',
                'data shows', 'report', 'claims', 'states that', 'confirms',
                'proves', 'evidence', 'found that', 'discovered', 'announced'
            ]

            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in claim_indicators):
                clean_claim = self._clean_claim(sentence)
                if clean_claim:
                    claims.append(clean_claim)

        # If no indicator-based claims found, fall back to first meaningful sentences
        if not claims:
            for sentence in sentences[:3]:
                clean = self._clean_claim(sentence)
                if clean:
                    claims.append(clean)

        # Deduplicate
        unique_claims = list(dict.fromkeys(claims))
        return unique_claims[:3]

    def _clean_claim(self, claim: str) -> str:
        """
        Clean and shorten claim for Google Fact Check API matching.
        The API works best with SHORT keyword phrases (6-8 words), not
        long verbatim sentences. Overly specific long queries rarely match.
        """
        # Remove common fluff prefixes
        fluff = ['BREAKING:', 'SHOCKING:', 'JUST IN:', 'READ MORE:', 'WATCH:',
                 'EXCLUSIVE:', 'URGENT:', 'UPDATE:']
        for f in fluff:
            claim = claim.replace(f, '').replace(f.lower(), '')

        # Remove leading conjunctions / filler that add nothing to the search
        claim = re.sub(r'^(and|but|so|then|also|however|meanwhile)\s+', '', claim.strip(), flags=re.IGNORECASE)

        # Collapse whitespace
        claim = ' '.join(claim.split())

        # Strip possessives and punctuation that confuse the API
        claim = re.sub(r"'s\b", '', claim)
        claim = re.sub(r'["\']', '', claim)

        words = claim.split()

        # Too short to be meaningful
        if len(words) < 4:
            return None

        # Keep only first 8 words — short queries match the Fact Check DB far better
        return ' '.join(words[:8])
    
    def _check_known_false(self, text_lower: str) -> Optional[str]:
        """Check against database of known false claims (fuzzy-ish)"""
        # Remove common separators for easier matching
        clean_text = text_lower.replace('-', ' ').replace('_', ' ')
        for false_claim in self.known_false_claims:
            clean_false = false_claim.replace('-', ' ')
            if clean_false in clean_text:
                return false_claim
        return None
    
    def _query_google_factcheck(self, claim: str) -> List[Dict]:
        """
        Query Google Fact Check API
        
        Args:
            claim: Claim text to check
            
        Returns:
            List of fact-check results
        """
        try:
            params = {
                'key': self.api_key,
                'query': claim,
                'languageCode': 'en'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                claims = data.get('claims', [])
                
                results = []
                for claim_review in claims:
                    # Extract fact-check information
                    claim_reviews = claim_review.get('claimReview', [])
                    
                    for review in claim_reviews:
                        rating = review.get('textualRating', '').upper()
                        publisher = review.get('publisher', {}).get('name', 'Unknown')
                        title = review.get('title', '')
                        url = review.get('url', '')
                        
                        results.append({
                            'rating': rating,
                            'publisher': publisher,
                            'title': title,
                            'url': url,
                            'claim_text': claim_review.get('text', '')
                        })
                
                return results
            
            elif response.status_code == 403:
                print("API key error: Check if Fact Check Tools API is enabled")
                return []
            else:
                print(f"Fact Check API error: {response.status_code}")
                return []
                
        except requests.exceptions.Timeout:
            print("Fact Check API timeout")
            return []
        except Exception as e:
            print(f"Fact Check API error: {e}")
            return []
    
    def _calculate_verdict(self, fact_check_results: List[Dict]) -> Dict:
        """
        Calculate overall verdict from fact-check results
        
        Args:
            fact_check_results: List of fact-check results from API
            
        Returns:
            Verdict dictionary
        """
        if not fact_check_results:
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 40,
                'fact_checks_found': 0,
                'explanation': 'No fact-checks found for these claims'
            }
        
        # Count ratings
        false_count = 0
        true_count = 0
        mixed_count = 0
        
        false_keywords = ['false', 'incorrect', 'pants on fire', 'mostly false', 'fake']
        true_keywords = ['true', 'correct', 'accurate', 'mostly true']
        mixed_keywords = ['mixed', 'half true', 'half-true', 'partly']
        
        for result in fact_check_results:
            rating = result['rating'].lower()
            
            if any(keyword in rating for keyword in false_keywords):
                false_count += 1
            elif any(keyword in rating for keyword in true_keywords):
                true_count += 1
            elif any(keyword in rating for keyword in mixed_keywords):
                mixed_count += 1
        
        total_checks = len(fact_check_results)
        
        # Determine verdict
        if false_count > 0:
            # Any false rating means likely false
            confidence = min(70 + (false_count * 10), 95)
            publishers = [r['publisher'] for r in fact_check_results[:3]]
            
            return {
                'verdict': 'FALSE',
                'confidence': confidence,
                'fact_checks_found': total_checks,
                'false_ratings': false_count,
                'true_ratings': true_count,
                'explanation': f'Rated FALSE by {false_count} fact-checker(s): {", ".join(publishers)}',
                'sources': fact_check_results[:3]
            }
        
        elif true_count > false_count:
            confidence = min(60 + (true_count * 10), 85)
            publishers = [r['publisher'] for r in fact_check_results[:3]]
            
            return {
                'verdict': 'TRUE',
                'confidence': confidence,
                'fact_checks_found': total_checks,
                'false_ratings': false_count,
                'true_ratings': true_count,
                'explanation': f'Verified TRUE by {true_count} fact-checker(s): {", ".join(publishers)}',
                'sources': fact_check_results[:3]
            }
        
        elif mixed_count > 0:
            return {
                'verdict': 'MIXED',
                'confidence': 55,
                'fact_checks_found': total_checks,
                'explanation': f'Mixed ratings from {total_checks} fact-checker(s) - partially true/false',
                'sources': fact_check_results[:3]
            }
        
        else:
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 50,
                'fact_checks_found': total_checks,
                'explanation': f'Found {total_checks} fact-check(s) but ratings unclear',
                'sources': fact_check_results[:3]
            }


# Test the fact checker
if __name__ == "__main__":
    import os
    
    print("="*60)
    print("GOOGLE FACT CHECK API TEST")
    print("="*60)
    
    # You need to set your API key
    API_KEY = input("Enter your Google Fact Check API key: ").strip()
    
    if not API_KEY:
        print(" No API key provided. Please set your API key.")
        exit(1)
    
    checker = FactChecker(API_KEY)
    
    # Test Case 1: Known false claim
    test1 = """
    Vaccines cause autism in children. This has been proven by multiple studies.
    The government is hiding this information from the public.
    """
    
    print("\n Test 1: Debunked Claim (Vaccines-Autism)")
    print("-" * 60)
    result1 = checker.check_claims(test1)
    print(f"Verdict: {result1['verdict']}")
    print(f"Confidence: {result1['confidence']}%")
    print(f"Fact-checks found: {result1['fact_checks_found']}")
    print(f"Explanation: {result1['explanation']}")
    
    # Test Case 2: Political claim
    test2 = """
    According to reports, the 2020 election was rigged.
    There was widespread voter fraud that changed the outcome.
    """
    
    print("\n Test 2: Political Claim")
    print("-" * 60)
    result2 = checker.check_claims(test2)
    print(f"Verdict: {result2['verdict']}")
    print(f"Confidence: {result2['confidence']}%")
    print(f"Fact-checks found: {result2['fact_checks_found']}")
    print(f"Explanation: {result2['explanation']}")
    
    # Test Case 3: General factual statement
    test3 = """
    Climate change is causing global temperatures to rise.
    Scientists have documented this trend over decades.
    """
    
    print("\n Test 3: Scientific Claim")
    print("-" * 60)
    result3 = checker.check_claims(test3)
    print(f"Verdict: {result3['verdict']}")
    print(f"Confidence: {result3['confidence']}%")
    print(f"Fact-checks found: {result3['fact_checks_found']}")
    print(f"Explanation: {result3['explanation']}")
    
    print("\n" + "="*60)
    print(" Tests Complete!")
    print("="*60)