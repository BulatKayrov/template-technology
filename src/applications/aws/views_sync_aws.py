from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse

from applications.aws.services import sync_aws_service

router = APIRouter(tags=["S3 Sync"])


@router.post("/create/bucket")
async def create_bucket(bucket_name: str):
    return sync_aws_service.create_bucket(bucket_name=bucket_name)


@router.post("/delete/bucket")
async def delete_bucket(bucket_name: str):
    return sync_aws_service.delete_bucket(bucket_name=bucket_name)


@router.get("/buckets")
async def get_buckets():
    return sync_aws_service.list_buckets()


@router.get("/object/{file_name}")
async def get_objects(file_name: str):
    res = sync_aws_service.get_object(object_name=file_name)
    return StreamingResponse(
        content=res["Body"],
        media_type=res["ContentType"],
        headers={
            "Content-Disposition": f"attachment; filename={file_name.split('/')[-1]}",
        },
    )


@router.post("/save/file")
async def save_file(file: UploadFile):
    sync_aws_service.upload_file(file=file)
    return {"status": "ok"}
