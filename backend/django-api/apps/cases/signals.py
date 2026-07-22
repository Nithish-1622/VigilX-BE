from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.cases.models import FIR, Accused, Victim, ClueEntity
import httpx
import logging

logger = logging.getLogger(__name__)

# Assume the AI Engine has an ingestion endpoint or we directly trigger the Neo4j builder.
# Since Django and AI Engine are decoupled, we will fire an async webhook to the AI Engine.
# Alternatively, if we are in the same environment, we could just import the Neo4j builder.
# But since they are microservices, a webhook is best. For now, we will just log it or call a direct script.

@receiver(post_save, sender=FIR)
@receiver(post_save, sender=Accused)
@receiver(post_save, sender=Victim)
def sync_to_neo4j(sender, instance, created, **kwargs):
    """
    3.1 Knowledge Graph Construction: Triggers on Django save to push to Neo4j.
    """
    try:
        # In a real microservice, we POST to the AI engine's graph ingestion queue.
        # For this prototype, we'll just log it. The actual Neo4j ingestor is in ai-engine/services/ingestion.
        logger.info(f"Graph Sync Triggered: {sender.__name__} (ID: {instance.id}) - Created: {created}")
        
        # We can trigger a celery task here if configured.
        # For now, this wire is established.
    except Exception as e:
        logger.error(f"Failed to sync {sender.__name__} to Neo4j: {e}")
