from __future__ import annotations

import json
import logging
import os
import re
import uuid
from datetime import UTC, datetime

from botocore.exceptions import ClientError
from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings
from app.models.document import Document, DocumentStatus
from app.models.job import ProcessingJob, ProcessingJobStatus
from app.schemas.auth import UserContext
from app.schemas.document import CompleteUploadRequest, InitUploadRequest
from app.services.queue import get_sqs_client
from app.services.storage import get_s3_client

logger = logging.getLogger(__name__)

SAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    basename = os.path.basename(filename.strip())
    sanitized = SAFE_FILENAME_PATTERN.sub("-", basename).strip("-.")
    if not sanitized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")
    return sanitized[:255]


def validate_upload_request(payload: InitUploadRequest, settings: Settings) -> None:
    if payload.content_type not in settings.allowed_content_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported content type")
    if payload.size_bytes > settings.max_upload_size_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds maximum allowed size")


def init_upload(db: Session, settings: Settings, user: UserContext, payload: InitUploadRequest) -> tuple[Document, str]:
    validate_upload_request(payload, settings)
    safe_filename = sanitize_filename(payload.filename)
    document = Document(
        user_id=uuid.UUID(user.user_id),
        filename=safe_filename,
        content_type=payload.content_type,
        size_bytes=payload.size_bytes,
        s3_bucket=settings.aws_s3_bucket,
        s3_key=f"documents/{user.user_id}/{uuid.uuid4()}/{safe_filename}",
        status=DocumentStatus.UPLOADED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    public_client = get_s3_client(settings, public=True)
    upload_url = public_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": document.s3_bucket,
            "Key": document.s3_key,
            "ContentType": document.content_type,
        },
        ExpiresIn=settings.presigned_url_ttl_seconds,
    )
    return document, upload_url


def complete_upload(db: Session, settings: Settings, user: UserContext, payload: CompleteUploadRequest) -> Document:
    document = _get_document_for_user(db, user.user_id, payload.document_id)
    s3_client = get_s3_client(settings)
    try:
        s3_client.head_object(Bucket=document.s3_bucket, Key=document.s3_key)
    except ClientError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded object not found in storage") from exc

    active_job = db.scalar(
        select(ProcessingJob)
        .where(
            ProcessingJob.document_id == document.id,
            ProcessingJob.status.in_([ProcessingJobStatus.QUEUED, ProcessingJobStatus.PROCESSING]),
        )
        .order_by(desc(ProcessingJob.created_at))
    )
    if active_job is not None:
        return document

    document.upload_completed_at = datetime.now(UTC)
    document.error_message = None
    job = ProcessingJob(document_id=document.id, status=ProcessingJobStatus.QUEUED)
    db.add(job)
    db.flush()

    queue_message = {
        "document_id": str(document.id),
        "user_id": user.user_id,
        "s3_bucket": document.s3_bucket,
        "s3_key": document.s3_key,
        "content_type": document.content_type,
        "job_id": str(job.id),
    }
    sqs_client = get_sqs_client(settings)
    response = sqs_client.send_message(QueueUrl=settings.aws_sqs_queue_url, MessageBody=json.dumps(queue_message))
    job.message_id = response.get("MessageId")
    db.commit()
    db.refresh(document)
    return document


def list_documents(db: Session, user: UserContext) -> list[Document]:
    return list(
        db.scalars(
            select(Document)
            .options(selectinload(Document.processing_jobs))
            .where(Document.user_id == uuid.UUID(user.user_id))
            .order_by(desc(Document.created_at))
        )
    )


def get_document(db: Session, user: UserContext, document_id: str) -> Document:
    return _get_document_for_user(db, user.user_id, document_id)


def get_download_url(settings: Settings, document: Document) -> str:
    if document.status != DocumentStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document is not ready for download")
    public_client = get_s3_client(settings, public=True)
    return public_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": document.s3_bucket, "Key": document.s3_key},
        ExpiresIn=settings.presigned_url_ttl_seconds,
    )


def delete_document(db: Session, settings: Settings, user: UserContext, document_id: str) -> None:
    document = _get_document_for_user(db, user.user_id, document_id)
    try:
        get_s3_client(settings).delete_object(Bucket=document.s3_bucket, Key=document.s3_key)
    except ClientError:
        logger.warning("failed_to_delete_s3_object", extra={"document_id": str(document.id), "s3_key": document.s3_key})
    db.delete(document)
    db.commit()


def _get_document_for_user(db: Session, user_id: str, document_id: str) -> Document:
    try:
        parsed_id = uuid.UUID(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found") from exc

    document = db.scalar(
        select(Document)
        .options(selectinload(Document.processing_jobs))
        .where(Document.id == parsed_id, Document.user_id == uuid.UUID(user_id))
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document
