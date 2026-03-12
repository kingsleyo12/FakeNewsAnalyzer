import sys
import os

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fake_news import HybridFakeNewsAnalyzer

def generate_typo_text(text):
    """Swap some key characters for numbers or symbols to evade basic keyword matching"""
    replacements = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '5'}
    chars = list(text)
    for i in range(len(chars)):
        if chars[i].lower() in replacements and i % 5 == 0:  # ~20% of matching chars
            chars[i] = replacements[chars[i].lower()]
    return "".join(chars)

def generate_whitespace_text(text):
    """Add random spaces inside long words to break tokenization and sub-word embeddings"""
    words = text.split()
    perturbed = []
    for word in words:
        if len(word) > 5:
            mid = len(word) // 2
            perturbed.append(word[:mid] + " " + word[mid:])
        else:
            perturbed.append(word)
    return " ".join(perturbed)

def generate_benign_append_text(text):
    """Append real, boring news to dilute the bad signal (a classic poisoning/evasion attack)"""
    benign = (
        " In other news, the local school board held a predictable meeting discussing the budget for next year. "
        "Weather forecasts indicate mild rain over the weekend with temperatures remaining stable near 70 degrees. "
        "The city council also voted to approve the new park renovation project."
    )
    return text + benign

def test_adversarial_robustness():
    print("[*] Initializing Analyzer for Adversarial Testing...")
    analyzer = HybridFakeNewsAnalyzer()
    
    baseline_text = (
        "SHOCKING: Scientists discover that 5G microchips are being secretly "
        "implanted via mandatory vaccines! The deep state planners and big pharma "
        "are hiding the truth to control your mind. Open your eyes sheeple before it's too late!"
    )
    
    # 1. Baseline Score
    res_base = analyzer.analyze(baseline_text)
    base_score = res_base['fake_news_probability']
    print("\n=======================================================")
    print(f" Baseline Fake News Probability: {base_score}%")
    print("=======================================================")
    
    assert base_score >= 70, f"Error: Baseline text failed to trigger a high fake news score. Score: {base_score}%"
    
    vulnerabilities_found = 0
    max_acceptable_drop = 30.0  # We allow up to a 30% confidence drop against perturbations
    
    # 2. Typo Injection (Leet Speak / Character Swapping)
    typo_text = generate_typo_text(baseline_text)
    res_typo = analyzer.analyze(typo_text)
    typo_score = res_typo['fake_news_probability']
    drop_typo = base_score - typo_score
    print(f"\n[Evasion 1] Typo Injection (Leet Speak):")
    print(f"Sample: {typo_text[:60]}...")
    print(f"Score:  {typo_score}% (Confidence Drop: {drop_typo:.1f}%)")
    if drop_typo > max_acceptable_drop:
        print("[!] VULNERABILITY DETECTED: Model is susceptible to Typo Injection evasion.")
        vulnerabilities_found += 1
        
    # 3. Whitespace Token Breaking
    ws_text = generate_whitespace_text(baseline_text)
    res_ws = analyzer.analyze(ws_text)
    ws_score = res_ws['fake_news_probability']
    drop_ws = base_score - ws_score
    print(f"\n[Evasion 2] Whitespace Injection (Token Breaking):")
    print(f"Sample: {ws_text[:60]}...")
    print(f"Score:  {ws_score}% (Confidence Drop: {drop_ws:.1f}%)")
    if drop_ws > max_acceptable_drop:
        print("[!] VULNERABILITY DETECTED: Model is susceptible to Whitespace / Token evasion.")
        vulnerabilities_found += 1
        
    # 4. Dilution Attack (Benign text appending)
    diluted_text = generate_benign_append_text(baseline_text)
    res_diluted = analyzer.analyze(diluted_text)
    diluted_score = res_diluted['fake_news_probability']
    drop_diluted = base_score - diluted_score
    print(f"\n[Evasion 3] Benign Text Dilution Attack:")
    print(f"Sample appended data: ... {diluted_text[-60:]}")
    print(f"Score:  {diluted_score}% (Confidence Drop: {drop_diluted:.1f}%)")
    if drop_diluted > max_acceptable_drop:
        print("[!] VULNERABILITY DETECTED: Model is susceptible to Dilution evasion.")
        vulnerabilities_found += 1
        
    print("\n=======================================================")
    if vulnerabilities_found > 0:
        print(f"❌ ADVERSARIAL TEST FAILED: {vulnerabilities_found} evasion vulnerabilities found.")
        print(f"The system's confidence dropped by more than {max_acceptable_drop}% points.")
        # We assert False here to ensure CI/CD pipelines fail when ran automatically
        assert False, "Adversarial Test Suite Failed. See logs for evasion vulnerabilities."
    else:
        print("✅ ADVERSARIAL TEST PASSED: Model showed strong robustness against perturbations!")

if __name__ == "__main__":
    test_adversarial_robustness()
