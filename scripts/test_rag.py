#!/usr/bin/env python3
"""
Test script for RAG system.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
load_dotenv(env_path)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.rag_service import rag_service


def test_rag():
    """Test RAG pipeline with sample queries."""
    
    test_queries = [
        "What are the DSM-5-TR diagnostic criteria for Major Depressive Disorder?",
        "Tell me about Borderline Personality Disorder",
        "What is the ICD code for ADHD?"
    ]
    
    print("=" * 80)
    print("RAG SYSTEM TEST")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {query}")
        print('='*80)
        
        try:
            result = rag_service.process_query(query)
            
            print(f"\n📝 RESPONSE ({len(result['response'])} chars):")
            print("-" * 80)
            print(result['response'][:500] + "..." if len(result['response']) > 500 else result['response'])
            
            print(f"\n📚 CITATIONS ({len(result['citations'])} found):")
            print("-" * 80)
            for citation in result['citations']:
                print(f"\n[{citation['id']}] {citation.get('disorder_name', 'N/A')} ({citation.get('icd_code', 'N/A')})")
                print(f"    Section: {citation.get('section_type', 'N/A')}")
                print(f"    Page: {citation.get('page', 'N/A')}")
                print(f"    Path: {citation.get('hierarchy_path', 'N/A')}")
                print(f"    Preview: {citation['content'][:100]}...")
            
            print("\n✅ Test passed!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_rag()
