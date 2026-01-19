"""
Configuration management using Pydantic Settings.
Loads configuration from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    environment: str = "development"
    secret_key: str = "dev-secret-key-change-in-production"
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        env="ALLOWED_ORIGINS"
    )

    # Database
    database_url: str = "sqlite:///./data/app.db"
    
    # Production database URL (Railway will set this)
    @property
    def production_database_url(self) -> str:
        import os
        return os.getenv("DATABASE_URL", self.database_url)
    
    vector_db_path: str = "./vector_db_hierarchical"
    
    # RAG Configuration
    use_rag: bool = True

    # LLM Configuration
    llm_provider: str = "groq"  # Changed from ollama to groq
    llm_api_key: str = ""
    llm_model: str = "mixtral-8x7b-32768"  # Groq model
    llm_temperature: float = 0.1
    
    # Groq API Key
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Pinecone Configuration
    pinecone_api_key: str = ""
    pinecone_environment: str = "gcp-starter"
    pinecone_index_name: str = "psych-agent"

    # Authentication
    jwt_secret_key: str = "dev-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Admin
    admin_email: str = "admin@example.com"

    # Server
    host: str = "0.0.0.0"
    port: int = 8001

    # Logging
    log_level: str = "INFO"
    
    # AssemblyAI Configuration
    assemblyai_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()
