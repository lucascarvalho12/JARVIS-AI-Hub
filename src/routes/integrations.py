from flask import Blueprint, jsonify, request
from src.models.ai_core import DeviceRegistry, TaskExecution, db
from datetime import datetime
import uuid
import json

integrations_bp = Blueprint('integrations', __name__)

# Smartphone Integration Endpoints
@integrations_bp.route('/smartphone/command', methods=['POST'])
def smartphone_command():
    """Process command from smartphone"""
    try:
        data = request.json
        user_id = data.get('user_id')
        command_text = data.get('command_text')
        command_audio_url = data.get('command_audio_url')
        context = data.get('context', {})
        
        if not user_id or not command_text:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Update smartphone device status
        smartphone_device = DeviceRegistry.query.filter_by(
            user_id=user_id,
            device_type='smartphone'
        ).first()
        
        if smartphone_device:
            smartphone_device.last_seen = datetime.utcnow()
            smartphone_device.status = 'active'
            db.session.commit()
        
        # Process command through AI Core (simplified)
        response_text = f"Processing command: {command_text}"
        action_required = False
        action_details = {}
        
        # Simple command processing
        if 'home' in command_text.lower():
            action_required = True
            action_details = {
                'type': 'home_control',
                'command': command_text,
                'context': context
            }
        elif 'car' in command_text.lower():
            action_required = True
            action_details = {
                'type': 'car_control',
                'command': command_text,
                'context': context
            }
        
        return jsonify({
            'status': 'success',
            'response_text': response_text,
            'action_required': action_required,
            'action_details': action_details
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/smartphone/sensor_data', methods=['POST'])
def smartphone_sensor_data():
    """Receive sensor data from smartphone"""
    try:
        data = request.json
        user_id = data.get('user_id')
        timestamp = data.get('timestamp')
        sensor_type = data.get('sensor_type')
        sensor_data = data.get('data', {})
        
        if not all([user_id, sensor_type]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Store sensor data (in production, use time-series database)
        # For now, just acknowledge receipt
        
        # Update device last seen
        smartphone_device = DeviceRegistry.query.filter_by(
            user_id=user_id,
            device_type='smartphone'
        ).first()
        
        if smartphone_device:
            smartphone_device.last_seen = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Received {sensor_type} data'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/smartphone/notifications', methods=['GET'])
def smartphone_notifications():
    """Get pending notifications for smartphone"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400
    
    # In production, this would fetch from a notification queue
    # For now, return sample notifications
    notifications = [
        {
            'notification_id': str(uuid.uuid4()),
            'title': 'AI Hub Update',
            'body': 'Your smart home system is ready',
            'timestamp': datetime.utcnow().isoformat(),
            'action_url': None
        }
    ]
    
    return jsonify({
        'status': 'success',
        'notifications': notifications
    })

# Car Integration Endpoints
@integrations_bp.route('/car/command', methods=['POST'])
def car_command():
    """Send command to car system"""
    try:
        data = request.json
        vehicle_id = data.get('vehicle_id')
        command_type = data.get('command_type')
        command_payload = data.get('command_payload', {})
        
        if not all([vehicle_id, command_type]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Update car device status
        car_device = DeviceRegistry.query.filter_by(
            device_id=vehicle_id,
            device_type='car'
        ).first()
        
        if car_device:
            car_device.last_seen = datetime.utcnow()
            car_device.status = 'active'
            db.session.commit()
        
        # Process car command
        command_responses = {
            'navigate': 'Navigation started',
            'play_media': 'Media playback started',
            'lock_doors': 'Doors locked',
            'unlock_doors': 'Doors unlocked',
            'start_engine': 'Engine started remotely',
            'set_climate': 'Climate control adjusted'
        }
        
        response_message = command_responses.get(command_type, 'Command processed')
        
        return jsonify({
            'status': 'success',
            'message': response_message
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/car/status', methods=['GET'])
def car_status():
    """Get current car status"""
    vehicle_id = request.args.get('vehicle_id')
    
    if not vehicle_id:
        return jsonify({'error': 'Missing vehicle_id parameter'}), 400
    
    # In production, this would fetch real vehicle data
    # For now, return sample status
    vehicle_status = {
        'fuel_level': 75.5,
        'door_locked': True,
        'engine_on': False,
        'location': {
            'latitude': 37.7749,
            'longitude': -122.4194
        },
        'tire_pressure': {
            'front_left': 32.1,
            'front_right': 32.3,
            'rear_left': 31.8,
            'rear_right': 32.0
        }
    }
    
    return jsonify({
        'status': 'success',
        'vehicle_status': vehicle_status
    })

# Smart Home Integration Endpoints
@integrations_bp.route('/home/devices', methods=['GET'])
def home_devices():
    """Get list of smart home devices"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400
    
    # Get home devices from registry
    home_devices = DeviceRegistry.query.filter_by(
        user_id=user_id,
        device_type='home_device'
    ).all()
    
    devices_list = []
    for device in home_devices:
        device_dict = device.to_dict()
        devices_list.append({
            'device_id': device_dict['device_id'],
            'name': device_dict['device_name'],
            'type': device_dict['device_category'],
            'room': 'Living Room',  # In production, this would be stored
            'capabilities': device_dict['capabilities']
        })
    
    return jsonify({
        'status': 'success',
        'devices': devices_list
    })

@integrations_bp.route('/home/device/<device_id>/control', methods=['POST'])
def home_device_control():
    """Control a specific smart home device"""
    try:
        data = request.json
        user_id = data.get('user_id')
        command = data.get('command')
        parameters = data.get('parameters', {})
        
        if not all([user_id, command]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find the device
        device = DeviceRegistry.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Update device status
        device.last_seen = datetime.utcnow()
        device.status = 'active'
        db.session.commit()
        
        # Process device command
        command_responses = {
            'turn_on': f'{device.device_name} turned on',
            'turn_off': f'{device.device_name} turned off',
            'set_brightness': f'{device.device_name} brightness set to {parameters.get("value", "unknown")}',
            'set_temperature': f'{device.device_name} temperature set to {parameters.get("value", "unknown")}°',
            'lock': f'{device.device_name} locked',
            'unlock': f'{device.device_name} unlocked'
        }
        
        response_message = command_responses.get(command, 'Command processed')
        
        return jsonify({
            'status': 'success',
            'message': response_message
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@integrations_bp.route('/home/scenes', methods=['GET'])
def home_scenes():
    """Get list of smart home scenes"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400
    
    # In production, scenes would be stored in database
    # For now, return sample scenes
    scenes = [
        {
            'scene_id': 'scene_1',
            'name': 'Good Morning',
            'description': 'Turn on lights, adjust thermostat, start coffee maker'
        },
        {
            'scene_id': 'scene_2',
            'name': 'Movie Time',
            'description': 'Dim lights, turn on TV, close blinds'
        },
        {
            'scene_id': 'scene_3',
            'name': 'Good Night',
            'description': 'Turn off all lights, lock doors, set security system'
        }
    ]
    
    return jsonify({
        'status': 'success',
        'scenes': scenes
    })

@integrations_bp.route('/home/scene/<scene_id>/activate', methods=['POST'])
def activate_home_scene():
    """Activate a smart home scene"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        # In production, this would execute the actual scene
        scene_names = {
            'scene_1': 'Good Morning',
            'scene_2': 'Movie Time',
            'scene_3': 'Good Night'
        }
        
        scene_name = scene_names.get(scene_id, 'Unknown Scene')
        
        return jsonify({
            'status': 'success',
            'message': f'{scene_name} scene activated'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Device Registration Endpoint
@integrations_bp.route('/register_device', methods=['POST'])
def register_integration_device():
    """Register a new device for integration"""
    try:
        data = request.json
        user_id = data.get('user_id')
        device_id = data.get('device_id')
        device_name = data.get('device_name')
        device_type = data.get('device_type')  # 'smartphone', 'car', 'home_device'
        device_category = data.get('device_category')  # 'light', 'thermostat', etc.
        capabilities = data.get('capabilities', [])
        
        if not all([user_id, device_id, device_name, device_type]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if device already exists
        existing_device = DeviceRegistry.query.filter_by(device_id=device_id).first()
        if existing_device:
            # Update existing device
            existing_device.device_name = device_name
            existing_device.device_type = device_type
            existing_device.device_category = device_category
            existing_device.set_capabilities(capabilities)
            existing_device.last_seen = datetime.utcnow()
            existing_device.status = 'active'
        else:
            # Create new device
            device = DeviceRegistry(
                user_id=user_id,
                device_id=device_id,
                device_name=device_name,
                device_type=device_type,
                device_category=device_category,
                status='active'
            )
            device.set_capabilities(capabilities)
            db.session.add(device)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Device registered successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

