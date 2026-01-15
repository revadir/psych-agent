#!/usr/bin/env python3
"""
Upload DSM-5-TR hierarchical chunks to Pinecone.
Converts ChromaDB chunks to embeddings and uploads to cloud.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.services.pinecone_service import get_pinecone_service


def load_chromadb_chunks():
    """Load all chunks from your hierarchical ChromaDB."""
    print("🔄 Loading chunks from ChromaDB...")
    
    # Initialize embeddings (same model as your local setup)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load your hierarchical vector DB
    vector_db_path = Path(__file__).parent.parent / "vector_db_hierarchical"
    
    if not vector_db_path.exists():
        raise FileNotFoundError(f"Vector DB not found at {vector_db_path}")
    
    vectorstore = Chroma(
        persist_directory=str(vector_db_path),
        embedding_function=embeddings
    )
    
    # Get all documents with their embeddings and metadata
    collection = vectorstore._collection
    results = collection.get(include=['documents', 'metadatas', 'embeddings'])
    
    documents = []
    for i, (doc_id, content, metadata, embedding) in enumerate(zip(
        results['ids'], 
        results['documents'], 
        results['metadatas'],
        results['embeddings']
    )):
        documents.append({
            'id': doc_id,
            'content': content,
            'embedding': embedding,
            'metadata': {
                'source': metadata.get('source', 'DSM-5-TR'),
                'page': metadata.get('page'),
                'disorder_name': metadata.get('disorder_name'),
                'icd_code': metadata.get('icd_code'),
                'section_type': metadata.get('section_type'),
                'hierarchy_path': metadata.get('hierarchy_path'),
                'chunk_type': metadata.get('chunk_type'),
                'chapter': metadata.get('chapter'),
                'section': metadata.get('section')
            }
        })
    
    print(f"✅ Loaded {len(documents)} chunks from ChromaDB")
    return documents


def upload_to_pinecone(documents):
    """Upload documents with embeddings to Pinecone."""
    print("🔄 Connecting to Pinecone...")
    
    pinecone_service = get_pinecone_service()
    
    print(f"🔄 Uploading {len(documents)} vectors to Pinecone...")
    
    # Prepare vectors for Pinecone
    vectors = []
    for doc in documents:
        # Clean metadata - remove null values
        clean_metadata = {}
        for key, value in doc['metadata'].items():
            if value is not None and value != '':
                clean_metadata[key] = str(value)  # Convert to string
        
        # Add content separately
        clean_metadata['content'] = doc['content']
        
        vectors.append({
            'id': doc['id'],
            'values': doc['embedding'],
            'metadata': clean_metadata
        })
    
    # Upload in batches (Pinecone limit: 100 vectors per batch)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        pinecone_service.index.upsert(vectors=batch)
        print(f"  Uploaded batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")
    
    print("✅ Upload complete!")


def test_search():
    """Test search functionality."""
    print("🔄 Testing search...")
    
    pinecone_service = get_pinecone_service()
    results = pinecone_service.search_similar_documents("Major Depressive Disorder", top_k=3)
    
    print(f"✅ Search returned {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.get('disorder_name', 'N/A')} ({result.get('icd_code', 'N/A')})")
        print(f"     Score: {result.get('score', 0):.3f}")


def main():
    """Main upload process."""
    print("=" * 80)
    print("DSM-5-TR HIERARCHICAL CHUNKS → PINECONE UPLOAD")
    print("=" * 80)
    
    try:
        # Load your ChromaDB chunks
        documents = load_chromadb_chunks()
        
        # Upload to Pinecone
        upload_to_pinecone(documents)
        
        # Test search
        test_search()
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS! Your DSM-5-TR chunks are now in Pinecone")
        print("✅ Cloud deployment ready")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Make sure:")
        print("   - PINECONE_API_KEY is set")
        print("   - vector_db_hierarchical/ exists")
        print("   - Pinecone index 'psych-agent' is created")


if __name__ == "__main__":
    main()
