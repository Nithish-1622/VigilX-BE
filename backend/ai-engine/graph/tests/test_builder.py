import pytest
from unittest.mock import patch, MagicMock

from graph.builder import GraphBuilder
from graph.exceptions import GraphBuilderError, SchemaValidationError
from graph.schemas.nodes import BaseNode
from graph.schemas.relationships import BaseRelationship

class DummyNode(BaseNode):
    pass

class DummyRelationship(BaseRelationship):
    pass

@pytest.fixture
def builder():
    return GraphBuilder()

@patch('graph.builder.graph_manager')
def test_merge_node_success(mock_graph_manager, builder):
    mock_graph_manager.execute_write_query.return_value = [{"n": {"id": "123", "source_system": "DJANGO"}}]
    
    node = DummyNode(id="123", source_system="DJANGO", created_at="2026-07-11")
    result = builder.merge_node(node)
    
    assert result["id"] == "123"
    
    # Assert query string
    args, kwargs = mock_graph_manager.execute_write_query.call_args
    query = args[0]
    assert "MERGE (n:DummyNode {id: $props.id})" in query
    assert "SET n += $props" in query
    
    # Assert parameters
    params = args[1]
    assert params["props"]["id"] == "123"

@patch('graph.builder.graph_manager')
def test_merge_node_custom_label(mock_graph_manager, builder):
    mock_graph_manager.execute_write_query.return_value = [{"n": {"id": "123"}}]
    
    node = DummyNode(id="123", source_system="DJANGO", created_at="2026-07-11")
    builder.merge_node(node, label="CustomNode")
    
    args, _ = mock_graph_manager.execute_write_query.call_args
    assert "MERGE (n:CustomNode {id: $props.id})" in args[0]

def test_merge_node_invalid_label(builder):
    node = DummyNode(id="123", source_system="DJANGO", created_at="2026-07-11")
    with pytest.raises(SchemaValidationError):
        builder.merge_node(node, label="Invalid Label With Spaces")

@patch('graph.builder.graph_manager')
def test_merge_relationship_success(mock_graph_manager, builder):
    mock_graph_manager.execute_write_query.return_value = [{"r": {"source_type": "API"}}]
    
    rel = DummyRelationship(source_type="API", generated_at="2026-07-11")
    result = builder.merge_relationship("source-123", "target-456", rel)
    
    assert result["source_type"] == "API"
    
    args, _ = mock_graph_manager.execute_write_query.call_args
    query = args[0]
    assert "MATCH (a {id: $source_id})" in query
    assert "MATCH (b {id: $target_id})" in query
    assert "MERGE (a)-[r:DummyRelationship]->(b)" in query
    
    params = args[1]
    assert params["source_id"] == "source-123"
    assert params["target_id"] == "target-456"

@patch('graph.builder.graph_manager')
def test_merge_relationship_no_records(mock_graph_manager, builder):
    mock_graph_manager.execute_write_query.return_value = []
    
    rel = DummyRelationship(source_type="API", generated_at="2026-07-11")
    with pytest.raises(GraphBuilderError, match="Missing source \\(source-123\\) or target"):
        builder.merge_relationship("source-123", "target-456", rel)
