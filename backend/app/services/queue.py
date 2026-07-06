import boto3

from app.core.config import Settings


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

