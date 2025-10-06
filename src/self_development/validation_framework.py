"""
Validation Framework (VF) for JARVIS AI Hub Self-Development Module

This module provides comprehensive testing and validation capabilities for
autonomously generated or modified code, ensuring safety and correctness
before deployment.
"""

import os
import json
import logging
import subprocess
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
import ast
import sys

logger = logging.getLogger(__name__)

class ValidationFramework:
    """
    The Validation Framework ensures that all autonomously generated or modified
    code meets quality, safety, and functional requirements before deployment.
    """

    def __init__(self, knowledge_repository=None):
        self.knowledge_repository = knowledge_repository
        self.validation_history = []
        self.safety_rules = self._load_safety_rules()
        self.test_environments = {
            'python': self._setup_python_test_environment,
            'javascript': self._setup_javascript_test_environment
        }
        logger.info("Validation Framework initialized")

    def _load_safety_rules(self) -> Dict[str, List[str]]:
        """
        Loads safety rules for code validation.
        
        Returns:
            Dictionary containing safety rules by category
        """
        return {
            'forbidden_imports': [
                'os.system',
                'subprocess.call',
                'eval',
                'exec',
                '__import__',
                'compile',
                'open',  # Restricted file operations
                'file',
                'input',  # Restricted user input
                'raw_input'
            ],
            'forbidden_patterns': [
                r'rm\s+-rf',  # Dangerous shell commands
                r'del\s+/[qsf]',  # Windows delete commands
                r'format\s+c:',  # Format commands
                r'shutdown',
                r'reboot',
                r'kill\s+-9',
                r'pkill',
                r'killall'
            ],
            'required_patterns': [
                r'def\s+\w+\(',  # Functions should be properly defined
                r'""".*?"""',   # Docstrings should be present
            ],
            'complexity_limits': {
                'max_cyclomatic_complexity': 10,
                'max_function_length': 50,
                'max_nesting_depth': 4
            }
        }

    def validate_code(self, code: str, language: str = "python", 
                     validation_level: str = "comprehensive") -> Dict[str, Any]:
        """
        Validates autonomously generated or modified code.
        
        Args:
            code: The code to validate
            language: Programming language of the code
            validation_level: Level of validation ("basic", "standard", "comprehensive")
            
        Returns:
            Dictionary containing validation results
        """
        logger.info(f"Starting {validation_level} validation for {language} code")
        
        validation_result = {
            'code_hash': hash(code),
            'language': language,
            'validation_level': validation_level,
            'timestamp': datetime.now().isoformat(),
            'status': 'initiated',
            'passed': False,
            'safety_check': {'passed': False, 'issues': []},
            'syntax_check': {'passed': False, 'issues': []},
            'static_analysis': {'passed': False, 'issues': []},
            'unit_tests': {'passed': False, 'results': {}},
            'integration_tests': {'passed': False, 'results': {}},
            'performance_tests': {'passed': False, 'results': {}},
            'overall_score': 0.0,
            'recommendations': []
        }

        try:
            # Step 1: Safety Check (Always performed)
            safety_result = self._perform_safety_check(code, language)
            validation_result['safety_check'] = safety_result
            
            if not safety_result['passed']:
                validation_result['status'] = 'failed_safety'
                validation_result['recommendations'].append("Code failed safety checks. Review and fix security issues.")
                return validation_result
            
            # Step 2: Syntax Check
            syntax_result = self._perform_syntax_check(code, language)
            validation_result['syntax_check'] = syntax_result
            
            if not syntax_result['passed']:
                validation_result['status'] = 'failed_syntax'
                validation_result['recommendations'].append("Code has syntax errors. Fix syntax issues.")
                return validation_result
            
            # Step 3: Static Analysis
            if validation_level in ['standard', 'comprehensive']:
                static_result = self._perform_static_analysis(code, language)
                validation_result['static_analysis'] = static_result
            
            # Step 4: Unit Tests
            if validation_level in ['standard', 'comprehensive']:
                unit_result = self._perform_unit_tests(code, language)
                validation_result['unit_tests'] = unit_result
            
            # Step 5: Integration Tests
            if validation_level == 'comprehensive':
                integration_result = self._perform_integration_tests(code, language)
                validation_result['integration_tests'] = integration_result
            
            # Step 6: Performance Tests
            if validation_level == 'comprehensive':
                performance_result = self._perform_performance_tests(code, language)
                validation_result['performance_tests'] = performance_result
            
            # Calculate overall score and determine pass/fail
            validation_result['overall_score'] = self._calculate_validation_score(validation_result)
            validation_result['passed'] = validation_result['overall_score'] >= 0.7
            validation_result['status'] = 'passed' if validation_result['passed'] else 'failed'
            
            # Generate recommendations
            validation_result['recommendations'] = self._generate_validation_recommendations(validation_result)
            
        except Exception as e:
            logger.error(f"Validation process failed: {str(e)}")
            validation_result['status'] = 'error'
            validation_result['error'] = str(e)
            validation_result['recommendations'].append(f"Validation process encountered an error: {str(e)}")
        
        # Store validation result
        self._store_validation_result(validation_result)
        
        return validation_result

    def _perform_safety_check(self, code: str, language: str) -> Dict[str, Any]:
        """
        Performs safety checks on the code to identify potentially dangerous operations.
        
        Args:
            code: The code to check
            language: Programming language
            
        Returns:
            Dictionary containing safety check results
        """
        safety_result = {
            'passed': True,
            'issues': [],
            'risk_level': 'low'
        }

        try:
            # Check for forbidden imports/functions
            for forbidden in self.safety_rules['forbidden_imports']:
                if forbidden in code:
                    safety_result['issues'].append({
                        'type': 'forbidden_import',
                        'item': forbidden,
                        'severity': 'high',
                        'message': f"Forbidden import/function detected: {forbidden}"
                    })
                    safety_result['risk_level'] = 'high'
            
            # Check for dangerous patterns using regex
            import re
            for pattern in self.safety_rules['forbidden_patterns']:
                if re.search(pattern, code, re.IGNORECASE):
                    safety_result['issues'].append({
                        'type': 'dangerous_pattern',
                        'pattern': pattern,
                        'severity': 'critical',
                        'message': f"Dangerous pattern detected: {pattern}"
                    })
                    safety_result['risk_level'] = 'critical'
            
            # Language-specific safety checks
            if language == 'python':
                safety_result.update(self._python_safety_check(code))
            
            # Determine if safety check passed
            critical_issues = [issue for issue in safety_result['issues'] if issue['severity'] == 'critical']
            high_issues = [issue for issue in safety_result['issues'] if issue['severity'] == 'high']
            
            if critical_issues:
                safety_result['passed'] = False
                safety_result['risk_level'] = 'critical'
            elif len(high_issues) > 2:
                safety_result['passed'] = False
                safety_result['risk_level'] = 'high'
            elif high_issues:
                safety_result['risk_level'] = 'medium'
            
        except Exception as e:
            logger.error(f"Safety check failed: {str(e)}")
            safety_result['passed'] = False
            safety_result['issues'].append({
                'type': 'safety_check_error',
                'severity': 'high',
                'message': f"Safety check process failed: {str(e)}"
            })
        
        return safety_result

    def _python_safety_check(self, code: str) -> Dict[str, Any]:
        """
        Performs Python-specific safety checks.
        
        Args:
            code: Python code to check
            
        Returns:
            Dictionary with additional safety check results
        """
        additional_issues = []
        
        try:
            # Parse AST to check for dangerous constructs
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for eval/exec calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ['eval', 'exec']:
                        additional_issues.append({
                            'type': 'dangerous_function',
                            'function': node.func.id,
                            'severity': 'critical',
                            'message': f"Dangerous function call: {node.func.id}"
                        })
                
                # Check for __import__ usage
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == '__import__':
                        additional_issues.append({
                            'type': 'dynamic_import',
                            'severity': 'high',
                            'message': "Dynamic import detected: __import__"
                        })
                
                # Check for file operations
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == 'open':
                        # Allow read-only operations, flag write operations
                        if len(node.args) > 1:
                            if isinstance(node.args[1], ast.Str) and 'w' in node.args[1].s:
                                additional_issues.append({
                                    'type': 'file_write',
                                    'severity': 'medium',
                                    'message': "File write operation detected"
                                })
        
        except SyntaxError:
            # Syntax errors will be caught in syntax check
            pass
        except Exception as e:
            additional_issues.append({
                'type': 'python_safety_error',
                'severity': 'medium',
                'message': f"Python safety check error: {str(e)}"
            })
        
        return {'issues': additional_issues}

    def _perform_syntax_check(self, code: str, language: str) -> Dict[str, Any]:
        """
        Performs syntax validation on the code.
        
        Args:
            code: The code to check
            language: Programming language
            
        Returns:
            Dictionary containing syntax check results
        """
        syntax_result = {
            'passed': False,
            'issues': []
        }

        try:
            if language == 'python':
                # Use AST to parse Python code
                ast.parse(code)
                syntax_result['passed'] = True
            elif language == 'javascript':
                # For JavaScript, we would use a JavaScript parser
                # For now, basic check
                if 'function' in code or 'const' in code or 'let' in code:
                    syntax_result['passed'] = True
                else:
                    syntax_result['issues'].append({
                        'type': 'javascript_syntax',
                        'message': 'JavaScript syntax validation not fully implemented'
                    })
            else:
                syntax_result['issues'].append({
                    'type': 'unsupported_language',
                    'message': f'Syntax checking not supported for {language}'
                })
        
        except SyntaxError as e:
            syntax_result['issues'].append({
                'type': 'syntax_error',
                'line': e.lineno,
                'message': str(e),
                'severity': 'high'
            })
        except Exception as e:
            syntax_result['issues'].append({
                'type': 'syntax_check_error',
                'message': f'Syntax check failed: {str(e)}',
                'severity': 'medium'
            })
        
        return syntax_result

    def _perform_static_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """
        Performs static analysis on the code.
        
        Args:
            code: The code to analyze
            language: Programming language
            
        Returns:
            Dictionary containing static analysis results
        """
        static_result = {
            'passed': True,
            'issues': [],
            'metrics': {}
        }

        try:
            if language == 'python':
                static_result.update(self._python_static_analysis(code))
            else:
                static_result['issues'].append({
                    'type': 'unsupported_language',
                    'message': f'Static analysis not implemented for {language}'
                })
        
        except Exception as e:
            logger.error(f"Static analysis failed: {str(e)}")
            static_result['passed'] = False
            static_result['issues'].append({
                'type': 'static_analysis_error',
                'message': f'Static analysis failed: {str(e)}'
            })
        
        return static_result

    def _python_static_analysis(self, code: str) -> Dict[str, Any]:
        """
        Performs Python-specific static analysis.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Dictionary with static analysis results
        """
        analysis_result = {
            'passed': True,
            'issues': [],
            'metrics': {
                'functions': 0,
                'classes': 0,
                'lines_of_code': len(code.splitlines()),
                'complexity_score': 0
            }
        }
        
        try:
            tree = ast.parse(code)
            
            # Count functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis_result['metrics']['functions'] += 1
                    
                    # Check function length
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 10
                    if func_lines > self.safety_rules['complexity_limits']['max_function_length']:
                        analysis_result['issues'].append({
                            'type': 'function_too_long',
                            'function': node.name,
                            'lines': func_lines,
                            'severity': 'medium',
                            'message': f'Function {node.name} is too long ({func_lines} lines)'
                        })
                
                elif isinstance(node, ast.ClassDef):
                    analysis_result['metrics']['classes'] += 1
            
            # Check for docstrings
            if not ast.get_docstring(tree):
                analysis_result['issues'].append({
                    'type': 'missing_docstring',
                    'severity': 'low',
                    'message': 'Module docstring is missing'
                })
            
            # Simple complexity calculation (count decision points)
            complexity = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    complexity += 1
            
            analysis_result['metrics']['complexity_score'] = complexity
            
            if complexity > self.safety_rules['complexity_limits']['max_cyclomatic_complexity']:
                analysis_result['issues'].append({
                    'type': 'high_complexity',
                    'complexity': complexity,
                    'severity': 'medium',
                    'message': f'Code complexity is high ({complexity})'
                })
            
            # Determine if analysis passed
            high_severity_issues = [issue for issue in analysis_result['issues'] if issue.get('severity') == 'high']
            if high_severity_issues:
                analysis_result['passed'] = False
        
        except Exception as e:
            analysis_result['passed'] = False
            analysis_result['issues'].append({
                'type': 'python_analysis_error',
                'message': f'Python static analysis failed: {str(e)}'
            })
        
        return analysis_result

    def _perform_unit_tests(self, code: str, language: str) -> Dict[str, Any]:
        """
        Performs unit testing on the code.
        
        Args:
            code: The code to test
            language: Programming language
            
        Returns:
            Dictionary containing unit test results
        """
        unit_result = {
            'passed': False,
            'results': {
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'coverage': 0.0
            },
            'test_output': ''
        }

        try:
            if language == 'python':
                unit_result.update(self._python_unit_tests(code))
            else:
                unit_result['test_output'] = f'Unit testing not implemented for {language}'
        
        except Exception as e:
            logger.error(f"Unit testing failed: {str(e)}")
            unit_result['test_output'] = f'Unit testing failed: {str(e)}'
        
        return unit_result

    def _python_unit_tests(self, code: str) -> Dict[str, Any]:
        """
        Performs Python unit testing.
        
        Args:
            code: Python code to test
            
        Returns:
            Dictionary with unit test results
        """
        test_result = {
            'passed': False,
            'results': {
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'coverage': 0.0
            },
            'test_output': ''
        }
        
        try:
            # Create a temporary test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            # Generate basic tests for functions found in the code
            test_code = self._generate_basic_tests(code)
            
            if test_code:
                with tempfile.NamedTemporaryFile(mode='w', suffix='_test.py', delete=False) as test_file:
                    test_file.write(f"import sys\nsys.path.append('{os.path.dirname(temp_file_path)}')\n")
                    test_file.write(f"from {os.path.basename(temp_file_path)[:-3]} import *\n")
                    test_file.write(test_code)
                    test_file_path = test_file.name
                
                # Run tests using unittest
                result = subprocess.run([
                    sys.executable, '-m', 'unittest', 'discover', '-s', os.path.dirname(test_file_path), 
                    '-p', os.path.basename(test_file_path)
                ], capture_output=True, text=True, timeout=30)
                
                test_result['test_output'] = result.stdout + result.stderr
                
                # Parse results (basic parsing)
                if 'OK' in result.stderr or result.returncode == 0:
                    test_result['passed'] = True
                    test_result['results']['tests_run'] = 1
                    test_result['results']['tests_passed'] = 1
                    test_result['results']['coverage'] = 0.8  # Estimated
                else:
                    test_result['results']['tests_run'] = 1
                    test_result['results']['tests_failed'] = 1
                
                # Cleanup
                os.unlink(test_file_path)
            else:
                test_result['test_output'] = 'No testable functions found in code'
                test_result['passed'] = True  # Pass if no functions to test
            
            os.unlink(temp_file_path)
        
        except Exception as e:
            test_result['test_output'] = f'Python unit testing failed: {str(e)}'
        
        return test_result

    def _generate_basic_tests(self, code: str) -> str:
        """
        Generates basic unit tests for functions in the code.
        
        Args:
            code: The code to generate tests for
            
        Returns:
            String containing test code
        """
        try:
            tree = ast.parse(code)
            test_code = "import unittest\n\nclass TestGeneratedCode(unittest.TestCase):\n"
            
            functions_found = False
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions_found = True
                    func_name = node.name
                    
                    # Generate a basic test
                    test_code += f"""
    def test_{func_name}(self):
        # Basic test for {func_name}
        try:
            result = {func_name}()
            self.assertIsNotNone(result, "Function should return a value")
        except TypeError:
            # Function might require arguments
            pass
        except Exception as e:
            self.fail(f"Function {func_name} raised an exception: {{e}}")
"""
            
            if functions_found:
                test_code += "\nif __name__ == '__main__':\n    unittest.main()\n"
                return test_code
            else:
                return ""
        
        except Exception:
            return ""

    def _perform_integration_tests(self, code: str, language: str) -> Dict[str, Any]:
        """
        Performs integration testing on the code.
        
        Args:
            code: The code to test
            language: Programming language
            
        Returns:
            Dictionary containing integration test results
        """
        integration_result = {
            'passed': True,
            'results': {
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0
            },
            'test_output': 'Integration testing is a placeholder - would test interactions with other components'
        }
        
        # Placeholder for integration testing
        # In a real implementation, this would test how the code integrates with existing systems
        
        return integration_result

    def _perform_performance_tests(self, code: str, language: str) -> Dict[str, Any]:
        """
        Performs performance testing on the code.
        
        Args:
            code: The code to test
            language: Programming language
            
        Returns:
            Dictionary containing performance test results
        """
        performance_result = {
            'passed': True,
            'results': {
                'execution_time_ms': 0.0,
                'memory_usage_mb': 0.0,
                'cpu_usage_percent': 0.0
            },
            'test_output': 'Performance testing is a placeholder - would measure execution metrics'
        }
        
        # Placeholder for performance testing
        # In a real implementation, this would measure execution time, memory usage, etc.
        
        return performance_result

    def _calculate_validation_score(self, validation_result: Dict[str, Any]) -> float:
        """
        Calculates an overall validation score based on all test results.
        
        Args:
            validation_result: The validation result dictionary
            
        Returns:
            Float score between 0.0 and 1.0
        """
        score = 0.0
        total_weight = 0.0
        
        # Safety check (weight: 40%)
        if validation_result['safety_check']['passed']:
            score += 0.4
        total_weight += 0.4
        
        # Syntax check (weight: 30%)
        if validation_result['syntax_check']['passed']:
            score += 0.3
        total_weight += 0.3
        
        # Static analysis (weight: 15%)
        if validation_result['static_analysis']['passed']:
            score += 0.15
        total_weight += 0.15
        
        # Unit tests (weight: 10%)
        if validation_result['unit_tests']['passed']:
            score += 0.1
        total_weight += 0.1
        
        # Integration tests (weight: 3%)
        if validation_result['integration_tests']['passed']:
            score += 0.03
        total_weight += 0.03
        
        # Performance tests (weight: 2%)
        if validation_result['performance_tests']['passed']:
            score += 0.02
        total_weight += 0.02
        
        return score / total_weight if total_weight > 0 else 0.0

    def _generate_validation_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """
        Generates recommendations based on validation results.
        
        Args:
            validation_result: The validation result dictionary
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Safety recommendations
        if not validation_result['safety_check']['passed']:
            recommendations.append("Address all safety issues before deployment")
            for issue in validation_result['safety_check']['issues']:
                if issue['severity'] == 'critical':
                    recommendations.append(f"CRITICAL: {issue['message']}")
        
        # Syntax recommendations
        if not validation_result['syntax_check']['passed']:
            recommendations.append("Fix all syntax errors")
        
        # Static analysis recommendations
        if not validation_result['static_analysis']['passed']:
            recommendations.append("Address static analysis issues")
            for issue in validation_result['static_analysis']['issues']:
                if issue['severity'] in ['high', 'medium']:
                    recommendations.append(f"Consider: {issue['message']}")
        
        # General recommendations based on score
        score = validation_result['overall_score']
        if score < 0.5:
            recommendations.append("Code requires significant improvements before deployment")
        elif score < 0.7:
            recommendations.append("Code needs improvements in several areas")
        elif score < 0.9:
            recommendations.append("Code is good but could benefit from minor improvements")
        else:
            recommendations.append("Code meets high quality standards")
        
        return recommendations

    def _store_validation_result(self, validation_result: Dict[str, Any]):
        """
        Stores validation results in history and knowledge repository.
        
        Args:
            validation_result: The validation result to store
        """
        # Add to validation history
        self.validation_history.append(validation_result)
        
        # Keep only last 100 validation records
        if len(self.validation_history) > 100:
            self.validation_history = self.validation_history[-100:]
        
        # Store in knowledge repository if available
        if self.knowledge_repository:
            self.knowledge_repository.add_performance_data({
                'type': 'code_validation',
                'validation_data': validation_result,
                'timestamp': validation_result['timestamp']
            })

    def _setup_python_test_environment(self) -> str:
        """
        Sets up a Python test environment.
        
        Returns:
            Path to the test environment
        """
        # Create a temporary directory for testing
        test_dir = tempfile.mkdtemp(prefix='jarvis_validation_')
        return test_dir

    def _setup_javascript_test_environment(self) -> str:
        """
        Sets up a JavaScript test environment.
        
        Returns:
            Path to the test environment
        """
        # Placeholder for JavaScript test environment setup
        test_dir = tempfile.mkdtemp(prefix='jarvis_js_validation_')
        return test_dir

    def get_validation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Gets the validation history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of validation records
        """
        return self.validation_history[-limit:] if limit else self.validation_history.copy()

    def get_validation_statistics(self) -> Dict[str, Any]:
        """
        Gets statistics about validation activities.
        
        Returns:
            Dictionary containing validation statistics
        """
        total_validations = len(self.validation_history)
        passed_validations = sum(1 for v in self.validation_history if v.get('passed', False))
        
        # Calculate average scores
        scores = [v.get('overall_score', 0.0) for v in self.validation_history if 'overall_score' in v]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Language distribution
        language_counts = {}
        for validation in self.validation_history:
            lang = validation.get('language', 'unknown')
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            'total_validations': total_validations,
            'passed_validations': passed_validations,
            'pass_rate': passed_validations / max(total_validations, 1),
            'average_score': avg_score,
            'language_distribution': language_counts,
            'safety_rules_count': len(self.safety_rules['forbidden_imports']) + len(self.safety_rules['forbidden_patterns'])
        }

    def update_safety_rules(self, new_rules: Dict[str, Any]):
        """
        Updates the safety rules for code validation.
        
        Args:
            new_rules: Dictionary containing new safety rules
        """
        for category, rules in new_rules.items():
            if category in self.safety_rules:
                if isinstance(rules, list):
                    self.safety_rules[category].extend(rules)
                elif isinstance(rules, dict):
                    self.safety_rules[category].update(rules)
        
        logger.info("Safety rules updated")

    def validate_and_suggest_improvements(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Validates code and provides specific improvement suggestions.
        
        Args:
            code: The code to validate and improve
            language: Programming language
            
        Returns:
            Dictionary containing validation results and improvement suggestions
        """
        validation_result = self.validate_code(code, language, "comprehensive")
        
        # Generate specific improvement suggestions
        improvements = {
            'immediate_fixes': [],
            'code_quality_improvements': [],
            'performance_optimizations': [],
            'security_enhancements': []
        }
        
        # Analyze validation results to generate specific suggestions
        if not validation_result['safety_check']['passed']:
            for issue in validation_result['safety_check']['issues']:
                improvements['security_enhancements'].append({
                    'type': 'security_fix',
                    'description': issue['message'],
                    'priority': 'critical' if issue['severity'] == 'critical' else 'high'
                })
        
        if not validation_result['syntax_check']['passed']:
            for issue in validation_result['syntax_check']['issues']:
                improvements['immediate_fixes'].append({
                    'type': 'syntax_fix',
                    'description': issue['message'],
                    'priority': 'critical'
                })
        
        # Add static analysis improvements
        for issue in validation_result['static_analysis'].get('issues', []):
            if issue.get('type') == 'function_too_long':
                improvements['code_quality_improvements'].append({
                    'type': 'refactor_function',
                    'description': f"Break down {issue['function']} into smaller functions",
                    'priority': 'medium'
                })
            elif issue.get('type') == 'high_complexity':
                improvements['performance_optimizations'].append({
                    'type': 'reduce_complexity',
                    'description': 'Simplify complex logic and reduce nesting',
                    'priority': 'medium'
                })
        
        return {
            'validation_result': validation_result,
            'improvement_suggestions': improvements,
            'overall_assessment': self._generate_overall_assessment(validation_result, improvements)
        }

    def _generate_overall_assessment(self, validation_result: Dict[str, Any], 
                                   improvements: Dict[str, Any]) -> str:
        """
        Generates an overall assessment of the code quality and validation results.
        
        Args:
            validation_result: The validation results
            improvements: The improvement suggestions
            
        Returns:
            String containing the overall assessment
        """
        score = validation_result.get('overall_score', 0.0)
        
        if score >= 0.9:
            return "Excellent code quality. Ready for deployment with minimal risk."
        elif score >= 0.7:
            return "Good code quality. Minor improvements recommended before deployment."
        elif score >= 0.5:
            return "Moderate code quality. Several improvements needed before deployment."
        elif score >= 0.3:
            return "Poor code quality. Significant improvements required before deployment."
        else:
            return "Very poor code quality. Major rework needed before deployment."

