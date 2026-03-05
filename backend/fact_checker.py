"""
Fact Checker Module (LLM Zero-Shot Agent)
Uses Groq's Llama-3-70B model to verify historical, scientific, and political claims
based on its extensive pre-training data.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FactChecker:
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.3-70b-versatile"  # Powerful model for factual recall
            # logger.info("  Fact Checker initialized with Groq API (Llama-3-70B)")
        except Exception as e:
            logger.error(f"Failed to initialize Groq Fact Checker: {e}")
            self.client = None

        # Known absurd claims that don't even need API calls
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
        if not self.client:
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 0,
                'fact_checks_found': 0,
                'explanation': 'Client not initialized'
            }

        if not text or len(text.strip()) < 10:
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 30,
                'fact_checks_found': 0,
                'explanation': 'Input too short to fact-check'
            }

        # Fast path: skip LLM for obvious conspiracy theories
        known_false = self._check_known_false(text.lower())
        if known_false:
            return {
                'verdict': 'FALSE',
                'confidence': 95,
                'fact_checks_found': 1,
                'explanation': 'Matches known universally debunked claim',
                'matched_claim': known_false
            }

        try:
            # Query the LLM
            logger.info("[*] Querying Llama-3 Fact Checker Agent...")
            return self._query_llm_fact_checker(text)
        except Exception as e:
            logger.error(f"LLM Fact Check API error: {e}")
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 40,
                'fact_checks_found': 0,
                'explanation': f'LLM API Exception: {str(e)}'
            }

    def _check_known_false(self, text_lower: str) -> Optional[str]:
        clean_text = text_lower.replace('-', ' ').replace('_', ' ')
        for false_claim in self.known_false_claims:
            clean_false = false_claim.replace('-', ' ')
            if clean_false in clean_text:
                return false_claim
        return None

    def _query_llm_fact_checker(self, text: str) -> Dict:
        prompt = f"""You are a professional fact-checker like Snopes or PolitiFact.
Analyze the following text/claims and determine if the core factual assertions are TRUE, FALSE, MIXED, or UNVERIFIED (if you don't know or if it's pure opinion).

Text to analyze:
\"\"\"{text}\"\"\"

Output your response ONLY as a strictly valid JSON object. Do not include markdown code blocks.
Format:
{{
    "verdict": "TRUE" | "FALSE" | "MIXED" | "UNVERIFIED",
    "confidence": integer between 0 and 100,
    "explanation": "A concise 1-sentence explanation of why it is true or false."
}}
"""
        
        # We enforce a JSON response format using Llama 3's function-calling/json mode
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a highly accurate, objective fact-checking AI. Output only raw JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0, # Complete determinism for fact checking
            max_tokens=200,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        
        try:
            result = json.loads(content)
            
            # Normalize the output
            verdict = result.get('verdict', 'UNVERIFIED').upper()
            if verdict not in ['TRUE', 'FALSE', 'MIXED', 'UNVERIFIED']:
                verdict = 'UNVERIFIED'
                
            confidence = int(result.get('confidence', 50))
            explanation = result.get('explanation', 'AI Fact Checker provided no explanation.')

            return {
                'verdict': verdict,
                'confidence': confidence,
                'fact_checks_found': 1 if verdict != 'UNVERIFIED' else 0,
                'explanation': f"{explanation}"
            }
            
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM JSON output")
            return {
                'verdict': 'UNVERIFIED',
                'confidence': 40,
                'fact_checks_found': 0,
                'explanation': 'Failed to parse AI response'
            }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    API_KEY = os.environ.get('GROQ_API_KEY')
    if not API_KEY:
        print("Please set GROQ_API_KEY environment variable")
        exit(1)
        
    checker = FactChecker(API_KEY)

    print("\n--- Test 1 ---")
    test_claim = "The United Nations has 193 member states."
    result = checker.check_claims(test_claim)
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Explanation: {result['explanation']}")
    
    print("\n--- Test 2 ---")
    test_claim = "Abraham Lincoln was the first president of the United States."
    result = checker.check_claims(test_claim)
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Explanation: {result['explanation']}")
