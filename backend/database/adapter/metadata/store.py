import json
import uuid
import datetime
from typing import Dict, Any, Optional

try:
    import asyncpg
except ImportError:
    asyncpg = None

from ..config.config import settings
from ..utils.observability import get_logger

logger = get_logger(__name__)

class MetadataStore:
    """
    Singleton for persisting database adapter metadata directly into PostgreSQL.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetadataStore, cls).__new__(cls)
            cls._instance.pool = None
            cls._instance.is_initialized = False
        return cls._instance
        
    async def initialize(self):
        if self.is_initialized or not settings.POSTGRES_METADATA_URL:
            return
            
        if asyncpg is None:
            logger.warning("asyncpg is not installed. MetadataStore cannot persist to Postgres.")
            return
            
        try:
            self.pool = await asyncpg.create_pool(dsn=settings.POSTGRES_METADATA_URL)
            self.is_initialized = True
            logger.info("MetadataStore connected to PostgreSQL.")
        except Exception as e:
            logger.error(f"Failed to initialize MetadataStore pool: {e}")
            
    async def save_metadata(self, source_uri: str, source_type: str, metadata: Dict[str, Any], profile: Optional[Dict[str, Any]] = None):
        """
        Upserts the metadata and profile payload into adapter_metadata table.
        """
        if not self.is_initialized and settings.POSTGRES_METADATA_URL:
            await self.initialize()
            
        if not self.pool:
            return
            
        profile = profile or {}
        now = datetime.datetime.utcnow()
        record_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO adapter_metadata (id, created_at, updated_at, source_uri, source_type, metadata_payload, profile_payload)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (source_uri) DO UPDATE SET 
            updated_at = EXCLUDED.updated_at,
            metadata_payload = EXCLUDED.metadata_payload,
            profile_payload = EXCLUDED.profile_payload;
        """
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    query,
                    record_id,
                    now,
                    now,
                    source_uri,
                    source_type,
                    json.dumps(metadata),
                    json.dumps(profile)
                )
            logger.info(f"Metadata saved for source: {source_uri}")
        except Exception as e:
            logger.error(f"Failed to save metadata to Postgres: {e}")
            
    async def close(self):
        if self.pool:
            await self.pool.close()
            self.is_initialized = False
            logger.info("MetadataStore pool closed.")

metadata_store = MetadataStore()
