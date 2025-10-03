"""
Schema Loader Module
Loads and matches skill schemas for dynamic skill routing
"""

import json
import os
import glob
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCHEMAS = {}

def load_schemas():
    """Load all skill schemas from the schemas directory"""
    global SCHEMAS
    SCHEMAS = {}
    
    # Get the base schemas directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schemas_dir = os.path.join(base_dir, "schemas")
    
    if not os.path.exists(schemas_dir):
        logger.warning(f"Schemas directory not found: {schemas_dir}")
        return
    
    # Load all JSON files in the schemas directory and subdirectories
    pattern = os.path.join(schemas_dir, "**", "*.json")
    schema_files = glob.glob(pattern, recursive=True)
    
    for schema_path in schema_files:
        try:
            # Extract skill name from directory structure
            rel_path = os.path.relpath(schema_path, schemas_dir)
            skill_name = os.path.dirname(rel_path)
            
            # If the schema is directly in schemas directory, use filename as skill name
            if skill_name == ".":
                skill_name = os.path.splitext(os.path.basename(schema_path))[0]
            
            # Load the schema
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_data = json.load(f)
                SCHEMAS[skill_name] = schema_data
                logger.info(f"Loaded schema for skill: {skill_name}")
                
        except Exception as e:
            logger.error(f"Failed to load schema from {schema_path}: {e}")
    
    logger.info(f"Loaded {len(SCHEMAS)} skill schemas")

def match_schema(input_data: dict):
    """
    Match input data to a skill schema
    
    Args:
        input_data (dict): The input data to match against schemas
        
    Returns:
        tuple: (skill_name, schema) if match found, (None, None) otherwise
    """
    if not isinstance(input_data, dict):
        return None, None
    
    # Try to match by action field (primary matching method)
    input_action = input_data.get("action")
    if input_action:
        for skill_name, schema in SCHEMAS.items():
            schema_action = schema.get("action")
            if schema_action and input_action.lower() == schema_action.lower():
                logger.info(f"Matched skill '{skill_name}' by action: {input_action}")
                return skill_name, schema
    
    # Try to match by intent field (secondary matching method)
    input_intent = input_data.get("intent")
    if input_intent:
        for skill_name, schema in SCHEMAS.items():
            schema_intent = schema.get("intent")
            if schema_intent and input_intent.lower() == schema_intent.lower():
                logger.info(f"Matched skill '{skill_name}' by intent: {input_intent}")
                return skill_name, schema
    
    # Try to match by keywords (tertiary matching method)
    input_text = input_data.get("message", "").lower()
    if input_text:
        for skill_name, schema in SCHEMAS.items():
            keywords = schema.get("keywords", [])
            if keywords and any(keyword.lower() in input_text for keyword in keywords):
                logger.info(f"Matched skill '{skill_name}' by keywords in: {input_text}")
                return skill_name, schema
    
    logger.debug(f"No schema match found for input: {input_data}")
    return None, None

def get_all_schemas():
    """Get all loaded schemas"""
    return SCHEMAS.copy()

def get_schema(skill_name: str):
    """Get a specific schema by skill name"""
    return SCHEMAS.get(skill_name)

def reload_schemas():
    """Reload all schemas from disk"""
    logger.info("Reloading schemas...")
    load_schemas()

# Load schemas on module import
load_schemas()

