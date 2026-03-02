"""
Fact Checker Module
Uses Google Fact Check Tools API
Improved confidence scoring + better claim extraction
"""

import requests
import re
from typing import Dict, List, Optional

class FactChecker:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

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
        claims = self._extract_claims(text)

        if not claims:
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 30,
                'fact_checks_found': 0,
                'explanation': 'No specific claims found to fact-check'
            }

        known_false = self._check_known_false(text.lower())
        if known_false:
            return {
                'verdict': 'FALSE',
                'confidence': 95,
                'fact_checks_found': 1,
                'explanation': 'Contains known debunked claim',
                'matched_claim': known_false
            }

        fact_check_results = []
        for claim in claims[:3]:
            try:
                print(f"[*] Querying API for: {claim}")
                results = self._query_google_factcheck(claim)
                if results:
                    fact_check_results.extend(results)
            except Exception as e:
                print(f"Fact check API error: {e}")

        return self._calculate_verdict(fact_check_results)

    def _extract_claims(self, text: str) -> List[str]:
        sentences = re.split(r'(?<![\d])([.!?]+)(?![\d])', text)
        sentences = [s.strip() for s in sentences if s and not re.fullmatch(r'[.!?]+', s.strip())]

        claims = []
        for sentence in sentences[:10]:
            if len(sentence) < 20:
                continue

            claim_indicators = [
                'according to', 'scientists', 'researchers', 'study shows',
                'data shows', 'report', 'claims', 'states that', 'confirms',
                'proves', 'evidence', 'found that', 'discovered', 'announced'
            ]

            if any(i in sentence.lower() for i in claim_indicators):
                clean = self._clean_claim(sentence)
                if clean:
                    claims.append(clean)

        if not claims:
            for sentence in sentences[:3]:
                clean = self._clean_claim(sentence)
                if clean:
                    claims.append(clean)

        return list(dict.fromkeys(claims))[:3]

    def _clean_claim(self, claim: str) -> Optional[str]:
        fluff = ['BREAKING:', 'SHOCKING:', 'JUST IN:', 'READ MORE:', 'WATCH:',
                 'EXCLUSIVE:', 'URGENT:', 'UPDATE:']
        for f in fluff:
            claim = claim.replace(f, '').replace(f.lower(), '')

        claim = re.sub(r'^(and|but|so|then|also|however|meanwhile)\s+', '', claim.strip(), flags=re.IGNORECASE)
        claim = ' '.join(claim.split())
        claim = re.sub(r"'s\b", '', claim)
        claim = re.sub(r'["\']', '', claim)

        words = claim.split()
        if len(words) < 4:
            return None

        return ' '.join(words[:14])  # improved matching

    def _check_known_false(self, text_lower: str) -> Optional[str]:
        clean_text = text_lower.replace('-', ' ').replace('_', ' ')
        for false_claim in self.known_false_claims:
            clean_false = false_claim.replace('-', ' ')
            if clean_false in clean_text:
                return false_claim
        return None

    def _query_google_factcheck(self, claim: str) -> List[Dict]:
        try:
            params = {'key': self.api_key, 'query': claim, 'languageCode': 'en'}
            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code != 200:
                print("Fact Check API error:", response.status_code)
                return []

            data = response.json()
            results = []

            for claim_review in data.get('claims', []):
                for review in claim_review.get('claimReview', []):
                    results.append({
                        'rating': review.get('textualRating', ''),
                        'publisher': review.get('publisher', {}).get('name', 'Unknown'),
                        'title': review.get('title', ''),
                        'url': review.get('url', ''),
                        'claim_text': claim_review.get('text', '')
                    })

            return results

        except Exception as e:
            print("Fact Check API error:", e)
            return []

    def _calculate_verdict(self, fact_check_results: List[Dict]) -> Dict:
        if not fact_check_results:
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 40,
                'fact_checks_found': 0,
                'explanation': 'No fact-checks found for these claims'
            }

        false_keywords = ['pants on fire', 'mostly false', 'false', 'incorrect', 'fake']
        true_keywords = ['mostly true', 'true', 'correct', 'accurate']
        mixed_keywords = ['mixed', 'half true', 'half-true', 'partly']

        false_count = true_count = mixed_count = 0

        for r in fact_check_results:
            rating = r['rating'].lower()
            if any(k in rating for k in false_keywords):
                false_count += 1
            elif any(k in rating for k in true_keywords):
                true_count += 1
            elif any(k in rating for k in mixed_keywords):
                mixed_count += 1

        total = len(fact_check_results)
        publishers = list({r['publisher'] for r in fact_check_results})
        publisher_bonus = min(len(publishers) * 5, 15)

        if false_count:
            confidence = min(75 + false_count * 10, 95)
            return {
                'verdict': 'FALSE',
                'confidence': confidence,
                'fact_checks_found': total,
                'explanation': f'Rated FALSE by {false_count} fact-checker(s): {", ".join(publishers[:3])}',
                'sources': fact_check_results[:3]
            }

        if true_count > false_count:
            confidence = min(70 + true_count * 12 + publisher_bonus, 95)
            return {
                'verdict': 'TRUE',
                'confidence': confidence,
                'fact_checks_found': total,
                'explanation': f'Verified TRUE by {true_count} fact-checker(s): {", ".join(publishers[:3])}',
                'sources': fact_check_results[:3]
            }

        if mixed_count:
            return {
                'verdict': 'MIXED',
                'confidence': 55,
                'fact_checks_found': total,
                'explanation': f'Mixed ratings from {total} fact-checker(s)',
                'sources': fact_check_results[:3]
            }

        return {
            'verdict': 'UNVERIFIED',
            'confidence': 50,
            'fact_checks_found': total,
            'explanation': f'Found {total} fact-check(s) but ratings unclear',
            'sources': fact_check_results[:3]
        }


if __name__ == "__main__":
    API_KEY = input("Enter your Google Fact Check API key: ").strip()
    checker = FactChecker(API_KEY)

    test_claim = "The United Nations has 193 member states."
    result = checker.check_claims(test_claim)

    print("\nVerdict:", result["verdict"])
    print("Confidence:", result["confidence"])
    print("Explanation:", result["explanation"])