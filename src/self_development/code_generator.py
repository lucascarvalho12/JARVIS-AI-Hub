"""
Code Generation Engine (CGE) for JARVIS AI Hub Self-Development Module

This module provides the core functionality for generating and modifying code
autonomously based on high-level objectives and learned patterns.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
from datetime import datetime

logger = logging.getLogger(__name__)

class CodeGenerationEngine:
    """
    The Code Generation Engine is responsible for synthesizing new code and
    modifying existing code based on instructions and contextual knowledge.
    """
    
    def __init__(self, knowledge_repository=None):
        """
        Initialize the Code Generation Engine.
        
        Args:
            knowledge_repository: Reference to the Knowledge & Learning Repository
        """
        self.client = OpenAI()  # Uses environment variables for API key
        self.knowledge_repository = knowledge_repository
        self.generation_history = []
        
        # Code generation templates
        self.templates = {
            'skill': self._load_skill_template(),
            'api_endpoint': self._load_api_template(),
            'utility_function': self._load_utility_template(),
            'test_case': self._load_test_template()
        }
        
        logger.info("Code Generation Engine initialized")
    
    def generate_code(self, objective: str, code_type: str = "auto", 
                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate code based on a high-level objective.
        
        Args:
            objective: Natural language description of what the code should do
            code_type: Type of code to generate (skill, api_endpoint, utility_function, test_case, auto)
            context: Additional context including existing code, dependencies, etc.
            
        Returns:
            Dictionary containing generated code, metadata, and analysis
        """
        try:
            logger.info(f"Generating code for objective: {objective}")
            
            # Determine code type if auto
            if code_type == "auto":
                code_type = self._determine_code_type(objective)
            
            # Prepare context for generation
            generation_context = self._prepare_context(objective, code_type, context)
            
            # Generate code using LLM
            generated_code = self._generate_with_llm(generation_context)
            
            # Post-process and validate
            result = self._post_process_code(generated_code, code_type, objective)
            
            # Store in generation history
            self._record_generation(objective, code_type, result)
            
            logger.info(f"Successfully generated {code_type} code")
            return result
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'code': None,
                'metadata': {}
            }
    
    def modify_code(self, existing_code: str, modification_objective: str,
                   file_path: str = None) -> Dict[str, Any]:
        """
        Modify existing code based on a specific objective.
        
        Args:
            existing_code: The current code to be modified
            modification_objective: What changes should be made
            file_path: Path to the file being modified (for context)
            
        Returns:
            Dictionary containing modified code and change analysis
        """
        try:
            logger.info(f"Modifying code: {modification_objective}")
            
            # Analyze existing code
            code_analysis = self._analyze_existing_code(existing_code, file_path)
            
            # Prepare modification context
            modification_context = {
                'existing_code': existing_code,
                'objective': modification_objective,
                'analysis': code_analysis,
                'file_path': file_path
            }
            
            # Generate modifications using LLM
            modified_code = self._modify_with_llm(modification_context)
            
            # Analyze changes
            change_analysis = self._analyze_changes(existing_code, modified_code)
            
            result = {
                'success': True,
                'original_code': existing_code,
                'modified_code': modified_code,
                'changes': change_analysis,
                'objective': modification_objective,
                'timestamp': datetime.now().isoformat()
            }
            
            # Record modification
            self._record_modification(modification_objective, result)
            
            logger.info("Code modification completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Code modification failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'original_code': existing_code,
                'modified_code': None
            }
    
    def generate_skill(self, skill_name: str, description: str, 
                      parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a new JARVIS skill with schema and implementation.
        
        Args:
            skill_name: Name of the skill to generate
            description: Description of what the skill should do
            parameters: Expected parameters for the skill
            
        Returns:
            Dictionary containing skill code, schema, and metadata
        """
        try:
            logger.info(f"Generating skill: {skill_name}")
            
            # Generate skill schema
            schema = self._generate_skill_schema(skill_name, description, parameters)
            
            # Generate skill implementation
            implementation = self._generate_skill_implementation(skill_name, description, schema)
            
            # Generate test cases
            tests = self._generate_skill_tests(skill_name, schema, implementation)
            
            result = {
                'success': True,
                'skill_name': skill_name,
                'schema': schema,
                'implementation': implementation,
                'tests': tests,
                'description': description,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully generated skill: {skill_name}")
            return result
            
        except Exception as e:
            logger.error(f"Skill generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'skill_name': skill_name
            }
    
    def _determine_code_type(self, objective: str) -> str:
        """Determine the type of code to generate based on the objective."""
        objective_lower = objective.lower()
        
        if any(keyword in objective_lower for keyword in ['skill', 'capability', 'function']):
            return 'skill'
        elif any(keyword in objective_lower for keyword in ['api', 'endpoint', 'route']):
            return 'api_endpoint'
        elif any(keyword in objective_lower for keyword in ['test', 'testing', 'verify']):
            return 'test_case'
        else:
            return 'utility_function'
    
    def _prepare_context(self, objective: str, code_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for code generation."""
        generation_context = {
            'objective': objective,
            'code_type': code_type,
            'template': self.templates.get(code_type, ''),
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            generation_context.update(context)
        
        # Add relevant knowledge from repository
        if self.knowledge_repository:
            relevant_patterns = self.knowledge_repository.get_relevant_patterns(objective)
            generation_context['patterns'] = relevant_patterns
        
        return generation_context
    
    def _generate_with_llm(self, context: Dict[str, Any]) -> str:
        """Generate code using the LLM."""
        prompt = self._build_generation_prompt(context)
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert software engineer specializing in Python and JavaScript development. Generate clean, well-documented, and efficient code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def _modify_with_llm(self, context: Dict[str, Any]) -> str:
        """Modify code using the LLM."""
        prompt = self._build_modification_prompt(context)
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert software engineer. Modify the provided code according to the specified objective while maintaining code quality and compatibility."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def _build_generation_prompt(self, context: Dict[str, Any]) -> str:
        """Build the prompt for code generation."""
        prompt = f"""
Generate {context['code_type']} code for the following objective:

Objective: {context['objective']}

Requirements:
- Write clean, well-documented Python code
- Follow PEP 8 style guidelines
- Include appropriate error handling
- Add docstrings and comments
- Ensure code is modular and reusable

Template (if applicable):
{context.get('template', 'No specific template')}

Additional Context:
{json.dumps(context.get('patterns', {}), indent=2)}

Please provide only the code without additional explanations.
"""
        return prompt
    
    def _build_modification_prompt(self, context: Dict[str, Any]) -> str:
        """Build the prompt for code modification."""
        prompt = f"""
Modify the following code according to the specified objective:

Objective: {context['objective']}

Current Code:
```python
{context['existing_code']}
```

Requirements:
- Maintain existing functionality unless explicitly changing it
- Follow the same coding style and patterns
- Add appropriate comments for changes
- Ensure backward compatibility where possible
- Handle edge cases and errors appropriately

File Path: {context.get('file_path', 'Unknown')}

Please provide only the modified code without additional explanations.
"""
        return prompt
    
    def _post_process_code(self, generated_code: str, code_type: str, objective: str) -> Dict[str, Any]:
        """Post-process and validate generated code."""
        # Extract code from markdown if present
        if '```python' in generated_code:
            code_start = generated_code.find('```python') + 9
            code_end = generated_code.find('```', code_start)
            if code_end != -1:
                generated_code = generated_code[code_start:code_end].strip()
        elif '```' in generated_code:
            code_start = generated_code.find('```') + 3
            code_end = generated_code.find('```', code_start)
            if code_end != -1:
                generated_code = generated_code[code_start:code_end].strip()
        
        # Basic validation
        validation_result = self._validate_code(generated_code)
        
        return {
            'success': True,
            'code': generated_code,
            'code_type': code_type,
            'objective': objective,
            'validation': validation_result,
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'lines_of_code': len(generated_code.split('\n')),
                'estimated_complexity': self._estimate_complexity(generated_code)
            }
        }
    
    def _validate_code(self, code: str) -> Dict[str, Any]:
        """Basic validation of generated code."""
        validation = {
            'syntax_valid': False,
            'has_docstring': False,
            'has_error_handling': False,
            'issues': []
        }
        
        try:
            # Check syntax
            compile(code, '<string>', 'exec')
            validation['syntax_valid'] = True
        except SyntaxError as e:
            validation['issues'].append(f"Syntax error: {str(e)}")
        
        # Check for docstring
        if '"""' in code or "'''" in code:
            validation['has_docstring'] = True
        
        # Check for error handling
        if 'try:' in code or 'except' in code:
            validation['has_error_handling'] = True
        
        return validation
    
    def _estimate_complexity(self, code: str) -> str:
        """Estimate code complexity based on simple heuristics."""
        lines = len(code.split('\n'))
        if lines < 10:
            return 'low'
        elif lines < 50:
            return 'medium'
        else:
            return 'high'
    
    def _analyze_existing_code(self, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze existing code to understand its structure and purpose."""
        analysis = {
            'lines_of_code': len(code.split('\n')),
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': self._estimate_complexity(code)
        }
        
        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('def '):
                func_name = line.split('(')[0].replace('def ', '')
                analysis['functions'].append(func_name)
            elif line.startswith('class '):
                class_name = line.split('(')[0].replace('class ', '').replace(':', '')
                analysis['classes'].append(class_name)
            elif line.startswith('import ') or line.startswith('from '):
                analysis['imports'].append(line)
        
        return analysis
    
    def _analyze_changes(self, original: str, modified: str) -> Dict[str, Any]:
        """Analyze the changes between original and modified code."""
        original_lines = original.split('\n')
        modified_lines = modified.split('\n')
        
        return {
            'lines_added': len(modified_lines) - len(original_lines),
            'original_length': len(original_lines),
            'modified_length': len(modified_lines),
            'change_ratio': abs(len(modified_lines) - len(original_lines)) / max(len(original_lines), 1)
        }
    
    def _generate_skill_schema(self, skill_name: str, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON schema for a new skill."""
        schema = {
            "name": skill_name,
            "version": "1.0",
            "description": description,
            "action": skill_name.lower().replace(' ', '_'),
            "keywords": [skill_name.lower()],
            "parameters": parameters or {}
        }
        return schema
    
    def _generate_skill_implementation(self, skill_name: str, description: str, schema: Dict[str, Any]) -> str:
        """Generate Python implementation for a skill."""
        prompt = f"""
Generate a Python skill implementation for JARVIS AI Hub:

Skill Name: {skill_name}
Description: {description}
Schema: {json.dumps(schema, indent=2)}

The skill should:
1. Have an execute(input_data: dict) -> dict function
2. Include proper error handling
3. Return a dictionary with 'response' and 'success' keys
4. Include logging
5. Follow the existing JARVIS skill pattern

Please provide only the Python code.
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Python developer creating JARVIS AI Hub skills."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def _generate_skill_tests(self, skill_name: str, schema: Dict[str, Any], implementation: str) -> str:
        """Generate test cases for a skill."""
        prompt = f"""
Generate Python test cases for this JARVIS skill:

Skill Name: {skill_name}
Schema: {json.dumps(schema, indent=2)}

Implementation:
```python
{implementation}
```

Generate comprehensive test cases using pytest that cover:
1. Normal operation
2. Edge cases
3. Error conditions
4. Input validation

Please provide only the test code.
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in Python testing with pytest."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def _record_generation(self, objective: str, code_type: str, result: Dict[str, Any]):
        """Record code generation in history."""
        record = {
            'timestamp': datetime.now().isoformat(),
            'objective': objective,
            'code_type': code_type,
            'success': result.get('success', False),
            'metadata': result.get('metadata', {})
        }
        self.generation_history.append(record)
        
        # Keep only last 100 records
        if len(self.generation_history) > 100:
            self.generation_history = self.generation_history[-100:]
    
    def _record_modification(self, objective: str, result: Dict[str, Any]):
        """Record code modification in history."""
        record = {
            'timestamp': datetime.now().isoformat(),
            'type': 'modification',
            'objective': objective,
            'success': result.get('success', False),
            'changes': result.get('changes', {})
        }
        self.generation_history.append(record)
    
    def _load_skill_template(self) -> str:
        """Load the skill template."""
        return '''
def execute(input_data: dict) -> dict:
    """
    Execute the {skill_name} skill.
    
    Args:
        input_data: Input data containing user request
        
    Returns:
        dict: Response from skill execution
    """
    try:
        # Skill implementation here
        return {
            "response": "Skill executed successfully!",
            "success": True
        }
    except Exception as e:
        return {
            "response": f"Error executing skill: {str(e)}",
            "success": False
        }
'''
    
    def _load_api_template(self) -> str:
        """Load the API endpoint template."""
        return '''
@app.route('/api/{endpoint}', methods=['POST'])
def {endpoint}():
    """API endpoint for {description}."""
    try:
        data = request.get_json()
        # Implementation here
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
'''
    
    def _load_utility_template(self) -> str:
        """Load the utility function template."""
        return '''
def {function_name}({parameters}):
    """
    {description}
    
    Args:
        {parameters}: Parameter descriptions
        
    Returns:
        Result of the operation
    """
    try:
        # Implementation here
        return result
    except Exception as e:
        raise Exception(f"Error in {function_name}: {str(e)}")
'''
    
    def _load_test_template(self) -> str:
        """Load the test case template."""
        return '''
import pytest

def test_{function_name}():
    """Test {function_name} functionality."""
    # Test implementation here
    assert True  # Replace with actual assertions

def test_{function_name}_error_handling():
    """Test error handling in {function_name}."""
    # Error test implementation here
    with pytest.raises(Exception):
        pass  # Replace with actual error test
'''
    
    def get_generation_history(self) -> List[Dict[str, Any]]:
        """Get the code generation history."""
        return self.generation_history.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about code generation activities."""
        total_generations = len(self.generation_history)
        successful_generations = sum(1 for record in self.generation_history if record.get('success', False))
        
        code_types = {}
        for record in self.generation_history:
            code_type = record.get('code_type', 'unknown')
            code_types[code_type] = code_types.get(code_type, 0) + 1
        
        return {
            'total_generations': total_generations,
            'successful_generations': successful_generations,
            'success_rate': successful_generations / max(total_generations, 1),
            'code_types': code_types,
            'last_generation': self.generation_history[-1]['timestamp'] if self.generation_history else None
        }

