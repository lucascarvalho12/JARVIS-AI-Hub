"""
AI Learning Routes
API endpoints for pattern recognition and adaptive responses
"""

from flask import Blueprint, request, jsonify
from src.ai_learning.pattern_recognition import PatternRecognitionEngine
from src.ai_learning.adaptive_responses import AdaptiveResponseSystem

ai_learning_bp = Blueprint('ai_learning', __name__)

# Initialize AI learning components
pattern_engine = PatternRecognitionEngine()
adaptive_system = AdaptiveResponseSystem()

@ai_learning_bp.route('/ai/patterns', methods=['GET'])
def get_user_patterns():
    """Get user behavior patterns"""
    try:
        user_id = request.args.get('user_id')
        days_back = int(request.args.get('days_back', 30))
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        patterns = pattern_engine.analyze_user_patterns(user_id, days_back)
        return jsonify(patterns)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_learning_bp.route('/ai/predict_intent', methods=['POST'])
def predict_intent():
    """Predict user intent from input"""
    try:
        data = request.get_json()
        user_input = data.get('user_input')
        context = data.get('context', {})
        
        if not user_input:
            return jsonify({'error': 'user_input is required'}), 400
        
        prediction = pattern_engine.predict_user_intent(user_input, context)
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_learning_bp.route('/ai/adaptive_response', methods=['POST'])
def generate_adaptive_response():
    """Generate adaptive response based on user patterns"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user_input = data.get('user_input')
        context = data.get('context', {})
        
        if not user_id or not user_input:
            return jsonify({'error': 'user_id and user_input are required'}), 400
        
        response = adaptive_system.generate_adaptive_response(user_id, user_input, context)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_learning_bp.route('/ai/suggestions', methods=['GET'])
def get_automation_suggestions():
    """Get automation suggestions based on user patterns"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        suggestions = pattern_engine.suggest_automations(user_id)
        return jsonify(suggestions)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_learning_bp.route('/ai/chat', methods=['POST'])
def ai_chat():
    """Enhanced chat endpoint with adaptive responses"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')
        message = data.get('message')
        context = data.get('context', {})
        
        if not message:
            return jsonify({'error': 'message is required'}), 400
        
        # Generate adaptive response
        response = adaptive_system.generate_adaptive_response(user_id, message, context)
        
        return jsonify({
            'status': 'success',
            'user_message': message,
            'ai_response': response.get('response', {}).get('text', 'I\'m here to help!'),
            'intent': response.get('intent'),
            'confidence': response.get('confidence'),
            'suggestions': response.get('response', {}).get('suggestions', []),
            'personalized': response.get('personalization_applied', False)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_learning_bp.route('/ai/health', methods=['GET'])
def ai_health_check():
    """Health check for AI learning system"""
    return jsonify({
        'status': 'healthy',
        'components': {
            'pattern_recognition': 'active',
            'adaptive_responses': 'active'
        },
        'version': '1.0.0'
    })

