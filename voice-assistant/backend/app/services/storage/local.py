import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional, Dict, Any
from app.services.storage.base import BaseStorage
from app.core.exceptions import StorageException


class LocalStorage(BaseStorage):
    """Local file system storage implementation"""
    
    def __init__(self, base_path: str = "./storage"):
        """
        Initialize local storage.
        
        Args:
            base_path: Base directory for storage
        """
        super().__init__()
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(
        self,
        file_content: BinaryIO,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload file to local storage.
        
        Args:
            file_content: File-like object to upload
            file_path: Relative path within storage
            metadata: Optional metadata (stored as .meta file)
        
        Returns:
            Full path to stored file
        """
        try:
            full_path = self.base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'wb') as f:
                shutil.copyfileobj(file_content, f)
            
            # Store metadata if provided
            if metadata:
                meta_path = full_path.with_suffix(full_path.suffix + '.meta')
                import json
                with open(meta_path, 'w') as f:
                    json.dump(metadata, f)
            
            return str(full_path)
        except Exception as e:
            raise StorageException(f"Failed to upload file: {str(e)}")
    
    async def download_file(self, file_path: str) -> bytes:
        """
        Download file from local storage.
        
        Args:
            file_path: Relative path within storage
        
        Returns:
            File content as bytes
        """
        try:
            full_path = self.base_path / file_path
            if not full_path.exists():
                raise StorageException(f"File not found: {file_path}")
            
            with open(full_path, 'rb') as f:
                return f.read()
        except StorageException:
            raise
        except Exception as e:
            raise StorageException(f"Failed to download file: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file from local storage.
        
        Args:
            file_path: Relative path within storage
        
        Returns:
            True if deleted successfully
        """
        try:
            full_path = self.base_path / file_path
            if full_path.exists():
                full_path.unlink()
                
                # Also delete metadata file if exists
                meta_path = full_path.with_suffix(full_path.suffix + '.meta')
                if meta_path.exists():
                    meta_path.unlink()
                
                return True
            return False
        except Exception as e:
            raise StorageException(f"Failed to delete file: {str(e)}")
    
    async def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists in local storage.
        
        Args:
            file_path: Relative path within storage
        
        Returns:
            True if file exists
        """
        full_path = self.base_path / file_path
        return full_path.exists()
    
    async def get_file_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """
        Get HTTP URL for local file (served via FastAPI).
        
        Args:
            file_path: Relative path within storage
            expires_in: Ignored for local storage
        
        Returns:
            HTTP URL like: http://localhost:8001/api/v1/recordings/files/...
        """
        from app.core.config import settings
        
        # Get relative path
        full_path = self.base_path / file_path
        relative_path = full_path.relative_to(self.base_path)
        
        # Convert to URL path (use forward slashes)
        url_path = str(relative_path).replace(os.sep, '/')
        
        # Use server_url if set, otherwise use localhost
        if settings.server_url:
            base_url = settings.server_url.rstrip('/')
        else:
            base_url = f"http://localhost:{settings.port}"
        
        return f"{base_url}/api/v1/recordings/files/{url_path}"
    
    async def list_files(self, prefix: Optional[str] = None) -> list[str]:
        """
        List files in local storage.
        
        Args:
            prefix: Optional prefix to filter files
        
        Returns:
            List of relative file paths
        """
        try:
            files = []
            search_path = self.base_path
            if prefix:
                search_path = search_path / prefix
            
            if search_path.exists():
                for file_path in search_path.rglob('*'):
                    if file_path.is_file() and not file_path.name.endswith('.meta'):
                        relative_path = file_path.relative_to(self.base_path)
                        files.append(str(relative_path))
            
            return files
        except Exception as e:
            raise StorageException(f"Failed to list files: {str(e)}")

