"""
Utility functions for the Local RAG Chatbot application.
"""

import re
import random
from functools import lru_cache
from cachetools import TTLCache, LRUCache

# Cache for storing responses to frequently asked questions (5 minute TTL)
response_cache = TTLCache(maxsize=1000, ttl=300)

# Cache for storing vector search results (10 minute TTL)
vector_search_cache = TTLCache(maxsize=500, ttl=600)

# Cache for storing commonly used treatment information
treatment_cache = LRUCache(maxsize=200)

# Precompiled regex patterns
PRICE_PATTERN = re.compile(r'([A-Za-z\s\-,/\(\)]+)\s+(\d+(?:\.\d+)?)\s*(?:BDT|Tk\.?)')
TREATMENT_PRICE_PATTERN = re.compile(r'^\d+\s+([A-Za-z0-9\s\-,/\(\)]+?)\s+BDT\s+(\d+(?:\.\d+)?)', flags=re.I)
SENTENCE_PATTERN = re.compile(r'[.!?]+')
PRICE_FORMAT_PATTERN = re.compile(r'(\d+)(?:\.00)?\s*(?:BDT|Tk\.?)')
SPACE_BEFORE_PRICE_PATTERN = re.compile(r'(?<=\S)(?=\d+\.00 BDT)')
BDT_QUERY_PATTERN = re.compile(r'^\s*(.+?)\s*BDT\s*$', flags=re.I)
GENERAL_PRICE_PATTERN = re.compile(r'BDT\s+(\d+(?:\.\d+)?)')

# Human-like response variations
RESPONSE_VARIATIONS = {
    "uncertainty": [
        "I don't have information about that in my database. I'd recommend consulting with a healthcare professional for personalized advice.",
        "That's beyond the scope of my current knowledge. Please consult with a qualified healthcare provider for specific guidance.",
        "I don't have details on that in my records. It would be best to speak with a healthcare professional for accurate information.",
        "I'm not able to provide information on that topic. I'd suggest reaching out to a medical professional for assistance."
    ],
    "pricing_unknown": [
        "I don't have pricing information about that in my database. Please contact the relevant healthcare facility directly for current pricing.",
        "I don't have that specific pricing information available. For the most up-to-date rates, I'd recommend contacting the healthcare provider directly.",
        "That pricing information isn't in my database. You'll need to check with the healthcare facility for their current rates.",
        "I don't have access to that pricing data. For accurate cost information, please reach out to the healthcare provider directly."
    ],
    "transitions": [
        "Based on the information I have, ",
        "According to my database, ",
        "From what I understand, ",
        "The information I have indicates that ",
        "My records show that ",
    ],
    "acknowledgments": [
        "I see you're asking about ",
        "You're interested in ",
        "Regarding your question about ",
        "Concerning ",
        "About your inquiry on ",
    ]
}

@lru_cache(maxsize=256)
def normalize_treatment_name(name):
    """Normalize treatment name for better matching (cached for performance)"""
    return re.sub(r'[^a-z0-9]', '', name.lower())

@lru_cache(maxsize=512)
def treatments_match(query, treatment):
    """Check if treatment names match (cached for performance)"""
    query_norm = normalize_treatment_name(query)
    treatment_norm = normalize_treatment_name(treatment)
    
    # Direct match
    if query_norm == treatment_norm:
        return True
    
    # Check if one is a substring of the other
    if query_norm in treatment_norm or treatment_norm in query_norm:
        return True
    
    # Check if most words match
    query_words = set(query_norm.split())
    treatment_words = set(treatment_norm.split())
    common_words = query_words.intersection(treatment_words)
    
    if common_words and len(common_words) / max(len(query_words), len(treatment_words)) > 0.6:
        return True
    
    return False

def is_price_query(query):
    """Check if the query is about pricing"""
    query_lower = query.lower()
    return any(word in query_lower for word in ['price', 'cost', 'how much', 'fee', 'charge', 'payment', 'rate', 'expense'])

def is_direct_price_query(query):
    """Check if the query is a direct price lookup (e.g., 'X-ray BDT')"""
    return bool(BDT_QUERY_PATTERN.match(query))

def extract_treatment_from_query(query):
    """Extract treatment name from a direct price query"""
    match = BDT_QUERY_PATTERN.match(query)
    if match:
        return match.group(1).strip()
    return None

def extract_price_from_text(text):
    """Extract treatment name and price from a text string."""
    match = TREATMENT_PRICE_PATTERN.search(text)
    if match:
        treatment = match.group(1).strip().lower()
        price = match.group(2).strip()
        return treatment, price
    return None, None

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

def format_price_response(response, price_info):
    """Format the response to include price information consistently"""
    response = PRICE_FORMAT_PATTERN.sub(r'\1.00 BDT', response)
    response = SPACE_BEFORE_PRICE_PATTERN.sub(' ', response)
    # Remove any remaining hashtags
    response = response.replace('#', '')
    return response

def ensure_sentence_limit(text, max_sentences=5):
    """Ensure the text has no more than the specified number of sentences"""
    sentences = re.split(r'([.!?])\s+', text)
    complete_sentences = []
    i = 0
    sentence_count = 0
    while i < len(sentences) and sentence_count < max_sentences:
        if i + 1 < len(sentences) and sentences[i+1] in ['.', '!', '?']:
            complete_sentences.append(sentences[i] + sentences[i+1])
            i += 2
            sentence_count += 1
        else:
            if sentences[i] and sentences[i] not in ['.', '!', '?']:
                if not sentences[i].strip().endswith(('.', '!', '?')):
                    complete_sentences.append(sentences[i] + '.')
                else:
                    complete_sentences.append(sentences[i])
                sentence_count += 1
            i += 1
    return ' '.join(complete_sentences)

def add_human_touch(response):
    """Add variations to make responses more human-like"""
    # Remove any hashtags
    response = response.replace('#', '')
    
    # Add transitions or acknowledgments at the beginning (30% chance)
    if random.random() < 0.3 and not any(response.startswith(phrase) for phrase in RESPONSE_VARIATIONS["transitions"] + RESPONSE_VARIATIONS["acknowledgments"]):
        response = random.choice(RESPONSE_VARIATIONS["transitions"]) + response[0].lower() + response[1:]
    
    # Replace standard uncertainty phrases with variations
    for phrase in ["I don't have information about that in my database"]:
        if phrase in response:
            response = response.replace(phrase, random.choice(RESPONSE_VARIATIONS["uncertainty"]))
    
    # Replace standard pricing phrases with variations
    for phrase in ["I don't have pricing information about that in my database"]:
        if phrase in response:
            response = response.replace(phrase, random.choice(RESPONSE_VARIATIONS["pricing_unknown"]))
    
    return response 