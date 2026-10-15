import boto3
from app.core.config import settings

def create_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
    )
    

s3_client=create_s3_client()