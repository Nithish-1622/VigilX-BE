import pytest
from unittest.mock import patch, MagicMock

from ml.retrieval import CaseRetriever
from ml.exceptions import IndexingError, RetrievalError

@pytest.fixture
def retriever():
    return CaseRetriever(collection_name="test_cases")

@patch('ml.retrieval.vector_manager')
def test_index_case_success(mock_vector_manager, retriever):
    mock_client = MagicMock()
    mock_vector_manager.get_client.return_value = mock_client
    
    retriever.index_case(
        case_id="b7147a06-880c-45fb-a039-4ab5a33190be", 
        vector=[0.1, 0.2, 0.3], 
        payload={"status": "Open"}
    )
    
    mock_client.upsert.assert_called_once()
    args, kwargs = mock_client.upsert.call_args
    assert kwargs["collection_name"] == "test_cases"
    
    point = kwargs["points"][0]
    assert point.id == "b7147a06-880c-45fb-a039-4ab5a33190be"
    assert point.vector == [0.1, 0.2, 0.3]
    assert point.payload == {"status": "Open"}

@patch('ml.retrieval.vector_manager')
def test_index_case_failure(mock_vector_manager, retriever):
    mock_client = MagicMock()
    mock_client.upsert.side_effect = Exception("Connection lost")
    mock_vector_manager.get_client.return_value = mock_client
    
    with pytest.raises(IndexingError):
        retriever.index_case("id", [0.1], {})

@patch('ml.retrieval.vector_manager')
def test_search_similar_cases_success(mock_vector_manager, retriever):
    mock_client = MagicMock()
    
    # Mocking Qdrant ScoredPoint response
    mock_hit = MagicMock()
    mock_hit.id = "123"
    mock_hit.score = 0.95
    mock_hit.payload = {"type": "Robbery"}
    
    mock_client.search.return_value = [mock_hit]
    mock_vector_manager.get_client.return_value = mock_client
    
    results = retriever.search_similar_cases([0.1, 0.2, 0.3], limit=1)
    
    assert len(results) == 1
    assert results[0]["case_id"] == "123"
    assert results[0]["score"] == 0.95
    assert results[0]["payload"]["type"] == "Robbery"
    
    mock_client.search.assert_called_once_with(
        collection_name="test_cases",
        query_vector=[0.1, 0.2, 0.3],
        limit=1
    )

@patch('ml.retrieval.vector_manager')
def test_search_similar_cases_failure(mock_vector_manager, retriever):
    mock_client = MagicMock()
    mock_client.search.side_effect = Exception("Collection not found")
    mock_vector_manager.get_client.return_value = mock_client
    
    with pytest.raises(RetrievalError):
        retriever.search_similar_cases([0.1])
