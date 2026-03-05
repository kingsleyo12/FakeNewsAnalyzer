"""
Artificial Verifier Module — powered by Groq (Llama 3)
Uses extremely fast Llama 3 for deep linguistic and logical analysis of claims.
(Drop-in replacement for GeminiAnalyzer / Anthropic Analyzer)
"""

import os
import json
import time
from typing import Dict

try:
    from openai import OpenAI
    OPENAI_PACKAGE_AVAILABLE = True
except ImportError:
    OPENAI_PACKAGE_AVAILABLE = False


class ArtificialVerifier:
    """
    Powered by Groq's high-speed inference engine running Llama 3 8B.
    """

    # Class-level cooldown: if quota exceeded, skip for a little bit
    _unavailable_until = 0

    def __init__(self, api_key: str):
        self.api_key = api_key
        if not OPENAI_PACKAGE_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")
            
        # Initialize the OpenAI client pointing to the Groq base URL
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )
        # Using Llama 3.1 8B because it's fast, free, and smart enough for this layer
        self.model = "llama-3.1-8b-instant"

    def analyze_text(self, text: str) -> Dict:
        """
        Performs deep reasoning on the provided text to detect misinformation.
        Fails immediately on quota/rate errors — never blocks the request.
        """
        # Skip entirely if we're in cooldown from a recent quota error
        if time.time() < ArtificialVerifier._unavailable_until:
            remaining = int(ArtificialVerifier._unavailable_until - time.time())
            print(f"  NLP Engine skipped (cooldown, {remaining}s remaining)")
            return self._unavailable_response()

        # Truncate to ~2000 chars to keep costs/tokens low
        text_snippet = text[:2000]

        prompt = f"""Analyze the following text for potential misinformation, fake news, or logical fallacies.
Respond ONLY with a valid JSON object (no markdown, no text outside the JSON) with these exact keys:
- probability: integer 0-100, probability the text is fake or misleading
- reasoning: string, one sentence explanation of your score
- fallacies: array of strings, logical fallacies identified (max 3, empty array if none)
- manipulation_tactics: array of strings, emotional/psychological manipulation tactics detected (max 3, empty array if none)
- verdict: string, exactly one of: TRUE / FALSE / MIXED / UNVERIFIED

Text to analyze:
{text_snippet}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert misinformation analyst. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.2,
                timeout=15,  # 15s hard timeout — never block longer than this
            )

            content = response.choices[0].message.content.strip()
            # Strip markdown fences if present
            content = content.replace('```json', '').replace('```', '').strip()
            
            # Additional cleanup for Llama outputs if it adds preamble
            if content.find('{') != -1 and content.rfind('}') != -1:
                content = content[content.find('{'):content.rfind('}')+1]

            result = json.loads(content)

            print(f" NLP Engine: {result.get('verdict', 'UNVERIFIED')} ({result.get('probability', 50)}% prob)")
            return {
                'probability': int(result.get('probability', 50)),
                'reasoning': result.get('reasoning', 'Analysis completed by Contextual NLP.'),
                'fallacies': result.get('fallacies', []),
                'manipulation_tactics': result.get('manipulation_tactics', []),
                'verdict': result.get('verdict', 'UNVERIFIED')
            }

        except Exception as e:
            error_str = str(e)
            print(f"NLP Engine error ({type(e).__name__}): {error_str[:150]}")

            rate_limit_signals = ['429', 'rate_limit', 'overloaded', 'Too Many Requests', 'insufficient', 'quota', 'credit']

            if any(kw.lower() in error_str.lower() for kw in rate_limit_signals):
                # Temporary rate limit or quota — 5 min cooldown for Groq
                ArtificialVerifier._unavailable_until = time.time() + 300
                print(f"  NLP Engine rate limited/quota — skipping layer for 5 minutes")
                
            return self._unavailable_response()

    def _unavailable_response(self) -> Dict:
        return {
            'probability': 50,
            'reasoning': "NLP analysis skipped (API unavailable or rate limited).",
            'fallacies': [],
            'manipulation_tactics': [],
            'verdict': 'UNVERIFIED'
        }


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("Please set GROQ_API_KEY in .env")
        sys.exit(1)

    analyzer = ArtificialVerifier(key)
    test_text = "Scientists have discovered that eating purple rocks can cure all diseases instantly!"
    print(json.dumps(analyzer.analyze_text(test_text), indent=2))
