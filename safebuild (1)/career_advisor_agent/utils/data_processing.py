"""Data processing utility functions."""

import re
import string
from typing import List, Set, Dict, Any, Optional

def normalize_text(text: str) -> str:
    """Normalize text by removing extra whitespace and converting to lowercase.
    
    Args:
        text: Text to normalize.
        
    Returns:
        Normalized text.
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace and convert to lowercase
    return text.strip().lower()

def format_duration(years: float) -> str:
    """Format a duration in years to a human-readable string.
    
    Args:
        years: Duration in years.
        
    Returns:
        Formatted duration string.
    """
    if years < 0:
        return "Invalid duration"
    
    if years < 1/12:  # Less than a month
        days = int(years * 365)
        return f"{days} day{'s' if days != 1 else ''}"
    
    if years < 1:  # Less than a year
        months = int(years * 12)
        return f"{months} month{'s' if months != 1 else ''}"
    
    # Handle years and months
    whole_years = int(years)
    months = int((years - whole_years) * 12)
    
    if months == 0:
        return f"{whole_years} year{'s' if whole_years != 1 else ''}"
    
    return f"{whole_years} year{'s' if whole_years != 1 else ''} and {months} month{'s' if months != 1 else ''}"

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts using a simple token overlap method.
    
    Args:
        text1: First text.
        text2: Second text.
        
    Returns:
        Similarity score between 0 and 1.
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalize texts
    text1 = normalize_text(text1)
    text2 = normalize_text(text2)
    
    # Tokenize and create sets
    set1 = set(text1.split())
    set2 = set(text2.split())
    
    # Calculate Jaccard similarity
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0

def extract_entities(text: str, entity_types: Optional[List[str]] = None) -> Dict[str, List[str]]:
    """Extract named entities from text using simple pattern matching.
    
    This is a simple implementation. In a real system, you would use NER from spaCy or similar.
    
    Args:
        text: Text to extract entities from.
        entity_types: Types of entities to extract. If None, extracts all types.
        
    Returns:
        Dictionary of entity types to lists of extracted entities.
    """
    # Simple patterns for demonstration purposes
    patterns = {
        "skills": r'\b(?:Python|Java|C\+\+|JavaScript|TypeScript|SQL|React|Angular|Vue|Node\.js|AWS|Azure|GCP|Docker|Kubernetes|git|REST|GraphQL|HTML|CSS|TensorFlow|PyTorch|scikit-learn|pandas|numpy)\b',
        "job_titles": r'\b(?:Software Engineer|Developer|Data Scientist|Product Manager|DevOps Engineer|SRE|QA Engineer|Tech Lead|CTO|CEO|Manager|Director|VP|Engineer|Architect)\b',
        "companies": r'\b(?:Google|Microsoft|Amazon|Apple|Facebook|Meta|Netflix|Uber|Airbnb|LinkedIn|Twitter|IBM|Intel|Oracle|Salesforce|Adobe)\b',
        "education": r'\b(?:Bachelor|Master|PhD|BS|MS|BA|MBA|Diploma|Certificate|Degree|University|College)\b'
    }
    
    if entity_types:
        # Filter to only the requested entity types
        patterns = {k: v for k, v in patterns.items() if k in entity_types}
    
    results = {}
    for entity_type, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        # Deduplicate while preserving order
        unique_matches = []
        seen = set()
        for match in matches:
            if match.lower() not in seen:
                unique_matches.append(match)
                seen.add(match.lower())
        
        results[entity_type] = unique_matches
    
    return results 