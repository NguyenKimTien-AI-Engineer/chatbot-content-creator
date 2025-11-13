import boto3
from loguru import logger

from configs import constant

AWS_DEFAULT_REGION = constant.AWS_DEFAULT_REGION

SUPPORT_FILE_TYPES = {
    "image/png": "png",
    "image/jpeg": ["jpg", "jpeg"],
}

AWS_BUCKET_NAME = constant.AWS_BUCKET_NAME

s3 = boto3.resource("s3")
bucket = s3.Bucket(AWS_BUCKET_NAME)


async def s3_upload(contents: bytes, key: str, mime_type: str):
    logger.info(f"Uploading {key} to s3")
    bucket.put_object(Key=key, Body=contents, ContentType=mime_type)
    file_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{key}"
    return file_url
