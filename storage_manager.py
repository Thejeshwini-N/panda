import os
import boto3
from datetime import datetime, timedelta
from config import settings
from typing import Optional
import tempfile

class StorageManager:
    def __init__(self):
        self.storage_type = settings.storage_type
        self.local_storage_path = settings.local_storage_path
        
        # Initialize cloud storage clients if needed
        if self.storage_type == "s3":
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            self.bucket_name = settings.s3_bucket_name
    
    def store_dataset(self, local_file_path: str, request_id: int) -> str:
        """Store dataset and return the storage path."""
        if self.storage_type == "local":
            return self._store_local(local_file_path, request_id)
        elif self.storage_type == "s3":
            return self._store_s3(local_file_path, request_id)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def _store_local(self, local_file_path: str, request_id: int) -> str:
        """Store file locally."""
        # Ensure storage directory exists
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        # Create request-specific directory
        request_dir = os.path.join(self.local_storage_path, f"requests/{request_id}")
        os.makedirs(request_dir, exist_ok=True)
        
        # Destination path
        filename = os.path.basename(local_file_path)
        storage_path = os.path.join(request_dir, filename)
        
        # If source and destination are the same file, skip copying
        try:
            if os.path.exists(storage_path) and os.path.samefile(local_file_path, storage_path):
                return storage_path
        except Exception:
            if os.path.abspath(local_file_path) == os.path.abspath(storage_path):
                return storage_path
        
        # Copy file without metadata to avoid Windows locking issues
        import shutil
        shutil.copyfile(local_file_path, storage_path)
        
        return storage_path
    
    def _store_s3(self, local_file_path: str, request_id: int) -> str:
        """Store file in S3."""
        if not self.bucket_name:
            raise ValueError("S3 bucket name not configured")
        
        # Generate S3 key
        filename = os.path.basename(local_file_path)
        s3_key = f"requests/{request_id}/{filename}"
        
        # Upload file to S3
        self.s3_client.upload_file(local_file_path, self.bucket_name, s3_key)
        
        # Return S3 path
        return f"s3://{self.bucket_name}/{s3_key}"
    
    def get_download_url(self, storage_path: str) -> str:
        """Get download URL for stored file."""
        if self.storage_type == "local":
            return self._get_local_download_url(storage_path)
        elif self.storage_type == "s3":
            return self._get_s3_download_url(storage_path)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def _get_local_download_url(self, storage_path: str) -> str:
        """Get local file download URL."""
        # For local storage, map to direct file endpoint using request_id
        if os.path.exists(storage_path):
            try:
                parts = storage_path.replace("\\", "/").split("/")
                idx = parts.index("requests")
                req_id = int(parts[idx + 1])
                return f"/api/v1/storage/download/{req_id}/file"
            except Exception:
                return "/api/v1/storage/download/0/file"
        else:
            raise FileNotFoundError(f"File not found: {storage_path}")
    
    def _get_s3_download_url(self, storage_path: str) -> str:
        """Get S3 presigned download URL."""
        # Parse S3 path
        if not storage_path.startswith("s3://"):
            raise ValueError("Invalid S3 path format")
        
        path_parts = storage_path[5:].split("/", 1)
        bucket_name = path_parts[0]
        key = path_parts[1]
        
        # Generate presigned URL (expires in 1 hour)
        from datetime import datetime, timedelta
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=3600
            )
            return url
        except Exception as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def delete_dataset(self, storage_path: str) -> bool:
        """Delete stored dataset."""
        if self.storage_type == "local":
            return self._delete_local(storage_path)
        elif self.storage_type == "s3":
            return self._delete_s3(storage_path)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def _delete_local(self, storage_path: str) -> bool:
        """Delete local file."""
        try:
            if os.path.exists(storage_path):
                os.remove(storage_path)
                return True
            return False
        except Exception:
            return False
    
    def _delete_s3(self, storage_path: str) -> bool:
        """Delete S3 file."""
        try:
            if not storage_path.startswith("s3://"):
                return False
            
            path_parts = storage_path[5:].split("/", 1)
            bucket_name = path_parts[0]
            key = path_parts[1]
            
            self.s3_client.delete_object(Bucket=bucket_name, Key=key)
            return True
        except Exception:
            return False
    
    def file_exists(self, storage_path: str) -> bool:
        """Check if file exists in storage."""
        if self.storage_type == "local":
            return os.path.exists(storage_path)
        elif self.storage_type == "s3":
            try:
                if not storage_path.startswith("s3://"):
                    return False
                
                path_parts = storage_path[5:].split("/", 1)
                bucket_name = path_parts[0]
                key = path_parts[1]
                
                self.s3_client.head_object(Bucket=bucket_name, Key=key)
                return True
            except Exception:
                return False
        else:
            return False
