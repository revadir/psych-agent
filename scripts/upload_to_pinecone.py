#!/usr/bin/env python3
"""
Script to upload DSM-5-TR data to Pinecone for cloud deployment.
Run this locally to populate the cloud vector database.
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.services.pinecone_service import get_pinecone_service


def load_local_vector_data():
    """Load processed documents from local vector database."""
    # Try to load from ChromaDB if available
    try:
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_db_path = Path(__file__).parent.parent / "vector_db_hierarchical"
        
        if vector_db_path.exists():
            vectorstore = Chroma(
                persist_directory=str(vector_db_path),
                embedding_function=embeddings
            )
            
            # Get all documents
            docs = vectorstore.get()
            
            documents = []
            for i, (doc_id, metadata, document) in enumerate(zip(docs['ids'], docs['metadatas'], docs['documents'])):
                documents.append({
                    "content": document,
                    "source": metadata.get("source", "DSM-5-TR"),
                    "page": metadata.get("page", "Unknown"),
                    "chapter": metadata.get("chapter", "Unknown"),
                    "section": metadata.get("section", "Unknown")
                })
            
            return documents
            
    except Exception as e:
        print(f"Could not load from ChromaDB: {e}")
    
    # Fallback: create sample documents for testing
    return [
        {
            "content": """Borderline Personality Disorder (F60.3)
            
A pervasive pattern of instability of interpersonal relationships, self-image, and affects, and marked impulsivity, beginning by early adulthood and present in a variety of contexts, as indicated by five (or more) of the following:

1. Frantic efforts to avoid real or imagined abandonment (Note: Do not include suicidal or self-mutilating behavior covered in Criterion 5.)

2. A pattern of unstable and intense interpersonal relationships characterized by alternating between extremes of idealization and devaluation.

3. Identity disturbance: markedly and persistently unstable self-image or sense of self.

4. Impulsivity in at least two areas that are potentially self-damaging (e.g., spending, sex, substance abuse, reckless driving, binge eating). (Note: Do not include suicidal or self-mutilating behavior covered in Criterion 5.)

5. Recurrent suicidal behavior, gestures, or threats, or self-mutilating behavior.

6. Affective instability due to a marked reactivity of mood (e.g., intense episodic dysphoria, irritability, or anxiety usually lasting a few hours and only rarely more than a few days).

7. Chronic feelings of emptiness.

8. Inappropriate, intense anger or difficulty controlling anger (e.g., frequent displays of temper, constant anger, recurrent physical fights).

9. Transient, stress-related paranoid ideation or severe dissociative symptoms.""",
            "source": "DSM-5-TR",
            "page": "663-666",
            "chapter": "Personality Disorders",
            "section": "Borderline Personality Disorder"
        },
        {
            "content": """Major Depressive Disorder (F32.x, F33.x)

A. Five (or more) of the following symptoms have been present during the same 2-week period and represent a change from previous functioning; at least one of the symptoms is either (1) depressed mood or (2) loss of interest or pleasure.

1. Depressed mood most of the day, nearly every day
2. Markedly diminished interest or pleasure in all, or almost all, activities
3. Significant weight loss when not dieting or weight gain
4. Insomnia or hypersomnia nearly every day
5. Psychomotor agitation or retardation nearly every day
6. Fatigue or loss of energy nearly every day
7. Feelings of worthlessness or excessive or inappropriate guilt
8. Diminished ability to think or concentrate, or indecisiveness
9. Recurrent thoughts of death, recurrent suicidal ideation""",
            "source": "DSM-5-TR",
            "page": "160-168",
            "chapter": "Depressive Disorders",
            "section": "Major Depressive Disorder"
        }
    ]


def main():
    """Upload documents to Pinecone."""
    print("🔄 Loading documents...")
    documents = load_local_vector_data()
    print(f"📄 Found {len(documents)} documents")
    
    if not documents:
        print("❌ No documents found to upload")
        return
    
    print("🔄 Connecting to Pinecone...")
    try:
        pinecone_service = get_pinecone_service()
        print("✅ Connected to Pinecone")
        
        print("🔄 Uploading documents...")
        pinecone_service.upsert_documents(documents)
        print("✅ Documents uploaded successfully!")
        
        # Test search
        print("🔄 Testing search...")
        results = pinecone_service.search_similar_documents("borderline personality disorder", top_k=2)
        print(f"✅ Search test returned {len(results)} results")
        
        for i, result in enumerate(results):
            print(f"  {i+1}. {result['chapter']} - {result['section']} (score: {result['score']:.3f})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have set the PINECONE_API_KEY environment variable")
        return


if __name__ == "__main__":
    main()
