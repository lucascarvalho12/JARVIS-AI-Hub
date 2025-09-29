from flask import Blueprint, jsonify, request
from src.models.ai_core import UserProfile, ConversationHistory, DeviceRegistry, TaskExecution, db
from datetime import datetime
import uuid
import json

ai_core_bp = Blueprint('ai_core', __name__)

# AI Core Engine - Natural Language Processing
@ai_core_bp.route('/ai/process_command', methods=['POST'])
def process_command():
    """Process natural language command from user"""
    try:
        data = request.json
        user_id = data.get('user_id')
        command_text = data.get('command_text')
        context = data.get('context', {})
        
        if not user_id or not command_text:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Simple NLU processing (in a real implementation, this would use advanced NLP)
        intent, entities = simple_nlu_processor(command_text)
        
        # Generate session ID for conversation tracking
        session_id = str(uuid.uuid4())
        
        # Process the intent and generate response
        ai_response = generate_ai_response(intent, entities, context, user_id)
        
        # Store conversation history
        conversation = ConversationHistory(
            user_id=user_id,
            session_id=session_id,
            user_input=command_text,
            ai_response=ai_response['response_text']
        )
        conversation.set_context_data(context)
        
        db.session.add(conversation)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'intent': intent,
            'entities': entities,
            'response_text': ai_response['response_text'],
            'action_required': ai_response.get('action_required', False),
            'action_details': ai_response.get('action_details', {})
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def simple_nlu_processor(text):
    """Simple NLU processor - in production, use advanced NLP models"""
    text_lower = text.lower()
    
    # Intent recognition
    if any(word in text_lower for word in ['turn on', 'switch on', 'activate']):
        intent = 'turn_on_device'
    elif any(word in text_lower for word in ['turn off', 'switch off', 'deactivate']):
        intent = 'turn_off_device'
    elif any(word in text_lower for word in ['set temperature', 'adjust temperature']):
        intent = 'set_temperature'
    elif any(word in text_lower for word in ['play music', 'play song']):
        intent = 'play_music'
    elif any(word in text_lower for word in ['navigate to', 'drive to', 'go to']):
        intent = 'navigate'
    elif any(word in text_lower for word in ['what is', 'tell me', 'how is']):
        intent = 'information_request'
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
    
    return intent, entities

def generate_ai_response(intent, entities, context, user_id):
    """Generate AI response based on intent and context"""
    responses = {
        'turn_on_device': "I'll turn on the {} for you.".format(entities.get('device_type', 'device')),
        'turn_off_device': "I'll turn off the {} for you.".format(entities.get('device_type', 'device')),
        'set_temperature': "I'll adjust the temperature as requested.",
        'play_music': "I'll start playing music for you.",
        'navigate': "I'll set up navigation for you.",
        'information_request': "Let me get that information for you.",
        'general_conversation': "I'm here to help! What would you like me to do?"
    }
    
    response_text = responses.get(intent, "I understand you want help, but I'm not sure how to assist with that specific request.")
    
    # Determine if action is required
    action_required = intent in ['turn_on_device', 'turn_off_device', 'set_temperature', 'play_music', 'navigate']
    
    action_details = {}
    if action_required:
        action_details = {
            'intent': intent,
            'entities': entities,
            'target_devices': get_relevant_devices(user_id, entities)
        }
    
    return {
        'response_text': response_text,
        'action_required': action_required,
        'action_details': action_details
    }

def get_relevant_devices(user_id, entities):
    """Get relevant devices based on entities"""
    device_type = entities.get('device_type')
    if device_type:
        devices = DeviceRegistry.query.filter_by(
            user_id=user_id,
            device_category=device_type,
            status='active'
        ).all()
        return [device.to_dict() for device in devices]
    return []

