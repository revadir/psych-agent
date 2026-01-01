"""
Enhanced ingestion script with better chunking for diagnostic criteria.
"""

import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import re

# Configuration
DATA_PATH = "data/dsm5-tr.pdf"
DB_PATH = "vector_db_enhanced"


def enhanced_chunking(docs):
    """Enhanced chunking that preserves diagnostic criteria sections."""
    enhanced_chunks = []
    
    for doc in docs:
        content = doc.page_content
        
        # Look for diagnostic criteria sections
        criteria_pattern = r'(Diagnostic Criteria.*?(?=\n[A-Z][a-z]|\n\d+\.|$))'
        criteria_matches = re.findall(criteria_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if criteria_matches:
            # This page contains diagnostic criteria
            for criteria in criteria_matches:
                # Create a chunk for the entire criteria section
                enhanced_chunks.append({
                    'content': criteria.strip(),
                    'metadata': {
                        **doc.metadata,
                        'chunk_type': 'diagnostic_criteria',
                        'page': doc.metadata.get('page', 0)
                    }
                })
        
        # Also do regular chunking for other content
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        regular_chunks = text_splitter.split_documents([doc])
        
        for chunk in regular_chunks:
            enhanced_chunks.append({
                'content': chunk.page_content,
                'metadata': {
                    **chunk.metadata,
                    'chunk_type': 'regular'
                }
            })
    
    return enhanced_chunks


def build_enhanced_vector_store():
    """Build vector store with enhanced chunking."""
    print("🔄 Loading PDF...")
    loader = PyMuPDFLoader(DATA_PATH)
    docs = loader.load()
    print(f"📄 Loaded {len(docs)} pages")

    print("🔄 Enhanced chunking...")
    enhanced_chunks = enhanced_chunking(docs)
    print(f"📦 Created {len(enhanced_chunks)} enhanced chunks")
    
    # Convert back to Document objects
    from langchain_core.documents import Document
    chunk_docs = []
    for chunk in enhanced_chunks:
        chunk_docs.append(Document(
            page_content=chunk['content'],
            metadata=chunk['metadata']
        ))

    print("🔄 Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("🔄 Building vector database...")
    # Remove old database
    if os.path.exists(DB_PATH):
        import shutil
        shutil.rmtree(DB_PATH)
    
    vector_db = Chroma.from_documents(
        documents=chunk_docs, 
        embedding=embeddings, 
        persist_directory=DB_PATH
    )
    
    print(f"✅ Enhanced vector database created with {len(chunk_docs)} chunks!")
    
    # Test search for BPD
    print("\n🔍 Testing search for 'Borderline Personality Disorder diagnostic criteria'...")
    results = vector_db.similarity_search("Borderline Personality Disorder diagnostic criteria F60.3", k=3)
    
    for i, result in enumerate(results):
        print(f"\n📋 Result {i+1}:")
        print(f"Content: {result.page_content[:300]}...")
        print(f"Metadata: {result.metadata}")


if __name__ == "__main__":
    build_enhanced_vector_store()
