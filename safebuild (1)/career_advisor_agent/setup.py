from setuptools import setup, find_packages

setup(
    name="career_advisor_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain==0.0.305",
        "tavily-python==0.2.3",
        "openai==1.3.0",
        "python-dotenv==1.0.0",
        "pydantic==2.4.2",
        "pandas==2.1.1",
        "requests==2.31.0",
    ],
) 