from pprint import pprint

from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse

from applications.aws.services import async_aws_service

router = APIRouter(tags=["S3 Async"])


@router.post("/upload/{bucket_name}")
async def push_to_aws(bucket_name: str, file: UploadFile):
    await async_aws_service.upload_file(bucket_name=bucket_name, file=file)
    return {"file": file.filename}


@router.get("/download/")
async def get_from_aws(filename: str, bucket_name: str):
    """
    TODO пересмотреть
    :param filename:
    :param bucket_name:
    :return:
    """
    file = await async_aws_service.download_file(
        bucket_name=bucket_name, filename=filename
    )
    pprint(file)

    return StreamingResponse(
        content=file["Body"],
        media_type=file["ContentType"],
        headers={
            "Content-Disposition": f"attachment; filename={filename.split('/')[-1]}"
        },
    )


@router.delete("/delete/{filename}")
async def delete_from_aws(filename: str, bucket_name: str):
    file = await async_aws_service.delete_file(bucket_name, filename)
    print(file)
    return {"status": "success"}


@router.get("/list/buckets")
async def get_from_aws_list():
    result = await async_aws_service.get_buckets()
    return [bucket["Name"] for bucket in result["Buckets"]]


@router.get("/delete/buckets")
async def delete_one_buckets(bucket_name: str):
    await async_aws_service.delete_bucket(bucket_name)
    return {"status": "success"}


@router.get("/delete/all/buckets")
async def delete_one_buckets():
    await async_aws_service.delete_all_buckets()
    return {"status": "success"}
