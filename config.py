"""
Configuration settings for Local RAG Chatbot.
"""

import os
from os.path import join, dirname, exists
from pathlib import Path

# API Keys (with default fallbacks)
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "pcsk_3FxEjX_PU14iod1t5qbzFUTBqnraZwCrLKYnT6Gbsf2z2bhKpmQGr4MCBHAUJJwTCbGh96")
PINECONE_ENV = os.environ.get("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_NAMESPACE = ""  # Default to empty namespace

# Vector store settings
TEST_INDEX_NAME = "test"
MEDICALBOT_INDEX_NAME = "medicalbot"

# Embedding model settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"  # Use CPU for embeddings

# LLM settings
LLM_MODEL_NAME = "Qwen2-1.5B-Instruct.Q8_0.gguf"
LLM_MODEL_PATH = "/Users/mubtasimfuad/Downloads/RAG-CHATBOT/models/model_files"
LLM_DEVICE = "gpu"  # Default device
LLM_CONTEXT_WINDOW = 2048
LLM_THREADS = os.cpu_count() or 4
LLM_BATCH_SIZE = 8

# Response settings
MAX_RESPONSE_TOKENS = 200
MAX_RESPONSE_SENTENCES = 5

# Cache settings
RESPONSE_CACHE_SIZE = 1000
RESPONSE_CACHE_TTL = 300  # 5 minutes in seconds
VECTOR_SEARCH_CACHE_SIZE = 500
VECTOR_SEARCH_CACHE_TTL = 600  # 10 minutes in seconds
TREATMENT_CACHE_SIZE = 200

# Application settings
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
PORT = int(os.environ.get("PORT", 8080))

# Query processing settings
SIMILARITY_SEARCH_K = 20  # Number of documents to retrieve
SIMILARITY_SCORE_THRESHOLD = 0.55  # Threshold for filtering results
FILTER_SCORE_THRESHOLD = 0.65  # Threshold for filtering price results

# System prompts
GENERAL_SYSTEM_PROMPT = """You are a helpful healthcare assistant. Please provide accurate and helpful information based on the context provided. If you cannot find the answer in the context, say so. Keep your responses concise and focused on the user's question."""

PRICE_SYSTEM_PROMPT = """You are a healthcare pricing assistant. Please provide accurate pricing information based on the context provided. If you cannot find the price in the context, say so. Always include the currency (BDT) and note that prices may vary by facility."""

# Create necessary directories
BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

for directory in [MODEL_DIR, DATA_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# Log file path
LOG_FILE = LOG_DIR / "medicalbot.log"