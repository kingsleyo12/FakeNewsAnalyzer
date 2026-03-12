from pydantic import ValidationError
from app import AnalysisRequest

def test_valid_request():
    payload = {
        "text": "This is a completely normal text that should pass validation without issues.",
        "url": "https://example.com"
    }
    req = AnalysisRequest(**payload)
    assert req.text == payload["text"]
    assert str(req.url) == payload["url"]

def test_xss_injection_request():
    payload = {
        "text": "<script>alert('XSS')</script> This text has an XSS payload.",
        "url": "https://example.com"
    }
    try:
        req = AnalysisRequest(**payload)
        assert False, "Should have raised ValidationError due to script tags"
    except ValidationError as e:
        assert "Potentially unsafe payload" in str(e)

def test_invalid_url():
    payload = {
        "text": "This is a normal text but the URL is bad. We still need 10 chars.",
        "url": "ht://bad-url"
    }
    try:
        req = AnalysisRequest(**payload)
        assert False, "Should have raised ValidationError due to bad URL"
    except ValidationError as e:
        assert "url" in str(e).lower()

def test_short_text():
    payload = {
        "text": "Tiny"
    }
    try:
        req = AnalysisRequest(**payload)
        assert False, "Should have raised ValidationError due to short text"
    except ValidationError as e:
        assert "10" in str(e) or "short" in str(e).lower()

def test_html_tag_removal():
    payload = {
        "text": "<b>This should be stripped of bold tags and still work perfectly fine!</b>"
    }
    req = AnalysisRequest(**payload)
    assert "<b>" not in req.text
    assert req.text == "This should be stripped of bold tags and still work perfectly fine!"

if __name__ == "__main__":
    print("Testing Valid Request...")
    test_valid_request()
    print("Testing Invalid URL...")
    test_invalid_url()
    print("Testing Short Text...")
    test_short_text()
    print("Testing XSS Injection...")
    test_xss_injection_request()
    print("Testing HTML Tag removal/handling...")
    test_html_tag_removal()
    print("All validation tests passed successfully!")
