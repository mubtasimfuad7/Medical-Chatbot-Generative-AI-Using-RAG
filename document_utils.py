"""
Document utilities for processing and formatting retrieved content.
"""

import re
import logging
from typing import Dict, List, Any, Tuple

from utils.pattern_matching import TREATMENT_PRICE_PATTERN, GENERAL_PRICE_PATTERN, PRICE_PATTERN

logger = logging.getLogger(__name__)

def extract_price_info(docs: List[Any]) -> Dict[str, str]:
    """Extract price information from documents."""
    price_info = {}
    
    for doc in docs:
        content = doc.page_content
        
        # Check metadata for price info first
        if hasattr(doc, 'metadata') and doc.metadata:
            if 'has_price_info' in doc.metadata and doc.metadata.get('has_price_info'):
                if 'price_data' in doc.metadata:
                    price_info.update(doc.metadata['price_data'])
                    continue
        
        # Try to extract treatment name and price using standard pattern
        matches = TREATMENT_PRICE_PATTERN.findall(content)
        if matches:
            for match in matches:
                treatment = match[0].strip().lower()
                price = match[1].strip()
                if treatment and not treatment.isdigit() and len(treatment) > 2:
                    price_info[treatment] = price
            continue
        
        # Try to extract treatments and prices using a more general approach
        # Look for price mentions
        price_matches = PRICE_PATTERN.findall(content)
        if price_matches:
            # Try to associate with treatment names
            lines = content.split('\n')
            for line in lines:
                line = line.strip().lower()
                if any(price in line for price in price_matches):
                    # This line contains a price, try to extract treatment
                    words = [w for w in line.split() if len(w) > 3 and not w.isdigit() and 
                             w not in ["price", "cost", "bdt", "taka", "charge", "treatment", "service", "procedure"]]
                    if words:
                        treatment = " ".join(words)
                        # Get the price from this line
                        price_match = PRICE_PATTERN.search(line)
                        if price_match:
                            price_info[treatment] = price_match.group(1)
        
        # Try to extract just price
        match = GENERAL_PRICE_PATTERN.search(content)
        if match:
            price = match.group(1).strip()
            # Try to extract treatment name from context
            words = content.lower().split()
            for word in words:
                if len(word) > 3 and word not in ["price", "cost", "bdt", "taka", "charge"]:
                    # Only add if we don't already have this treatment
                    if word not in price_info:
                        price_info[word] = price
                    break
    
    return price_info

def format_retrieved_context(docs: List[Any], doc_type: str = None) -> str:
    """Format retrieved documents into a context string.
    
    Args:
        docs: List of document objects
        doc_type: Optional type of documents (e.g., "Medical Information" or "Pricing Information")
    
    Returns:
        Formatted context string
    """
    if not docs:
        return ""
    
    # Concatenate document contents with separators and enhance with metadata
    context_parts = []
    
    # Add doc_type as a header if provided
    if doc_type:
        context_parts.append(f"--- {doc_type} ---")
    
    # First, add any documents that have price information (prioritize these)
    price_docs = []
    other_docs = []
    
    for doc in docs:
        has_price = False
        if hasattr(doc, 'page_content'):
            content = doc.page_content.strip()
            # Check if content contains price information
            if re.search(r'(?:price|cost|bdt|taka|tk)', content.lower()) or re.search(r'\d+(?:\.\d+)?', content):
                has_price = True
        
        if has_price:
            price_docs.append(doc)
        else:
            other_docs.append(doc)
    
    # Limit the number of docs to prevent context overflow
    # Prioritize price docs
    max_price_docs = min(3, len(price_docs))
    max_other_docs = min(2, len(other_docs))
    
    price_docs = price_docs[:max_price_docs]
    other_docs = other_docs[:max_other_docs]
    
    # Add price documents first
    for i, doc in enumerate(price_docs):
        content = doc.page_content.strip()
        
        # Limit content length to prevent context overflow
        if len(content) > 500:
            content = content[:500] + "... [content truncated]"
        
        # Add metadata if available
        metadata_str = ""
        if hasattr(doc, 'metadata') and doc.metadata:
            source = doc.metadata.get('source', 'Unknown')
            doc_type = doc.metadata.get('document_type', '')
            metadata_str = f" (Source: {source}{f', Type: {doc_type}' if doc_type else ''})"
        
        # Add section numbering for clarity
        context_parts.append(f"[PRICE INFO {i+1}]{metadata_str}: {content}")
    
    # Add other documents
    for i, doc in enumerate(other_docs):
        content = doc.page_content.strip()
        
        # Limit content length to prevent context overflow
        if len(content) > 500:
            content = content[:500] + "... [content truncated]"
        
        # Add metadata if available
        metadata_str = ""
        if hasattr(doc, 'metadata') and doc.metadata:
            source = doc.metadata.get('source', 'Unknown')
            doc_type = doc.metadata.get('document_type', '')
            metadata_str = f" (Source: {source}{f', Type: {doc_type}' if doc_type else ''})"
        
        # Add section numbering for clarity
        context_parts.append(f"[Section {i+1}]{metadata_str}: {content}")
    
    result = "\n\n".join(context_parts)
    
    # Final check to ensure the context is not too large (max 4000 chars)
    max_context_length = 4000
    if len(result) > max_context_length:
        logger.warning(f"Context too large ({len(result)} chars), truncating to {max_context_length}")
        result = result[:max_context_length] + "... [additional context truncated]"
    
    return result

def filter_documents_by_score(docs_with_scores: List[Tuple[Any, float]], 
                             threshold: float = 0.6,
                             is_price_query: bool = False) -> List[Any]:
    """Filter documents based on similarity score."""
    # For price queries, we want to be more lenient with the threshold
    if is_price_query:
        # Return all documents for price queries
        return [doc for doc, _ in docs_with_scores]
    
    # For other queries, use the threshold
    filtered_docs = []
    for doc, score in docs_with_scores:
        if score < threshold:
            filtered_docs.append(doc)
    
    return filtered_docs

def enhance_query(query: str, is_price_query: bool = False) -> str:
    """Enhance the query for better search results."""
    enhanced_query = query
    
    # Add price terms for price queries that don't already have them
    if is_price_query and not any(term in query.lower() for term in ['price', 'cost']):
        enhanced_query += " price cost"
    
    # Add treatment terms for queries ending with BDT
    if query.upper().endswith("BDT"):
        treatment_name = query[:-3].strip()
        enhanced_query = f"{treatment_name} treatment procedure price cost"
    
    return enhanced_query 