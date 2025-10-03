"""
Orchestrator Module
Handles skill routing, circuit breaking, and GPT fallback for the JARVIS AI Hub
"""

import importlib
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

from pybreaker import CircuitBreaker, CircuitBreakerError
from prometheus_client import Counter, Histogram
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import schema loader
from src.schema_loader import match_schema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
SKILL_CALLS = Counter("skill_calls_total", "Total skill executions", ["skill"])
SKILL_FAILURES = Counter("skill_failures_total", "Total skill failures", ["skill"])
GPT_CALLS = Counter("gpt_calls_total", "Total GPT fallback calls")
REQUEST_DURATION = Histogram("request_duration_seconds", "Request processing duration", ["type"])

# Circuit breaker configuration
CIRCUIT_BREAKER_CONFIG = {
    "fail_max": 3,          # Number of failures before opening circuit
    "reset_timeout": 30     # Seconds before attempting to close circuit
}

# Create circuit breaker
breaker = CircuitBreaker(**CIRCUIT_BREAKER_CONFIG)

# OpenAI client (lazy initialization)
_openai_client = None

def get_openai_client():
    """Get or create OpenAI client"""
    global _openai_client
    if _openai_client is None:
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not found in environment variables")
                return None
            _openai_client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except ImportError:
            logger.error("OpenAI library not installed. Install with: pip install openai")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return None
    return _openai_client

