# config.py
# Global configuration settings for ColdIQ pipeline

# LLM model to use - swapping this one line changes the model everywhere
LLM_MODEL = "gemini-2.0-flash"

# Minimum qualifier score (0-100) to proceed with application
QUALIFIER_THRESHOLD = 60

# Maximum number of review/revision cycles before giving up
MAX_REVIEW_LOOPS = 3

# Path to your RAG knowledge base documents
DATA_PATH = "data/"

# Path to save application logs
LOG_PATH = "logs/"