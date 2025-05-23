"""OpenRouter LLM interface for AI interactions."""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Union
import sys
import os

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(".."))

from config import Config
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenRouterLLM:
    """Interface for interacting with OpenRouter LLM API using OpenAI client."""
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, 
                 retry_delay: float = 1.0, timeout: int = None):
        """Initialize the OpenRouter LLM interface.
        
        Args:
            api_key: OpenRouter API key. If None, uses the one from Config.
            max_retries: Maximum number of retries on failure.
            retry_delay: Delay between retries in seconds.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key or Config.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.base_url = Config.OPENROUTER_BASE_URL
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout or Config.API_TIMEOUT
        
        # Initialize OpenAI client
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
        # Extra headers for OpenRouter
        self.extra_headers = {
            "HTTP-Referer": "https://career-advisor-agent.com",  # Replace with your actual site
            "X-Title": "Career Advisor Agent"
        }
        
        # Cost tracking
        self.total_tokens = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
    
    def generate_text(self, prompt: Union[str, List[Dict[str, str]]],
                      model: str = "openai/gpt-4o-mini",
                      temperature: float = 0.7,
                      max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate text using the specified LLM model.
        
        Args:
            prompt: Text prompt or list of chat messages.
            model: Model identifier to use.
            temperature: Sampling temperature (0-1).
            max_tokens: Maximum tokens to generate.
            
        Returns:
            Response containing generated text and metadata.
            
        Raises:
            Exception: If the request fails after all retries.
        """
        # Handle both string prompts and chat format
        if isinstance(prompt, str):
            messages = [
                {"role": "user", "content": prompt}
            ]
        else:
            messages = prompt
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"OpenRouter request attempt {attempt + 1}/{self.max_retries}")
                
                completion = self.client.chat.completions.create(
                    extra_headers=self.extra_headers,
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Track usage if available
                if hasattr(completion, "usage"):
                    usage = completion.usage
                    self.total_prompt_tokens += usage.prompt_tokens
                    self.total_completion_tokens += usage.completion_tokens
                    self.total_tokens += usage.total_tokens
                
                logger.info(f"OpenRouter request successful")
                return {
                    "choices": [
                        {
                            "message": {
                                "content": completion.choices[0].message.content
                            }
                        }
                    ]
                }
                
            except Exception as e:
                logger.warning(f"OpenRouter request attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    sleep_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"OpenRouter request failed after {self.max_retries} attempts: {str(e)}")
                    raise Exception(f"Failed to get LLM response after {self.max_retries} attempts") from e
    
    def get_completion(self, prompt: str, **kwargs) -> str:
        """Simplified interface to get just the completion text.
        
        Args:
            prompt: Text prompt.
            **kwargs: Additional parameters to pass to generate_text.
            
        Returns:
            Generated text string.
        """
        response = self.generate_text(prompt, **kwargs)
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics.
        
        Returns:
            Dictionary with usage statistics.
        """
        return {
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "estimated_cost": self.total_cost
        } 