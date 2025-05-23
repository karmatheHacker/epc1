"""Base agent class with common functionality for all agents."""

import logging
from typing import Dict, Any, Optional
import json
import time
import sys
import os

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(".."))

from tools.tavily_search import TavilySearchTool
from tools.llm_interface import OpenRouterLLM

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base agent class with common functionality."""
    
    def __init__(self, llm: Optional[OpenRouterLLM] = None, 
                 search_tool: Optional[TavilySearchTool] = None):
        """Initialize the base agent.
        
        Args:
            llm: OpenRouter LLM interface. If None, a new instance is created.
            search_tool: Tavily search tool. If None, a new instance is created.
        """
        self.llm = llm or OpenRouterLLM()
        self.search_tool = search_tool or TavilySearchTool()
        self.execution_time = 0
        self.result_cache = {}
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main functionality.
        
        Args:
            input_data: Input data for the agent to process.
            
        Returns:
            Results of the agent's processing.
            
        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        start_time = time.time()
        
        try:
            # This should be implemented by subclasses
            raise NotImplementedError("Subclasses must implement execute()")
        finally:
            self.execution_time = time.time() - start_time
            logger.info(f"{self.__class__.__name__} execution completed in {self.execution_time:.2f} seconds")
    
    def _cache_result(self, key: str, data: Any) -> None:
        """Cache result data for potential reuse.
        
        Args:
            key: Cache key.
            data: Data to cache.
        """
        self.result_cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def _get_cached_result(self, key: str, max_age_seconds: int = 3600) -> Optional[Any]:
        """Retrieve cached result if available and not expired.
        
        Args:
            key: Cache key.
            max_age_seconds: Maximum age of cached data in seconds.
            
        Returns:
            Cached data or None if not available or expired.
        """
        if key not in self.result_cache:
            return None
        
        cached = self.result_cache[key]
        age = time.time() - cached["timestamp"]
        
        if age > max_age_seconds:
            logger.debug(f"Cached data for {key} is too old ({age:.2f} seconds)")
            return None
        
        logger.debug(f"Using cached data for {key} ({age:.2f} seconds old)")
        return cached["data"]
    
    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with provided variables.
        
        Args:
            template: Prompt template with {variable} placeholders.
            **kwargs: Variables to substitute into the template.
            
        Returns:
            Formatted prompt string.
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing required variable in prompt template: {e}")
            raise ValueError(f"Missing required variable in prompt template: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics.
        
        Returns:
            Dictionary with performance statistics.
        """
        return {
            "execution_time": self.execution_time,
            "llm_usage": self.llm.get_usage_stats() if self.llm else None,
            "cache_size": len(self.result_cache)
        } 