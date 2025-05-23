"""Utility functions for the Career Advisor Agent."""

# Import individual utilities for easy access
try:
    from career_advisor_agent.utils.data_processing import (
        format_duration, calculate_similarity, extract_entities, normalize_text
    )
except ImportError:
    pass 