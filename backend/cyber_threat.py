"""
Cyber Threat Intelligence Module
================================
Analyzes text and URLs for cybersecurity threats including phishing,
social engineering, and malicious content indicators.

Academic Justification:
- Weighted scoring reflects real-world threat assessment methodologies
- Multiple indicator categories provide comprehensive coverage
- Risk scoring aligns with NIST cybersecurity framework principles
- Heuristic detection complements signature-based approaches

Percentage Calculation:
- URL analysis (phishing indicators, suspicious domains)
- Content analysis (social engineering patterns)
- Urgency/pressure tactics detection
- Credential harvesting indicators
- Final score: weighted sum of all threat categories
"""

import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse


class CyberThreatAnalyzer:
    """
    Analyzes content for cybersecurity threats and returns risk scores.
    """
    
    def __init__(self):
        # Phishing keywords commonly used in attacks
        self.phishing_keywords = {
            'verify your account', 'confirm your identity', 'update your information',
            'suspended', 'unauthorized access', 'security alert', 'unusual activity',
            'click here immediately', 'act now', 'limited time', 'expires soon',
            'your account will be', 'failure to', 'within 24 hours', 'within 48 hours',
            'verify immediately', 'confirm now', 'urgent action required'
        }
        
        # Social engineering patterns
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
        
        # Urgency indicators
        self.urgency_indicators = {
            'urgent', 'immediately', 'right now', 'asap', 'emergency',
            'act fast', 'dont delay', 'time sensitive', 'expires',
            'last chance', 'final notice', 'action required', 'respond now'
        }
        
        # Credential harvesting indicators
        self.credential_indicators = {
            'password', 'username', 'login', 'signin', 'sign in',
            'credit card', 'ssn', 'social security', 'bank account',
            'routing number', 'pin', 'cvv', 'security code', 'mother maiden'
        }
        
        # Suspicious TLDs often used in phishing
        self.suspicious_tlds = {
            '.xyz', '.top', '.club', '.work', '.click', '.link',
            '.info', '.online', '.site', '.website', '.space',
            '.tk', '.ml', '.ga', '.cf', '.gq'  # Free TLDs
        }
        
        # Legitimate domains (whitelist)
        self.trusted_domains = {
            'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
            'facebook.com', 'twitter.com', 'linkedin.com', 'github.com',
            'stackoverflow.com', 'wikipedia.org', 'gov', 'edu'
        }
    
    def analyze(self, text: str, url: Optional[str] = None) -> Dict:
        """
        Analyze text and optional URL for cyber threats.
        
        Returns:
            dict: {
                "risk_score": float (0-100),
                "factors": dict with detailed breakdown
            }
        """
        text_lower = text.lower()
        
        # Calculate individual threat scores
        phishing_score = self._calculate_phishing_score(text_lower)
        social_eng_score = self._calculate_social_engineering_score(text_lower)
        urgency_score = self._calculate_urgency_score(text_lower)
        credential_score = self._calculate_credential_harvesting_score(text_lower)
        url_score = self._analyze_url(url) if url else 0
        
        # Extract URLs from text if none provided
        if not url:
            extracted_urls = self._extract_urls(text)
            if extracted_urls:
                url_scores = [self._analyze_url(u) for u in extracted_urls[:5]]
                url_score = max(url_scores) if url_scores else 0
        
        # Weighted combination based on threat severity
        # Academic note: Weights reflect relative danger of each indicator type
        weights = {
            'phishing': 0.25,
            'social_engineering': 0.20,
            'urgency': 0.15,
            'credential': 0.25,
            'url': 0.15
        }
        
        base_risk = (
            phishing_score * weights['phishing'] +
            social_eng_score * weights['social_engineering'] +
            urgency_score * weights['urgency'] +
            credential_score * weights['credential'] +
            url_score * weights['url']
        )
        
        # Apply multiplier for combined threats (synergistic risk)
        threat_count = sum(1 for s in [phishing_score, social_eng_score, 
                                       credential_score, url_score] if s > 50)
        if threat_count >= 3:
            base_risk *= 1.2  # 20% increase for multiple high threats
        
        risk_score = max(0, min(100, base_risk))
        
        return {
            "risk_score": risk_score,
            "factors": {
                "phishing_indicators": round(phishing_score, 1),
                "social_engineering_score": round(social_eng_score, 1),
                "urgency_pressure_score": round(urgency_score, 1),
                "credential_harvesting_risk": round(credential_score, 1),
                "url_risk_score": round(url_score, 1),
                "detected_threats": self._get_detected_threats(
                    phishing_score, social_eng_score, urgency_score,
                    credential_score, url_score
                ),
                "explanation": self._generate_explanation(
                    phishing_score, social_eng_score, urgency_score,
                    credential_score, url_score
                )
            }
        }
    
    def _calculate_phishing_score(self, text: str) -> float:
        """
        Detect phishing indicators in text.
        
        Scoring: Each keyword match adds to score, with diminishing returns
        to prevent over-scoring on keyword-stuffed content.
        """
        matches = sum(1 for keyword in self.phishing_keywords if keyword in text)
        
        # Logarithmic scaling to prevent over-scoring
        if matches == 0:
            return 0
        
        # First match = 30%, each additional adds less
        score = 30 + (matches - 1) * 15
        return min(100, score)
    
    def _calculate_social_engineering_score(self, text: str) -> float:
        """
        Detect social engineering patterns using regex matching.
        """
        pattern_matches = 0
        
        for pattern in self.social_engineering_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                pattern_matches += 1
        
        # Each pattern match = 20%
        score = pattern_matches * 20
        return min(100, score)
    
    def _calculate_urgency_score(self, text: str) -> float:
        """
        Measure urgency/pressure tactics commonly used in attacks.
        """
        urgency_matches = sum(1 for indicator in self.urgency_indicators 
                             if indicator in text)
        
        # Check for time-based pressure
        time_patterns = [
            r'\b\d+\s*(?:hour|day|minute)s?\b',
            r'\bexpires?\s+(?:in|on|at)\b',
            r'\bdeadline\b',
            r'\blast\s+(?:chance|warning|notice)\b'
        ]
        time_matches = sum(1 for p in time_patterns if re.search(p, text, re.IGNORECASE))
        
        # Combine scores
        score = urgency_matches * 15 + time_matches * 20
        return min(100, score)
    
    def _calculate_credential_harvesting_score(self, text: str) -> float:
        """
        Detect attempts to harvest credentials or sensitive information.
        """
        credential_matches = sum(1 for indicator in self.credential_indicators 
                                if indicator in text)
        
        # Check for form-like requests
        form_patterns = [
            r'(?:enter|type|provide|input)\s+(?:your|the)',
            r'(?:fill|complete)\s+(?:out|in|the)',
            r'(?:submit|send)\s+(?:your|the)',
        ]
        form_matches = sum(1 for p in form_patterns if re.search(p, text, re.IGNORECASE))
        
        score = credential_matches * 12 + form_matches * 15
        return min(100, score)
    
    def _analyze_url(self, url: str) -> float:
        """
        Analyze URL for phishing and malicious indicators.
        
        Checks:
        - Suspicious TLDs
        - IP address instead of domain
        - Excessive subdomains
        - Typosquatting patterns
        - URL shorteners
        - Suspicious characters
        """
        if not url:
            return 0
        
        try:
            # Clean and parse URL
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            risk_score = 0
            
            # Check for IP address instead of domain
            if re.match(r'\d+\.\d+\.\d+\.\d+', domain):
                risk_score += 40
            
            # Check for suspicious TLDs
            for tld in self.suspicious_tlds:
                if domain.endswith(tld):
                    risk_score += 25
                    break
            
            # Check for excessive subdomains (more than 3)
            subdomain_count = domain.count('.')
            if subdomain_count > 3:
                risk_score += 20
            
            # Check for typosquatting of known brands
            typosquat_patterns = [
                r'g[o0]{2}gle', r'faceb[o0]{2}k', r'amaz[o0]n',
                r'micr[o0]s[o0]ft', r'app[l1]e', r'paypa[l1]',
                r'netf[l1]ix', r'[l1]inkedin'
            ]
            for pattern in typosquat_patterns:
                if re.search(pattern, domain):
                    risk_score += 35
                    break
            
            # Check for URL shorteners
            shorteners = ['bit.ly', 'tinyurl', 't.co', 'goo.gl', 'ow.ly', 'is.gd']
            if any(s in domain for s in shorteners):
                risk_score += 15
            
            # Check for suspicious path patterns
            suspicious_paths = ['login', 'signin', 'verify', 'secure', 'account', 'update']
            if any(p in path for p in suspicious_paths):
                risk_score += 15
            
            # Check for @ symbol (credential injection)
            if '@' in url:
                risk_score += 30
            
            # Check for excessive special characters
            special_chars = sum(1 for c in url if c in '-_~')
            if special_chars > 5:
                risk_score += 10
            
            # Reduce score for trusted domains
            for trusted in self.trusted_domains:
                if trusted in domain:
                    risk_score = max(0, risk_score - 30)
                    break
            
            return min(100, risk_score)
            
        except Exception:
            return 20  # Default moderate risk for unparseable URLs
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text content."""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # Also find URLs without protocol
        domain_pattern = r'\b(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
        domains = re.findall(domain_pattern, text)
        
        return list(set(urls + domains))
    
    def _get_detected_threats(self, phishing: float, social: float,
                             urgency: float, credential: float, url: float) -> List[str]:
        """Return list of detected threat types."""
        threats = []
        
        if phishing > 40:
            threats.append("Phishing indicators")
        if social > 40:
            threats.append("Social engineering patterns")
        if urgency > 40:
            threats.append("Urgency/pressure tactics")
        if credential > 40:
            threats.append("Credential harvesting attempt")
        if url > 40:
            threats.append("Suspicious URL detected")
        
        return threats if threats else ["No significant threats detected"]
    
    def _generate_explanation(self, phishing: float, social: float,
                             urgency: float, credential: float, url: float) -> str:
        """Generate human-readable threat explanation."""
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
        
        if not explanations:
            explanations.append("Low threat indicators")
        
        return "; ".join(explanations)
