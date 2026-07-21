import re
import os
from typing import Any
from ..core.exceptions import InvalidSourceError

class SecurityManager:
    """
    Handles query sanitization, path validation, and injection prevention.
    """
    
    @staticmethod
    def sanitize_sql(query: str) -> str:
        """
        Basic SQL injection mitigation for raw queries.
        Note: Connectors should use parameterized queries, but this serves as a fallback.
        """
        # Very rudimentary pattern, real production would use strict tokenizing
        forbidden_patterns = [
            r"(?i)\bDROP\b",
            r"(?i)\bTRUNCATE\b",
            r"(?i)\bDELETE\b",
            r"(?i)\bALTER\b",
            r"(?i)\bEXEC\b",
            r"(?i)\bUNION\b"
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, query):
                raise ValueError(f"Potentially unsafe SQL detected: {pattern} keyword found.")
        return query

    @staticmethod
    def sanitize_cypher(query: str) -> str:
        """Sanitize Cypher queries against Neo4j injections."""
        forbidden_patterns = [
            r"(?i)\bDETACH DELETE\b",
            r"(?i)\bREMOVE\b",
            r"(?i)\bDROP\b"
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, query):
                raise ValueError(f"Potentially unsafe Cypher detected: {pattern} keyword found.")
        return query

    @staticmethod
    def validate_file_path(base_dir: str, target_path: str) -> str:
        """
        Prevents directory traversal (e.g., ../../../etc/passwd).
        """
        resolved_base = os.path.abspath(base_dir)
        resolved_target = os.path.abspath(os.path.join(base_dir, target_path))
        
        if not resolved_target.startswith(resolved_base):
            raise InvalidSourceError("Path traversal detected.")
            
        if not os.path.exists(resolved_target):
            raise InvalidSourceError(f"File not found: {resolved_target}")
            
        return resolved_target

    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        """Sanitizes user input to prevent LLM Prompt Injection attacks."""
        # Strip invisible characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', prompt)
        return sanitized
