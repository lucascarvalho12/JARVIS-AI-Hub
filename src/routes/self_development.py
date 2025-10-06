from flask import Blueprint, request, jsonify
from src.self_development.self_development_orchestrator import SelfDevelopmentOrchestrator
import logging

logger = logging.getLogger(__name__)

self_development_bp = Blueprint("self_development_bp", __name__)
sdo = SelfDevelopmentOrchestrator()

@self_development_bp.route("/self-develop", methods=["POST"])
def initiate_self_development():
    """
    API endpoint to initiate a self-development task for JARVIS.
    Expects a JSON payload with a 'goal' and optional 'priority'.
    """
    try:
        data = request.get_json()
        goal = data.get("goal")
        priority = data.get("priority", "medium")

        if not goal:
            return jsonify({"success": False, "message": "'goal' is required"}), 400

        logger.info(f"Received request to initiate self-development: {goal}")
        result = sdo.initiate_self_development(goal, priority)

        return jsonify({"success": True, "data": result}), 200

    except Exception as e:
        logger.error(f"Error initiating self-development: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@self_development_bp.route("/self-develop/history", methods=["GET"])
def get_self_development_history():
    """
    API endpoint to retrieve the history of self-development activities.
    """
    try:
        history = sdo.knowledge_repository.get_self_development_history()
        return jsonify({"success": True, "data": history}), 200
    except Exception as e:
        logger.error(f"Error retrieving self-development history: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@self_development_bp.route("/self-develop/stats", methods=["GET"])
def get_self_development_stats():
    """
    API endpoint to retrieve statistics about self-development activities.
    """
    try:
        stats = sdo.code_generator.get_statistics()
        return jsonify({"success": True, "data": stats}), 200
    except Exception as e:
        logger.error(f"Error retrieving self-development statistics: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


