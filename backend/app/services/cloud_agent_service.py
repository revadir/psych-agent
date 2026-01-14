"""
Cloud-based agent service using Groq and Pinecone.
"""

import os
from typing import Dict, Any, List
from app.core.config import settings
from app.services.groq_service import groq_service
from app.services.pinecone_service import get_pinecone_service


class CloudAgentService:
    """Agent service using cloud providers (Groq + Pinecone)."""
    
    def __init__(self):
        self.use_cloud = os.getenv("USE_CLOUD_SERVICES", "true").lower() == "true"
        
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query using cloud services."""
        try:
            if self.use_cloud:
                return self._process_with_cloud(query)
            else:
                return self._process_with_fallback(query)
        except Exception as e:
            import traceback
            print(f"Agent processing error: {e}")
            print(traceback.format_exc())
            # Return error details for debugging
            return {
                "response": f"I apologize, but I'm experiencing technical difficulties: {str(e)}. Please try again.",
                "citations": []
            }
    
    def _process_with_cloud(self, query: str) -> Dict[str, Any]:
        """Process query using Groq and Pinecone."""
        # Search for relevant documents
        pinecone = get_pinecone_service()
        relevant_docs = pinecone.search_similar_documents(query, top_k=3)
        
        # Build context from documents
        context = ""
        citations = []
        
        for i, doc in enumerate(relevant_docs):
            context += f"\n\nDocument {i+1}:\n{doc['content']}"
            citations.append({
                "id": i + 1,
                "document": doc["source"],
                "chapter": doc["chapter"],
                "section": doc["section"],
                "page": doc["page"],
                "content": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                "full_content": doc["content"],
                "source": doc["source"],
                "preview": doc["content"][:150] + "..." if len(doc["content"]) > 150 else doc["content"]
            })
        
        # Generate response using Groq
        messages = [
            {
                "role": "system",
                "content": """You are a psychiatric clinical decision support assistant. Use the provided DSM-5-TR context to answer questions about diagnostic criteria, symptoms, and clinical features. Always cite your sources and be precise about diagnostic criteria."""
            },
            {
                "role": "user",
                "content": f"Context from DSM-5-TR:\n{context}\n\nQuestion: {query}\n\nPlease provide a detailed response based on the context above."
            }
        ]
        
        response = groq_service.generate_response(messages)
        
        return {
            "response": response,
            "citations": citations
        }
    
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
cloud_agent_service = CloudAgentService()
