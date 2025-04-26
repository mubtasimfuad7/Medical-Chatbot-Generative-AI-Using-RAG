"""
Response formatting utilities for the Local RAG Chatbot.
"""

import random
import logging
import re
from typing import Dict, List, Optional
from .pattern_matching import PRICE_FORMAT_PATTERN, SPACE_BEFORE_PRICE_PATTERN

logger = logging.getLogger(__name__)

# Response variations for more human-like answers
RESPONSE_VARIATIONS = {
    "uncertainty": [
        "I don't have enough information to answer that question accurately. Could you try asking something else?",
        "I'm unable to find information about that in my knowledge base. Could you try rephrasing your question?",
        "I don't have specific data on that in my database. Is there something else I can help you with?",
        "I don't have sufficient information to provide an accurate answer to that question. Would you like to ask about something else?"
    ],
    "pricing_unknown": [
        "I don't have pricing information for that specific treatment or service in my database. Would you like me to help you with something else?",
        "I couldn't find the cost information for that specific service. Prices can vary by healthcare provider, so it might be best to contact them directly.",
        "I don't have that pricing data in my records. For accurate pricing, I recommend contacting your healthcare provider directly.",
        "I don't have the specific cost information for that in my database. Healthcare pricing can vary based on many factors."
    ],
    "direct_price_response": [
        "The cost for {treatment} is {price}.00 BDT based on our healthcare provider database.",
        "{treatment} costs {price}.00 BDT according to our current pricing information.",
        "The price for {treatment} is {price}.00 BDT as per our healthcare records.",
        "Based on our data, {treatment} costs {price}.00 BDT."
    ],
    "price_disclaimer": [
        " Actual prices may vary depending on the healthcare facility and specific circumstances.",
        " Please note that this is an approximate cost and may vary between providers.",
        " Keep in mind that final costs may differ based on your specific situation and the healthcare provider.",
        " This is an estimated cost and actual prices might vary."
    ],
    "greeting": [
        "Hello! I'm Local RAG Chatbot, your healthcare assistant. How can I help you today?",
        "Hi there! I'm Local RAG Chatbot, ready to assist with your healthcare questions. What can I help you with?",
        "Welcome! I'm Local RAG Chatbot, your medical information assistant. How may I assist you today?",
        "Greetings! I'm Local RAG Chatbot, here to help with your healthcare inquiries. What would you like to know?"
    ],
    "llm_error": [
        "I'm having trouble processing your question at the moment. Our systems might be experiencing high demand. Could you try again in a moment?",
        "I apologize, but my language model is having difficulty generating a response. Could you try simplifying your question?",
        "I'm experiencing some technical difficulties with generating a response. Would you mind rephrasing your question?",
        "It seems I'm having trouble formulating a proper response to your query. Can you try asking in a different way?"
    ],
    "search_error": [
        "I'm having difficulty searching my knowledge base right now. This could be a temporary issue. Could you try again shortly?",
        "I can't seem to retrieve the information you're looking for at the moment. Would you mind trying again?",
        "I'm experiencing issues accessing my medical database. Please try your question again in a moment.",
        "Something went wrong when searching for information. This is likely a temporary issue. Could you try once more?"
    ],
    "connection_error": [
        "I'm having trouble connecting to my knowledge sources at the moment. This might be a temporary network issue.",
        "There seems to be a connection problem with my databases. Please try your question again in a moment.",
        "I can't reach some of my information sources right now. This is likely a temporary issue that will resolve shortly.",
        "I'm experiencing some connectivity issues. Could you try your question again? If the problem persists, it might be resolved soon."
    ],
    "timeout_error": [
        "Your request is taking longer than expected to process. This might be due to high demand or the complexity of your question.",
        "I'm having trouble responding in a timely manner. Could you try a simpler question or try again later?",
        "It's taking me longer than usual to find an answer. This could be due to system load. Please try again shortly.",
        "I wasn't able to complete your request in time. Our systems might be busy at the moment. Please try again."
    ],
    "general_error": [
        "I encountered an unexpected issue while processing your request. Could you try asking in a different way?",
        "Something went wrong on my end. This is likely a temporary issue. Could you try your question again?",
        "I apologize, but I ran into a problem while handling your question. Would you mind rephrasing it?",
        "I hit a snag while working on your request. This is probably temporary. Could you try again?"
    ]
}

