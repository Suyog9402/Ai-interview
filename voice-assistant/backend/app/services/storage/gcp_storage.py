"""
GCP Cloud Storage implementation (stub for future implementation)
"""
from app.services.storage.base import BaseStorage
from app.core.exceptions import StorageException


class GCPStorage(BaseStorage):
    """GCP Cloud Storage implementation - to be implemented"""
    
    def __init__(self, bucket: str, credentials_path: str):
        super().__init__()
        self.bucket = bucket
        self.credentials_path = credentials_path
        raise StorageException("GCP Cloud Storage not yet implemented")
    
    async def upload_file(self, file_content, file_path: str, metadata=None) -> str:
        raise NotImplementedError("GCP Cloud Storage not yet implemented")
    
    async def download_file(self, file_path: str) -> bytes:
        raise NotImplementedError("GCP Cloud Storage not yet implemented")
    
    async def delete_file(self, file_path: str) -> bool:
        raise NotImplementedError("GCP Cloud Storage not yet implemented")
    
    async def file_exists(self, file_path: str) -> bool:
        raise NotImplementedError("GCP Cloud Storage not yet implemented")
    
    async def get_file_url(self, file_path: str, expires_in=None) -> str:
        raise NotImplementedError("GCP Cloud Storage not yet implemented")
    
    async def list_files(self, prefix=None) -> list[str]:
        raise NotImplementedError("GCP Cloud Storage not yet implemented")

