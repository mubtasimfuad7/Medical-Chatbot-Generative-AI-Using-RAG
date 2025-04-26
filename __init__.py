"""
Utils package initialization.
"""

try:
    # Import all utility modules
    from .pattern_matching import (
        PRICE_PATTERN, 
        TREATMENT_PRICE_PATTERN, 
        BDT_QUERY_PATTERN,
        GENERAL_PRICE_PATTERN, 
        PRICE_KEYWORDS,
        BOT_KEYWORDS,
        normalize_treatment_name,
        treatments_match,
        is_price_query,
        is_direct_price_query,
        extract_treatment_from_query
    )
    
    from .response_formatter import (
        RESPONSE_VARIATIONS,
        add_human_touch,
        format_price_response,
        format_response,
        get_error_response
    )
    
    from .text_processing import ensure_sentence_limit
    
    from .document_utils import (
        extract_price_info,
        format_retrieved_context,
        filter_documents_by_score,
        enhance_query
    )
    
    from .cache import (
        response_cache,
        vector_search_cache,
        treatment_cache,
        document_cache,
        clear_caches
    )
    
except ImportError as e:
    print(f"Error importing utility modules: {str(e)}")
    print("Make sure all dependencies are installed:")
    print("pip install -r requirements.txt")

__all__ = [
    'normalize_treatment_name',
    'treatments_match', 
    'is_price_query',
    'is_direct_price_query',
    'extract_treatment_from_query',
    'PRICE_PATTERN', 
    'TREATMENT_PRICE_PATTERN', 
    'BDT_QUERY_PATTERN',
    'GENERAL_PRICE_PATTERN', 
    'PRICE_KEYWORDS',
    'BOT_KEYWORDS',
    'RESPONSE_VARIATIONS',
    'add_human_touch',
    'format_price_response',
    'format_response',
    'get_error_response',
    'ensure_sentence_limit',
    'extract_price_info',
    'format_retrieved_context',
    'filter_documents_by_score',
    'enhance_query',
    'response_cache',
    'vector_search_cache',
    'treatment_cache',
    'document_cache',
    'clear_caches'
]