"""Tavily search wrapper with error handling and retry logic."""

import logging
import time
import json
from typing import Dict, List, Any, Optional
import requests
import sys
import os

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(".."))

from config import Config

logger = logging.getLogger(__name__)

class TavilySearchTool:
    """Tavily search wrapper with error handling and retry logic."""
    
    BASE_URL = "https://api.tavily.com/search"
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, 
                 retry_delay: float = 1.0, timeout: int = None):
        """Initialize the Tavily search tool.
        
        Args:
            api_key: Tavily API key. If None, uses the one from Config.
            max_retries: Maximum number of retries on failure.
            retry_delay: Delay between retries in seconds.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key or Config.TAVILY_API_KEY
        if not self.api_key:
            raise ValueError("Tavily API key is required")
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout or Config.API_TIMEOUT
        self.headers = {"Content-Type": "application/json"}
    
    def search(self, query: str, search_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform a search with retry logic.
        
        Args:
            query: Search query string.
            search_params: Additional search parameters.
            
        Returns:
            Search results as a dictionary.
            
        Raises:
            Exception: If the search fails after all retries.
        """
        search_params = search_params or {}
        payload = {
            "api_key": self.api_key,
            "query": query,
            **search_params
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Tavily search attempt {attempt + 1}/{self.max_retries}: {query}")
                response = requests.post(
                    self.BASE_URL,
                    headers=self.headers,
                    data=json.dumps(payload),
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Tavily search successful: {query}")
                return result
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tavily search attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    sleep_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Tavily search failed after {self.max_retries} attempts: {str(e)}")
                    raise Exception(f"Failed to get search results after {self.max_retries} attempts") from e
    
    def search_job_market(self, query: str) -> Dict[str, Any]:
        """Specialized search for job market research.
        
        Args:
            query: Job market related query.
            
        Returns:
            Search results focused on job market data.
        """
        search_params = Config.TAVILY_SEARCH_PARAMS_JOB.copy()
        search_params.update({
            "include_domains": ["linkedin.com", "indeed.com", "glassdoor.com", 
                               "monster.com", "dice.com", "bls.gov"],
            "search_depth": "advanced"
        })
        
        return self.search(query, search_params)
    
    def search_courses(self, query: str) -> Dict[str, Any]:
        """Specialized search for online courses and learning resources.
        
        Args:
            query: Course or learning resource related query.
            
        Returns:
            Search results focused on educational resources.
        """
        search_params = Config.TAVILY_SEARCH_PARAMS_COURSE.copy()
        search_params.update({
            "include_domains": ["coursera.org", "udemy.com", "edx.org", "pluralsight.com", 
                               "udacity.com", "linkedin.com/learning", "skillshare.com"],
            "search_depth": "advanced"
        })
        
        return self.search(query, search_params) 