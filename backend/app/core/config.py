from functools import lru_cache
from typing import List

import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "docops-backend"
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = "postgresql+psycopg://docops:docops@postgres:5432/docops"

    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "docops-documents-local"
    aws_s3_endpoint_url: str | None = None
    aws_s3_public_endpoint_url: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_s3_force_path_style: bool = False
    aws_sqs_queue_url: str = ""
    aws_sqs_endpoint_url: str | None = None

    presigned_url_ttl_seconds: int = 900
    max_upload_size_bytes: int = 10 * 1024 * 1024
    allowed_content_types: List[str] = Field(
        default_factory=lambda: [
            "application/pdf",
            "text/plain",
            "text/markdown",
            "text/csv",
            "application/json",
        ]
    )

    auth_trust_headers: bool = False
    dev_user_id: str = "00000000-0000-0000-0000-000000000001"
    dev_user_email: str = "demo@docops.local"
    dev_user_name: str = "Demo User"
    cors_allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("allowed_content_types", "cors_allowed_origins", mode="before")
    @classmethod
    def parse_list_env(cls, value):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