# User Profile Management
@ai_core_bp.route('/ai/profile', methods=['GET'])
def get_user_profile():
    """Get user profile and preferences"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400
    
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': 'User profile not found'}), 404
    
    return jsonify(profile.to_dict())

@ai_core_bp.route('/ai/profile', methods=['POST'])
def create_user_profile():
    """Create or update user profile"""
    try:
        data = request.json
        user_id = data.get('user_id')
        name = data.get('name')
        preferences = data.get('preferences', {})
        
        if not user_id or not name:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if profile exists
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        
        if profile:
            # Update existing profile
            profile.name = name
            profile.set_preferences(preferences)
            profile.updated_at = datetime.utcnow()
        else:
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                name=name
            )
            profile.set_preferences(preferences)
            db.session.add(profile)
        
        db.session.commit()
        return jsonify(profile.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Device Registry Management
@ai_core_bp.route('/ai/devices', methods=['GET'])
def get_user_devices():
    """Get all devices for a user"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400
    
    devices = DeviceRegistry.query.filter_by(user_id=user_id).all()
    return jsonify([device.to_dict() for device in devices])

@ai_core_bp.route('/ai/devices', methods=['POST'])
def register_device():
    """Register a new device"""
    try:
        data = request.json
        user_id = data.get('user_id')
        device_id = data.get('device_id')
        device_name = data.get('device_name')
        device_type = data.get('device_type')
        device_category = data.get('device_category')
        capabilities = data.get('capabilities', [])
        
        if not all([user_id, device_id, device_name, device_type]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if device already exists
        existing_device = DeviceRegistry.query.filter_by(device_id=device_id).first()
        if existing_device:
            return jsonify({'error': 'Device already registered'}), 409
        
        device = DeviceRegistry(
            user_id=user_id,
            device_id=device_id,
            device_name=device_name,
            device_type=device_type,
            device_category=device_category
        )
        device.set_capabilities(capabilities)
        
        db.session.add(device)
        db.session.commit()
        
        return jsonify(device.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_core_bp.route('/ai/devices/<device_id>', methods=['PUT'])
def update_device_status():
    """Update device status and last seen timestamp"""
    try:
        device = DeviceRegistry.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        data = request.json
        if 'status' in data:
            device.status = data['status']
        
        device.last_seen = datetime.utcnow()
        db.session.commit()
        
        return jsonify(device.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Task Execution Management
@ai_core_bp.route('/ai/tasks', methods=['GET'])
def get_user_tasks():
    """Get task execution history for a user"""
    user_id = request.args.get('user_id')
    status = request.args.get('status')  # Optional filter by status
    
    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400
    
    query = TaskExecution.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    
    tasks = query.order_by(TaskExecution.started_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])

@ai_core_bp.route('/ai/tasks', methods=['POST'])
def create_task():
    """Create a new task execution record"""
    try:
        data = request.json
        user_id = data.get('user_id')
        task_name = data.get('task_name')
        task_type = data.get('task_type', 'command')
        input_data = data.get('input_data', {})
        
        if not all([user_id, task_name]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        task = TaskExecution(
            user_id=user_id,
            task_id=str(uuid.uuid4()),
            task_name=task_name,
            task_type=task_type,
            status='pending'
        )
        task.set_input_data(input_data)
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify(task.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_core_bp.route('/ai/tasks/<task_id>', methods=['PUT'])
def update_task_status():
    """Update task execution status"""
    try:
        task = TaskExecution.query.filter_by(task_id=task_id).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.json
        if 'status' in data:
            task.status = data['status']
            if data['status'] in ['completed', 'failed']:
                task.completed_at = datetime.utcnow()
        
        if 'output_data' in data:
            task.set_output_data(data['output_data'])
        
        if 'error_message' in data:
            task.error_message = data['error_message']
        
        db.session.commit()
        return jsonify(task.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Conversation History
@ai_core_bp.route('/ai/conversations', methods=['GET'])
def get_conversation_history():
    """Get conversation history for a user"""
    user_id = request.args.get('user_id')
    session_id = request.args.get('session_id')  # Optional filter by session
    limit = request.args.get('limit', 50, type=int)
    
    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400
    
    query = ConversationHistory.query.filter_by(user_id=user_id)
    if session_id:
        query = query.filter_by(session_id=session_id)
    
    conversations = query.order_by(ConversationHistory.timestamp.desc()).limit(limit).all()
    return jsonify([conv.to_dict() for conv in conversations])

