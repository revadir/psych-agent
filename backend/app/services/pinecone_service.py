"""
Pinecone vector database service for cloud deployment.
"""

import os
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from app.core.config import settings


class PineconeService:
    """Service for interacting with Pinecone vector database."""
    
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY") or settings.pinecone_api_key
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
        
        self.pc = Pinecone(api_key=api_key)
        self.index_name = os.getenv("PINECONE_INDEX_NAME", settings.pinecone_index_name)
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        
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
                    dimension=384,  # all-MiniLM-L6-v2 dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
        except Exception as e:
            print(f"Error ensuring index exists: {e}")
    
    def search_similar_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents in Pinecone."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            documents = []
            for match in results.matches:
                if match.score > 0.7:  # Similarity threshold
                    documents.append({
                        "content": match.metadata.get("content", ""),
                        "source": match.metadata.get("source", "DSM-5-TR"),
                        "page": match.metadata.get("page", "Unknown"),
                        "chapter": match.metadata.get("chapter", "Unknown"),
                        "section": match.metadata.get("section", "Unknown"),
                        "score": match.score
                    })
            
            return documents
            
        except Exception as e:
            print(f"Pinecone search error: {e}")
            return []
    
    def upsert_documents(self, documents: List[Dict[str, Any]]):
        """Upload documents to Pinecone (for initial setup)."""
        try:
            vectors = []
            for i, doc in enumerate(documents):
                embedding = self.embedding_model.encode(doc["content"]).tolist()
                vectors.append({
                    "id": f"doc_{i}",
                    "values": embedding,
                    "metadata": {
                        "content": doc["content"],
                        "source": doc.get("source", "DSM-5-TR"),
                        "page": doc.get("page", "Unknown"),
                        "chapter": doc.get("chapter", "Unknown"),
                        "section": doc.get("section", "Unknown")
                    }
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
                print(f"Uploaded batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")
                
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
