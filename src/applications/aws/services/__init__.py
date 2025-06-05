from .async_aws import aws_service as async_aws_service
from .sync_aws import sync_aws_service

__all__ = [
    async_aws_service,
    sync_aws_service,
]