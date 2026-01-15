"""
Cloud-based agent service using RAG + Groq.
Automatically selects ChromaDB (local) or Pinecone (cloud).
"""

import os
from typing import Dict, Any, List
from app.core.config import settings


class CloudAgentService:
    """Agent service that adapts to local or cloud environment."""
    
    def __init__(self):
        self.use_rag = os.getenv("USE_RAG", "true").lower() == "true"
        self.environment = settings.environment
        print(f"🔍 CloudAgentService initialized: USE_RAG={os.getenv('USE_RAG')}, use_rag={self.use_rag}")
        
    def process_query(self, query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process query using appropriate RAG or fallback to LLM-only."""
        print(f"🔍 CloudAgentService.process_query called")
        print(f"🔍 USE_RAG={os.getenv('USE_RAG')}")
        print(f"🔍 self.use_rag={self.use_rag}")
        import sys
        sys.stdout.flush()  # Force flush
        
        try:
            if self.use_rag:
                print(f"🔍 Attempting RAG processing...")
                return self._process_with_rag(query, conversation_history)
            else:
                print(f"🔍 Using LLM-only (USE_RAG=false)")
                return self._process_llm_only(query, conversation_history)
        except Exception as e:
            import traceback
            print(f"Agent processing error: {e}")
            print(traceback.format_exc())
            return {
                "response": f"I apologize, but I'm experiencing technical difficulties: {str(e)}. Please try again.",
                "citations": []
            }
    
    def _process_with_rag(self, query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process query using RAG (ChromaDB local, Pinecone cloud)."""
        try:
            # Check if we should use cloud RAG
            use_cloud_rag = os.getenv("USE_CLOUD_RAG", "false").lower() == "true"
            print(f"🔍 USE_CLOUD_RAG={os.getenv('USE_CLOUD_RAG')}, use_cloud_rag={use_cloud_rag}")
            
            if use_cloud_rag:
                # Use Pinecone for cloud
                print("🔍 Using Pinecone cloud RAG service")
                from app.services.cloud_rag_service import cloud_rag_service
                return cloud_rag_service.process_query(query, conversation_history)
            else:
                # Use ChromaDB for local
                print("🔍 Using ChromaDB local RAG service")
                from app.services.rag_service import rag_service
                return rag_service.process_query(query, conversation_history)
                
        except Exception as e:
            print(f"RAG processing failed: {e}, falling back to LLM-only")
            import traceback
            print(f"RAG error traceback: {traceback.format_exc()}")
            import sys
            sys.stdout.flush()
            return self._process_llm_only(query, conversation_history)
    
    def _process_llm_only(self, query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Fallback: Process query using Groq without RAG."""
        try:
            from app.services.groq_service import groq_service
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a psychiatric clinical decision support assistant with expertise in DSM-5-TR diagnostic criteria. 

Provide detailed, accurate information about:
- Diagnostic criteria for psychiatric disorders
- Symptoms and clinical features
- Differential diagnosis considerations
- ICD-10 codes where applicable

Always structure your responses clearly and cite DSM-5-TR when discussing diagnostic criteria.
Note: You are currently operating without access to the full DSM-5-TR database."""
                }
            ]
            
            if conversation_history:
                for msg in conversation_history[-4:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": query})
            
            response = groq_service.generate_response(messages)
            
            return {
                "response": response,
                "citations": []
            }
        except Exception as e:
            import traceback
            print(f"Error in _process_llm_only: {e}")
            print(traceback.format_exc())
            raise
    
    def _process_with_fallback(self, query: str) -> Dict[str, Any]:
        """Fallback processing for common queries."""
        # Simple keyword-based responses for common psychiatric terms
        fallback_responses = {
            "borderline personality disorder": {
                "response": """**Borderline Personality Disorder (F60.3)**

A pervasive pattern of instability of interpersonal relationships, self-image, and affects, and marked impulsivity, beginning by early adulthood and present in a variety of contexts, as indicated by five (or more) of the following:

1. Frantic efforts to avoid real or imagined abandonment
2. A pattern of unstable and intense interpersonal relationships
3. Identity disturbance: markedly and persistently unstable self-image
4. Impulsivity in at least two areas that are potentially self-damaging
5. Recurrent suicidal behavior, gestures, or threats, or self-mutilating behavior
6. Affective instability due to a marked reactivity of mood
7. Chronic feelings of emptiness
8. Inappropriate, intense anger or difficulty controlling anger
9. Transient, stress-related paranoid ideation or severe dissociative symptoms

*Note: This is a simplified version. Please refer to the complete DSM-5-TR for full diagnostic criteria.*""",
                "citations": [{
                    "id": 1,
                    "document": "DSM-5-TR",
                    "chapter": "Personality Disorders",
                    "section": "Borderline Personality Disorder",
                    "icd_code": "F60.3",
                    "page": "663-666",
                    "content": "Diagnostic criteria for Borderline Personality Disorder",
                    "source": "DSM-5-TR"
                }]
            }
        }
        
        # Check for keyword matches
        query_lower = query.lower()
        for keyword, response_data in fallback_responses.items():
            if keyword in query_lower:
                return response_data
        
        # Default response
        return {
            "response": "I can help you with psychiatric diagnostic criteria and clinical information. Please ask about specific disorders, symptoms, or diagnostic criteria from the DSM-5-TR.",
            "citations": []
        }


# Global instance
print(f"🔍 Creating CloudAgentService instance...")
cloud_agent_service = CloudAgentService()
print(f"🔍 CloudAgentService instance created")
