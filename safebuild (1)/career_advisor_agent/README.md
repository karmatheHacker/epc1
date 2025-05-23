# Career Advisor Agent

An AI-powered career advisor that analyzes professional profiles to extract skills and provide career assessments.

## Features

- **Profile Analysis**: Extract skills and assess career progression
- **Skill Extraction**: Identify technical, soft, and domain skills with proficiency levels
- **Career Assessment**: Evaluate strengths, weaknesses, and future trajectory
- **Education Relevance**: Analyze the relevance of education to career path

## Setup

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Set up your API keys:
   - Create an account on [OpenRouter](https://openrouter.ai/) and get an API key
   - Create an account on [Tavily](https://tavily.com/) and get an API key
   - Set the API keys in the environment or directly in the code:
     ```python
     os.environ["TAVILY_API_KEY"] = "your-tavily-api-key"
     os.environ["OPENROUTER_API_KEY"] = "your-openrouter-api-key"
     ```

## Usage

1. Create a text file with the professional profile to analyze (see `sample_profile.txt` for an example)

2. Run the agent with:
   ```
   python main.py --profile your_profile.txt
   ```

3. View the results in the generated `profile_analysis_results.json` file

## Sample Output

The output is a JSON file containing:
- List of extracted skills with categories and proficiency levels
- Overall experience level assessment
- Career progression analysis
- Strengths and weaknesses
- Career trajectory predictions
- Education relevance assessment

## Project Structure

- `agents/`: Contains the agent implementation
  - `base_agent.py`: Base agent class with common functionality
  - `profile_analyzer.py`: Profile analyzer implementation
- `config/`: Configuration settings
- `tools/`: External services integration
  - `llm_interface.py`: LLM provider integration (OpenRouter)
  - `search_tool.py`: Search integration (Tavily)
- `utils/`: Utility functions
- `main.py`: Main entry point

## API Keys

The system requires:
- OpenRouter API key: For LLM capabilities
- Tavily API key: For web search capabilities when needed

## Requirements

- Python 3.8+
- Dependencies listed in requirements.txt 