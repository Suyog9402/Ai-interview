"""
Azure Blob Storage implementation (stub for future implementation)
"""
from app.services.storage.base import BaseStorage
from app.core.exceptions import StorageException


class AzureBlobStorage(BaseStorage):
    """Azure Blob Storage implementation - to be implemented"""
    
    def __init__(self, account_name: str, account_key: str, container: str):
        super().__init__()
        self.account_name = account_name
        self.account_key = account_key
        self.container = container
        raise StorageException("Azure Blob Storage not yet implemented")
    
    async def upload_file(self, file_content, file_path: str, metadata=None) -> str:
        raise NotImplementedError("Azure Blob Storage not yet implemented")
    
    async def download_file(self, file_path: str) -> bytes:
        raise NotImplementedError("Azure Blob Storage not yet implemented")
    
    async def delete_file(self, file_path: str) -> bool:
        raise NotImplementedError("Azure Blob Storage not yet implemented")
    
    async def file_exists(self, file_path: str) -> bool:
        raise NotImplementedError("Azure Blob Storage not yet implemented")
    
    async def get_file_url(self, file_path: str, expires_in=None) -> str:
        raise NotImplementedError("Azure Blob Storage not yet implemented")
    
    async def list_files(self, prefix=None) -> list[str]:
        raise NotImplementedError("Azure Blob Storage not yet implemented")

