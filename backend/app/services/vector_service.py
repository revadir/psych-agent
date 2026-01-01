"""
Vector database service for managing DSM-5-TR embeddings.
"""

import os
from typing import List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings


class VectorService:
    """Service for interacting with the vector database."""

    def __init__(self):
        """Initialize the vector service with configuration from settings."""
        self.db_path = self._get_vector_db_path()
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Vector database not found at {self.db_path}")
            
        self.vector_db = Chroma(
            persist_directory=self.db_path, 
            embedding_function=self.embeddings
        )

    def _get_vector_db_path(self) -> str:
        """Get absolute path to vector database."""
        if settings.vector_db_path.startswith("./"):
            return os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "..", "..", 
                settings.vector_db_path.replace("./", "")
            ))
        return settings.vector_db_path

    def similarity_search(self, query: str, k: int = 3) -> List:
        """
        Perform similarity search on the vector database.

        Args:
            query: The search query
            k: Number of results to return

        Returns:
            List of relevant documents
        """
        return self.vector_db.similarity_search(query, k=k)

    def get_retriever(self, search_kwargs: Optional[dict] = None):
        """
        Get a retriever for the vector database.

        Args:
            search_kwargs: Additional search parameters

        Returns:
            A retriever instance
        """
        if search_kwargs is None:
            search_kwargs = {"k": 3}
        return self.vector_db.as_retriever(search_kwargs=search_kwargs)
