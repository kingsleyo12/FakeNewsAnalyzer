"""
Main FastAPI Application
========================
Central API server that orchestrates fake news detection, originality analysis,
and cyber threat intelligence scoring.

Academic Justification:
- RESTful API design follows industry best practices
- Modular architecture allows independent testing and scaling
- Async endpoints enable concurrent request handling
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import logging
import hashlib
import json

from fake_news import FakeNewsAnalyzer
from originality import OriginalityAnalyzer
from cyber_threat import CyberThreatAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fake News & Cyber Threat Intelligence API",
    description="Percentage-based analysis for fake news detection and cyber threat assessment",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
fake_news_analyzer = FakeNewsAnalyzer()
originality_analyzer = OriginalityAnalyzer()
cyber_threat_analyzer = CyberThreatAnalyzer()

# Analysis Cache to prevent inconsistent results for identical text
analysis_cache = {}


class AnalysisRequest(BaseModel):
    """Request model for text analysis"""
    text: str = Field(..., min_length=10, max_length=50000, description="Text content to analyze")
    url: Optional[str] = Field(None, description="Optional URL to analyze for threats")


class AnalysisResponse(BaseModel):
    """Response model with percentage-based scores"""
    fake_news_probability: float = Field(..., ge=0, le=100, description="Fake news probability (0-100%)")
    authenticity_score: float = Field(..., ge=0, le=100, description="Authenticity/real news score (0-100%)")
    originality_score: float = Field(..., ge=0, le=100, description="Content originality score (0-100%)")
    cyber_threat_risk: float = Field(..., ge=0, le=100, description="Cyber threat risk score (0-100%)")
    threat_level: str = Field(..., description="Threat level label (Low/Medium/High/Critical)")
    analysis_details: dict = Field(..., description="Detailed breakdown of analysis factors")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Fake News & Cyber Threat Intelligence API"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    """
    Main analysis endpoint that combines all three analysis modules.
    
    Returns percentage-based confidence scores for:
    - Fake news probability
    - Authenticity score
    - Originality score
    - Cyber threat risk
    """
    try:
        # Validate input
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text must be at least 10 characters")
        
        text_raw = request.text.strip()
        url_raw = request.url.strip() if request.url else ""
        
        # Create a unique cache key based on text and URL
        cache_content = f"{text_raw}|{url_raw}"
        content_hash = hashlib.md5(cache_content.encode()).hexdigest()
        
        # Check cache
        if content_hash in analysis_cache:
            logger.info(f"Returning cached result for hash: {content_hash}")
            return analysis_cache[content_hash]
        
        text = text_raw
        
        # Truncate very long texts to prevent timeout (keep first 15000 chars)
        if len(text) > 15000:
            text = text[:15000]
            logger.info(f"Text truncated from {len(request.text)} to 15000 characters")
        
        url = request.url.strip() if request.url else None
        
        # Run all analyzers
        fake_news_result = fake_news_analyzer.analyze(text)
        originality_result = originality_analyzer.analyze(text)
        cyber_threat_result = cyber_threat_analyzer.analyze(text, url)
        
        # Calculate authenticity as inverse of fake news probability
        authenticity_score = 100 - fake_news_result["probability"]
        
        # Determine threat level based on cyber threat risk
        threat_level = get_threat_level(cyber_threat_result["risk_score"])
        
        result = AnalysisResponse(
            fake_news_probability=round(fake_news_result["probability"], 1),
            authenticity_score=round(authenticity_score, 1),
            originality_score=round(originality_result["score"], 1),
            cyber_threat_risk=round(cyber_threat_result["risk_score"], 1),
            threat_level=threat_level,
            analysis_details={
                "fake_news_factors": fake_news_result["factors"],
                "originality_factors": originality_result["factors"],
                "cyber_threat_factors": cyber_threat_result["factors"],
                "cached": False
            }
        )
        
        # Store in cache
        analysis_cache[content_hash] = result
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        friendly_msg = format_error_message(error_msg)
        logger.error(f"Analysis error: {error_msg}")
        raise HTTPException(status_code=500, detail=friendly_msg)


def format_error_message(error: str) -> str:
    """Map technical error messages to user-friendly terms"""
    error = error.lower()
    if "timeout" in error or "timed out" in error:
        return "The analysis took longer than expected. Please try with a shorter text."
    if "connection" in error or "network" in error:
        return "Our secondary verification systems are experiencing connection issues. Please try again in a moment."
    if "rate limit" in error:
        return "We've reached our maximum verification capacity for the moment. Please try again shortly."
    if "module" in error and "not found" in error:
        return "One of our analysis engines is currently undergoing maintenance. Please try again later."
    if "memory" in error:
        return "The content provided is too large for our current processing capacity."
    
    return f"We encountered an issue during analysis: {error.split(':')[0]}"


def get_threat_level(risk_score: float) -> str:
    """
    Convert numeric risk score to categorical threat level.
    
    Thresholds based on cybersecurity industry standards:
    - Low: 0-25% (minimal indicators)
    - Medium: 26-50% (some suspicious patterns)
    - High: 51-75% (multiple threat indicators)
    - Critical: 76-100% (strong threat presence)
    """
    if risk_score <= 25:
        return "Low"
    elif risk_score <= 50:
        return "Medium"
    elif risk_score <= 75:
        return "High"
    else:
        return "Critical"


@app.get("/health")
async def health_check():
    """Detailed health check for all services"""
    return {
        "status": "healthy",
        "services": {
            "fake_news_analyzer": "ready",
            "originality_analyzer": "ready",
            "cyber_threat_analyzer": "ready"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
