"""
Cyber Threat Intelligence Module
================================
Analyzes text and URLs for cybersecurity threats including phishing,
social engineering, and malicious content indicators.
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

try:
    from urlhaus_checker import URLhausChecker
    URLHAUS_AVAILABLE = True
except ImportError:
    URLHAUS_AVAILABLE = False


class CyberThreatAnalyzer:

    def __init__(self):
        self.phishing_keywords = {
            'verify your account', 'confirm your identity', 'update your information',
            'suspended', 'unauthorized access', 'security alert', 'unusual activity',
            'click here immediately', 'act now', 'limited time', 'expires soon',
            'your account will be', 'failure to', 'within 24 hours', 'within 48 hours',
            'verify immediately', 'confirm now', 'urgent action required'
        }

        self.social_engineering_patterns = [
            r'(?:click|tap) (?:here|this|the link)',
            r'(?:enter|provide|confirm) your (?:password|credentials|login)',
            r'(?:bank|paypal|amazon|apple|microsoft|google) (?:account|security)',
            r'(?:won|winner|selected|chosen) (?:a |the )?(?:prize|lottery|gift)',
            r'(?:inheritance|million|billion) (?:dollars|usd|euros)',
            r'(?:nigerian|foreign) (?:prince|diplomat|official)',
            r'wire (?:transfer|money)',
            r'(?:western union|moneygram)',
        ]

        self.urgency_indicators = {
            'urgent', 'immediately', 'right now', 'asap', 'emergency',
            'act fast', 'dont delay', 'time sensitive', 'expires',
            'last chance', 'final notice', 'action required', 'respond now'
        }

        self.credential_indicators = {
            'password', 'username', 'login', 'signin', 'sign in',
            'credit card', 'ssn', 'social security', 'bank account',
            'routing number', 'pin', 'cvv', 'security code', 'mother maiden'
        }

        self.suspicious_tlds = {
            '.xyz', '.top', '.club', '.work', '.click', '.link',
            '.info', '.online', '.site', '.website', '.space',
            '.tk', '.ml', '.ga', '.cf', '.gq'
        }

        self.trusted_domains = {
            'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
            'facebook.com', 'twitter.com', 'linkedin.com', 'github.com',
            'stackoverflow.com', 'wikipedia.org', 'gov', 'edu'
        }

        self.malware_patterns = {
            'crypto scams': ['send bitcoin', 'send eth', 'wallet address', 'double your crypto',
                             'guaranteed returns', 'investment opportunity', 'crypto giveaway'],
            'tech support scams': ['call this number', 'microsoft support', 'virus detected',
                                   'computer infected', 'refund department', 'tech support'],
            'romance scams': ['send money', 'western union', 'gift cards', 'stranded',
                              'medical emergency', 'help me financially'],
            'advance fee fraud': ['transfer fee', 'release funds', 'processing fee',
                                  'claim your prize', 'lottery winnings']
        }

        self.dark_web_terms = {
            'ransomware', 'botnet', 'keylogger', 'rootkit', 'trojan',
            'zero-day', 'exploit kit', 'ddos', 'doxxing', 'swatting',
            'carding', 'fullz', 'drops', 'mule account'
        }

        # URLhaus API integration
        if URLHAUS_AVAILABLE:
            self.urlhaus = URLhausChecker()
            print(" URLhaus malware database connected")
        else:
            self.urlhaus = None

    def analyze(self, text: str, url: Optional[str] = None) -> Dict:
        text_lower = text.lower()

        # Calculate all component scores
        phishing_score = self._calculate_phishing_score(text_lower)
        social_eng_score = self._calculate_social_engineering_score(text_lower)
        urgency_score = self._calculate_urgency_score(text_lower)
        credential_score = self._calculate_credential_harvesting_score(text_lower)
        malware_score = self._calculate_malware_score(text_lower)

        url_score = 0
        if url:
            url_score = self._analyze_url(url)
        else:
            extracted_urls = self._extract_urls(text)
            if extracted_urls:
                url_scores = [self._analyze_url(u) for u in extracted_urls[:5]]
                url_score = max(url_scores) if url_scores else 0

        # URLhaus API check
        urlhaus_score = 0
        urlhaus_details = "No URLs checked"
        if self.urlhaus:
            try:
                urlhaus_result = self.urlhaus.extract_and_check(text)
                urlhaus_score = urlhaus_result['risk_score']
                urlhaus_details = urlhaus_result['details']
                if urlhaus_score > 0:
                    url_score = max(url_score, urlhaus_score)
            except Exception as e:
                print(f"URLhaus error: {e}")

        # Use highest score + bonus for multiple active threats
        component_scores = [
            phishing_score, social_eng_score,
            urgency_score, credential_score,
            malware_score, url_score
        ]

        highest_score = max(component_scores)
        active_threats = sum(1 for s in component_scores if s > 20)
        multi_threat_bonus = (active_threats - 1) * 10 if active_threats > 1 else 0

        risk_score = min(100, highest_score + multi_threat_bonus)

        return {
            "risk_score": round(risk_score, 1),
            "threat_level": self._get_threat_level(risk_score),
            "factors": {
                "phishing_indicators": round(phishing_score, 1),
                "social_engineering_score": round(social_eng_score, 1),
                "urgency_pressure_score": round(urgency_score, 1),
                "credential_harvesting_risk": round(credential_score, 1),
                "url_risk_score": round(url_score, 1),
                "malware_patterns": round(malware_score, 1),
                "urlhaus_check": urlhaus_details,
                "detected_threats": self._get_detected_threats(
                    phishing_score, social_eng_score, urgency_score,
                    credential_score, url_score, malware_score
                ),
                "explanation": self._generate_explanation(
                    phishing_score, social_eng_score, urgency_score,
                    credential_score, url_score, malware_score
                )
            }
        }

    def _calculate_phishing_score(self, text: str) -> float:
        matches = sum(1 for keyword in self.phishing_keywords if keyword in text)
        if matches == 0:
            return 0
        score = matches * 30
        return min(100, score)

    def _calculate_social_engineering_score(self, text: str) -> float:
        pattern_matches = sum(
            1 for pattern in self.social_engineering_patterns
            if re.search(pattern, text, re.IGNORECASE)
        )
        return min(100, pattern_matches * 25)

    def _calculate_urgency_score(self, text: str) -> float:
        urgency_matches = sum(1 for indicator in self.urgency_indicators if indicator in text)
        time_patterns = [
            r'\b\d+\s*(?:hour|day|minute)s?\b',
            r'\bexpires?\s+(?:in|on|at)\b',
            r'\bdeadline\b',
            r'\blast\s+(?:chance|warning|notice)\b'
        ]
        time_matches = sum(1 for p in time_patterns if re.search(p, text, re.IGNORECASE))
        return min(100, urgency_matches * 25 + time_matches * 25)

    def _calculate_credential_harvesting_score(self, text: str) -> float:
        credential_matches = sum(1 for indicator in self.credential_indicators if indicator in text)
        form_patterns = [
            r'(?:enter|type|provide|input)\s+(?:your|the)',
            r'(?:fill|complete)\s+(?:out|in|the)',
            r'(?:submit|send)\s+(?:your|the)',
        ]
        form_matches = sum(1 for p in form_patterns if re.search(p, text, re.IGNORECASE))
        return min(100, credential_matches * 30 + form_matches * 20)

    def _calculate_malware_score(self, text: str) -> float:
        score = 0
        text_lower = text.lower()
        for category, patterns in self.malware_patterns.items():
            matches = sum(1 for p in patterns if p in text_lower)
            if matches > 0:
                score += 40 * matches
        dark_matches = sum(1 for term in self.dark_web_terms if term in text_lower)
        score += dark_matches * 25
        return min(100, score)

    def _get_threat_level(self, score: float) -> str:
        if score >= 75:
            return "Critical"
        elif score >= 50:
            return "High"
        elif score >= 25:
            return "Medium"
        else:
            return "Low"

    def _analyze_url(self, url: str) -> float:
        if not url:
            return 0
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            risk_score = 0

            if re.match(r'\d+\.\d+\.\d+\.\d+', domain):
                risk_score += 40
            for tld in self.suspicious_tlds:
                if domain.endswith(tld):
                    risk_score += 25
                    break
            if domain.count('.') > 3:
                risk_score += 20
            typosquat_patterns = [
                r'g[o0]{2}gle', r'faceb[o0]{2}k', r'amaz[o0]n',
                r'micr[o0]s[o0]ft', r'app[l1]e', r'paypa[l1]',
            ]
            for pattern in typosquat_patterns:
                if re.search(pattern, domain):
                    risk_score += 35
                    break
            shorteners = ['bit.ly', 'tinyurl', 't.co', 'goo.gl', 'ow.ly']
            if any(s in domain for s in shorteners):
                risk_score += 15
            suspicious_paths = ['login', 'signin', 'verify', 'secure', 'account', 'update']
            if any(p in path for p in suspicious_paths):
                risk_score += 15
            if '@' in url:
                risk_score += 30
            for trusted in self.trusted_domains:
                if trusted in domain:
                    risk_score = max(0, risk_score - 30)
                    break
            return min(100, risk_score)
        except Exception:
            return 20

    def _extract_urls(self, text: str) -> List[str]:
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)

    def _get_detected_threats(self, phishing, social, urgency, credential, url, malware=0) -> List[str]:
        threats = []
        if phishing > 30:
            threats.append("Phishing indicators")
        if social > 30:
            threats.append("Social engineering patterns")
        if urgency > 30:
            threats.append("Urgency/pressure tactics")
        if credential > 30:
            threats.append("Credential harvesting attempt")
        if url > 30:
            threats.append("Suspicious URL detected")
        if malware > 30:
            threats.append("Malware/scam patterns detected")
        return threats if threats else ["No significant threats detected"]

    def _generate_explanation(self, phishing, social, urgency, credential, url, malware=0) -> str:
        explanations = []
        if phishing > 60:
            explanations.append("High phishing risk detected")
        elif phishing > 30:
            explanations.append("Some phishing indicators present")
        if social > 60:
            explanations.append("Strong social engineering patterns")
        elif social > 30:
            explanations.append("Possible manipulation tactics")
        if urgency > 60:
            explanations.append("High-pressure urgency tactics")
        if credential > 60:
            explanations.append("Likely credential harvesting attempt")
        elif credential > 30:
            explanations.append("Requests for sensitive information")
        if url > 60:
            explanations.append("Highly suspicious URL")
        elif url > 30:
            explanations.append("URL shows some risk indicators")
        if malware > 50:
            explanations.append("Malware or scam content detected")
        if not explanations:
            explanations.append("Low threat indicators")
        return "; ".join(explanations)  