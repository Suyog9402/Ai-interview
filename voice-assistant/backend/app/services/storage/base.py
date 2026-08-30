from app.services.interfaces.storage import StorageInterface
from typing import BinaryIO, Optional, Dict, Any


class BaseStorage(StorageInterface):
    """Base class for storage implementations with common functionality"""
    
    def __init__(self):
        """Initialize base storage"""
        pass
    
    async def upload_file(
        self,
        file_content: BinaryIO,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def download_file(self, file_path: str) -> bytes:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def delete_file(self, file_path: str) -> bool:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def file_exists(self, file_path: str) -> bool:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def get_file_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """Base implementation - should be overridden"""
        raise NotImplementedError
    
    async def list_files(self, prefix: Optional[str] = None) -> list[str]:
        """Base implementation - should be overridden"""
        raise NotImplementedError

