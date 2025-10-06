"""
Knowledge & Learning Repository (KLR) for JARVIS AI Hub Self-Development Module

This module serves as JARVIS's long-term memory for self-development,
storing learned patterns, code snippets, research findings, and performance data.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class KnowledgeRepository:
    """
    The KLR stores and manages all relevant information required for code generation,
    analysis, and research, enabling continuous learning and improvement.
    """

    def __init__(self, db_path: str = "knowledge_base.json"):
        self.db_path = db_path
        self.knowledge_base = self._load_knowledge_base()
        logger.info(f"Knowledge & Learning Repository initialized from {db_path}")

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """
        Loads the knowledge base from a JSON file.
        """
        if os.path.exists(self.db_path):
            with open(self.db_path, "r") as f:
                return json.load(f)
        return {
            "code_snippets": [],
            "design_patterns": [],
            "research_findings": [],
            "performance_data": [],
            "error_logs_fixes": [],
            "skill_schemas": [],
            "learning_models": [],
            "self_development_history": []
        }

    def _save_knowledge_base(self):
        """
        Saves the knowledge base to a JSON file.
        """
        with open(self.db_path, "w") as f:
            json.dump(self.knowledge_base, f, indent=2)

    def add_code_snippet(self, snippet: Dict[str, Any]):
        """
        Adds a reusable code snippet to the repository.
        """
        snippet["timestamp"] = datetime.now().isoformat()
        self.knowledge_base["code_snippets"].append(snippet)
        self._save_knowledge_base()
        logger.debug(f"Added code snippet: {snippet.get("name", "Unnamed")}")

    def get_code_snippets(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves code snippets, optionally filtered by a query.
        """
        if query:
            return [s for s in self.knowledge_base["code_snippets"] if query.lower() in json.dumps(s).lower()]
        return self.knowledge_base["code_snippets"]

    def add_design_pattern(self, pattern: Dict[str, Any]):
        """
        Adds a design pattern to the repository.
        """
        pattern["timestamp"] = datetime.now().isoformat()
        self.knowledge_base["design_patterns"].append(pattern)
        self._save_knowledge_base()
        logger.debug(f"Added design pattern: {pattern.get("name", "Unnamed")}")

    def get_design_patterns(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves design patterns, optionally filtered by a query.
        """
        if query:
            return [p for p in self.knowledge_base["design_patterns"] if query.lower() in json.dumps(p).lower()]
        return self.knowledge_base["design_patterns"]

    def add_research_finding(self, finding: Dict[str, Any]):
        """
        Adds a research finding to the repository.
        """
        finding["timestamp"] = datetime.now().isoformat()
        self.knowledge_base["research_findings"].append(finding)
        self._save_knowledge_base()
        logger.debug(f"Added research finding: {finding.get("title", "Untitled")}")

    def get_research_findings(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves research findings, optionally filtered by a query.
        """
        if query:
            return [f for f in self.knowledge_base["research_findings"] if query.lower() in json.dumps(f).lower()]
        return self.knowledge_base["research_findings"]

    def add_performance_data(self, data: Dict[str, Any]):
        """
        Adds performance data to the repository.
        """
        data["timestamp"] = datetime.now().isoformat()
        self.knowledge_base["performance_data"].append(data)
        self._save_knowledge_base()
        logger.debug(f"Added performance data for: {data.get("component", "Unnamed")}")

    def get_performance_data(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves performance data, optionally filtered by a query.
        """
        if query:
            return [d for d in self.knowledge_base["performance_data"] if query.lower() in json.dumps(d).lower()]
        return self.knowledge_base["performance_data"]

    def add_error_log_fix(self, log_fix: Dict[str, Any]):
        """
        Adds an error log and its corresponding fix to the repository.
        """
        log_fix["timestamp"] = datetime.now().isoformat()
        self.knowledge_base["error_logs_fixes"].append(log_fix)
        self._save_knowledge_base()
        logger.debug(f"Added error log/fix for: {log_fix.get("error_type", "Unnamed")}")

    def get_error_log_fixes(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves error logs and fixes, optionally filtered by a query.
        """
        if query:
            return [lf for lf in self.knowledge_base["error_logs_fixes"] if query.lower() in json.dumps(lf).lower()]
        return self.knowledge_base["error_logs_fixes"]

    def add_skill_schema(self, schema: Dict[str, Any]):
        """
        Adds a skill schema to the repository.
        """
        schema["timestamp"] = datetime.now().isoformat()
        self.knowledge_base["skill_schemas"].append(schema)
        self._save_knowledge_base()
        logger.debug(f"Added skill schema: {schema.get("name", "Unnamed")}")

    def get_skill_schemas(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves skill schemas, optionally filtered by a query.
        """
        if query:
            return [s for s in self.knowledge_base["skill_schemas"] if query.lower() in json.dumps(s).lower()]
        return self.knowledge_base["skill_schemas"]

    def add_self_development_history(self, record: Dict[str, Any]):
        """
        Adds a record of self-development activity (e.g., code generation, modification).
        """
        record["timestamp"] = datetime.now().isoformat()
        self.knowledge_base["self_development_history"].append(record)
        self._save_knowledge_base()
        logger.debug(f"Added self-development history record: {record.get("type", "Unnamed")}")

    def get_self_development_history(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves self-development history records, optionally filtered by a query.
        """
        if query:
            return [r for r in self.knowledge_base["self_development_history"] if query.lower() in json.dumps(r).lower()]
        return self.knowledge_base["self_development_history"]

    def get_relevant_patterns(self, objective: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves patterns (code snippets, design patterns) relevant to a given objective.
        This is a simplified implementation; a real system would use vector embeddings for semantic search.
        """
        relevant = []
        # Simple keyword matching for now
        keywords = objective.lower().split()

        for snippet in self.knowledge_base["code_snippets"]:
            if any(k in json.dumps(snippet).lower() for k in keywords):
                relevant.append({"type": "code_snippet", "data": snippet})
        for pattern in self.knowledge_base["design_patterns"]:
            if any(k in json.dumps(pattern).lower() for k in keywords):
                relevant.append({"type": "design_pattern", "data": pattern})

        return relevant[:limit]

import os


