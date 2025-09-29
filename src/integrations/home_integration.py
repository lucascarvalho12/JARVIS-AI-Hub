"""
Home Integration Module
Handles communication and integration with smart home devices and systems
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.models.ai_core import DeviceRegistry, TaskExecution, db

class HomeIntegration:
    """Handles smart home device integration and automation"""
    
    def __init__(self):
        self.device_type = "home_device"
        self.supported_device_categories = [
            "light",
            "thermostat", 
            "lock",
            "camera",
            "sensor",
            "switch",
            "outlet",
            "fan",
            "blinds",
            "garage_door",
            "doorbell",
            "smoke_detector",
            "security_system",
            "speaker",
            "tv",
            "appliance"
        ]
        
        # Device state cache
        self.device_states = {}
        
        # Predefined scenes
        self.scenes = {
            "good_morning": {
                "name": "Good Morning",
                "description": "Turn on lights, adjust thermostat, start coffee maker",
                "actions": [
                    {"device_category": "light", "action": "turn_on", "brightness": 80},
                    {"device_category": "thermostat", "action": "set_temperature", "temperature": 72},
                    {"device_category": "appliance", "action": "start", "device_name": "coffee_maker"}
                ]
            },
            "movie_time": {
                "name": "Movie Time", 
                "description": "Dim lights, turn on TV, close blinds",
                "actions": [
                    {"device_category": "light", "action": "dim", "brightness": 20},
                    {"device_category": "tv", "action": "turn_on"},
                    {"device_category": "blinds", "action": "close"}
                ]
            },
            "good_night": {
                "name": "Good Night",
                "description": "Turn off all lights, lock doors, set security system",
                "actions": [
                    {"device_category": "light", "action": "turn_off"},
                    {"device_category": "lock", "action": "lock"},
                    {"device_category": "security_system", "action": "arm"}
                ]
            },
            "away_mode": {
                "name": "Away Mode",
                "description": "Secure home when leaving",
                "actions": [
                    {"device_category": "light", "action": "turn_off"},
                    {"device_category": "thermostat", "action": "set_temperature", "temperature": 68},
                    {"device_category": "lock", "action": "lock"},
                    {"device_category": "security_system", "action": "arm"}
                ]
            }
        }
    
    def register_home_device(self, user_id: str, device_id: str, device_name: str,
                           device_category: str, room: str, capabilities: List[str] = None) -> Dict[str, Any]:
        """Register a new smart home device"""
        try:
            if device_category not in self.supported_device_categories:
                return {"status": "error", "message": f"Unsupported device category: {device_category}"}
            
            if capabilities is None:
                capabilities = self._get_default_capabilities(device_category)
            
            # Check if device already exists
            existing_device = DeviceRegistry.query.filter_by(device_id=device_id).first()
            if existing_device:
                # Update existing device
                existing_device.device_name = device_name
                existing_device.device_category = device_category
                existing_device.set_capabilities(capabilities)
                existing_device.last_seen = datetime.utcnow()
                existing_device.status = 'active'
                db.session.commit()
                return {"status": "updated", "device": existing_device.to_dict()}
            else:
                # Create new device
                device = DeviceRegistry(
                    user_id=user_id,
                    device_id=device_id,
                    device_name=device_name,
                    device_type=self.device_type,
                    device_category=device_category,
                    status='active'
                )
                device.set_capabilities(capabilities)
                db.session.add(device)
                db.session.commit()
                
                # Initialize device state
                self.device_states[device_id] = {
                    "room": room,
                    "state": "off" if device_category in ["light", "switch", "outlet"] else "unknown",
                    "last_updated": datetime.utcnow().isoformat()
                }
                
                return {"status": "created", "device": device.to_dict()}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def control_device(self, device_id: str, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Control a specific smart home device"""
        try:
            if parameters is None:
                parameters = {}
            
            device = DeviceRegistry.query.filter_by(device_id=device_id).first()
            if not device:
                return {"status": "error", "message": "Device not found"}
            
            # Update device last seen
            device.last_seen = datetime.utcnow()
            device.status = 'active'
            db.session.commit()
            
            # Execute command based on device category
            result = self._execute_device_command(device, command, parameters)
            
            # Update device state cache
            if device_id in self.device_states:
                self.device_states[device_id]["last_updated"] = datetime.utcnow().isoformat()
                if "state" in result:
                    self.device_states[device_id]["state"] = result["state"]
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_device_state(self, device_id: str) -> Dict[str, Any]:
        """Get current state of a smart home device"""
        try:
            device = DeviceRegistry.query.filter_by(device_id=device_id).first()
            if not device:
                return {"status": "error", "message": "Device not found"}
            
            # Get cached state or create default
            state = self.device_states.get(device_id, {
                "state": "unknown",
                "last_updated": datetime.utcnow().isoformat()
            })
            
            return {
                "status": "success",
                "device_id": device_id,
                "device_name": device.device_name,
                "device_category": device.device_category,
                "capabilities": device.get_capabilities(),
                "current_state": state
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_devices_by_room(self, user_id: str, room: str) -> Dict[str, Any]:
        """Get all devices in a specific room"""
        try:
            devices = DeviceRegistry.query.filter_by(
                user_id=user_id,
                device_type=self.device_type
            ).all()
            
            room_devices = []
            for device in devices:
                device_state = self.device_states.get(device.device_id, {})
                if device_state.get("room", "").lower() == room.lower():
                    device_info = device.to_dict()
                    device_info["current_state"] = device_state
                    room_devices.append(device_info)
            
            return {
                "status": "success",
                "room": room,
                "devices": room_devices
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def activate_scene(self, user_id: str, scene_id: str) -> Dict[str, Any]:
        """Activate a predefined home automation scene"""
        try:
            if scene_id not in self.scenes:
                return {"status": "error", "message": f"Scene '{scene_id}' not found"}
            
            scene = self.scenes[scene_id]
            results = []
            
            # Execute each action in the scene
            for action in scene["actions"]:
                device_category = action["device_category"]
                command = action["action"]
                parameters = {k: v for k, v in action.items() if k not in ["device_category", "action"]}
                
                # Find devices of this category for the user
                devices = DeviceRegistry.query.filter_by(
                    user_id=user_id,
                    device_type=self.device_type,
                    device_category=device_category
                ).all()
                
                for device in devices:
                    # Skip specific device name filtering if specified
                    if "device_name" in parameters:
                        if device.device_name.lower() != parameters["device_name"].lower():
                            continue
                        parameters = {k: v for k, v in parameters.items() if k != "device_name"}
                    
                    result = self.control_device(device.device_id, command, parameters)
                    results.append({
                        "device_id": device.device_id,
                        "device_name": device.device_name,
                        "result": result
                    })
            
            return {
                "status": "success",
                "scene": scene["name"],
                "message": f"Scene '{scene['name']}' activated",
                "results": results
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_available_scenes(self) -> Dict[str, Any]:
        """Get list of available automation scenes"""
        return {
            "status": "success",
            "scenes": [
                {
                    "scene_id": scene_id,
                    "name": scene_data["name"],
                    "description": scene_data["description"]
                }
                for scene_id, scene_data in self.scenes.items()
            ]
        }
    
    def create_automation(self, user_id: str, automation_name: str, 
                         trigger: Dict[str, Any], actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a custom home automation"""
        try:
            # In production, store automation rules in database
            automation_id = f"auto_{datetime.utcnow().timestamp()}"
            
            automation = {
                "automation_id": automation_id,
                "name": automation_name,
                "user_id": user_id,
                "trigger": trigger,
                "actions": actions,
                "created_at": datetime.utcnow().isoformat(),
                "active": True
            }
            
            # For now, just return the automation definition
            return {
                "status": "success",
                "message": f"Automation '{automation_name}' created",
                "automation": automation
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def process_sensor_data(self, device_id: str, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process sensor data and trigger automations if needed"""
        try:
            device = DeviceRegistry.query.filter_by(device_id=device_id).first()
            if not device:
                return {"status": "error", "message": "Device not found"}
            
            # Update device last seen
            device.last_seen = datetime.utcnow()
            db.session.commit()
            
            # Update device state with sensor data
            if device_id in self.device_states:
                self.device_states[device_id].update(sensor_data)
                self.device_states[device_id]["last_updated"] = datetime.utcnow().isoformat()
            
            # Analyze sensor data for automation triggers
            triggers = self._analyze_sensor_data(device, sensor_data)
            
            return {
                "status": "success",
                "message": "Sensor data processed",
                "triggers": triggers
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _get_default_capabilities(self, device_category: str) -> List[str]:
        """Get default capabilities for a device category"""
        capability_map = {
            "light": ["on_off", "brightness", "color"],
            "thermostat": ["temperature_control", "mode_control", "scheduling"],
            "lock": ["lock_unlock", "status_monitoring"],
            "camera": ["video_streaming", "motion_detection", "recording"],
            "sensor": ["data_monitoring", "alerting"],
            "switch": ["on_off"],
            "outlet": ["on_off", "power_monitoring"],
            "fan": ["on_off", "speed_control"],
            "blinds": ["open_close", "position_control"],
            "garage_door": ["open_close", "status_monitoring"],
            "doorbell": ["video_streaming", "motion_detection", "two_way_audio"],
            "smoke_detector": ["smoke_detection", "alerting"],
            "security_system": ["arm_disarm", "zone_control", "alerting"],
            "speaker": ["audio_playback", "volume_control"],
            "tv": ["on_off", "channel_control", "volume_control"],
            "appliance": ["on_off", "mode_control"]
        }
        
        return capability_map.get(device_category, ["basic_control"])
    
    def _execute_device_command(self, device: DeviceRegistry, command: str, 
                              parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command on specific device based on its category"""
        category = device.device_category
        
        if category == "light":
            return self._control_light(device, command, parameters)
        elif category == "thermostat":
            return self._control_thermostat(device, command, parameters)
        elif category == "lock":
            return self._control_lock(device, command, parameters)
        elif category == "camera":
            return self._control_camera(device, command, parameters)
        elif category in ["switch", "outlet"]:
            return self._control_switch(device, command, parameters)
        elif category == "fan":
            return self._control_fan(device, command, parameters)
        elif category == "blinds":
            return self._control_blinds(device, command, parameters)
        elif category == "security_system":
            return self._control_security_system(device, command, parameters)
        else:
            return self._control_generic_device(device, command, parameters)
    
    def _control_light(self, device: DeviceRegistry, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control light device"""
        if command == "turn_on":
            brightness = parameters.get("brightness", 100)
            return {
                "status": "success",
                "message": f"{device.device_name} turned on at {brightness}% brightness",
                "state": "on",
                "brightness": brightness
            }
        elif command == "turn_off":
            return {
                "status": "success", 
                "message": f"{device.device_name} turned off",
                "state": "off"
            }
        elif command == "dim" or command == "set_brightness":
            brightness = parameters.get("brightness", 50)
            return {
                "status": "success",
                "message": f"{device.device_name} brightness set to {brightness}%",
                "state": "on",
                "brightness": brightness
            }
        elif command == "set_color":
            color = parameters.get("color", "white")
            return {
                "status": "success",
                "message": f"{device.device_name} color set to {color}",
                "state": "on",
                "color": color
            }
        else:
            return {"status": "error", "message": f"Unknown light command: {command}"}
    
    def _control_thermostat(self, device: DeviceRegistry, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control thermostat device"""
        if command == "set_temperature":
            temperature = parameters.get("temperature", 72)
            return {
                "status": "success",
                "message": f"{device.device_name} temperature set to {temperature}°F",
                "state": "active",
                "temperature": temperature
            }
        elif command == "set_mode":
            mode = parameters.get("mode", "auto")
            return {
                "status": "success",
                "message": f"{device.device_name} mode set to {mode}",
                "state": "active",
                "mode": mode
            }
        else:
            return {"status": "error", "message": f"Unknown thermostat command: {command}"}
    
    def _control_lock(self, device: DeviceRegistry, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control lock device"""
        if command == "lock":
            return {
                "status": "success",
                "message": f"{device.device_name} locked",
                "state": "locked"
            }
        elif command == "unlock":
            return {
                "status": "success",
                "message": f"{device.device_name} unlocked", 
                "state": "unlocked"
            }
        else:
            return {"status": "error", "message": f"Unknown lock command: {command}"}
    
    def _control_camera(self, device: DeviceRegistry, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control camera device"""
        if command == "start_recording":
            return {
                "status": "success",
                "message": f"{device.device_name} started recording",
                "state": "recording"
            }
        elif command == "stop_recording":
            return {
                "status": "success",
                "message": f"{device.device_name} stopped recording",
                "state": "idle"
            }
        elif command == "take_snapshot":
            return {
                "status": "success",
                "message": f"{device.device_name} snapshot taken",
                "state": "idle"
            }
        else:
            return {"status": "error", "message": f"Unknown camera command: {command}"}
    
    def _control_switch(self, device: DeviceRegistry, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control switch/outlet device"""
        if command == "turn_on":
            return {
                "status": "success",
                "message": f"{device.device_name} turned on",
                "state": "on"
            }
        elif command == "turn_off":
            return {
                "status": "success",
                "message": f"{device.device_name} turned off",
                "state": "off"
            }
        else:
            return {"status": "error", "message": f"Unknown switch command: {command}"}
    
    def _control_fan(self, device: DeviceRegistry, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control fan device"""
        if command == "turn_on":
            speed = parameters.get("speed", "medium")
            return {
                "status": "success",
                "message": f"{device.device_name} turned on at {speed} speed",
                "state": "on",
                "speed": speed
            }
        elif command == "turn_off":
            return {
                "status": "success",
                "message": f"{device.device_name} turned off",
                "state": "off"
            }
        elif command == "set_speed":
            speed = parameters.get("speed", "medium")
            return {
                "status": "success",
                "message": f"{device.device_name} speed set to {speed}",
                "state": "on",
                "speed": speed
            }
        else:
            return {"status": "error", "message": f"Unknown fan command: {command}"}
    
    def _control_blinds(self, device: DeviceRegistry, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control blinds device"""
        if command == "open":
            return {
                "status": "success",
                "message": f"{device.device_name} opened",
                "state": "open"
            }
        elif command == "close":
            return {
                "status": "success",
                "message": f"{device.device_name} closed",
                "state": "closed"
            }
        elif command == "set_position":
            position = parameters.get("position", 50)
            return {
                "status": "success",
                "message": f"{device.device_name} position set to {position}%",
                "state": "partial",
                "position": position
            }
        else:
            return {"status": "error", "message": f"Unknown blinds command: {command}"}
    
    def _control_security_system(self, device: DeviceRegistry, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control security system"""
        if command == "arm":
            mode = parameters.get("mode", "away")
            return {
                "status": "success",
                "message": f"Security system armed in {mode} mode",
                "state": "armed",
                "mode": mode
            }
        elif command == "disarm":
            return {
                "status": "success",
                "message": "Security system disarmed",
                "state": "disarmed"
            }
        else:
            return {"status": "error", "message": f"Unknown security system command: {command}"}
    
    def _control_generic_device(self, device: DeviceRegistry, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Control generic device"""
        return {
            "status": "success",
            "message": f"{device.device_name} command '{command}' executed",
            "state": "active"
        }
    
    def _analyze_sensor_data(self, device: DeviceRegistry, sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze sensor data for automation triggers"""
        triggers = []
        
        # Motion detection
        if "motion" in sensor_data and sensor_data["motion"]:
            triggers.append({
                "type": "motion_detected",
                "device_id": device.device_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Temperature thresholds
        if "temperature" in sensor_data:
            temp = sensor_data["temperature"]
            if temp > 80:  # Fahrenheit
                triggers.append({
                    "type": "high_temperature",
                    "device_id": device.device_id,
                    "value": temp,
                    "timestamp": datetime.utcnow().isoformat()
                })
            elif temp < 60:
                triggers.append({
                    "type": "low_temperature", 
                    "device_id": device.device_id,
                    "value": temp,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Door/window open detection
        if "door_open" in sensor_data and sensor_data["door_open"]:
            triggers.append({
                "type": "door_opened",
                "device_id": device.device_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return triggers

