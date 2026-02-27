
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Add parent directory to path so we can import modules if run from tests/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fake_news import FakeNewsAnalyzer
from originality import OriginalityAnalyzer
from cyber_threat import CyberThreatAnalyzer

load_dotenv()

def run_all_tests():
    print("="*80)
    print("🛡️  FAKE NEWS ANALYZER - MASTER TEST SUITE")
    print("="*80)

    # 1. INITIALization
    print("\n[STEP 1] Initializing Core Engines...")
    try:
        fn = FakeNewsAnalyzer()
        orig = OriginalityAnalyzer()
        ct = CyberThreatAnalyzer()
        print("✅ Engines Ready.")
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return

    # 2. TEST CASES (Aggregated from all test files)
    test_suite = [
        {
            "name": "REAL NEWS (Standard)",
            "text": "The Bank of England has raised interest rates to 5.25% in an effort to combat persistent inflation.",
            "url": "https://www.bbc.com",
            "type": "legit"
        },
        {
            "name": "ABSURD FAKE (Satire)",
            "text": "Scientists Confirm That Nigerian Aunty Hand-clapping Is a Completely New Form of Quantum Communication.",
            "url": "http://satire-news.com",
            "type": "fake"
        },
        {
            "name": "PHISHING (Cyber)",
            "text": "URGENT: Your bank account is suspended. Click here to verify your credentials: http://fake-bank-login.xyz",
            "url": "http://fake-bank-login.xyz",
            "type": "cyber"
        },
        {
            "name": "CRYPTO SCAM",
            "text": "Send 1 BTC to this wallet and get 2 BTC back instantly! Guaranteed returns by Elon Musk.",
            "url": "http://crypto-double.tk",
            "type": "cyber"
        }
    ]

    for test in test_suite:
        print(f"\n>>> TESTING: {test['name']}")
        print("-" * 40)
        
        fn_res = fn.analyze(test['text'])
        orig_res = orig.analyze(test['text'])
        ct_res = ct.analyze(test['text'], test['url'])

        print(f"Fake Prob: {fn_res['probability']}% | Full Analysis: {fn_res['is_full_analysis']}")
        print(f"Originality: {orig_res['score']}%")
        print(f"Cyber Risk: {ct_res['risk_score']}% ({ct_res['threat_level']})")
        print(f"Threats: {ct_res['factors']['detected_threats']}")

    # 3. API CONNECTIVITY
    print("\n[STEP 3] System Health Check...")
    
    # Fact Check API
    key = os.getenv('GOOGLE_FACT_CHECK_KEY')
    if key:
        try:
            r = requests.get(f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query=test&key={key}", timeout=5)
            print(f"Google Fact Check API: {'ONLINE' if r.status_code == 200 else 'OFFLINE/ERROR'}")
        except:
            print("Google Fact Check API: OFFLINE")
    
    # Web Search
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        import time
        time.sleep(5)  # Let DDG rate-limit cool down after test cases
        with DDGS() as ddgs:
            list(ddgs.text("test", max_results=1))
            print("Web Search Verifier: ONLINE")
    except Exception as e:
        err = str(e).lower()
        if "ratelimit" in err:
            print("Web Search Verifier: RATE-LIMITED (module works, but temporarily throttled by DuckDuckGo)")
        else:
            print(f"Web Search Verifier: OFFLINE ({e})")

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)

if __name__ == "__main__":
    run_all_tests()
