"""
Text processing utilities for the Local RAG Chatbot.
"""

import re
import random
import logging
from typing import List
from .pattern_matching import PRICE_PATTERN, TREATMENT_PRICE_PATTERN

logger = logging.getLogger(__name__)

# Regex pattern for identifying sentence boundaries
SENTENCE_PATTERN = re.compile(r'(?<=[.!?])\s+')

def count_sentences(text):
    """Count the number of sentences in text"""
    sentence_count = len(SENTENCE_PATTERN.findall(text))
    return sentence_count

def ensure_sentence_limit(text: str, max_sentences: int = 5) -> str:
    """Limit the number of sentences in the response."""
    sentences = SENTENCE_PATTERN.split(text.strip())
    
    # If already within limit, return as is
    if len(sentences) <= max_sentences:
        return text
    
    # Otherwise, limit to max_sentences
    limited_text = '. '.join(sentences[:max_sentences])
    
    # Ensure proper ending punctuation
    if not limited_text.endswith(('.', '!', '?')):
        limited_text += '.'
    
    return limited_text

def extract_price_info(docs):
    """Extract price information from document metadata and content"""
    price_data = {}
    for doc in docs:
        # Check metadata if available
        if doc.metadata.get('has_price_info') and 'price_data' in doc.metadata:
            price_data.update(doc.metadata['price_data'])
            
        # Also scan the content for price patterns
        content = doc.page_content
        price_matches = PRICE_PATTERN.findall(content)
        for treatment, price in price_matches:
            treatment = treatment.strip()
            if treatment and not treatment.isdigit():
                price_data[treatment.lower()] = price  # store keys in lowercase
                
    return price_data

def extract_price_from_text(text):
    """Extract treatment name and price from a text string."""
    match = TREATMENT_PRICE_PATTERN.search(text)
    if match:
        treatment = match.group(1).strip().lower()
        price = match.group(2).strip()
        return treatment, price
    return None, None

def format_retrieved_context(retrieved_docs):
    """Format documents with metadata and highlighted price information"""
    price_info = extract_price_info(retrieved_docs)
    context_parts = []
    
    for doc in retrieved_docs:
        content = doc.page_content
        source = doc.metadata.get('source', 'Unknown')
        doc_type = f" ({doc.metadata.get('document_type')})" if doc.metadata.get('document_type') else ""
        content_type = f" - {doc.metadata.get('content_type')}" if doc.metadata.get('content_type') else ""
        context_parts.append(f"- {content} (Source: {source}{doc_type}{content_type})")
        
    if price_info:
        price_entries = [f"- {treatment.title()}: {price} BDT" for treatment, price in price_info.items()]
        context_parts.append("\nPrice Information:\n" + "\n".join(price_entries))
        
    return "\n\n".join(context_parts)