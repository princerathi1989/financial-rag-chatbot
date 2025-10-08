"""Core configuration and settings for the financial multi-agent chatbot."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key for LLM and embeddings")
    openai_model: str = Field("gpt-4-turbo-preview", description="OpenAI model for chat completions")
    openai_embedding_model: str = Field("text-embedding-3-small", description="OpenAI model for embeddings")
    
    # LangSmith Configuration (Optional)
    langsmith_api_key: Optional[str] = Field(None, description="LangSmith API key for tracing")
    langsmith_project: str = Field("financial-chatbot", description="LangSmith project name")
    langsmith_endpoint: str = Field("https://api.smith.langchain.com", description="LangSmith API endpoint")
    langchain_tracing_v2: Optional[str] = Field(None, description="Enable LangChain tracing v2")
    
    _storage_base_dir: Path = Path(__file__).resolve().parents[1] / "storage"
    chroma_persist_directory: str = Field(
        default_factory=lambda: str((Path(__file__).resolve().parents[1] / "storage" / "chroma_db").resolve()),
        description="Chroma vector store persistence directory"
    )
    upload_directory: str = Field(
        default_factory=lambda: str((Path(__file__).resolve().parents[1] / "storage" / "uploads").resolve()),
        description="Directory for uploaded files"
    )
    temp_directory: str = Field(
        default_factory=lambda: str((Path(__file__).resolve().parents[1] / "storage" / "temp").resolve()),
        description="Directory for temporary files"
    )
    
    # Production Cloud Configuration
    environment: str = Field("development", description="Environment: development, staging, production")
    
    vector_store_type: str = Field("pinecone", description="Vector store type: pinecone only")
    pinecone_api_key: Optional[str] = Field(None, description="Pinecone API key")
    pinecone_environment: str = Field("us-east-1", description="Pinecone environment/region")
    pinecone_index_name: str = Field("financial-documents", description="Pinecone index name")
    pinecone_metric: str = Field("cosine", description="Pinecone similarity metric")
    
    database_type: str = Field("memory", description="Database type: memory only for session-based processing")
    
    # Application Settings
    debug: bool = Field(False, description="Enable debug mode")
    log_level: str = Field("INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR")
    max_file_size_mb: int = Field(50, description="Maximum file size in MB")
    max_chunk_size: int = Field(1000, description="Maximum chunk size for text splitting")
    chunk_overlap: int = Field(200, description="Chunk overlap for text splitting")
    
    # Production Settings
    api_host: str = Field("0.0.0.0", description="API server host")
    api_port: int = Field(8000, description="API server port")
    workers: int = Field(1, description="Number of worker processes")
    reload: bool = Field(False, description="Enable auto-reload for development")
    
    # Agent Settings
    rag_top_k_results: int = Field(5, description="Number of top results for RAG retrieval")
    summary_max_length: int = Field(500, description="Maximum length for summaries")
    mcq_num_questions: int = Field(5, description="Number of MCQ questions to generate")
    analytics_confidence_threshold: float = Field(0.8, description="Confidence threshold for analytics")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()


def ensure_directories():
    """Ensure required directories exist."""
    os.makedirs(settings.upload_directory, exist_ok=True)
    os.makedirs(settings.temp_directory, exist_ok=True)
    if settings.vector_store_type.lower() == "chroma":
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)


def setup_langsmith():
    """Setup LangSmith tracing if API key is provided."""
    if settings.langsmith_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint
        print(f"LangSmith tracing enabled for project: {settings.langsmith_project}")
    else:
        print("LangSmith tracing disabled - no API key provided")

