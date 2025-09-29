from src.models.user import db
from datetime import datetime
import json

class UserProfile(db.Model):
    """User profile and preferences model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    preferences = db.Column(db.Text)  # JSON string for flexible preferences
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserProfile {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'preferences': json.loads(self.preferences) if self.preferences else {},
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def set_preferences(self, preferences_dict):
        """Set user preferences as JSON"""
        self.preferences = json.dumps(preferences_dict)

    def get_preferences(self):
        """Get user preferences as dictionary"""
        return json.loads(self.preferences) if self.preferences else {}

class ConversationHistory(db.Model):
    """Store conversation history for context awareness"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    session_id = db.Column(db.String(120), nullable=False)
    user_input = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    context_data = db.Column(db.Text)  # JSON string for contextual information
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ConversationHistory {self.user_id}:{self.session_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'user_input': self.user_input,
            'ai_response': self.ai_response,
            'context_data': json.loads(self.context_data) if self.context_data else {},
            'timestamp': self.timestamp.isoformat()
        }

    def set_context_data(self, context_dict):
        """Set context data as JSON"""
        self.context_data = json.dumps(context_dict)

    def get_context_data(self):
        """Get context data as dictionary"""
        return json.loads(self.context_data) if self.context_data else {}

class DeviceRegistry(db.Model):
    """Registry of connected devices"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    device_id = db.Column(db.String(120), unique=True, nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)  # 'smartphone', 'car', 'home_device'
    device_category = db.Column(db.String(50))  # 'light', 'thermostat', 'lock', etc.
    capabilities = db.Column(db.Text)  # JSON string for device capabilities
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive', 'offline'
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DeviceRegistry {self.device_name}:{self.device_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'device_category': self.device_category,
            'capabilities': json.loads(self.capabilities) if self.capabilities else [],
            'status': self.status,
            'last_seen': self.last_seen.isoformat(),
            'created_at': self.created_at.isoformat()
        }

    def set_capabilities(self, capabilities_list):
        """Set device capabilities as JSON"""
        self.capabilities = json.dumps(capabilities_list)

    def get_capabilities(self):
        """Get device capabilities as list"""
        return json.loads(self.capabilities) if self.capabilities else []

class TaskExecution(db.Model):
    """Track task execution and orchestration"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    task_id = db.Column(db.String(120), unique=True, nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)  # 'command', 'automation', 'proactive'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'running', 'completed', 'failed'
    input_data = db.Column(db.Text)  # JSON string for task input
    output_data = db.Column(db.Text)  # JSON string for task output
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<TaskExecution {self.task_name}:{self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'task_name': self.task_name,
            'task_type': self.task_type,
            'status': self.status,
            'input_data': json.loads(self.input_data) if self.input_data else {},
            'output_data': json.loads(self.output_data) if self.output_data else {},
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def set_input_data(self, input_dict):
        """Set task input data as JSON"""
        self.input_data = json.dumps(input_dict)

    def get_input_data(self):
        """Get task input data as dictionary"""
        return json.loads(self.input_data) if self.input_data else {}

    def set_output_data(self, output_dict):
        """Set task output data as JSON"""
        self.output_data = json.dumps(output_dict)

    def get_output_data(self):
        """Get task output data as dictionary"""
        return json.loads(self.output_data) if self.output_data else {}

