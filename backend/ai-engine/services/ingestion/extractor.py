import logging
from typing import Dict, Any, List
import datetime

from graph.schemas.nodes import CaseNode, PersonNode, NodeType
from graph.schemas.relationships import BaseRelationship, RelationshipType
from graph.builder import GraphBuilder

logger = logging.getLogger(__name__)

class CaseExtractor:
    """
    Service responsible for extracting nodes and relationships from 
    REST API JSON payloads and ingesting them into the graph.
    """
    
    def __init__(self, builder: GraphBuilder):
        self.builder = builder
        
    def process_case_payload(self, payload: Dict[str, Any]) -> None:
        """
        Parses a nested case dictionary, extracting all entities and their relationships.
        Expected format roughly aligns with the Django API serializers for CaseMaster.
        """
        try:
            # 1. Extract and Merge CaseNode
            case_id = str(payload.get("CaseMasterID", ""))
            case_node = CaseNode(
                id=f"CASE_{case_id}",
                source_system="DJANGO_API",
                created_at=datetime.datetime.utcnow().isoformat(),
                case_number=payload.get("CaseNo", ""),
                status=payload.get("CaseStatusName", "Unknown"),
                reported_date=payload.get("CrimeRegisteredDate", "")
            )
            self.builder.merge_node(case_node, label=NodeType.CASE.value)
            
            # 2. Extract and Merge Complainants
            for complainant in payload.get("Complainants", []):
                person_id = f"COMP_{complainant.get('ComplainantID')}"
                person_node = PersonNode(
                    id=person_id,
                    source_system="DJANGO_API",
                    created_at=datetime.datetime.utcnow().isoformat(),
                    age_group=str(complainant.get("AgeYear", ""))
                )
                self.builder.merge_node(person_node, label=NodeType.WITNESS.value) # Mapping complainant to general witness/person
                
                # Relationship: FILED_BY (Complainant -> Case)
                # Wait, usually a complainant files a case. Let's make it FILED_BY from Person to Case.
                rel = BaseRelationship(source_type="DJANGO_API", generated_at=datetime.datetime.utcnow().isoformat())
                self.builder.merge_relationship(person_id, case_node.id, rel, rel_type="FILED_BY")
                
            # 3. Extract and Merge Victims
            for victim in payload.get("Victims", []):
                person_id = f"VIC_{victim.get('VictimMasterID')}"
                person_node = PersonNode(
                    id=person_id,
                    source_system="DJANGO_API",
                    created_at=datetime.datetime.utcnow().isoformat(),
                    age_group=str(victim.get("AgeYear", ""))
                )
                self.builder.merge_node(person_node, label=NodeType.VICTIM.value)
                
                # Relationship: VICTIM_OF
                rel = BaseRelationship(source_type="DJANGO_API", generated_at=datetime.datetime.utcnow().isoformat())
                self.builder.merge_relationship(person_id, case_node.id, rel, rel_type=RelationshipType.VICTIM_OF.value)

            # 4. Extract and Merge Accused
            for accused in payload.get("Accused", []):
                person_id = f"ACC_{accused.get('AccusedMasterID')}"
                person_node = PersonNode(
                    id=person_id,
                    source_system="DJANGO_API",
                    created_at=datetime.datetime.utcnow().isoformat(),
                    age_group=str(accused.get("AgeYear", ""))
                )
                self.builder.merge_node(person_node, label=NodeType.ACCUSED.value)
                
                # Relationship: ACCUSED_IN
                rel = BaseRelationship(source_type="DJANGO_API", generated_at=datetime.datetime.utcnow().isoformat())
                self.builder.merge_relationship(person_id, case_node.id, rel, rel_type=RelationshipType.ACCUSED_IN.value)

            logger.info(f"Successfully processed case payload for CaseMasterID: {case_id}")
            
        except Exception as e:
            logger.error(f"Failed to process case payload: {payload.get('CaseMasterID')}", exc_info=True)
            raise
