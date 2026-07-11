from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmbeddingDocument:
    doc_id: str
    text: str


class EmbeddingPipeline:
    """
    Placeholder embedding pipeline.
    Integrate provider SDKs later through this boundary.
    """

    async def embed_documents(self, docs: list[EmbeddingDocument]) -> list[list[float]]:
        # Deterministic zero vectors to keep API shape stable until vector provider integration.
        return [[0.0] * 8 for _ in docs]
