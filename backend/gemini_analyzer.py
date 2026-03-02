"""
Gemini AI Analyzer Module
Uses Google Gemini API for deep linguistic and logical analysis of claims.
"""

import os
import json
import google.generativeai as genai
from typing import Dict, Optional

class GeminiAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        # Using flash for speed and efficiency
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_text(self, text: str) -> Dict:
        """
        Performs deep reasoning on the provided text to detect misinformation.
        """
        prompt = f"""
        Analyze the following text for potential misinformation, fake news, or logical fallacies.
        Provide a detailed analysis in JSON format with the following keys:
        - probability: (0-100) probability that the text is fake/misleading
        - reasoning: a brief explanation of why you gave this score
        - fallacies: a list of logical fallacies identified (if any)
        - manipulation_tactics: a list of emotional or psychological manipulation tactics detected
        - verdict: (TRUE/FALSE/MIXED/UNVERIFIED)

        Text to analyze:
        {text}

        Respond ONLY with the JSON object.
        """

        try:
            response = self.model.generate_content(prompt)
            # Remove markdown code blocks if present
            response_text = response.text.replace('```json', '').replace('```', '').strip()
            result = json.loads(response_text)
            
            # Ensure required keys exist
            return {
                'probability': result.get('probability', 50),
                'reasoning': result.get('reasoning', 'Analysis completed by AI.'),
                'fallacies': result.get('fallacies', []),
                'manipulation_tactics': result.get('manipulation_tactics', []),
                'verdict': result.get('verdict', 'UNVERIFIED')
            }
        except Exception as e:
            print(f"Gemini API error: {e}")
            return {
                'probability': 50,
                'reasoning': f"AI analysis failed: {str(e)}",
                'fallacies': [],
                'manipulation_tactics': [],
                'verdict': 'UNVERIFIED'
            }

if __name__ == "__main__":
    # Quick test
    import sys
    load_dotenv()
    key = os.getenv("GOOGLE_GEMINI_KEY")
    if not key:
        print("Please set GOOGLE_GEMINI_KEY in .env")
        sys.exit(1)
        
    analyzer = GeminiAnalyzer(key)
    test_text = "Scientists have discovered that eating purple rocks can cure all diseases instantly!"
    print(json.dumps(analyzer.analyze_text(test_text), indent=2))
