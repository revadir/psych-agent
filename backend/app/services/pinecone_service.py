"""
Pinecone vector database service for cloud deployment.
"""

import os
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings


class PineconeService:
    """Service for interacting with Pinecone vector database."""
    
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY") or settings.pinecone_api_key
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
        
        self.pc = Pinecone(api_key=api_key)
        self.index_name = os.getenv("PINECONE_INDEX_NAME", settings.pinecone_index_name)
        
        # Initialize index
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)
    
    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists."""
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                print(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # Standard embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
        except Exception as e:
            print(f"Error ensuring index exists: {e}")
    
    def search_similar_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents in Pinecone using inference API."""
        try:
            print(f"Searching for: {query}")
            
            # Use Pinecone's inference API
            from pinecone import Pinecone
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            
            # Use multilingual-e5-large (1024 dimensions)
            embeddings_response = pc.inference.embed(
                model="multilingual-e5-large",
                inputs=[query],
                parameters={"input_type": "query", "truncate": "END"}
            )
            
            query_embedding = embeddings_response[0].values  # Full 1024 dimensions
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            documents = []
            for match in results.get('matches', []):
                doc = {
                    'score': match.get('score', 0),
                    **match.get('metadata', {})
                }
                documents.append(doc)
            
            print(f"Found {len(documents)} results from Pinecone")
            return documents
            
        except Exception as e:
            print(f"Pinecone search error: {e}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def upsert_documents(self, documents: List[Dict[str, Any]]):
        """Upload documents to Pinecone (for initial setup)."""
        try:
            print(f"Would upload {len(documents)} documents to Pinecone")
            # Implementation will be added after we get embeddings working
            pass
                
        except Exception as e:
            print(f"Pinecone upsert error: {e}")


# Global instance (will be initialized when needed)
pinecone_service = None

def get_pinecone_service():
    """Get or create Pinecone service instance."""
    global pinecone_service
    if pinecone_service is None:
        pinecone_service = PineconeService()
    return pinecone_service
