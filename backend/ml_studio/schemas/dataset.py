from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class DatasetPreviewRow(BaseModel):
    """A single preview row shown after upload."""
    prompt: str
    completion: str


class DatasetUploadResponse(BaseModel):
    """Returned after a successful dataset upload."""
    dataset_id: str
    tenant_id: str = "default"
    filename: str
    format: str  # "jsonl" or "csv"
    row_count: int
    file_size_bytes: int
    uploaded_at: datetime
    preview: list[DatasetPreviewRow] = Field(default_factory=list, max_length=5)
    warnings: list[str] = Field(default_factory=list)


class DatasetRecord(BaseModel):
    """Metadata for a stored dataset (from registry)."""
    dataset_id: str
    tenant_id: str = "default"
    filename: str
    format: str
    row_count: int
    file_size_bytes: int
    uploaded_at: datetime
    file_path: str


class DatasetListResponse(BaseModel):
    """Response for listing all datasets."""
    datasets: list[DatasetRecord]
    total: int


class DatasetDeleteResponse(BaseModel):
    """Response after deleting a dataset."""
    dataset_id: str
    deleted: bool
    message: str


class DatasetAugmentResponse(BaseModel):
    """Response after augmenting a dataset via synthetic generation."""
    source_dataset_id: str
    augmented_dataset_id: str
    tenant_id: str = "default"
    target_rows: int
    generated_rows: int
    message: str
