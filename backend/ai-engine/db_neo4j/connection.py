import logging
from typing import Any, Dict, List, Optional
import sys
import os

import sys
import importlib.util

import sys
import importlib.util

# Robustly load the official PyPI neo4j package
local_modules = {k: v for k, v in sys.modules.items() if k == 'neo4j' or k.startswith('neo4j.')}
for k in local_modules:
    sys.modules.pop(k, None)

official_neo4j = None
original_sys_path = list(sys.path)
sys.path = [p for p in sys.path if 'ai-engine' not in p and p != '' and p != '.']

try:
    spec = importlib.util.find_spec('neo4j')
    if spec:
        official_neo4j = importlib.util.module_from_spec(spec)
        sys.modules['neo4j'] = official_neo4j
        spec.loader.exec_module(official_neo4j)
except Exception:
    pass

# We must extract what we need from the official driver before restoring sys.modules
GraphDatabase = official_neo4j.GraphDatabase if official_neo4j else None
Driver = official_neo4j.Driver if official_neo4j else None
Session = official_neo4j.Session if official_neo4j else None
ServiceUnavailable = official_neo4j.exceptions.ServiceUnavailable if official_neo4j else Exception
AuthError = official_neo4j.exceptions.AuthError if official_neo4j else Exception
ClientError = official_neo4j.exceptions.ClientError if official_neo4j else Exception

sys.path = original_sys_path

# Remove all official neo4j modules from sys.modules to prevent pollution
official_modules = [k for k in sys.modules if k == 'neo4j' or k.startswith('neo4j.')]
for k in official_modules:
    sys.modules.pop(k, None)

# Restore local modules
for k, v in local_modules.items():
    sys.modules[k] = v

if not official_neo4j:
    raise ImportError("Could not load official neo4j driver")



from .config import get_settings, Neo4jSettings
from .exceptions import GraphConnectionError, GraphQueryError

logger = logging.getLogger(__name__)

class Neo4jConnectionManager:
    """
    Manages the lifecycle of the Neo4j driver and provides methods for safely
    executing parameterized Cypher queries.
    """
    
    def __init__(self):
        self._driver: Optional[Driver] = None
        self._settings: Optional[Neo4jSettings] = None
        
    def initialize(self) -> None:
        """Initializes the Neo4j driver using configuration from environment."""
        if self._driver is not None:
            return  # Already initialized
            
        self._settings = get_settings()
        
        try:
            self._driver = GraphDatabase.driver(
                self._settings.neo4j_uri,
                auth=(self._settings.neo4j_username, self._settings.neo4j_password)
            )
            # Verify connectivity immediately
            self._driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {self._settings.neo4j_uri}")
        except AuthError as e:
            logger.error("Authentication failed for Neo4j connection.")
            raise GraphConnectionError("Invalid Neo4j credentials provided.") from e
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable at {self._settings.neo4j_uri}.")
            raise GraphConnectionError("Could not connect to Neo4j service.") from e
        except Exception as e:
            logger.error("An unexpected error occurred while connecting to Neo4j.")
            raise GraphConnectionError("Unexpected graph connection error.") from e

    def close(self) -> None:
        """Safely closes the Neo4j driver connection."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed safely.")

    def get_session(self) -> Session:
        """
        Returns a new Neo4j session bound to the configured database.
        Caller is responsible for closing the session (use as a context manager).
        """
        if self._driver is None or self._settings is None:
            self.initialize()
            
        return self._driver.session(database=self._settings.neo4j_database)

    def execute_read_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a parameterized read-only Cypher query.
        
        Args:
            query: The parameterized Cypher query string.
            parameters: Dictionary of parameters for the query.
            
        Returns:
            A list of dictionaries representing the records returned.
        """
        params = parameters or {}
        try:
            with self.get_session() as session:
                result = session.execute_read(lambda tx: tx.run(query, **params).data())
                return result
        except ClientError as e:
            logger.error("Client error executing read query.", exc_info=True)
            raise GraphQueryError("Invalid read query or parameters.") from e
        except Exception as e:
            logger.error("Unexpected error executing read query.", exc_info=True)
            raise GraphQueryError("Failed to execute read query.") from e

    def execute_write_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a parameterized write Cypher query.
        
        Args:
            query: The parameterized Cypher query string.
            parameters: Dictionary of parameters for the query.
            
        Returns:
            A list of dictionaries representing the records returned (if any).
        """
        params = parameters or {}
        try:
            with self.get_session() as session:
                result = session.execute_write(lambda tx: tx.run(query, **params).data())
                return result
        except ClientError as e:
            logger.error("Client error executing write query.", exc_info=True)
            raise GraphQueryError("Invalid write query or parameters.") from e
        except Exception as e:
            logger.error("Unexpected error executing write query.", exc_info=True)
            raise GraphQueryError("Failed to execute write query.") from e

# Global instance for use across the application
graph_manager = Neo4jConnectionManager()
