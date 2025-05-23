"""Configuration module for the Career Advisor Agent."""

import os
import json

class Config:
    """Global configuration management."""
    
    # API Keys
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # API Configuration
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Parse JSON configurations from environment
    TAVILY_SEARCH_PARAMS_JOB = json.loads(os.getenv("TAVILY_SEARCH_PARAMS_JOB", 
                                                   '{"search_depth": "advanced", "max_results": 10}'))
    TAVILY_SEARCH_PARAMS_COURSE = json.loads(os.getenv("TAVILY_SEARCH_PARAMS_COURSE", 
                                                      '{"search_depth": "advanced", "max_results": 10}'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Rate Limiting
    RATE_LIMIT_MINUTE = int(os.getenv("RATE_LIMIT_MINUTE", "60"))
    RATE_LIMIT_HOUR = int(os.getenv("RATE_LIMIT_HOUR", "1000"))
    
    # Timeout Settings
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    
    @classmethod
    def validate(cls):
        """Validate the configuration settings."""
        if not cls.TAVILY_API_KEY:
            raise ValueError("Missing TAVILY_API_KEY in environment variables.")
        
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("Missing OPENROUTER_API_KEY in environment variables.") 