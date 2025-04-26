"""
Local RAG Chatbot - Main Application

This is the main application file that initializes and runs the Local RAG Chatbot, 
which provides medical information
and pricing details from a knowledge base using LLM and vector search.
"""

import os
import time
import logging
import random
import threading
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any

from flask import Flask, request, jsonify, render_template, redirect, url_for
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Application state tracking
app_state = {
    "vector_stores_initialized": False,
    "llm_initialized": False,
    "initialization_errors": [],
    "in_maintenance_mode": False
}

# Fallback error responses for a more natural feel
ERROR_RESPONSES = [
    "I apologize, but I'm having trouble processing your request right now. Could you try rephrasing your question?",
    "Something went wrong while I was retrieving that information. Can you try asking in a different way?",
    "I seem to be having difficulty with that question. Could you try again or ask something else?",
    "I ran into an issue while processing your question. Could you try again with a more specific query?"
]

MAINTENANCE_RESPONSES = [
    "I'm currently in maintenance mode and can't process your request right now. Please try again later.",
    "Our system is undergoing maintenance at the moment. Please try again in a little while.",
    "I'm sorry, but I'm temporarily unavailable due to system maintenance. Please check back soon.",
    "The service is currently undergoing updates. Please try again later when we're back online."
]

# Try to import and initialize components, but don't crash if they fail
try:
    # Import modular components
    from models.vector_store import initialize_vector_stores
    from models.llm import get_llm
    from services.query_processor import process_query
    from services.bot_info import BOT_INFO
    from utils.cache import response_cache, clear_caches
    from utils.pattern_matching import is_direct_price_query, extract_treatment_from_query
    
    # Initialize vector stores
    try:
        initialize_vector_stores()
        app_state["vector_stores_initialized"] = True
        logger.info("Vector stores initialized successfully")
    except Exception as vs_error:
        error_msg = f"Error initializing vector stores: {str(vs_error)}"
        app_state["initialization_errors"].append(error_msg)
        logger.error(error_msg, exc_info=True)
        logger.warning("Note: This may happen if Pinecone API key is not properly set in environment variables")
    
    # Initialize LLM
    try:
        get_llm()
        app_state["llm_initialized"] = True
        logger.info("LLM initialized successfully")
    except Exception as llm_error:
        error_msg = f"Error initializing LLM: {str(llm_error)}"
        app_state["initialization_errors"].append(error_msg)
        logger.error(error_msg, exc_info=True)
        logger.warning("Note: Make sure the LLM model file exists in the models/model_files directory")
    
    # Set maintenance mode to False regardless of initialization status
    # This allows the app to function in degraded mode even if some components failed to initialize
    app_state["in_maintenance_mode"] = False
    if app_state["initialization_errors"]:
        logger.warning("Application starting in degraded mode with the following issues:")
        for err in app_state["initialization_errors"]:
            logger.warning(f"  - {err}")
    else:
        logger.info("Application starting in normal mode with all components initialized")
        
except Exception as e:
    error_msg = f"Critical error during import/setup: {str(e)}"
    app_state["initialization_errors"].append(error_msg)
    logger.error(error_msg, exc_info=True)
    app_state["in_maintenance_mode"] = True
    
    # Define fallback BOT_INFO if it couldn't be imported
    BOT_INFO = {
        "name": "Local RAG Chatbot",
        "version": "1.0-maintenance",
        "description": "An advanced healthcare assistant (currently in maintenance mode)"
    }

# Create a priority thread pool for handling requests
executor = ThreadPoolExecutor(max_workers=3)

# Helper function to check if a query is a direct price query (ends with BDT)
def is_bdt_price_query(query):
    """Check if the query is a direct BDT price lookup (ends with BDT)."""
    return query.upper().endswith("BDT") or is_direct_price_query(query)

