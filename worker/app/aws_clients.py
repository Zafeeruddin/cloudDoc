import boto3
from botocore.client import Config

from app.config import Settings


def get_s3_client(settings: Settings):
    kwargs = {
        "service_name": "s3",
        "region_name": settings.aws_region,
        "endpoint_url": settings.aws_s3_endpoint_url,
        "config": Config(signature_version="s3v4", s3={"addressing_style": "path" if settings.aws_s3_force_path_style else "auto"}),
    }
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    return boto3.client(**kwargs)


def get_sqs_client(settings: Settings):
    kwargs = {
        "service_name": "sqs",
        "region_name": settings.aws_region,
        "endpoint_url": settings.aws_sqs_endpoint_url,
    }
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    return boto3.client(**kwargs)

