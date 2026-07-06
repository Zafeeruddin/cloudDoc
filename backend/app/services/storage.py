from __future__ import annotations

from botocore.client import Config
import boto3

from app.core.config import Settings


def _client_kwargs(settings: Settings, public: bool = False) -> dict:
    endpoint_url = settings.aws_s3_public_endpoint_url if public else settings.aws_s3_endpoint_url
    kwargs = {
        "service_name": "s3",
        "region_name": settings.aws_region,
        "endpoint_url": endpoint_url,
        "config": Config(signature_version="s3v4", s3={"addressing_style": "path" if settings.aws_s3_force_path_style else "auto"}),
    }
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    return kwargs


def get_s3_client(settings: Settings, public: bool = False):
    return boto3.client(**_client_kwargs(settings, public=public))

