from sqlalchemy import text
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Response, status

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.job import ProcessingJob
from app.schemas.auth import UserContext
from app.schemas.document import (
    CompleteUploadRequest,
    DocumentRead,
    DownloadUrlResponse,
    HealthResponse,
    InitUploadRequest,
    InitUploadResponse,
    ProcessingJobRead,
)
from app.services.auth import get_current_user
from app.services.documents import complete_upload, delete_document, get_document, get_download_url, init_upload, list_documents

router = APIRouter()


def _latest_job(document) -> ProcessingJob | None:
    if not document.processing_jobs:
        return None
    return max(document.processing_jobs, key=lambda job: job.created_at)


def _serialize_job(job: ProcessingJob | None) -> ProcessingJobRead | None:
    if job is None:
        return None
    return ProcessingJobRead(
        id=str(job.id),
        status=job.status.value,
        error_message=job.error_message,
        result_payload=job.result_payload,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
    )


def _serialize_document(document) -> DocumentRead:
    latest_job = _latest_job(document)
    return DocumentRead(
        id=str(document.id),
        filename=document.filename,
        content_type=document.content_type,
        size_bytes=document.size_bytes,
        status=document.status.value,
        s3_bucket=document.s3_bucket,
        s3_key=document.s3_key,
        error_message=document.error_message,
        extracted_text=document.extracted_text,
        result_payload=document.result_payload,
        upload_completed_at=document.upload_completed_at,
        processed_at=document.processed_at,
        created_at=document.created_at,
        updated_at=document.updated_at,
        latest_job=_serialize_job(latest_job),
    )


@router.get("/health", response_model=HealthResponse)
def healthcheck(db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse(
        status="ok",
        database="ok",
        queue="configured" if settings.aws_sqs_queue_url else "missing",
    )


@router.post("/documents/init-upload", response_model=InitUploadResponse)
def create_upload(
    payload: InitUploadRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    user: UserContext = Depends(get_current_user),
) -> InitUploadResponse:
    document, upload_url = init_upload(db, settings, user, payload)
    return InitUploadResponse(
        document_id=str(document.id),
        upload_url=upload_url,
        s3_bucket=document.s3_bucket,
        s3_key=document.s3_key,
        expires_in=settings.presigned_url_ttl_seconds,
        status=document.status.value,
    )


@router.post("/documents/complete-upload", response_model=DocumentRead)
def finalize_upload(
    payload: CompleteUploadRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    user: UserContext = Depends(get_current_user),
) -> DocumentRead:
    document = complete_upload(db, settings, user, payload)
    db.refresh(document)
    return _serialize_document(document)


@router.get("/documents", response_model=list[DocumentRead])
def get_documents(
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_current_user),
) -> list[DocumentRead]:
    documents = list_documents(db, user)
    return [_serialize_document(document) for document in documents]


@router.get("/documents/{document_id}", response_model=DocumentRead)
def get_document_by_id(
    document_id: str,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_current_user),
) -> DocumentRead:
    document = get_document(db, user, document_id)
    return _serialize_document(document)


@router.get("/documents/{document_id}/download-url", response_model=DownloadUrlResponse)
def create_download_url(
    document_id: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    user: UserContext = Depends(get_current_user),
) -> DownloadUrlResponse:
    document = get_document(db, user, document_id)
    download_url = get_download_url(settings, document)
    return DownloadUrlResponse(
        document_id=str(document.id),
        download_url=download_url,
        expires_in=settings.presigned_url_ttl_seconds,
    )


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    document_id: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    user: UserContext = Depends(get_current_user),
) -> Response:
    delete_document(db, settings, user, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

