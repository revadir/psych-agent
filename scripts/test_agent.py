#!/usr/bin/env python3
"""
Test the enhanced agent service.
"""

import sys
import os
import json

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.agent_service import get_agent_service

def test_agent_service():
    """Test the agent service functionality."""
    try:
        print("Initializing agent service...")
        agent = get_agent_service()
        print("✅ Agent service initialized successfully")
        
        # Test query
        test_query = "Patient reports 3 weeks of persistent sadness, loss of interest in activities, and difficulty sleeping. Does this meet criteria for Major Depressive Disorder?"
        
        print(f"\nProcessing query: {test_query[:80]}...")
        result = agent.process_query(test_query)
        
        print("✅ Query processed successfully")
        print(f"Response length: {len(result['response'])} characters")
        print(f"Citations: {len(result['citations'])} found")
        print(f"Model used: {result['model']}")
        
        # Print formatted result
        print("\n" + "="*50)
        print("AGENT RESPONSE:")
        print("="*50)
        print(result['response'][:500] + "..." if len(result['response']) > 500 else result['response'])
        
        print("\n" + "="*50)
        print("CITATIONS:")
        print("="*50)
        for i, citation in enumerate(result['citations'], 1):
            print(f"{i}. {citation['content']}")
        
        print(f"\n✅ Agent service test completed successfully!")
        
    except Exception as e:
        print(f"❌ Agent service test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_service()