def format_response(text: str, max_sentences: Optional[int] = None) -> str:
    """Format the response text with a natural introduction and sentence limit."""
    if not text:
        return "I apologize, but I couldn't find any relevant information for your query."
    
    # Add a random introduction
    intro = random.choice(RESPONSE_VARIATIONS["greeting"])
    
    # Limit sentences if specified
    if max_sentences:
        sentences = text.split('.')
        if len(sentences) > max_sentences:
            text = '. '.join(sentences[:max_sentences]) + '.'
    
    return f"{intro} {text}"

def format_direct_price_response(treatment: str, price: str) -> str:
    """Format a direct price response for treatment BDT queries."""
    # Format the base response with treatment name and price
    response_template = random.choice(RESPONSE_VARIATIONS["direct_price_response"])
    price_response = response_template.format(
        treatment=treatment.strip().title(),
        price=price.strip()
    )
    
    # Add a disclaimer about price variations
    price_response += random.choice(RESPONSE_VARIATIONS["price_disclaimer"])
    
    return price_response

def add_price_info(response: str, treatment: str, price: str) -> str:
    """Add price information to the response in a natural way."""
    # Check if response already contains price information
    if f"{price}.00 BDT" in response:
        return response
    
    # Add price information in a natural way
    price_str = f"{price}.00 BDT"
    
    # Check if the treatment is already mentioned
    if treatment.lower() in response.lower():
        # Try to add price info after treatment mention
        pattern = re.compile(re.escape(treatment), re.IGNORECASE)
        # Find all matches of the treatment name
        matches = list(pattern.finditer(response))
        if matches:
            # Add after the first mention
            match = matches[0]
            insert_pos = match.end()
            response_parts = [response[:insert_pos], f" costs {price_str}", response[insert_pos:]]
            return "".join(response_parts)
    
    # Otherwise, add at the beginning or end
    if len(response) < 80:
        # Add to the end for short responses
        return f"{response} The cost for {treatment} is {price_str}."
    else:
        # Add as a new sentence at the end
        if response.endswith('.'):
            return f"{response} The cost for {treatment} is {price_str}."
        else:
            return f"{response}. The cost for {treatment} is {price_str}."

def format_error_response(error: str, error_type: str = "general_error") -> str:
    """Format error messages in a user-friendly way based on error type."""
    if error_type in RESPONSE_VARIATIONS:
        return random.choice(RESPONSE_VARIATIONS[error_type])
    return random.choice(RESPONSE_VARIATIONS["general_error"])

def add_human_touch(response: str) -> str:
    """Add slight variations to responses to make them more human-like."""
    # Small chance to add a phrase at the beginning
    if random.random() < 0.3:
        starters = [
            "Based on my information, ",
            "According to my database, ",
            "From what I can tell, ",
            "As per my knowledge, "
        ]
        response = random.choice(starters) + response[0].lower() + response[1:]
    
    # Small chance to add a phrase at the end
    if random.random() < 0.2 and not response.endswith("?") and not "let me know" in response.lower():
        enders = [
            " Hope that helps!",
            " Does that answer your question?",
            " Is there anything else you'd like to know?",
            " Let me know if you need any clarification."
        ]
        response = response + random.choice(enders)
    
    return response

def format_price_response(response: str, price_info: Dict[str, str] = None) -> str:
    """Format a response, ensuring pricing information is formatted correctly."""
    if not price_info:
        return response
    
    try:
        modified_response = response
        
        # Ensure BDT format consistency
        modified_response = modified_response.replace(" BDT", ".00 BDT")
        
        # Fix spacing before BDT prices
        modified_response = SPACE_BEFORE_PRICE_PATTERN.sub(' ', modified_response)
        
        # Check if the response already contains price information
        has_price = bool(PRICE_FORMAT_PATTERN.search(modified_response))
        
        # If no price in response yet, try to add it
        if not has_price and price_info:
            # Find the best treatment match from price_info to add
            best_match = None
            for item, price in price_info.items():
                if item.lower() in modified_response.lower():
                    # If this treatment is mentioned in the response, use it
                    best_match = (item, price)
                    break
            
            # Add price information if we found a match
            if best_match:
                modified_response = add_price_info(modified_response, best_match[0], best_match[1])
        
        return modified_response
    except Exception as e:
        logger.error(f"Error formatting price response: {str(e)}")
        # Don't modify the response if there's an error
        return response

def get_error_response(error_type: str = "uncertainty"):
    """Get a random human-like error response based on error type."""
    if error_type in RESPONSE_VARIATIONS:
        return random.choice(RESPONSE_VARIATIONS[error_type])
    return random.choice(RESPONSE_VARIATIONS["uncertainty"])