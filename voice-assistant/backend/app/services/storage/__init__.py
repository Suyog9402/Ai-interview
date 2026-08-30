from app.services.storage.base import BaseStorage
from app.services.storage.local import LocalStorage
from app.core.config import settings
from app.services.interfaces.storage import StorageInterface
from app.core.exceptions import StorageException

# Cloud storage implementations (stubs for now)
# from app.services.storage.azure_blob import AzureBlobStorage
# from app.services.storage.aws_s3 import AWSS3Storage
# from app.services.storage.gcp_storage import GCPStorage


def get_storage() -> StorageInterface:
    """
    Factory function to get the appropriate storage provider based on config.
    """
    provider = settings.storage_provider.lower()
    
    if provider == "local":
        return LocalStorage(base_path=settings.storage_local_path)
    elif provider == "azure":
        # return AzureBlobStorage(
        #     account_name=settings.storage_azure_account_name,
        #     account_key=settings.storage_azure_account_key,
        #     container=settings.storage_azure_container
        # )
        raise StorageException("Azure Blob Storage not yet implemented")
    elif provider == "aws":
        # return AWSS3Storage(
        #     access_key=settings.storage_aws_access_key,
        #     secret_key=settings.storage_aws_secret_key,
        #     bucket=settings.storage_aws_bucket,
        #     region=settings.storage_aws_region
        # )
        raise StorageException("AWS S3 Storage not yet implemented")
    elif provider == "gcp":
        # return GCPStorage(
        #     bucket=settings.storage_gcp_bucket,
        #     credentials_path=settings.storage_gcp_credentials_path
        # )
        raise StorageException("GCP Cloud Storage not yet implemented")
    else:
        raise StorageException(f"Unknown storage provider: {provider}")

__all__ = ["get_storage", "BaseStorage", "LocalStorage"]

