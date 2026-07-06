from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.models import DocumentStatus


class InitUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=255)
    size_bytes: int = Field(gt=0)


class InitUploadResponse(BaseModel):
    document_id: str
    upload_url: str
    s3_bucket: str
    s3_key: str
    status: DocumentStatus
    expires_in: int


class CompleteUploadRequest(BaseModel):
    document_id: str


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    original_filename: str
    content_type: str
    size_bytes: int
    s3_bucket: str
    s3_key: str
    status: DocumentStatus
    extracted_text: str | None
    summary: str | None
    extracted_metadata: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class DownloadUrlResponse(BaseModel):
    document_id: str
    download_url: str
    expires_in: int


class MessageResponse(BaseModel):
    message: str
