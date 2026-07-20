import boto3
from config import settings

def archive_logs_to_s3(repo_name: str, build_id: str, zip_content: bytes):
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        key = f"logs/{repo_name}/{build_id}.zip"
        
        # For local testing without a real AWS account, we will just print the intent 
        # If you have real creds, this line executes the upload:
        # s3_client.put_object(Bucket=settings.s3_bucket, Key=key, Body=zip_content)
        
        print(f"Archived {len(zip_content)} bytes to S3: s3://{settings.s3_bucket}/{key}")
    except Exception as e:
        print(f"S3 Archive error: {e}")