#!/usr/bin/env python
# Career Advisor Agent - Main Entry Point

import os
import logging
import json
import argparse
import sys
from pathlib import Path

# Add the parent directory to the sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set API keys directly (for testing)
os.environ["TAVILY_API_KEY"] = "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"
os.environ["OPENROUTER_API_KEY"] = "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"

def read_profile_from_file(file_path):
    """Read profile data from a file."""
    with open(file_path, 'r') as file:
        return file.read()

def main():
    """Main entry point for the Career Advisor Agent."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Career Advisor Agent')
    parser.add_argument('--profile', type=str, help='Path to a file containing the profile data')
    args = parser.parse_args()
    
    logger.info("Starting Career Advisor Agent...")
    
    try:
        # Import directly from the local directory
        sys.path.insert(0, os.path.abspath("."))
        from agents.profile_analyzer import ProfileAnalyzerAgent
        
        # Get profile data
        profile_text = None
        if args.profile:
            profile_text = read_profile_from_file(args.profile)
        
        if not profile_text:
            logger.info("No profile provided. Please provide a profile using --profile option.")
            logger.info("Example: python main.py --profile my_profile.txt")
            return
        
        # Initialize Profile Analyzer Agent
        profile_analyzer = ProfileAnalyzerAgent()
        
        # Analyze profile
        logger.info("Analyzing provided profile...")
        results = profile_analyzer.execute({"profile_text": profile_text})
        
        # Display results
        logger.info(f"Profile analysis completed. Extracted {len(results['skills'])} skills.")
        logger.info(f"Experience Level: {results['experience_level']}")
        logger.info(f"Strengths: {', '.join(results['strengths'])}")
        
        # Save results to file
        output_file = "profile_analysis_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error running Career Advisor Agent: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("Career Advisor Agent execution complete.")

if __name__ == "__main__":
    main() 