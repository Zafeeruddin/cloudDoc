import json

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import get_settings

settings = get_settings()


def _aws_client(service_name: str, endpoint_url: str | None = None):
    return boto3.client(
        service_name,
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        endpoint_url=endpoint_url,
        config=Config(s3={"addressing_style": "path" if settings.s3_force_path_style else "virtual"}),
    )


def get_s3_client():
    return _aws_client("s3", settings.s3_endpoint_url)


def get_presign_s3_client():
    return _aws_client("s3", settings.s3_public_endpoint_url or settings.s3_endpoint_url)


def get_sqs_client():
    return _aws_client("sqs", settings.sqs_endpoint_url)


def generate_upload_url(bucket: str, key: str, content_type: str) -> str:
    client = get_presign_s3_client()
    return client.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": bucket, "Key": key, "ContentType": content_type},
        ExpiresIn=settings.s3_presign_expiration_seconds,
    )


def generate_download_url(bucket: str, key: str) -> str:
    client = get_presign_s3_client()
    return client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=settings.s3_download_expiration_seconds,
    )


def verify_object_exists(bucket: str, key: str) -> None:
    try:
        get_s3_client().head_object(Bucket=bucket, Key=key)
    except ClientError as exc:
        raise ValueError(f"S3 object not found for key {key}") from exc


def delete_object_if_exists(bucket: str, key: str) -> None:
    try:
        get_s3_client().delete_object(Bucket=bucket, Key=key)
    except ClientError:
        return


def send_processing_message(payload: dict) -> str:
    response = get_sqs_client().send_message(
        QueueUrl=settings.sqs_queue_url,
        MessageBody=json.dumps(payload),
    )
    return response["MessageId"]
