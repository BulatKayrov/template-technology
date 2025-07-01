# Тут примеры как использовать те или иные технологии

## S3 хранилище

1. Создаем докер сервис MinIO
2. Устанавливаем либо boto3 либо aiobotocore
3. Писем сервисы
```dockerfile
  minio:
    image: minio/minio:latest
    container_name: minio
    restart: unless-stopped
    ports:
      - "${MINIO_API_PORT}:9000"  # API порт
      - "${MINIO_CONSOLE_PORT}:9001"  # WebUI порт
    volumes:
      - ./volumes/s3-storage:/data
      - ./volumes/s3-config:/root/.minio
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
      - MINIO_BROWSER_REDIRECT_URL=http://${MINIO_DOMAIN}:${MINIO_CONSOLE_PORT}
      - MINIO_DOMAIN=${MINIO_DOMAIN}
    command: server /data --console-address ":9001"
    healthcheck:
      test: [ "CMD", "curl", "-f", "http://localhost:9000/minio/health/live" ]
      interval: 30s
      timeout: 20s
      retries: 3
```

### Синхронный вариант

```python
from pprint import pprint

import boto3
from fastapi import UploadFile

from core.conf import settings


class S3Service:

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        endpoint_url: str,
        bucket_name: str = None,
    ):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
        )
        self.bucket_name = bucket_name

    def upload_file(self, file: UploadFile, bucket_name: str = None):
        if bucket_name is None:
            res = self.client.put_object(
                Body=file.file, Bucket=self.bucket_name, Key=file.filename
            )
            pprint(res)
            return
        self.client.put_object(Body=file.file, Bucket=bucket_name, Key=file.filename)

    def all_methods(self):
        pprint(self.client.__dir__())

    def create_bucket(self, bucket_name: str):
        return self.client.create_bucket(Bucket=bucket_name)

    def delete_bucket(self, bucket_name: str = None):
        if bucket_name:
            self.client.delete_bucket(Bucket=bucket_name)
            return
        self.client.delete_bucket(Bucket=self.bucket_name)

    def list_buckets(self):
        res = self.client.list_buckets()
        return [_["Name"] for _ in res["Buckets"]]

    def delete_all_buckets(self):
        pass

    def get_object(self, object_name: str, bucket_name: str = None):
        if bucket_name:
            res = self.client.get_object(Bucket=bucket_name, Key=object_name)
            return res
        res = self.client.get_object(Bucket=self.bucket_name, Key=object_name)
        return res


sync_aws_service = S3Service(
    aws_access_key_id=settings.MINIO_ROOT_USER,
    aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
    endpoint_url=settings.s3_endpoint,
    bucket_name="yoyo",
)
```
### Асинхронный вариант

```python
from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from fastapi import UploadFile

from core.conf import settings


class S3Service:

    def __init__(self, access_key, secret_key, endpoint):
        self.config = {
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key,
            'endpoint_url': endpoint,
        }
        self.session = get_session()

    @asynccontextmanager
    async def _client(self):
        async with self.session.create_client('s3', **self.config) as c:
            yield c

    async def upload_file(self, bucket_name: str, file: UploadFile):
        """Сохраняем файл в S3, если бакета (папки) нету, то создаем ее"""
        async with self._client() as s3:
            result = await self.get_buckets()
            if bucket_name in [bucket['Name'] for bucket in result['Buckets']]:
                await s3.put_object(Bucket=bucket_name, Key=file.filename, Body=file.file)
                return
            await s3.create_bucket(Bucket=bucket_name)
            await s3.put_object(Bucket=bucket_name, Key=file.filename, Body=file.file)

    async def download_file(self, bucket_name: str, filename: str):
        """Получаем обьект из S3"""
        async with self._client() as s3:
            return await s3.get_object(Bucket=bucket_name, Key=filename)

    async def delete_file(self, bucket_name: str, filename: str):
        """Удаляем обьект из S3"""
        async with self._client() as s3:
            return await s3.delete_object(Bucket=bucket_name, Key=filename)

    async def create_bucket(self, bucket_name: str):
        """Создаем бакет в S3"""
        async with self._client() as s3:
            await s3.create_bucket(Bucket=bucket_name)

    async def get_buckets(self):
        """Получаем все бакеты из S3"""
        async with self._client() as s3:
            return await s3.list_buckets()

    async def delete_bucket(self, bucket_name: str):
        """Удаляем бакет по имени из S3"""
        async with self._client() as s3:
            return await s3.delete_bucket(Bucket=bucket_name)

    async def delete_all_buckets(self):
        """удаляем все бакеты из S3"""
        result = await self.get_buckets()
        if list_buckets := [bucket['Name'] for bucket in result['Buckets']]:
            for item in list_buckets:
                await self.delete_bucket(item)
        return


aws_service = S3Service(
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    endpoint=settings.s3_endpoint,
)

```