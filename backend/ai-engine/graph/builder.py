import logging
from typing import Dict, Any, Optional

from db_neo4j.connection import graph_manager
from db_neo4j.exceptions import GraphQueryError
from .exceptions import GraphBuilderError, SchemaValidationError
from .schemas.nodes import BaseNode
from .schemas.relationships import BaseRelationship

logger = logging.getLogger(__name__)

class GraphBuilder:
    """
    Translates Pydantic schemas into Cypher queries and ingests them into Neo4j.
    """
    
    def _sanitize_label(self, label: str) -> str:
        """Ensures labels are safe to inject directly into Cypher."""
        if not label.isalnum():
            raise SchemaValidationError(f"Invalid label format: {label}")
        return label

    def merge_node(self, node: BaseNode, label: Optional[str] = None) -> Dict[str, Any]:
        """
        Merges a node into the graph. Uses the Pydantic model class name as the label 
        unless explicitly provided.
        """
        node_label = self._sanitize_label(label or node.__class__.__name__)
        props = node.model_dump(exclude_none=True)
        
        if 'id' not in props:
            raise SchemaValidationError("Node schema must contain an 'id' field for MERGE operation.")
            
        cypher = f"""
        MERGE (n:{node_label} {{id: $props.id}})
        SET n += $props
        RETURN n
        """
        
        try:
            records = graph_manager.execute_write_query(cypher, {"props": props})
            if not records:
                raise GraphBuilderError("Node merge returned no records.")
            return dict(records[0]["n"])
        except GraphQueryError as e:
            logger.error(f"Failed to merge node {node_label} with id {props.get('id')}")
            raise GraphBuilderError(f"Cypher execution failed: {e}") from e

    def merge_relationship(self, source_id: str, target_id: str, relationship: BaseRelationship, rel_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Merges a directed relationship between two existing nodes by their IDs.
        Uses the Pydantic model class name as the RelationshipType unless explicitly provided.
        """
        type_str = self._sanitize_label(rel_type or relationship.__class__.__name__)
        props = relationship.model_dump(exclude_none=True)
        
        cypher = f"""
        MATCH (a {{id: $source_id}})
        MATCH (b {{id: $target_id}})
        MERGE (a)-[r:{type_str}]->(b)
        SET r += $props
        RETURN r
        """
        
        try:
            records = graph_manager.execute_write_query(cypher, {
                "source_id": source_id,
                "target_id": target_id,
                "props": props
            })
            if not records:
                raise GraphBuilderError(f"Relationship merge failed. Missing source ({source_id}) or target ({target_id}) node?")
            return dict(records[0]["r"])
        except GraphQueryError as e:
            logger.error(f"Failed to merge relationship {type_str} from {source_id} to {target_id}")
            raise GraphBuilderError(f"Cypher execution failed: {e}") from e
