"""
AWS S3 utility functions
"""

import boto3
from botocore.exceptions import ClientError
import os
from typing import Optional
import aiofiles
import asyncio

from app.core.config import settings


# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)


async def upload_file_to_s3(
    file_content: bytes = None,
    file_path: str = None,
    s3_key: str = None,
    content_type: str = "application/octet-stream"
) -> str:
    """
    Upload file to S3 bucket
    
    Args:
        file_content: File content as bytes (if uploading from memory)
        file_path: Path to local file (if uploading from disk)
        s3_key: S3 object key (path in bucket)
        content_type: MIME type of the file
        
    Returns:
        Public URL of the uploaded file
    """
    
    if not s3_key:
        raise ValueError("S3 key is required")
    
    if file_content:
        # Upload from memory
        try:
            s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type
            )
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")
    
    elif file_path:
        # Upload from file
        try:
            with open(file_path, 'rb') as file:
                s3_client.upload_fileobj(
                    file,
                    settings.S3_BUCKET_NAME,
                    s3_key,
                    ExtraArgs={'ContentType': content_type}
                )
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")
    else:
        raise ValueError("Either file_content or file_path must be provided")
    
    # Return public URL
    return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"


async def download_file_from_s3(s3_url: str, local_path: str) -> None:
    """
    Download file from S3
    
    Args:
        s3_url: S3 URL or key
        local_path: Path to save the file locally
    """
    
    # Extract key from URL if needed
    if s3_url.startswith("https://") or s3_url.startswith("http://"):
        # Parse S3 key from URL
        parts = s3_url.split(f"{settings.S3_BUCKET_NAME}.s3")
        if len(parts) > 1:
            s3_key = parts[1].split(".amazonaws.com/")[1]
        else:
            s3_key = s3_url.split("/")[-1]
    else:
        s3_key = s3_url
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download file
        s3_client.download_file(
            settings.S3_BUCKET_NAME,
            s3_key,
            local_path
        )
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            raise Exception(f"File not found in S3: {s3_key}")
        else:
            raise Exception(f"Failed to download from S3: {str(e)}")


def generate_presigned_url(s3_key: str, expiration: int = 3600) -> str:
    """
    Generate a presigned URL for S3 object
    
    Args:
        s3_key: S3 object key
        expiration: URL expiration time in seconds
        
    Returns:
        Presigned URL
    """
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=expiration
        )
    except ClientError as e:
        raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    return response


def delete_file_from_s3(s3_key: str) -> bool:
    """
    Delete file from S3
    
    Args:
        s3_key: S3 object key
        
    Returns:
        True if successful
    """
    try:
        s3_client.delete_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key
        )
        return True
    except ClientError as e:
        raise Exception(f"Failed to delete from S3: {str(e)}")


def list_files_in_s3(prefix: str = "", max_keys: int = 1000) -> list:
    """
    List files in S3 bucket with given prefix
    
    Args:
        prefix: Prefix to filter objects
        max_keys: Maximum number of keys to return
        
    Returns:
        List of S3 object keys
    """
    try:
        response = s3_client.list_objects_v2(
            Bucket=settings.S3_BUCKET_NAME,
            Prefix=prefix,
            MaxKeys=max_keys
        )
        
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        else:
            return []
    
    except ClientError as e:
        raise Exception(f"Failed to list S3 objects: {str(e)}")


async def upload_large_file_multipart(
    file_path: str,
    s3_key: str,
    content_type: str = "application/octet-stream",
    chunk_size: int = 5 * 1024 * 1024  # 5MB chunks
) -> str:
    """
    Upload large file using multipart upload
    
    Args:
        file_path: Path to local file
        s3_key: S3 object key
        content_type: MIME type
        chunk_size: Size of each chunk in bytes
        
    Returns:
        Public URL of uploaded file
    """
    
    # Initiate multipart upload
    response = s3_client.create_multipart_upload(
        Bucket=settings.S3_BUCKET_NAME,
        Key=s3_key,
        ContentType=content_type
    )
    
    upload_id = response['UploadId']
    parts = []
    
    try:
        # Upload file in chunks
        async with aiofiles.open(file_path, 'rb') as file:
            part_number = 1
            
            while True:
                data = await file.read(chunk_size)
                if not data:
                    break
                
                # Upload part
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: s3_client.upload_part(
                        Bucket=settings.S3_BUCKET_NAME,
                        Key=s3_key,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=data
                    )
                )
                
                parts.append({
                    'PartNumber': part_number,
                    'ETag': response['ETag']
                })
                
                part_number += 1
        
        # Complete multipart upload
        s3_client.complete_multipart_upload(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        
        return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
    
    except Exception as e:
        # Abort multipart upload on error
        s3_client.abort_multipart_upload(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            UploadId=upload_id
        )
        raise Exception(f"Failed to upload large file: {str(e)}")
