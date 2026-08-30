"""
AWS S3 Storage implementation (stub for future implementation)
"""
from app.services.storage.base import BaseStorage
from app.core.exceptions import StorageException


class AWSS3Storage(BaseStorage):
    """AWS S3 Storage implementation - to be implemented"""
    
    def __init__(self, access_key: str, secret_key: str, bucket: str, region: str):
        super().__init__()
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.region = region
        raise StorageException("AWS S3 Storage not yet implemented")
    
    async def upload_file(self, file_content, file_path: str, metadata=None) -> str:
        raise NotImplementedError("AWS S3 Storage not yet implemented")
    
    async def download_file(self, file_path: str) -> bytes:
        raise NotImplementedError("AWS S3 Storage not yet implemented")
    
    async def delete_file(self, file_path: str) -> bool:
        raise NotImplementedError("AWS S3 Storage not yet implemented")
    
    async def file_exists(self, file_path: str) -> bool:
        raise NotImplementedError("AWS S3 Storage not yet implemented")
    
    async def get_file_url(self, file_path: str, expires_in=None) -> str:
        raise NotImplementedError("AWS S3 Storage not yet implemented")
    
    async def list_files(self, prefix=None) -> list[str]:
        raise NotImplementedError("AWS S3 Storage not yet implemented")

