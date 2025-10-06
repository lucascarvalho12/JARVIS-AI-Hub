"""
Code Analysis & Evaluation Unit (CAEU) for JARVIS AI Hub Self-Development Module

This module provides functionalities for rigorously analyzing and evaluating code
for correctness, performance, security, and adherence to coding standards.
"""

import os
import json
import logging
import subprocess
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """
    The Code Analysis & Evaluation Unit (CAEU) performs static and dynamic analysis
    on code, executes tests, and provides feedback on code quality and performance.
    """

    def __init__(self):
        logger.info("Code Analysis & Evaluation Unit initialized")

    def analyze_code(self, code: str, language: str = "python", file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Performs static analysis on the provided code.

        Args:
            code: The code string to analyze.
            language: The programming language of the code (e.g., "python", "javascript").
            file_path: Optional path to the file if it exists (for context).

        Returns:
            A dictionary containing various analysis metrics and findings.
        """
        analysis_results = {
            "syntax_valid": False,
            "linting_issues": [],
            "security_vulnerabilities": [],
            "complexity_score": None,
            "readability_score": None,
            "has_docstrings": False,
            "has_type_hints": False,
            "functions_found": [],
            "classes_found": [],
            "imports_found": [],
            "lines_of_code": len(code.splitlines()),
            "analysis_timestamp": datetime.now().isoformat()
        }

        try:
            if language == "python":
                analysis_results.update(self._analyze_python_code(code, file_path))
            elif language == "javascript":
                analysis_results.update(self._analyze_javascript_code(code, file_path))
            # Add more languages as needed
            else:
                analysis_results["linting_issues"].append(f"Unsupported language for detailed analysis: {language}")

            analysis_results["syntax_valid"] = True # If no syntax error during specific language analysis

        except SyntaxError as e:
            analysis_results["linting_issues"].append(f"Syntax error: {str(e)}")
        except Exception as e:
            logger.error(f"General error during code analysis: {str(e)}")
            analysis_results["linting_issues"].append(f"Analysis error: {str(e)}")

        return analysis_results

    def _analyze_python_code(self, code: str, file_path: Optional[str]) -> Dict[str, Any]:
        """
        Performs Python-specific static analysis.
        """
        results = {
            "linting_issues": [],
            "complexity_score": None,
            "readability_score": None,
            "has_docstrings": False,
            "has_type_hints": False,
            "functions_found": [],
            "classes_found": [],
            "imports_found": []
        }

        # Use AST for deeper analysis
        try:
            import ast
            tree = ast.parse(code)
            results["has_docstrings"] = ast.getdoc(tree) is not None

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    results["functions_found"].append(node.name)
                    if node.returns or any(arg.annotation for arg in node.args.args):
                        results["has_type_hints"] = True
                elif isinstance(node, ast.ClassDef):
                    results["classes_found"].append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    results["imports_found"].append(ast.get_source_segment(code, node))

        except SyntaxError as e:
            raise e # Re-raise to be caught by analyze_code
        except Exception as e:
            results["linting_issues"].append(f"AST analysis error: {str(e)}")

        # Use pylint for linting and complexity (if installed and available)
        try:
            # Pylint requires a file, so write to a temp file
            temp_file_path = "_temp_jarvis_code.py"
            with open(temp_file_path, "w") as f:
                f.write(code)

            # Run pylint
            pylint_output = subprocess.run(
                ["pylint", "--output-format=json", temp_file_path],
                capture_output=True, text=True, check=False
            )
            os.remove(temp_file_path)

            if pylint_output.stdout:
                pylint_json = json.loads(pylint_output.stdout)
                for msg in pylint_json:
                    results["linting_issues"].append({
                        "type": msg["type"],
                        "msg_id": msg["message-id"],
                        "symbol": msg["symbol"],
                        "line": msg["line"],
                        "column": msg["column"],
                        "message": msg["message"]
                    })

                # Extract complexity (pylint doesn't give a single score easily, need to parse report)
                # For simplicity, we'll just note if there are too many warnings/errors related to complexity
                # A more advanced implementation would parse the full text report or use a dedicated tool like radon

        except FileNotFoundError:
            logger.warning("Pylint not found. Skipping detailed Python linting.")
            results["linting_issues"].append("Pylint not installed. Install with 'pip install pylint' for detailed linting.")
        except Exception as e:
            logger.error(f"Error running pylint: {str(e)}")
            results["linting_issues"].append(f"Pylint execution error: {str(e)}")

        # Basic security checks (can be expanded with tools like Bandit)
        if "os.system" in code or "subprocess.run" in code:
            results["security_vulnerabilities"].append("Potential command injection risk (os.system/subprocess.run detected).")

        return results

    def _analyze_javascript_code(self, code: str, file_path: Optional[str]) -> Dict[str, Any]:
        """
        Performs JavaScript-specific static analysis (placeholder).
        """
        results = {
            "linting_issues": [],
            "complexity_score": None,
            "readability_score": None,
            "has_docstrings": False, # JS comments are different
            "has_type_hints": False, # TS would have this
            "functions_found": [],
            "classes_found": [],
            "imports_found": []
        }
        results["linting_issues"].append("JavaScript analysis is a placeholder. Implement ESLint/JSHint integration.")
        # Placeholder for ESLint or JSHint integration
        return results

    def execute_tests(self, code: str, language: str = "python", test_framework: str = "pytest") -> Dict[str, Any]:
        """
        Executes tests on the provided code within a sandboxed environment.

        Args:
            code: The test code to execute.
            language: The programming language of the test code.
            test_framework: The testing framework to use (e.g., "pytest").

        Returns:
            A dictionary containing test results (passed, failed, errors, coverage).
        """
        test_results = {
            "success": False,
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "coverage": None,
            "output": "",
            "execution_timestamp": datetime.now().isoformat()
        }

        if language == "python" and test_framework == "pytest":
            try:
                # Pytest requires a file, so write to a temp file
                temp_test_file_path = "_temp_jarvis_test.py"
                with open(temp_test_file_path, "w") as f:
                    f.write(code)

                # Run pytest in a subprocess
                pytest_output = subprocess.run(
                    ["pytest", "--json-report", "--json-report-file=report.json", temp_test_file_path],
                    capture_output=True, text=True, check=False
                )
                test_results["output"] = pytest_output.stdout + pytest_output.stderr

                if os.path.exists("report.json"):
                    with open("report.json", "r") as f:
                        report_data = json.load(f)
                    test_results["total_tests"] = report_data["summary"]["total"]
                    test_results["passed"] = report_data["summary"].get("passed", 0)
                    test_results["failed"] = report_data["summary"].get("failed", 0)
                    test_results["success"] = test_results["failed"] == 0
                    os.remove("report.json")
                else:
                    test_results["errors"].append("Pytest JSON report not generated.")

                os.remove(temp_test_file_path)

            except FileNotFoundError:
                logger.warning("Pytest not found. Skipping test execution.")
                test_results["errors"].append("Pytest not installed. Install with 'pip install pytest pytest-json-report' for test execution.")
            except Exception as e:
                logger.error(f"Error running pytest: {str(e)}")
                test_results["errors"].append(f"Pytest execution error: {str(e)}")
        else:
            test_results["errors"].append(f"Unsupported test framework or language: {test_framework}/{language}")

        return test_results

    def evaluate_performance(self, code: str, language: str = "python", iterations: int = 100) -> Dict[str, Any]:
        """
        Evaluates the runtime performance of a given code snippet.
        This would typically run in a Secure Execution Environment (SEE).

        Args:
            code: The code snippet to evaluate.
            language: The language of the code.
            iterations: Number of times to run the code for averaging.

        Returns:
            A dictionary with performance metrics (e.g., execution time, memory usage).
        """
        performance_metrics = {
            "execution_time_avg_ms": None,
            "memory_usage_avg_mb": None,
            "cpu_usage_avg_percent": None,
            "evaluation_timestamp": datetime.now().isoformat()
        }

        if language == "python":
            try:
                import timeit
                import tracemalloc

                # Time execution
                setup_code = ""
                stmt_code = code
                # If the code defines functions, we need to call them
                if "def " in code:
                    # Simple heuristic: find the last defined function and call it
                    last_func_name = None
                    for line in code.splitlines():
                        if line.strip().startswith("def "):
                            last_func_name = line.strip().split(" ")[1].split("(")[0]
                    if last_func_name:
                        setup_code = code
                        stmt_code = f"{last_func_name}()"
                    else:
                        # If no function, assume it's a script to be run directly
                        pass

                timer = timeit.Timer(stmt=stmt_code, setup=setup_code)
                times = timer.repeat(repeat=3, number=iterations)
                performance_metrics["execution_time_avg_ms"] = (sum(times) / len(times)) * 1000 / iterations

                # Memory usage (basic snapshot)
                tracemalloc.start()
                exec(code)
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                performance_metrics["memory_usage_avg_mb"] = peak / (1024 * 1024)

            except Exception as e:
                logger.error(f"Python performance evaluation failed: {str(e)}")
                performance_metrics["errors"] = f"Performance evaluation error: {str(e)}"
        else:
            performance_metrics["errors"] = f"Unsupported language for performance evaluation: {language}"

        return performance_metrics

    def compare_code(self, original_code: str, modified_code: str) -> Dict[str, Any]:
        """
        Compares two versions of code and highlights differences.

        Args:
            original_code: The original code string.
            modified_code: The modified code string.

        Returns:
            A dictionary detailing the differences.
        """
        import difflib
        diff = list(difflib.unified_diff(
            original_code.splitlines(keepends=True),
            modified_code.splitlines(keepends=True),
            fromfile='original.py',
            tofile='modified.py'
        ))

        return {
            "diff_present": len(diff) > 0,
            "diff_output": "".join(diff),
            "lines_added": sum(1 for line in diff if line.startswith('+') and not line.startswith('+++')),
            "lines_removed": sum(1 for line in diff if line.startswith('-') and not line.startswith('---')),
            "comparison_timestamp": datetime.now().isoformat()
        }

from datetime import datetime
from typing import Optional


