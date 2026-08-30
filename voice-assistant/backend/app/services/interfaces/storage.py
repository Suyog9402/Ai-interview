from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Dict, Any
from pathlib import Path


class StorageInterface(ABC):
    """Interface for storage providers (local, Azure, AWS, GCP)"""
    
    @abstractmethod
    async def upload_file(
        self,
        file_content: BinaryIO,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a file to storage.
        
        Args:
            file_content: File-like object to upload
            file_path: Destination path in storage
            metadata: Optional metadata to store with file
        
        Returns:
            Storage path/URL of uploaded file
        """
        pass
    
    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        """
        Download a file from storage.
        
        Args:
            file_path: Path to file in storage
        
        Returns:
            File content as bytes
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to file in storage
        
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            file_path: Path to file in storage
        
        Returns:
            True if file exists
        """
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """
        Get a URL to access the file (for cloud storage, can be signed URL).
        
        Args:
            file_path: Path to file in storage
            expires_in: Optional expiration time in seconds for signed URLs
        
        Returns:
            URL to access the file
        """
        pass
    
    @abstractmethod
    async def list_files(self, prefix: Optional[str] = None) -> list[str]:
        """
        List files in storage with optional prefix filter.
        
        Args:
            prefix: Optional prefix to filter files
        
        Returns:
            List of file paths
        """
        pass

