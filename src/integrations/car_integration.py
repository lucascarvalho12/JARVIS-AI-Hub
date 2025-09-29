"""
Car Integration Module
Handles communication and integration with vehicle systems
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.models.ai_core import DeviceRegistry, TaskExecution, db

class CarIntegration:
    """Handles car/vehicle integration and communication"""
    
    def __init__(self):
        self.device_type = "car"
        self.supported_capabilities = [
            "navigation",
            "media_control",
            "climate_control",
            "door_locks",
            "engine_control",
            "diagnostics",
            "fuel_monitoring",
            "tire_pressure",
            "location_tracking",
            "emergency_services"
        ]
        
        # Vehicle status cache
        self.vehicle_status_cache = {}
    
    def register_vehicle(self, user_id: str, vehicle_id: str, vehicle_name: str,
                        make: str, model: str, year: int, capabilities: List[str] = None) -> Dict[str, Any]:
        """Register a new vehicle"""
        try:
            if capabilities is None:
                capabilities = ["navigation", "media_control", "door_locks", "diagnostics"]
            
            # Validate capabilities
            valid_capabilities = [cap for cap in capabilities if cap in self.supported_capabilities]
            
            # Check if vehicle already exists
            existing_vehicle = DeviceRegistry.query.filter_by(device_id=vehicle_id).first()
            if existing_vehicle:
                # Update existing vehicle
                existing_vehicle.device_name = vehicle_name
                existing_vehicle.set_capabilities(valid_capabilities)
                existing_vehicle.last_seen = datetime.utcnow()
                existing_vehicle.status = 'active'
                db.session.commit()
                return {"status": "updated", "vehicle": existing_vehicle.to_dict()}
            else:
                # Create new vehicle
                vehicle = DeviceRegistry(
                    user_id=user_id,
                    device_id=vehicle_id,
                    device_name=vehicle_name,
                    device_type=self.device_type,
                    device_category="vehicle",
                    status='active'
                )
                vehicle.set_capabilities(valid_capabilities)
                db.session.add(vehicle)
                db.session.commit()
                
                # Initialize vehicle status cache
                self.vehicle_status_cache[vehicle_id] = {
                    "make": make,
                    "model": model,
                    "year": year,
                    "fuel_level": 100.0,
                    "engine_on": False,
                    "doors_locked": True,
                    "location": {"latitude": 0.0, "longitude": 0.0},
                    "speed": 0.0,
                    "last_updated": datetime.utcnow().isoformat()
                }
                
                return {"status": "created", "vehicle": vehicle.to_dict()}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def execute_vehicle_command(self, vehicle_id: str, command_type: str, 
                              parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a command on the vehicle"""
        try:
            if parameters is None:
                parameters = {}
            
            # Update vehicle last seen
            self._update_vehicle_status(vehicle_id)
            
            # Process different command types
            if command_type == "navigation":
                return self._handle_navigation_command(vehicle_id, parameters)
            elif command_type == "media_control":
                return self._handle_media_command(vehicle_id, parameters)
            elif command_type == "climate_control":
                return self._handle_climate_command(vehicle_id, parameters)
            elif command_type == "door_control":
                return self._handle_door_command(vehicle_id, parameters)
            elif command_type == "engine_control":
                return self._handle_engine_command(vehicle_id, parameters)
            elif command_type == "emergency":
                return self._handle_emergency_command(vehicle_id, parameters)
            else:
                return {"status": "error", "message": f"Unknown command type: {command_type}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_vehicle_status(self, vehicle_id: str) -> Dict[str, Any]:
        """Get current vehicle status and diagnostics"""
        try:
            vehicle = DeviceRegistry.query.filter_by(device_id=vehicle_id).first()
            if not vehicle:
                return {"status": "error", "message": "Vehicle not found"}
            
            # Get cached status or create default
            status = self.vehicle_status_cache.get(vehicle_id, {
                "fuel_level": 75.0,
                "engine_on": False,
                "doors_locked": True,
                "location": {"latitude": 37.7749, "longitude": -122.4194},
                "speed": 0.0,
                "tire_pressure": {
                    "front_left": 32.0,
                    "front_right": 32.0,
                    "rear_left": 31.5,
                    "rear_right": 31.5
                },
                "engine_temperature": 195.0,
                "battery_voltage": 12.6,
                "odometer": 45000,
                "last_updated": datetime.utcnow().isoformat()
            })
            
            return {
                "status": "success",
                "vehicle_id": vehicle_id,
                "vehicle_name": vehicle.device_name,
                "vehicle_status": status,
                "capabilities": vehicle.get_capabilities()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def process_vehicle_telemetry(self, vehicle_id: str, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming telemetry data from vehicle"""
        try:
            # Update vehicle last seen
            self._update_vehicle_status(vehicle_id)
            
            # Update status cache with new telemetry
            if vehicle_id not in self.vehicle_status_cache:
                self.vehicle_status_cache[vehicle_id] = {}
            
            self.vehicle_status_cache[vehicle_id].update(telemetry_data)
            self.vehicle_status_cache[vehicle_id]["last_updated"] = datetime.utcnow().isoformat()
            
            # Analyze telemetry for alerts
            alerts = self._analyze_telemetry(vehicle_id, telemetry_data)
            
            return {
                "status": "success",
                "message": "Telemetry processed",
                "alerts": alerts
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_navigation_route(self, vehicle_id: str, destination: str, 
                           current_location: Dict[str, float] = None) -> Dict[str, Any]:
        """Calculate navigation route to destination"""
        try:
            # In production, integrate with mapping services (Google Maps, HERE, etc.)
            # For now, return mock route data
            
            route_data = {
                "destination": destination,
                "estimated_time": "25 minutes",
                "distance": "12.5 miles",
                "route_steps": [
                    "Head north on Main St",
                    "Turn right on Highway 101",
                    "Take exit 15 for Downtown",
                    "Arrive at destination"
                ],
                "traffic_conditions": "moderate",
                "fuel_required": 0.8  # gallons
            }
            
            return {
                "status": "success",
                "route": route_data
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _update_vehicle_status(self, vehicle_id: str):
        """Update vehicle last seen timestamp"""
        vehicle = DeviceRegistry.query.filter_by(device_id=vehicle_id).first()
        if vehicle:
            vehicle.last_seen = datetime.utcnow()
            vehicle.status = 'active'
            db.session.commit()
    
    def _handle_navigation_command(self, vehicle_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle navigation-related commands"""
        destination = parameters.get("destination")
        if not destination:
            return {"status": "error", "message": "Destination required for navigation"}
        
        # Get route information
        route = self.get_navigation_route(vehicle_id, destination)
        
        # In production, send navigation data to vehicle's infotainment system
        return {
            "status": "success",
            "message": f"Navigation started to {destination}",
            "route_info": route.get("route", {})
        }
    
    def _handle_media_command(self, vehicle_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle media control commands"""
        action = parameters.get("action", "play")
        media_type = parameters.get("media_type", "music")
        content = parameters.get("content", "")
        
        actions = {
            "play": f"Playing {media_type}" + (f": {content}" if content else ""),
            "pause": "Media paused",
            "stop": "Media stopped",
            "next": "Skipped to next track",
            "previous": "Skipped to previous track",
            "volume_up": "Volume increased",
            "volume_down": "Volume decreased"
        }
        
        message = actions.get(action, f"Media command '{action}' executed")
        
        return {
            "status": "success",
            "message": message,
            "media_state": {
                "action": action,
                "media_type": media_type,
                "content": content
            }
        }
    
    def _handle_climate_command(self, vehicle_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle climate control commands"""
        action = parameters.get("action", "set_temperature")
        temperature = parameters.get("temperature", 72)
        fan_speed = parameters.get("fan_speed", "auto")
        
        # Update vehicle status cache
        if vehicle_id in self.vehicle_status_cache:
            self.vehicle_status_cache[vehicle_id]["climate"] = {
                "temperature": temperature,
                "fan_speed": fan_speed,
                "ac_on": True
            }
        
        return {
            "status": "success",
            "message": f"Climate set to {temperature}°F with {fan_speed} fan speed",
            "climate_state": {
                "temperature": temperature,
                "fan_speed": fan_speed,
                "ac_on": True
            }
        }
    
    def _handle_door_command(self, vehicle_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle door lock/unlock commands"""
        action = parameters.get("action", "lock")
        doors = parameters.get("doors", "all")
        
        # Update vehicle status cache
        if vehicle_id in self.vehicle_status_cache:
            self.vehicle_status_cache[vehicle_id]["doors_locked"] = (action == "lock")
        
        return {
            "status": "success",
            "message": f"Doors {action}ed",
            "door_state": {
                "action": action,
                "doors": doors,
                "locked": (action == "lock")
            }
        }
    
    def _handle_engine_command(self, vehicle_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle engine start/stop commands"""
        action = parameters.get("action", "start")
        
        # Update vehicle status cache
        if vehicle_id in self.vehicle_status_cache:
            self.vehicle_status_cache[vehicle_id]["engine_on"] = (action == "start")
        
        return {
            "status": "success",
            "message": f"Engine {action}ed remotely",
            "engine_state": {
                "action": action,
                "engine_on": (action == "start")
            }
        }
    
    def _handle_emergency_command(self, vehicle_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency commands"""
        emergency_type = parameters.get("type", "general")
        location = parameters.get("location", {})
        
        # In production, contact emergency services
        return {
            "status": "success",
            "message": "Emergency services contacted",
            "emergency_info": {
                "type": emergency_type,
                "vehicle_id": vehicle_id,
                "location": location,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def _analyze_telemetry(self, vehicle_id: str, telemetry_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze telemetry data for potential alerts"""
        alerts = []
        
        # Check fuel level
        fuel_level = telemetry_data.get("fuel_level", 100)
        if fuel_level < 15:
            alerts.append({
                "type": "low_fuel",
                "severity": "warning",
                "message": f"Fuel level is low: {fuel_level}%"
            })
        
        # Check tire pressure
        tire_pressure = telemetry_data.get("tire_pressure", {})
        for tire, pressure in tire_pressure.items():
            if pressure < 28:  # PSI
                alerts.append({
                    "type": "low_tire_pressure",
                    "severity": "warning",
                    "message": f"Low tire pressure in {tire}: {pressure} PSI"
                })
        
        # Check engine temperature
        engine_temp = telemetry_data.get("engine_temperature", 195)
        if engine_temp > 220:  # Fahrenheit
            alerts.append({
                "type": "high_engine_temperature",
                "severity": "critical",
                "message": f"Engine temperature is high: {engine_temp}°F"
            })
        
        # Check battery voltage
        battery_voltage = telemetry_data.get("battery_voltage", 12.6)
        if battery_voltage < 12.0:
            alerts.append({
                "type": "low_battery",
                "severity": "warning",
                "message": f"Battery voltage is low: {battery_voltage}V"
            })
        
        return alerts

