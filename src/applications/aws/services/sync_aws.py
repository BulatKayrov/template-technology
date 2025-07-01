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
