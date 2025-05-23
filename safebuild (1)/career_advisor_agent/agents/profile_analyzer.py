"""Profile Analyzer Agent for skill extraction and career analysis."""

import logging
from typing import Dict, Any, List, Optional
import json
import sys
import os

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(".."))

from pydantic import BaseModel, Field, validator

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class Skill(BaseModel):
    """Model for a professional skill."""
    
    name: str = Field(..., description="Name of the skill")
    category: str = Field(..., description="Category of the skill (technical, soft, domain)")
    level: str = Field(..., description="Proficiency level (beginner, intermediate, advanced, expert)")
    years_experience: float = Field(..., description="Years of experience with this skill")
    
    @validator('level')
    def validate_level(cls, v):
        """Validate the skill level."""
        allowed_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if v.lower() not in allowed_levels:
            raise ValueError(f"Skill level must be one of: {', '.join(allowed_levels)}")
        return v.lower()
    
    @validator('category')
    def validate_category(cls, v):
        """Validate the skill category."""
        allowed_categories = ['technical', 'soft', 'domain']
        if v.lower() not in allowed_categories:
            raise ValueError(f"Skill category must be one of: {', '.join(allowed_categories)}")
        return v.lower()

class ProfileAnalysis(BaseModel):
    """Model for profile analysis results."""
    
    skills: List[Skill] = Field(..., description="List of identified skills")
    experience_level: str = Field(..., description="Overall experience level")
    career_progression: str = Field(..., description="Analysis of career progression")
    strengths: List[str] = Field(..., description="Identified strengths")
    weaknesses: List[str] = Field(..., description="Identified weaknesses")
    career_trajectory: str = Field(..., description="Analysis of career trajectory")
    education_relevance: str = Field(..., description="Analysis of education relevance")
    
    @validator('experience_level')
    def validate_experience_level(cls, v):
        """Validate the experience level."""
        allowed_levels = ['entry', 'junior', 'mid', 'senior', 'lead', 'executive']
        if v.lower() not in allowed_levels:
            raise ValueError(f"Experience level must be one of: {', '.join(allowed_levels)}")
        return v.lower()