# Define routes
@app.route('/')
def index():
    """Render the main index page."""
    maintenance = "true" if app_state["in_maintenance_mode"] else "false"
    return render_template(
        'index.html', 
        bot_name=BOT_INFO.get('name', 'Local RAG Chatbot'), 
        bot_version=BOT_INFO.get('version', '1.0'),
        maintenance_mode=maintenance
    )

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat requests and return responses."""
    try:
        # Check if system is in maintenance mode
        if app_state["in_maintenance_mode"]:
            return jsonify({
                "response": random.choice(MAINTENANCE_RESPONSES),
                "maintenance_mode": True
            })
            
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
        
        question = data['message'].strip()
        logger.info(f"Received question: {question}")
        
        # Process the question
        start_time = time.time()
        
        # Check if this is a direct price query (treatment BDT format)
        is_price_query = is_bdt_price_query(question)
        if is_price_query:
            logger.info(f"Detected BDT price query: {question}")
        
        # Use try-except block specifically for processing
        try:
            response = process_query(question)
            
            # Ensure we have a response
            if not response:
                response = random.choice(ERROR_RESPONSES)
        except Exception as processing_error:
            logger.error(f"Error processing query: {str(processing_error)}", exc_info=True)
            response = random.choice(ERROR_RESPONSES)
        
        processing_time = time.time() - start_time
        logger.info(f"Response generated in {processing_time:.2f} seconds")
        
        return jsonify({
            "response": response,
            "processing_time": f"{processing_time:.2f}s",
            "is_price_query": is_price_query
        })
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        # Return a user-friendly error without exposing details
        return jsonify({
            "response": random.choice(ERROR_RESPONSES)
        }), 200  # Return 200 instead of 500 to handle error gracefully

# Add backwards compatibility for old chat endpoint
@app.route('/chat', methods=['POST'])
def legacy_chat():
    """Redirect old chat endpoint to new API."""
    try:
        # Check if system is in maintenance mode
        if app_state["in_maintenance_mode"]:
            return jsonify({
                "answer": random.choice(MAINTENANCE_RESPONSES),
                "maintenance_mode": True
            })
            
        data = request.get_json()
        if data and 'question' in data:
            # Transform the old format to new format
            transformed_data = {'message': data['question']}
            # Process using the same logic as the new endpoint
            question = transformed_data['message'].strip()
            logger.info(f"Legacy endpoint - Received question: {question}")
            
            # Check if this is a direct price query (treatment BDT format)
            is_price_query = is_bdt_price_query(question)
            if is_price_query:
                logger.info(f"Legacy endpoint - Detected BDT price query: {question}")
            
            # Process the question
            start_time = time.time()
            try:
                response = process_query(question)
                if not response:
                    response = random.choice(ERROR_RESPONSES)
            except Exception as processing_error:
                logger.error(f"Error processing legacy query: {str(processing_error)}", exc_info=True)
                response = random.choice(ERROR_RESPONSES)
            
            processing_time = time.time() - start_time
            
            # Return in the old format expected by the frontend
            return jsonify({
                "answer": response,
                "is_price_query": is_price_query
            })
        else:
            return jsonify({"error": "No question provided"}), 400
    
    except Exception as e:
        logger.error(f"Error in legacy chat endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "answer": random.choice(ERROR_RESPONSES)
        }), 200

@app.route('/api/price', methods=['GET'])
def direct_price_query():
    """Direct price lookup endpoint."""
    try:
        # Check if system is in maintenance mode
        if app_state["in_maintenance_mode"]:
            return jsonify({
                "response": random.choice(MAINTENANCE_RESPONSES),
                "maintenance_mode": True
            }), 503
        
        treatment = request.args.get('treatment')
        if not treatment:
            return jsonify({"error": "No treatment specified"}), 400
        
        # Format as a BDT query and process
        query = f"{treatment} BDT"
        logger.info(f"Direct price endpoint - Query: {query}")
        
        try:
            response = process_query(query)
            
            # Extract just the price if possible
            price_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:BDT|Tk)', response)
            price = price_match.group(1) if price_match else None
            
            return jsonify({
                "treatment": treatment,
                "price": price,
                "response": response,
                "found": price is not None
            })
        except Exception as processing_error:
            logger.error(f"Error in price lookup: {str(processing_error)}", exc_info=True)
            return jsonify({
                "treatment": treatment,
                "price": None,
                "response": random.choice(ERROR_RESPONSES),
                "found": False
            })
        
    except Exception as e:
        logger.error(f"Error in price endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "degraded" if app_state["in_maintenance_mode"] else "ok", 
        "bot_name": BOT_INFO.get('name', 'Local RAG Chatbot'), 
        "version": BOT_INFO.get('version', '1.0'),
        "components": {
            "vector_stores": "ok" if app_state["vector_stores_initialized"] else "error",
            "llm": "ok" if app_state["llm_initialized"] else "error"
        },
        "errors": app_state["initialization_errors"] if app_state["initialization_errors"] else []
    })

# Add legacy health check for backward compatibility
@app.route('/health', methods=['GET'])
def legacy_health_check():
    """Legacy health check endpoint."""
    return jsonify({
        "status": "degraded" if app_state["in_maintenance_mode"] else "healthy", 
        "model": BOT_INFO.get('name', 'Local RAG Chatbot'), 
        "version": BOT_INFO.get('version', '1.0')
    })

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear all caches."""
    try:
        # Check if system is in maintenance mode
        if app_state["in_maintenance_mode"]:
            return jsonify({
                "status": "error", 
                "message": "Cannot clear cache while in maintenance mode"
            }), 503
            
        clear_caches()
        return jsonify({"status": "success", "message": "All caches cleared successfully"})
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """System status endpoint with detailed information."""
    return jsonify({
        "status": "degraded" if app_state["in_maintenance_mode"] else "ok", 
        "maintenance_mode": app_state["in_maintenance_mode"],
        "components": {
            "vector_stores": "ok" if app_state["vector_stores_initialized"] else "error",
            "llm": "ok" if app_state["llm_initialized"] else "error"
        },
        "errors": app_state["initialization_errors"],
        "bot_info": BOT_INFO
    })

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)