from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

from app.config import get_settings


class Storage:
    def put_bytes(self, key: str, payload: bytes, content_type: str) -> None:
        raise NotImplementedError

    def get_bytes(self, key: str) -> bytes:
        raise NotImplementedError

    def public_url(self, key: str) -> str:
        raise NotImplementedError


class LocalStorage(Storage):
    def __init__(self) -> None:
        settings = get_settings()
        self.root = Path(settings.data_dir) / "objects"
        self.root.mkdir(parents=True, exist_ok=True)
        self.base = settings.public_base_url.rstrip("/")

    def _path(self, key: str) -> Path:
        safe = Path(key)
        if safe.is_absolute() or ".." in safe.parts:
            raise ValueError("Invalid object key")
        path = (self.root / safe).resolve()
        if not str(path).startswith(str(self.root.resolve())):
            raise ValueError("Invalid object key")
        return path

    def put_bytes(self, key: str, payload: bytes, content_type: str) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

    def get_bytes(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def public_url(self, key: str) -> str:
        return f"{self.base}/media/{quote(key, safe='/')}"


class S3Storage(Storage):
    def __init__(self) -> None:
        import boto3
        from botocore.client import Config

        settings = get_settings()
        self.bucket = settings.s3_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=Config(signature_version="s3v4"),
        )
        existing = [b["Name"] for b in self.client.list_buckets().get("Buckets", [])]
        if self.bucket not in existing:
            self.client.create_bucket(Bucket=self.bucket)

    def put_bytes(self, key: str, payload: bytes, content_type: str) -> None:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=payload, ContentType=content_type)

    def get_bytes(self, key: str) -> bytes:
        return self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()

    def public_url(self, key: str) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=3600,
        )


@lru_cache
def get_storage() -> Storage:
    if get_settings().storage_backend.lower() == "s3":
        return S3Storage()
    return LocalStorage()
