"""
Device Control Skill
Handles smart home device control requests
"""

import logging
import re
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Simulated device registry
DEVICES = {
    "living_room_light": {"type": "light", "location": "living room", "state": "off", "brightness": 50},
    "bedroom_light": {"type": "light", "location": "bedroom", "state": "off", "brightness": 75},
    "kitchen_light": {"type": "light", "location": "kitchen", "state": "on", "brightness": 100},
    "main_thermostat": {"type": "thermostat", "location": "main", "temperature": 72, "mode": "auto"},
    "front_door_lock": {"type": "lock", "location": "front door", "state": "locked"},
    "security_system": {"type": "security", "location": "main", "state": "armed", "mode": "home"}
}

def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute device control commands
    
    Args:
        input_data (dict): Input containing device control request
        
    Returns:
        dict: Result of device control operation
    """
    try:
        # Extract message and parse device control intent
        message = input_data.get("message", "").lower()
        user_id = input_data.get("user_id", "anonymous")
        
        # Parse the device control request
        parsed_request = parse_device_request(message)
        
        if not parsed_request:
            return {
                "response": "I couldn't understand which device you want to control. Please specify the device and action.",
                "success": False
            }
        
        # Execute the device control
        result = control_device(parsed_request, user_id)
        
        return result
        
    except Exception as e:
        logger.exception(f"Error in device_control skill: {e}")
        return {
            "response": "I encountered an error while trying to control the device. Please try again.",
            "error": str(e),
            "success": False
        }

def parse_device_request(message: str) -> Dict[str, Any]:
    """
    Parse natural language device control request
    
    Args:
        message (str): Natural language message
        
    Returns:
        dict: Parsed device control parameters
    """
    message = message.lower().strip()
    
    # Device type patterns
    device_patterns = {
        "light": r"light|lamp|lighting",
        "thermostat": r"thermostat|temperature|heat|cool|ac|air",
        "lock": r"lock|door",
        "security": r"security|alarm|system"
    }
    
    # Action patterns
    action_patterns = {
        "on": r"turn on|switch on|activate|enable",
        "off": r"turn off|switch off|deactivate|disable",
        "toggle": r"toggle|switch",
        "set": r"set|adjust|change",
        "lock": r"lock",
        "unlock": r"unlock"
    }
    
    # Location patterns
    location_patterns = {
        "living room": r"living room|lounge",
        "bedroom": r"bedroom|bed room",
        "kitchen": r"kitchen",
        "front door": r"front door|main door|entrance"
    }
    
    parsed = {}
    
    # Find device type
    for device_type, pattern in device_patterns.items():
        if re.search(pattern, message):
            parsed["device_type"] = device_type
            break
    
    # Find action
    for action, pattern in action_patterns.items():
        if re.search(pattern, message):
            parsed["action"] = action
            break
    
    # Find location
    for location, pattern in location_patterns.items():
        if re.search(pattern, message):
            parsed["location"] = location
            break
    
    # Extract numeric values (for temperature, brightness, etc.)
    numbers = re.findall(r'\d+', message)
    if numbers:
        parsed["value"] = int(numbers[0])
    
    # If we found at least a device type or action, return the parsed result
    if "device_type" in parsed or "action" in parsed:
        return parsed
    
    return None

def control_device(request: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Control a specific device based on parsed request
    
    Args:
        request (dict): Parsed device control request
        user_id (str): User ID for logging
        
    Returns:
        dict: Result of device control operation
    """
    device_type = request.get("device_type")
    action = request.get("action")
    location = request.get("location")
    value = request.get("value")
    
    # Find matching device
    matching_devices = []
    for device_id, device_info in DEVICES.items():
        if device_type and device_info["type"] != device_type:
            continue
        if location and location not in device_info.get("location", ""):
            continue
        matching_devices.append((device_id, device_info))
    
    if not matching_devices:
        return {
            "response": f"I couldn't find a {device_type or 'device'} {f'in the {location}' if location else ''} to control.",
            "success": False
        }
    
    # Use the first matching device
    device_id, device_info = matching_devices[0]
    
    # Perform the action
    response_message = ""
    
    if action == "on":
        if device_info["type"] == "light":
            DEVICES[device_id]["state"] = "on"
            response_message = f"I've turned on the {device_info['location']} {device_info['type']}."
        elif device_info["type"] == "security":
            DEVICES[device_id]["state"] = "armed"
            response_message = f"I've armed the {device_info['location']} security system."
        else:
            response_message = f"I've turned on the {device_info['location']} {device_info['type']}."
    
    elif action == "off":
        if device_info["type"] == "light":
            DEVICES[device_id]["state"] = "off"
            response_message = f"I've turned off the {device_info['location']} {device_info['type']}."
        elif device_info["type"] == "security":
            DEVICES[device_id]["state"] = "disarmed"
            response_message = f"I've disarmed the {device_info['location']} security system."
        else:
            response_message = f"I've turned off the {device_info['location']} {device_info['type']}."
    
    elif action == "set" and device_info["type"] == "thermostat":
        if value:
            DEVICES[device_id]["temperature"] = value
            response_message = f"I've set the thermostat to {value} degrees."
        else:
            response_message = "Please specify the temperature you'd like to set."
    
    elif action == "lock" and device_info["type"] == "lock":
        DEVICES[device_id]["state"] = "locked"
        response_message = f"I've locked the {device_info['location']}."
    
    elif action == "unlock" and device_info["type"] == "lock":
        DEVICES[device_id]["state"] = "unlocked"
        response_message = f"I've unlocked the {device_info['location']}."
    
    elif action == "toggle":
        if device_info["type"] == "light":
            current_state = DEVICES[device_id]["state"]
            new_state = "off" if current_state == "on" else "on"
            DEVICES[device_id]["state"] = new_state
            response_message = f"I've turned {new_state} the {device_info['location']} {device_info['type']}."
        else:
            response_message = f"I can't toggle the {device_info['type']}. Please specify on or off."
    
    else:
        response_message = f"I'm not sure how to {action} the {device_info['type']}."
    
    # Log the action
    logger.info(f"User {user_id} controlled device {device_id}: {action}")
    
    return {
        "response": response_message,
        "device_controlled": {
            "id": device_id,
            "type": device_info["type"],
            "location": device_info["location"],
            "new_state": DEVICES[device_id]
        },
        "success": True,
        "timestamp": datetime.utcnow().isoformat()
    }

def get_device_status(device_type: str = None, location: str = None) -> Dict[str, Any]:
    """
    Get status of devices
    
    Args:
        device_type (str): Filter by device type
        location (str): Filter by location
        
    Returns:
        dict: Device status information
    """
    filtered_devices = {}
    
    for device_id, device_info in DEVICES.items():
        if device_type and device_info["type"] != device_type:
            continue
        if location and location not in device_info.get("location", ""):
            continue
        filtered_devices[device_id] = device_info.copy()
    
    return {
        "devices": filtered_devices,
        "count": len(filtered_devices),
        "timestamp": datetime.utcnow().isoformat()
    }

