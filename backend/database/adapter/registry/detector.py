from typing import Optional
from urllib.parse import urlparse
import os

class SourceDetector:
    """
    Automatically detects the data source type from a connection string or file path.
    """
    
    @staticmethod
    def detect_source_type(connection_string: str) -> str:
        """
        Parses the connection string to determine the source type.
        Examples:
        'postgres://...' -> 'postgresql'
        'mongodb://...' -> 'mongodb'
        '/path/to/file.csv' -> 'csv'
        """
        # Check if it's a known URL scheme
        parsed = urlparse(connection_string)
        if parsed.scheme:
            scheme = parsed.scheme.lower()
            # Handle aliases
            if scheme in ('postgres', 'postgresql'):
                return 'postgresql'
            if scheme in ('mysql', 'sqlite', 'mongodb', 'neo4j', 'redis', 'elasticsearch'):
                return scheme
            if scheme in ('http', 'https'):
                # Heuristic: might be an API or a remote file
                if connection_string.endswith('.pdf'): return 'pdf'
                if connection_string.endswith('.csv'): return 'csv'
                return 'api'
                
        # Fallback: check if it's a file path
        if os.path.exists(connection_string) or '.' in connection_string.split(os.sep)[-1]:
            ext = os.path.splitext(connection_string)[1].lower()
            if ext == '.csv': return 'csv'
            if ext in ('.xls', '.xlsx'): return 'excel'
            if ext == '.pdf': return 'pdf'
            if ext == '.json': return 'json'
            if ext == '.xml': return 'xml'
            if ext == '.yaml': return 'yaml'
            if ext == '.txt': return 'txt'
            if ext == '.md': return 'markdown'
            if ext == '.docx': return 'docx'
            
        raise ValueError(f"Unable to auto-detect source type for: {connection_string}")
