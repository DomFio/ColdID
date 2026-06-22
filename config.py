# config.py
# Global configuration settings for ColdIQ pipeline
# Loads API keys from .env file securely using python-dotenv

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys - loaded from .env, never hardcoded
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# LLM model to use - swapping this one line changes the model everywhere
LLM_MODEL = "gpt-4o-mini"

# Minimum qualifier score (0-100) to proceed with application
QUALIFIER_THRESHOLD = 60

# Maximum number of review/revision cycles before giving up
MAX_REVIEW_LOOPS = 3

# Path to your RAG knowledge base documents
DATA_PATH = "data/"

# Path to save application logs
LOG_PATH = "logs/"

# Maximum word count for drafted emails
MAX_EMAIL_WORDS = 250