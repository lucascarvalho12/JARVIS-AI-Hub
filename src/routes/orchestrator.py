"""
Orchestrator Routes
API endpoints for the enhanced JARVIS AI Hub with skill routing and GPT fallback
"""

import asyncio
from flask import Blueprint, request, jsonify
from prometheus_client import generate_latest
from src.orchestrator import handle_request, get_system_status, reset_circuit_breaker
from src.schema_loader import get_all_schemas, reload_schemas

orchestrator_bp = Blueprint('orchestrator', __name__)

@orchestrator_bp.route('/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with skill routing and GPT fallback"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract message and user_id
        message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Prepare input data for orchestrator
        input_data = {
            'message': message,
            'user_id': user_id,
            'timestamp': data.get('timestamp'),
            'context': data.get('context', {})
        }
        
        # Handle the request through orchestrator
        # Since Flask doesn't natively support async, we'll run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(handle_request(input_data, user_id))
        finally:
            loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'response': 'I apologize, but I encountered an error while processing your request.'
        }), 500

@orchestrator_bp.route('/skills', methods=['GET'])
def get_skills():
    """Get all available skills and their schemas"""
    try:
        schemas = get_all_schemas()
        
        skills_info = []
        for skill_name, schema in schemas.items():
            skills_info.append({
                'name': skill_name,
                'description': schema.get('description', 'No description available'),
                'version': schema.get('version', '1.0'),
                'keywords': schema.get('keywords', []),
                'examples': schema.get('examples', [])
            })
        
        return jsonify({
            'skills': skills_info,
            'total_count': len(skills_info)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orchestrator_bp.route('/skills/reload', methods=['POST'])
def reload_skills():
    """Reload all skill schemas from disk"""
    try:
        reload_schemas()
        schemas = get_all_schemas()
        
        return jsonify({
            'message': 'Skills reloaded successfully',
            'skill_count': len(schemas),
            'skills': list(schemas.keys())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orchestrator_bp.route('/system/status', methods=['GET'])
def system_status():
    """Get system status including circuit breaker information"""
    try:
        status = get_system_status()
        schemas = get_all_schemas()
        
        status.update({
            'skills_loaded': len(schemas),
            'available_skills': list(schemas.keys())
        })
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orchestrator_bp.route('/system/circuit-breaker/reset', methods=['POST'])
def reset_breaker():
    """Reset the circuit breaker manually"""
    try:
        reset_circuit_breaker()
        
        return jsonify({
            'message': 'Circuit breaker reset successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orchestrator_bp.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    try:
        from flask import Response
        metrics_data = generate_latest()
        return Response(metrics_data, mimetype='text/plain')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orchestrator_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        status = get_system_status()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': status['timestamp'],
            'circuit_breaker_state': status['circuit_breaker']['state'],
            'openai_available': status['openai_available']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

