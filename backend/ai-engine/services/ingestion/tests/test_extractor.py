import pytest
from unittest.mock import MagicMock, call

from services.ingestion.extractor import CaseExtractor

@pytest.fixture
def mock_builder():
    builder = MagicMock()
    return builder

@pytest.fixture
def extractor(mock_builder):
    return CaseExtractor(builder=mock_builder)

def test_process_case_payload_success(extractor, mock_builder):
    payload = {
        "CaseMasterID": 101,
        "CaseNo": "FIR-2026-001",
        "CaseStatusName": "Open",
        "CrimeRegisteredDate": "2026-07-10",
        "Complainants": [
            {"ComplainantID": 1, "AgeYear": 40}
        ],
        "Victims": [
            {"VictimMasterID": 2, "AgeYear": 35}
        ],
        "Accused": [
            {"AccusedMasterID": 3, "AgeYear": 25}
        ]
    }
    
    extractor.process_case_payload(payload)
    
    # Assert nodes were merged (1 case + 1 comp + 1 vic + 1 acc)
    assert mock_builder.merge_node.call_count == 4
    
    # Validate Case Node
    case_call = mock_builder.merge_node.mock_calls[0]
    case_node = case_call.args[0]
    label = case_call.kwargs.get("label")
    assert case_node.id == "CASE_101"
    assert case_node.case_number == "FIR-2026-001"
    assert label == "Case"
    
    # Assert relationships were merged (1 comp + 1 vic + 1 acc)
    assert mock_builder.merge_relationship.call_count == 3
    
    # Extract relationships
    rel_calls = mock_builder.merge_relationship.mock_calls
    rel_types = [call.kwargs.get("rel_type") for call in rel_calls]
    
    assert "FILED_BY" in rel_types
    assert "VICTIM_OF" in rel_types
    assert "ACCUSED_IN" in rel_types

def test_process_case_payload_empty(extractor, mock_builder):
    payload = {
        "CaseMasterID": 999
    }
    
    extractor.process_case_payload(payload)
    
    # Only the case node should be merged
    assert mock_builder.merge_node.call_count == 1
    assert mock_builder.merge_relationship.call_count == 0
