from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "docops-worker"
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://docops:docops@postgres:5432/docops"

    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "docops-documents-local"
    aws_s3_endpoint_url: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_s3_force_path_style: bool = False
    aws_sqs_queue_url: str = ""
    aws_sqs_endpoint_url: str | None = None

    worker_poll_wait_seconds: int = 20
    worker_poll_batch_size: int = 5
    worker_visibility_timeout: int = 60
    worker_health_port: int = 8081

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