class ProfileAnalyzerAgent(BaseAgent):
    """Agent for analyzing professional profiles."""
    
    SKILL_EXTRACTION_PROMPT = """
    Analyze the following professional profile and extract all the skills mentioned.
    For each skill, determine:
    1. The skill name
    2. The category (technical, soft, domain)
    3. The estimated proficiency level (beginner, intermediate, advanced, expert)
    4. The estimated years of experience with the skill

    Return the results as a JSON array of objects with the following structure:
    [
        {{
            "name": "skill name",
            "category": "skill category",
            "level": "proficiency level",
            "years_experience": years as a number
        }}
    ]

    Your response must contain ONLY the JSON array and nothing else.

    Profile to analyze:
    {profile_text}
    """
    
    PROFILE_ANALYSIS_PROMPT = """
    Perform a comprehensive analysis of the following professional profile.
    Consider the skills, experience, education, and career history to provide:

    1. An overall experience level (entry, junior, mid, senior, lead, executive)
    2. An analysis of career progression (e.g. "steady advancement in software engineering roles")
    3. A list of 3-5 key strengths
    4. A list of 2-4 potential weaknesses or areas for improvement
    5. An analysis of career trajectory and potential future paths
    6. An assessment of the relevance of their education to their career

    Return the results in JSON format with the following structure:
    {{
        "experience_level": "level",
        "career_progression": "analysis",
        "strengths": ["strength1", "strength2", ...],
        "weaknesses": ["weakness1", "weakness2", ...],
        "career_trajectory": "analysis",
        "education_relevance": "analysis"
    }}

    Your response must contain ONLY the JSON object and nothing else.

    Profile to analyze:
    {profile_text}
    
    Skills already identified:
    {skills_json}
    """
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the profile analysis.
        
        Args:
            input_data: Input data containing the profile to analyze.
                Must contain 'profile_text' key.
            
        Returns:
            Analysis results including skills and career assessment.
            
        Raises:
            ValueError: If required input data is missing.
        """
        if 'profile_text' not in input_data:
            raise ValueError("Profile text is required for analysis")
        
        profile_text = input_data['profile_text']
        
        # Extract skills
        skills = self._extract_skills(profile_text)
        logger.info(f"Extracted {len(skills)} skills from profile")
        
        # Perform detailed profile analysis
        skills_json = json.dumps([skill.dict() for skill in skills])
        analysis = self._analyze_profile(profile_text, skills_json)
        
        # Combine results into a ProfileAnalysis object
        profile_analysis = ProfileAnalysis(
            skills=skills,
            **analysis
        )
        
        # Cache the results
        self._cache_result(f"profile_analysis_{hash(profile_text)}", profile_analysis.dict())
        
        return profile_analysis.dict()
    
    def _extract_skills(self, profile_text: str) -> List[Skill]:
        """Extract skills from the profile text.
        
        Args:
            profile_text: Profile text to analyze.
            
        Returns:
            List of extracted Skill objects.
        """
        prompt = self._format_prompt(self.SKILL_EXTRACTION_PROMPT, profile_text=profile_text)
        
        try:
            response = self.llm.get_completion(prompt, temperature=0.3)
            # Try to find JSON content in the response
            try:
                # Find the first opening bracket and the last closing bracket
                start_idx = response.find('[')
                end_idx = response.rfind(']')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx+1]
                    skills_data = json.loads(json_str)
                else:
                    # If no brackets found, try loading the entire response
                    skills_data = json.loads(response)
            except json.JSONDecodeError:
                # Last resort: try to clean the string
                clean_response = response.strip()
                # Remove code block markers if present
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]
                clean_response = clean_response.strip()
                skills_data = json.loads(clean_response)
            
            skills = []
            for skill_data in skills_data:
                try:
                    skill = Skill(**skill_data)
                    skills.append(skill)
                except Exception as e:
                    logger.warning(f"Failed to parse skill data: {e}")
            
            return skills
        except Exception as e:
            logger.error(f"Failed to extract skills: {e}")
            # Return empty list in case of failure
            return []
    
    def _analyze_profile(self, profile_text: str, skills_json: str) -> Dict[str, Any]:
        """Analyze the profile for career progression and potential.
        
        Args:
            profile_text: Profile text to analyze.
            skills_json: JSON string of previously extracted skills.
            
        Returns:
            Dictionary with analysis results.
        """
        prompt = self._format_prompt(
            self.PROFILE_ANALYSIS_PROMPT, 
            profile_text=profile_text,
            skills_json=skills_json
        )
        
        try:
            response = self.llm.get_completion(prompt, temperature=0.5)
            # Try to find JSON content in the response
            try:
                # Find the first opening brace and the last closing brace
                start_idx = response.find('{')
                end_idx = response.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx+1]
                    analysis_data = json.loads(json_str)
                else:
                    # If no braces found, try loading the entire response
                    analysis_data = json.loads(response)
            except json.JSONDecodeError:
                # Last resort: try to clean the string
                clean_response = response.strip()
                # Remove code block markers if present
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]
                clean_response = clean_response.strip()
                analysis_data = json.loads(clean_response)
            
            # Validate the expected fields exist
            required_fields = [
                "experience_level", "career_progression", "strengths", 
                "weaknesses", "career_trajectory", "education_relevance"
            ]
            
            for field in required_fields:
                if field not in analysis_data:
                    logger.warning(f"Missing required field in analysis response: {field}")
                    # Add a default value
                    if field in ["strengths", "weaknesses"]:
                        analysis_data[field] = []
                    else:
                        analysis_data[field] = "Not enough information to analyze"
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Failed to analyze profile: {e}")
            # Return default analysis in case of failure
            return {
                "experience_level": "mid",  # Default to mid-level
                "career_progression": "Unable to analyze career progression",
                "strengths": ["Unable to identify strengths"],
                "weaknesses": ["Unable to identify areas for improvement"],
                "career_trajectory": "Unable to analyze career trajectory",
                "education_relevance": "Unable to analyze education relevance"
            } 