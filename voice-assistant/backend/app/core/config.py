from pydantic_settings import BaseSettings
from typing import Optional, List, Union
import os

def _parse_origins(v: Union[str, List[str]]) -> List[str]:
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        return [x.strip() for x in v.split(",") if x.strip()]
    return []

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Interview Assistant API"
    version: str = "1.0.0"
    debug: bool = False
    port: int = 8001
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database settings - using PostgreSQL
    database_url: str
    
    # PostgreSQL specific settings
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 1800
    
    # CORS settings (set ALLOWED_ORIGINS env as comma-separated to override in production)
    allowed_origins: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://interview.eastus2.cloudapp.azure.com",
        "http://interview.eastus2.cloudapp.azure.com",
    ]

    @property
    def allowed_origins_list(self) -> List[str]:
        return _parse_origins(self.allowed_origins)
    
    # Email settings (for future email verification)
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Storage Configuration
    storage_provider: str = "local"  # local, azure, aws, gcp
    storage_local_path: str = "./storage"
    storage_azure_account_name: Optional[str] = None
    storage_azure_account_key: Optional[str] = None
    storage_azure_container: Optional[str] = None
    storage_aws_access_key: Optional[str] = None
    storage_aws_secret_key: Optional[str] = None
    storage_aws_bucket: Optional[str] = None
    storage_aws_region: Optional[str] = None
    storage_gcp_bucket: Optional[str] = None
    storage_gcp_credentials_path: Optional[str] = None
    
    # Transcription Configuration
    transcriber_provider: str = "openai_realtime"  # openai_realtime, azure_realtime
    openai_api_key: Optional[str] = None
    openai_realtime_model: str = "gpt-4o-realtime-preview"
    azure_speech_key: Optional[str] = None
    azure_speech_region: Optional[str] = None
    
    # Vector Store Configuration
    vector_store_provider: str = "chroma"  # chroma, weaviate, pgvector
    vector_store_path: str = "./db/vector_store"
    vector_store_collection_resumes: str = "resumes"
    vector_store_collection_transcripts: str = "transcripts"
    vector_store_collection_jds: str = "job_descriptions"
    weaviate_url: Optional[str] = None
    weaviate_api_key: Optional[str] = None
    pgvector_connection_string: Optional[str] = None
    
    # Extraction Configuration
    extraction_model: str = "gpt-4o"
    extraction_temperature: float = 0.1
    
    # Matching Configuration
    matching_default_threshold: float = 0.65
    matching_hard_filter_enabled: bool = True
    
    # RAG Configuration
    rag_retrieval_top_k: int = 10
    rag_rerank_top_k: int = 5
    rag_hybrid_alpha: float = 0.5  # 0=keyword, 1=vector
    
    # Memory Configuration
    memory_working_ttl_hours: int = 24
    memory_long_term_retention_days: int = 365
    
    # Server URL for generating file URLs (update in production)
    server_url: Optional[str] = None  # e.g., "http://yourdomain.com" or "https://yourserver.com"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings() 