async def handle_request(input_data: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
    """
    Handle incoming requests by routing to skills or falling back to GPT
    
    Args:
        input_data (dict): The input data containing user request
        user_id (str): Optional user ID for personalization
        
    Returns:
        dict: Response from skill or GPT fallback
    """
    start_time = datetime.utcnow()
    
    try:
        # Ensure input_data is a dictionary
        if not isinstance(input_data, dict):
            input_data = {"message": str(input_data)}
        
        # Add user_id to input_data if provided
        if user_id:
            input_data["user_id"] = user_id
        
        # Try to match a skill schema
        skill_name, schema = match_schema(input_data)
        
        if skill_name and schema:
            # Execute the matched skill
            result = await execute_skill(skill_name, input_data)
            
            # Record metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            REQUEST_DURATION.labels(type="skill").observe(duration)
            
            return result
        
        # No skill matched - use GPT fallback
        result = await gpt_fallback(input_data)
        
        # Record metrics
        duration = (datetime.utcnow() - start_time).total_seconds()
        REQUEST_DURATION.labels(type="gpt_fallback").observe(duration)
        
        return result
        
    except Exception as e:
        logger.exception(f"Error in handle_request: {e}")
        duration = (datetime.utcnow() - start_time).total_seconds()
        REQUEST_DURATION.labels(type="error").observe(duration)
        
        return {
            "response": "I apologize, but I encountered an error while processing your request. Please try again.",
            "error": True,
            "timestamp": datetime.utcnow().isoformat()
        }

async def execute_skill(skill_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a specific skill with circuit breaker protection
    
    Args:
        skill_name (str): Name of the skill to execute
        input_data (dict): Input data for the skill
        
    Returns:
        dict: Result from skill execution
    """
    try:
        # Import the skill module dynamically
        skill_module_name = f"src.skills.{skill_name}"
        
        # Check if module is already imported
        if skill_module_name in sys.modules:
            skill_module = sys.modules[skill_module_name]
        else:
            skill_module = importlib.import_module(skill_module_name)
        
        # Increment skill call counter
        SKILL_CALLS.labels(skill=skill_name).inc()
        
        # Execute skill with circuit breaker protection
        if hasattr(skill_module, 'execute'):
            result = breaker.call(skill_module.execute, input_data)
        elif hasattr(skill_module, 'handle'):
            result = breaker.call(skill_module.handle, input_data)
        else:
            raise AttributeError(f"Skill module {skill_name} must have an 'execute' or 'handle' function")
        
        logger.info(f"Skill '{skill_name}' executed successfully")
        
        # Ensure result is a dictionary
        if not isinstance(result, dict):
            result = {"response": str(result)}
        
        # Add metadata
        result.update({
            "skill_used": skill_name,
            "timestamp": datetime.utcnow().isoformat(),
            "success": True
        })
        
        return result
        
    except CircuitBreakerError:
        SKILL_FAILURES.labels(skill=skill_name).inc()
        logger.error(f"Skill '{skill_name}' disabled by circuit breaker")
        
        return {
            "response": f"The '{skill_name}' capability is temporarily unavailable. Please try again later.",
            "skill_used": skill_name,
            "circuit_breaker_open": True,
            "timestamp": datetime.utcnow().isoformat(),
            "success": False
        }
        
    except ImportError as e:
        SKILL_FAILURES.labels(skill=skill_name).inc()
        logger.error(f"Failed to import skill module '{skill_name}': {e}")
        
        return {
            "response": f"The '{skill_name}' capability is not available.",
            "skill_used": skill_name,
            "error": "module_not_found",
            "timestamp": datetime.utcnow().isoformat(),
            "success": False
        }
        
    except Exception as e:
        SKILL_FAILURES.labels(skill=skill_name).inc()
        logger.exception(f"Error executing skill '{skill_name}': {e}")
        
        return {
            "response": f"An error occurred while executing the '{skill_name}' capability.",
            "skill_used": skill_name,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "success": False
        }

async def gpt_fallback(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback to OpenAI GPT when no skill matches
    
    Args:
        input_data (dict): Input data for GPT
        
    Returns:
        dict: Response from GPT
    """
    logger.info("No schema matched. Using OpenAI GPT fallback.")
    GPT_CALLS.inc()
    
    try:
        client = get_openai_client()
        if not client:
            return {
                "response": "I'm sorry, but I'm unable to process that request right now. The AI service is not available.",
                "error": "openai_unavailable",
                "timestamp": datetime.utcnow().isoformat(),
                "success": False
            }
        
        # Extract message from input_data
        user_message = input_data.get("message", str(input_data))
        user_id = input_data.get("user_id", "anonymous")
        
        # Create system message with context
        system_message = """You are JARVIS, an advanced AI assistant inspired by Tony Stark's AI companion. 
You are intelligent, helpful, and slightly witty. You can help with a wide range of tasks including:
- Answering questions and providing information
- Helping with device control and automation
- Providing recommendations and suggestions
- Assisting with planning and organization
- General conversation and support

Respond in a helpful and engaging manner, maintaining the sophisticated yet approachable personality of JARVIS."""
        
        # Add user context if available
        if user_id != "anonymous":
            system_message += f"\n\nYou are currently assisting user: {user_id}"
        
        # Make the API call
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective model
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        response_text = completion.choices[0].message.content
        
        return {
            "response": response_text,
            "source": "gpt_fallback",
            "model": "gpt-4o-mini",
            "timestamp": datetime.utcnow().isoformat(),
            "success": True
        }
        
    except Exception as e:
        logger.exception(f"OpenAI GPT fallback failed: {e}")
        
        return {
            "response": "I apologize, but I'm unable to process that request right now. Please try again later.",
            "error": str(e),
            "source": "gpt_fallback",
            "timestamp": datetime.utcnow().isoformat(),
            "success": False
        }

def get_system_status() -> Dict[str, Any]:
    """
    Get current system status including circuit breaker states
    
    Returns:
        dict: System status information
    """
    return {
        "circuit_breaker": {
            "state": breaker.current_state,
            "fail_counter": breaker.fail_counter,
            "last_failure": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None,
            "next_attempt": breaker.next_attempt_time.isoformat() if breaker.next_attempt_time else None
        },
        "openai_available": get_openai_client() is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

def reset_circuit_breaker():
    """Reset the circuit breaker manually"""
    breaker.reset()
    logger.info("Circuit breaker reset manually")

# Initialize the module
logger.info("Orchestrator module initialized")

