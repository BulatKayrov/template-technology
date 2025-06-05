from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from fastapi import UploadFile

from conf import settings


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
