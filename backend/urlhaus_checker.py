import requests
import re
from typing import Dict, Optional

class URLhausChecker:
    """
    Checks URLs against URLhaus malware database (abuse.ch)
    Free, no API key required
    """
    
    def __init__(self):
        self.api_url = "https://urlhaus-api.abuse.ch/v1/url/"
        self.host_api = "https://urlhaus-api.abuse.ch/v1/host/"
    
    def check_url(self, url: str) -> Dict:
        """Check a single URL against URLhaus database"""
        try:
            response = requests.post(
                self.api_url,
                data={"url": url},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("query_status") == "is_malware":
                    return {
                        "is_malicious": True,
                        "threat": data.get("threat", "malware"),
                        "tags": data.get("tags", []),
                        "risk_score": 95,
                        "source": "URLhaus"
                    }
                elif data.get("query_status") == "no_results":
                    return {
                        "is_malicious": False,
                        "risk_score": 0,
                        "source": "URLhaus"
                    }
            
            return {"is_malicious": False, "risk_score": 0, "source": "URLhaus"}
            
        except Exception as e:
            print(f"URLhaus check failed: {e}")
            return {"is_malicious": False, "risk_score": 0, "source": "URLhaus (unavailable)"}
    
    def extract_and_check(self, text: str) -> Dict:
        """Extract URLs from text and check them"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        if not urls:
            return {
                "urls_found": 0,
                "malicious_urls": 0,
                "risk_score": 0,
                "details": "No URLs found in text"
            }
        
        malicious = []
        for url in urls[:5]:  # Check max 5 URLs
            result = self.check_url(url)
            if result.get("is_malicious"):
                malicious.append({
                    "url": url,
                    "threat": result.get("threat", "unknown")
                })
        
        risk_score = 95 if malicious else 0
        
        return {
            "urls_found": len(urls),
            "malicious_urls": len(malicious),
            "risk_score": risk_score,
            "malicious_details": malicious,
            "details": f"{len(malicious)} malicious URL(s) found" if malicious else "No malicious URLs detected"
        }


if __name__ == "__main__":
    checker = URLhausChecker()
    
    print("=== URLhaus Checker Test ===")
    
    # Test with a known safe URL
    print("\nTest 1: Safe URL")
    result = checker.check_url("https://google.com")
    print(f"Malicious: {result['is_malicious']}")
    print(f"Risk Score: {result['risk_score']}")
    
    # Test with text containing URLs
    print("\nTest 2: Text with URL")
    result2 = checker.extract_and_check(
        "Click here to verify: https://google.com"
    )
    print(f"URLs found: {result2['urls_found']}")
    print(f"Malicious: {result2['malicious_urls']}")
    print(f"Details: {result2['details']}")