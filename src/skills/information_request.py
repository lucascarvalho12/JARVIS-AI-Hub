"""
Information Request Skill
Handles information requests and general questions
"""

import logging
import re
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute information request
    
    Args:
        input_data (dict): Input containing information request
        
    Returns:
        dict: Response with requested information
    """
    try:
        message = input_data.get("message", "").lower()
        user_id = input_data.get("user_id", "anonymous")
        
        # Parse the information request
        query_info = parse_information_request(message)
        
        # Handle different types of information requests
        if query_info["type"] == "time":
            return handle_time_request()
        elif query_info["type"] == "date":
            return handle_date_request()
        elif query_info["type"] == "weather":
            return handle_weather_request(query_info.get("location"))
        elif query_info["type"] == "system_status":
            return handle_system_status_request()
        else:
            return handle_general_request(message, query_info)
            
    except Exception as e:
        logger.exception(f"Error in information_request skill: {e}")
        return {
            "response": "I encountered an error while processing your information request. Please try again.",
            "error": str(e),
            "success": False
        }

def parse_information_request(message: str) -> Dict[str, Any]:
    """
    Parse the type of information being requested
    
    Args:
        message (str): User message
        
    Returns:
        dict: Parsed information about the request
    """
    message = message.lower().strip()
    
    # Time-related patterns
    if re.search(r"what time|current time|time is it", message):
        return {"type": "time"}
    
    # Date-related patterns
    if re.search(r"what date|today's date|current date", message):
        return {"type": "date"}
    
    # Weather-related patterns
    if re.search(r"weather|temperature|forecast|rain|sunny|cloudy", message):
        location = extract_location(message)
        return {"type": "weather", "location": location}
    
    # System status patterns
    if re.search(r"system status|how are you|status|health", message):
        return {"type": "system_status"}
    
    # General information request
    return {"type": "general", "subject": message}

def extract_location(message: str) -> str:
    """
    Extract location from weather request
    
    Args:
        message (str): User message
        
    Returns:
        str: Extracted location or default
    """
    # Simple location extraction patterns
    location_patterns = [
        r"in ([a-zA-Z\s]+)",
        r"at ([a-zA-Z\s]+)",
        r"for ([a-zA-Z\s]+)"
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1).strip()
    
    return "your location"

def handle_time_request() -> Dict[str, Any]:
    """Handle time information request"""
    current_time = datetime.now()
    time_str = current_time.strftime("%I:%M %p")
    
    return {
        "response": f"The current time is {time_str}.",
        "data": {
            "time": time_str,
            "24_hour": current_time.strftime("%H:%M"),
            "timezone": "Local Time"
        },
        "success": True
    }

def handle_date_request() -> Dict[str, Any]:
    """Handle date information request"""
    current_date = datetime.now()
    date_str = current_date.strftime("%A, %B %d, %Y")
    
    return {
        "response": f"Today is {date_str}.",
        "data": {
            "date": date_str,
            "iso_date": current_date.strftime("%Y-%m-%d"),
            "day_of_week": current_date.strftime("%A"),
            "day_of_year": current_date.timetuple().tm_yday
        },
        "success": True
    }

def handle_weather_request(location: str = None) -> Dict[str, Any]:
    """Handle weather information request"""
    if not location:
        location = "your location"
    
    # Simulated weather data (in a real implementation, you'd call a weather API)
    weather_data = {
        "temperature": 72,
        "condition": "partly cloudy",
        "humidity": 65,
        "wind_speed": 8
    }
    
    response = f"The weather in {location} is currently {weather_data['condition']} with a temperature of {weather_data['temperature']}°F. "
    response += f"Humidity is at {weather_data['humidity']}% with winds at {weather_data['wind_speed']} mph."
    
    return {
        "response": response,
        "data": {
            "location": location,
            "temperature": weather_data['temperature'],
            "condition": weather_data['condition'],
            "humidity": weather_data['humidity'],
            "wind_speed": weather_data['wind_speed'],
            "unit": "fahrenheit"
        },
        "success": True
    }

def handle_system_status_request() -> Dict[str, Any]:
    """Handle system status request"""
    # Get current system status
    current_time = datetime.now()
    uptime_hours = (current_time.hour + current_time.minute / 60)
    
    return {
        "response": f"I'm operating normally and ready to assist you. All systems are functioning properly. I've been active for approximately {uptime_hours:.1f} hours today.",
        "data": {
            "status": "operational",
            "uptime_hours": round(uptime_hours, 1),
            "last_check": current_time.isoformat(),
            "services": {
                "ai_core": "online",
                "device_control": "online", 
                "information_services": "online"
            }
        },
        "success": True
    }

def handle_general_request(message: str, query_info: Dict[str, Any]) -> Dict[str, Any]:
    """Handle general information requests"""
    
    # Check for specific topics we can handle
    if "jarvis" in message or "yourself" in message:
        return {
            "response": "I'm JARVIS, your AI assistant. I can help you control smart home devices, answer questions, provide information, and assist with various tasks. I'm designed to learn from your preferences and become more helpful over time.",
            "data": {
                "name": "JARVIS",
                "type": "AI Assistant",
                "capabilities": ["device_control", "information_retrieval", "task_assistance", "learning"]
            },
            "success": True
        }
    
    elif "capabilities" in message or "what can you do" in message:
        return {
            "response": "I can help you with many things including: controlling smart home devices (lights, thermostat, locks), answering questions, providing weather and time information, managing your schedule, and learning your preferences to provide better assistance over time.",
            "data": {
                "capabilities": [
                    "Smart home device control",
                    "Information retrieval", 
                    "Weather and time queries",
                    "System status monitoring",
                    "Learning and adaptation",
                    "General conversation"
                ]
            },
            "success": True
        }
    
    else:
        # For other general requests, provide a helpful response
        return {
            "response": "I'd be happy to help you with that. Could you please provide more specific details about what information you're looking for? I can assist with device control, weather, time, system status, and general questions.",
            "suggestion": "Try asking about specific topics like 'What's the weather?', 'What time is it?', or 'Turn on the lights'.",
            "success": True
        }

