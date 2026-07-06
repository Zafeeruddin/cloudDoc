from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from botocore.exceptions import ClientError
from sqlalchemy import desc, select

from app.aws_clients import get_s3_client, get_sqs_client
from app.config import get_settings
from app.db import SessionLocal
from app.models import Document, DocumentStatus, ProcessingJob, ProcessingJobStatus
from app.processor import extract_text_and_metadata

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("docops-worker")
settings = get_settings()
s3_client = get_s3_client(settings)
sqs_client = get_sqs_client(settings)


def main() -> None:
    start_health_server()
    logger.info("worker_started")
    while True:
        messages = poll_messages()
        if not messages:
            continue
        for message in messages:
            handle_message(message)


def poll_messages() -> list[dict]:
    response = sqs_client.receive_message(
        QueueUrl=settings.aws_sqs_queue_url,
        MaxNumberOfMessages=settings.worker_poll_batch_size,
        WaitTimeSeconds=settings.worker_poll_wait_seconds,
        VisibilityTimeout=settings.worker_visibility_timeout,
    )
    return response.get("Messages", [])


def handle_message(message: dict) -> None:
    receipt_handle = message["ReceiptHandle"]
    try:
        payload = json.loads(message["Body"])
        process_payload(payload)
    except Exception as exc:  # noqa: BLE001
        logger.exception("message_processing_failed", extra={"message_id": message.get("MessageId")})
        try:
            mark_failed_from_message(message, str(exc))
        finally:
            delete_message(receipt_handle)
        return

    delete_message(receipt_handle)


def process_payload(payload: dict) -> None:
    document_id = uuid.UUID(payload["document_id"])
    job_id = uuid.UUID(payload["job_id"]) if payload.get("job_id") else None
    with SessionLocal() as db:
        document = db.get(Document, document_id)
        if document is None:
            logger.warning("document_missing", extra={"document_id": str(document_id)})
            return

        job = _resolve_job(db, document_id, job_id)
        if job is None:
            logger.warning("job_missing", extra={"document_id": str(document_id), "job_id": str(job_id) if job_id else None})
            return

        now = datetime.now(UTC)
        job.status = ProcessingJobStatus.PROCESSING
        job.started_at = now
        document.status = DocumentStatus.PROCESSING
        document.error_message = None
        db.commit()

        try:
            content = s3_client.get_object(Bucket=payload["s3_bucket"], Key=payload["s3_key"])["Body"].read()
            extracted_text, metadata = extract_text_and_metadata(content, document.filename, payload["content_type"])
            metadata["s3_key"] = document.s3_key
            metadata["processed_at"] = now.isoformat()
            job.status = ProcessingJobStatus.COMPLETED
            job.completed_at = datetime.now(UTC)
            job.result_payload = metadata
            document.status = DocumentStatus.COMPLETED
            document.extracted_text = extracted_text
            document.result_payload = metadata
            document.processed_at = datetime.now(UTC)
            document.error_message = None
            db.commit()
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            logger.exception("document_processing_failed", extra={"document_id": str(document_id)})
            _mark_failed(db, document_id, job.id, str(exc))


def mark_failed_from_message(message: dict, error_message: str) -> None:
    try:
        payload = json.loads(message["Body"])
    except (KeyError, json.JSONDecodeError):
        return
    document_id = payload.get("document_id")
    job_id = payload.get("job_id")
    if not document_id or not job_id:
        return
    with SessionLocal() as db:
        _mark_failed(db, uuid.UUID(document_id), uuid.UUID(job_id), error_message)


def _mark_failed(db, document_id: uuid.UUID, job_id: uuid.UUID, error_message: str) -> None:
    document = db.get(Document, document_id)
    job = db.get(ProcessingJob, job_id)
    if document is None or job is None:
        return
    job.status = ProcessingJobStatus.FAILED
    job.error_message = error_message[:2000]
    job.completed_at = datetime.now(UTC)
    document.status = DocumentStatus.FAILED
    document.error_message = error_message[:2000]
    document.processed_at = datetime.now(UTC)
    db.commit()


def _resolve_job(db, document_id: uuid.UUID, job_id: uuid.UUID | None) -> ProcessingJob | None:
    if job_id:
        job = db.get(ProcessingJob, job_id)
        if job is not None:
            return job
    return db.scalar(
        select(ProcessingJob)
        .where(ProcessingJob.document_id == document_id)
        .order_by(desc(ProcessingJob.created_at))
    )


def delete_message(receipt_handle: str) -> None:
    try:
        sqs_client.delete_message(QueueUrl=settings.aws_sqs_queue_url, ReceiptHandle=receipt_handle)
    except ClientError:
        logger.exception("delete_message_failed")
        time.sleep(1)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = b'{"status":"ok"}'
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def start_health_server() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", settings.worker_health_port), HealthHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()


if __name__ == "__main__":
    main()
