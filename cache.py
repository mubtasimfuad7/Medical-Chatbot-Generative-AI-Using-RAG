"""
Caching utilities for the Local RAG Chatbot.
"""

import logging
from cachetools import TTLCache, LRUCache

logger = logging.getLogger(__name__)

# Cache for previously seen questions and responses
# TTL of 24 hours (86400 seconds)
response_cache = TTLCache(maxsize=500, ttl=86400)

# Cache for vector search results 
# TTL of 3 hours (10800 seconds)
vector_search_cache = TTLCache(maxsize=200, ttl=10800)

# Cache for treatment price lookups
# Larger TTL as treatment prices don't change frequently
treatment_cache = TTLCache(maxsize=100, ttl=172800)  # 48 hours

# Cache for document chunks
document_cache = LRUCache(maxsize=1000)

def clear_caches():
    """Clear all caches."""
    global response_cache, vector_search_cache, treatment_cache, document_cache
    
    logger.info("Clearing all caches")
    response_cache.clear()
    vector_search_cache.clear()
    treatment_cache.clear()
    document_cache.clear()
    logger.info("All caches cleared successfully")