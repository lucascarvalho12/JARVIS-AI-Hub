"""
Smartphone Integration Module
Handles communication and integration with smartphone devices
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.models.ai_core import DeviceRegistry, ConversationHistory, TaskExecution, db

class SmartphoneIntegration:
    """Handles smartphone device integration and communication"""
    
    def __init__(self):
        self.device_type = "smartphone"
        self.supported_capabilities = [
            "voice_input",
            "location_tracking", 
            "notifications",
            "camera",
            "microphone",
            "accelerometer",
            "gyroscope",
            "compass",
            "proximity_sensor"
        ]
    
    def register_smartphone(self, user_id: str, device_id: str, device_name: str, 
                          capabilities: List[str] = None) -> Dict[str, Any]:
        """Register a new smartphone device"""
        try:
            if capabilities is None:
                capabilities = ["voice_input", "location_tracking", "notifications"]
            
            # Validate capabilities
            valid_capabilities = [cap for cap in capabilities if cap in self.supported_capabilities]
            
            # Check if device already exists
            existing_device = DeviceRegistry.query.filter_by(device_id=device_id).first()
            if existing_device:
                # Update existing device
                existing_device.device_name = device_name
                existing_device.set_capabilities(valid_capabilities)
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
                    device_category="mobile",
                    status='active'
                )
                device.set_capabilities(valid_capabilities)
                db.session.add(device)
                db.session.commit()
                return {"status": "created", "device": device.to_dict()}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def process_voice_command(self, user_id: str, device_id: str, 
                            command_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process voice command from smartphone"""
        try:
            if context is None:
                context = {}
            
            # Update device last seen
            self._update_device_status(device_id)
            
            # Simple intent recognition (in production, use advanced NLP)
            intent, entities = self._analyze_command(command_text)
            
            # Generate response based on intent
            response = self._generate_response(intent, entities, context, user_id)
            
            # Store conversation history
            conversation = ConversationHistory(
                user_id=user_id,
                session_id=device_id + "_" + str(datetime.utcnow().timestamp()),
                user_input=command_text,
                ai_response=response['text']
            )
            conversation.set_context_data(context)
            db.session.add(conversation)
            db.session.commit()
            
            return {
                "status": "success",
                "intent": intent,
                "entities": entities,
                "response": response,
                "requires_action": response.get('requires_action', False)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def handle_sensor_data(self, user_id: str, device_id: str, 
                          sensor_type: str, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming sensor data from smartphone"""
        try:
            # Update device last seen
            self._update_device_status(device_id)
            
            # Process different types of sensor data
            if sensor_type == "location":
                return self._process_location_data(user_id, device_id, sensor_data)
            elif sensor_type == "accelerometer":
                return self._process_motion_data(user_id, device_id, sensor_data)
            elif sensor_type == "microphone":
                return self._process_audio_data(user_id, device_id, sensor_data)
            else:
                # Store generic sensor data
                return self._store_sensor_data(user_id, device_id, sensor_type, sensor_data)
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def send_notification(self, user_id: str, device_id: str, 
                         title: str, message: str, action_url: str = None) -> Dict[str, Any]:
        """Send notification to smartphone"""
        try:
            # In production, this would use push notification services (FCM, APNS)
            notification_data = {
                "title": title,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "action_url": action_url
            }
            
            # For now, store notification in database for retrieval
            # In production, send via push notification service
            
            return {
                "status": "success",
                "message": "Notification sent",
                "notification_id": f"notif_{datetime.utcnow().timestamp()}"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get current status of smartphone device"""
        try:
            device = DeviceRegistry.query.filter_by(device_id=device_id).first()
            if not device:
                return {"status": "error", "message": "Device not found"}
            
            return {
                "status": "success",
                "device_status": {
                    "device_id": device.device_id,
                    "device_name": device.device_name,
                    "status": device.status,
                    "last_seen": device.last_seen.isoformat(),
                    "capabilities": device.get_capabilities()
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _update_device_status(self, device_id: str):
        """Update device last seen timestamp"""
        device = DeviceRegistry.query.filter_by(device_id=device_id).first()
        if device:
            device.last_seen = datetime.utcnow()
            device.status = 'active'
            db.session.commit()
    
    def _analyze_command(self, command_text: str) -> tuple:
        """Simple command analysis - in production, use advanced NLP"""
        text_lower = command_text.lower()
        
        # Intent recognition
        if any(word in text_lower for word in ['turn on', 'switch on', 'activate']):
            intent = 'device_control_on'
        elif any(word in text_lower for word in ['turn off', 'switch off', 'deactivate']):
            intent = 'device_control_off'
        elif any(word in text_lower for word in ['set temperature', 'adjust temperature']):
            intent = 'climate_control'
        elif any(word in text_lower for word in ['play music', 'play song']):
            intent = 'media_control'
        elif any(word in text_lower for word in ['navigate to', 'drive to', 'go to']):
            intent = 'navigation'
        elif any(word in text_lower for word in ['what is', 'tell me', 'how is']):
            intent = 'information_request'
        elif any(word in text_lower for word in ['remind me', 'set reminder']):
            intent = 'reminder'
        else:
            intent = 'general_conversation'
        
        # Simple entity extraction
        entities = {}
        if 'lights' in text_lower:
            entities['device_type'] = 'lights'
        elif 'thermostat' in text_lower:
            entities['device_type'] = 'thermostat'
        elif 'music' in text_lower:
            entities['media_type'] = 'music'
        elif 'car' in text_lower:
            entities['target_system'] = 'car'
        elif 'home' in text_lower:
            entities['target_system'] = 'home'
        
        return intent, entities
    
    def _generate_response(self, intent: str, entities: Dict[str, Any], 
                          context: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Generate appropriate response based on intent"""
        responses = {
            'device_control_on': f"I'll turn on the {entities.get('device_type', 'device')} for you.",
            'device_control_off': f"I'll turn off the {entities.get('device_type', 'device')} for you.",
            'climate_control': "I'll adjust the temperature as requested.",
            'media_control': "I'll start playing music for you.",
            'navigation': "I'll set up navigation for you.",
            'information_request': "Let me get that information for you.",
            'reminder': "I'll set that reminder for you.",
            'general_conversation': "I'm here to help! What would you like me to do?"
        }
        
        response_text = responses.get(intent, "I understand you want help, but I'm not sure how to assist with that specific request.")
        
        # Determine if action is required
        requires_action = intent in ['device_control_on', 'device_control_off', 'climate_control', 
                                   'media_control', 'navigation', 'reminder']
        
        return {
            'text': response_text,
            'requires_action': requires_action,
            'intent': intent,
            'entities': entities
        }
    
    def _process_location_data(self, user_id: str, device_id: str, 
                             location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process GPS location data"""
        # In production, store in time-series database
        # For now, just acknowledge receipt
        return {
            "status": "success",
            "message": "Location data processed",
            "location": {
                "latitude": location_data.get("latitude"),
                "longitude": location_data.get("longitude"),
                "accuracy": location_data.get("accuracy"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def _process_motion_data(self, user_id: str, device_id: str, 
                           motion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process accelerometer/motion data"""
        # Analyze motion patterns for activity recognition
        return {
            "status": "success",
            "message": "Motion data processed",
            "activity": self._detect_activity(motion_data)
        }
    
    def _process_audio_data(self, user_id: str, device_id: str, 
                          audio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process audio/microphone data"""
        # In production, this would include speech-to-text processing
        return {
            "status": "success",
            "message": "Audio data processed",
            "audio_level": audio_data.get("level", 0)
        }
    
    def _store_sensor_data(self, user_id: str, device_id: str, 
                          sensor_type: str, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store generic sensor data"""
        # In production, store in time-series database
        return {
            "status": "success",
            "message": f"{sensor_type} data stored",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _detect_activity(self, motion_data: Dict[str, Any]) -> str:
        """Simple activity detection based on motion data"""
        # In production, use machine learning for activity recognition
        acceleration = motion_data.get("acceleration", {})
        total_acceleration = sum([
            abs(acceleration.get("x", 0)),
            abs(acceleration.get("y", 0)),
            abs(acceleration.get("z", 0))
        ])
        
        if total_acceleration > 15:
            return "running"
        elif total_acceleration > 8:
            return "walking"
        elif total_acceleration > 2:
            return "moving"
        else:
            return "stationary"

