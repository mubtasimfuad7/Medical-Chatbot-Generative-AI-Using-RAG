"""
Pattern matching utilities for the Local RAG Chatbot.
"""

import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Precompiled regex patterns
PRICE_PATTERN = re.compile(r'(?:cost|price)[^\d]*?(\d+)', re.IGNORECASE)
TREATMENT_PRICE_PATTERN = re.compile(r'([a-zA-Z\s]+)\s*(?:cost|price)[^\d]*?(\d+)', re.IGNORECASE)
BDT_QUERY_PATTERN = re.compile(r'^\s*(.+?)\s*(?:BDT|Tk\.?|Taka)\s*$', flags=re.I)
GENERAL_PRICE_PATTERN = re.compile(r'(?:cost|price|charge)[^\d]*(\d+)', re.IGNORECASE)
PRICE_FORMAT_PATTERN = re.compile(r'(\d+)(?:\.00)?\s*(?:BDT|Tk\.?)')
SPACE_BEFORE_PRICE_PATTERN = re.compile(r'(?<=\S)(?=\d+\.00 BDT)')

# Keywords for detecting queries about the bot itself
BOT_KEYWORDS = [
    'who are you', 'what are you', 'your name', 'tell me about you', 
    'what do you do', 'how do you work', 'what can you do', 'your capabilities',
    'who created you', 'your creator', 'your purpose', 'built you',
    'how were you made', 'what are your limitations', 'what can\'t you do',
    'local rag chatbot', 'rag chatbot', 'chatbot', 'local rag',
    'your functions', 'your abilities', 'ai assistant', 'virtual assistant'
]

# Keywords for detecting price-related queries
PRICE_KEYWORDS = [
    'price', 'cost', 'fee', 'charge', 'payment', 'pay', 'expense', 'bill',
    'pricing', 'costs', 'fees', 'expensive', 'cheap', 'affordable',
    'how much', 'how many', 'bdt', 'taka', 'tk'
]

# Add a more comprehensive price detection pattern that handles various formats
COMPREHENSIVE_PRICE_PATTERN = re.compile(r'(?:(?:price|cost|fee|charge)(?:\s+(?:for|of))?\s+)?([A-Za-z0-9\s\-,/\(\)]+?)(?:\s+(?:is|:|\-|\=))?\s*(?:BDT|Tk\.?|Taka)\s*(\d+(?:\.\d+)?)', flags=re.I)

def normalize_treatment_name(treatment: str) -> str:
    """Normalize a treatment name for better matching."""
    # Remove special characters, extra spaces, and convert to lowercase
    normalized = re.sub(r'[^\w\s]', '', treatment.lower())
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def treatments_match(treatment1: str, treatment2: str) -> bool:
    """Check if two treatment names match, accounting for variations."""
    # Normalize both treatments
    norm1 = normalize_treatment_name(treatment1)
    norm2 = normalize_treatment_name(treatment2)
    
    # Direct match
    if norm1 == norm2:
        return True
    
    # Check if one is contained in the other
    if norm1 in norm2 or norm2 in norm1:
        return True
    
    # Check for word-level matches (at least 70% of words match)
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    # If either set is empty, no match
    if not words1 or not words2:
        return False
    
    # Calculate overlap percentage
    intersection = words1.intersection(words2)
    smaller_set_size = min(len(words1), len(words2))
    
    if smaller_set_size == 0:
        return False
    
    overlap_percentage = len(intersection) / smaller_set_size
    return overlap_percentage >= 0.7

def is_price_query(query: str) -> bool:
    """Determine if a query is related to pricing."""
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in PRICE_KEYWORDS)

def is_direct_price_query(text):
    """
    Check if the text is a direct price query.
    Detects both "how much is X" format and "X BDT" format.
    """
    if not text:
        return False
        
    # Check for "X BDT" pattern
    if BDT_QUERY_PATTERN.match(text):
        return True
        
    # Check for "how much" questions
    how_much_patterns = [
        r'how\s+much\s+(?:does|is|for|will|would|should)?',
        r'what\s+(?:is|are)\s+the\s+(?:price|cost|fee|charge)',
        r'(?:price|cost|fee|charge)\s+(?:of|for)',
        r'how\s+(?:expensive|costly)',
    ]
    
    text_lower = text.lower()
    for pattern in how_much_patterns:
        if re.search(pattern, text_lower):
            return True
            
    return False

def extract_treatment_from_query(query):
    """Extract the treatment name from a price query."""
    # Check first for X BDT format
    bdt_match = BDT_QUERY_PATTERN.match(query)
    if bdt_match:
        return bdt_match.group(1).strip()
    
    # Handle "how much" queries
    how_much_patterns = [
        r'how\s+much\s+(?:does|is|for|will|would|should)?\s+(?:a|an|the)?\s*(.+?)(?:\s+cost|\s+price|\s+charge|\s+fee)?(?:\?|$|in\s+(?:bdt|taka|tk))',
        r'what\s+(?:is|are)\s+the\s+(?:price|cost|fee|charge)(?:\s+of|\s+for)?\s+(?:a|an|the)?\s*(.+?)(?:\?|$|in\s+(?:bdt|taka|tk))',
        r'(?:price|cost|fee|charge)\s+(?:of|for)\s+(?:a|an|the)?\s*(.+?)(?:\?|$|in\s+(?:bdt|taka|tk))',
    ]
    
    query_lower = query.lower()
    for pattern in how_much_patterns:
        match = re.search(pattern, query_lower)
        if match:
            return match.group(1).strip()
    
    return None