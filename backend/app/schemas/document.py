from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class InitUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=512)
    content_type: str = Field(min_length=1, max_length=255)
    size_bytes: int = Field(gt=0)


class InitUploadResponse(BaseModel):
    document_id: str
    upload_url: str
    s3_bucket: str
    s3_key: str
    expires_in: int
    status: str


class CompleteUploadRequest(BaseModel):
    document_id: str


class DownloadUrlResponse(BaseModel):
    document_id: str
    download_url: str
    expires_in: int


class ProcessingJobRead(BaseModel):
    id: str
    status: str
    error_message: str | None = None
    result_payload: dict[str, Any] | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class DocumentRead(BaseModel):
    id: str
    filename: str
    content_type: str
    size_bytes: int
    status: str
    s3_bucket: str
    s3_key: str
    error_message: str | None = None
    extracted_text: str | None = None
    result_payload: dict[str, Any] | None = None
    upload_completed_at: datetime | None = None
    processed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    latest_job: ProcessingJobRead | None = None


class HealthResponse(BaseModel):
    status: str
    database: str
    queue: str

