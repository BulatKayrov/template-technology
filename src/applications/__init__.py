from fastapi import APIRouter

from .aws.views import router as aws_router
from .aws.views_sync_aws import router as aws_sync_router

router = APIRouter()
router.include_router(aws_router)
router.include_router(aws_sync_router)