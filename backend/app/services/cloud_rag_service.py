"""
Cloud RAG service using Pinecone + Groq.
"""

import os
from typing import Dict, Any, List
from app.services.pinecone_service import get_pinecone_service
from app.services.groq_service import groq_service


class CloudRAGService:
    """RAG service for cloud deployment using Pinecone."""
    
    def __init__(self):
        self.pinecone_service = get_pinecone_service()
    
    def process_query(self, query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process query using Pinecone + Groq."""
        # 1. Search Pinecone
        results = self.pinecone_service.search_similar_documents(query, top_k=5)
        
        # 2. Format citations
        citations = self._format_citations(results)
        
        # 3. Build context
        context = self._build_context(results)
        
        # 4. Generate response
        response = self._generate_response(query, context, conversation_history)
        
        return {
            "response": response,
            "citations": citations
        }
    
    def _format_citations(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Format Pinecone results as citations."""
        citations = []
        for idx, result in enumerate(results, 1):
            citations.append({
                "id": idx,
                "content": result.get("content", "")[:200] + "...",
                "full_content": result.get("content", ""),
                "source": result.get("source", "DSM-5-TR"),
                "page": result.get("page"),
                "disorder_name": result.get("disorder_name"),
                "icd_code": result.get("icd_code"),
                "section_type": result.get("section_type"),
                "hierarchy_path": result.get("hierarchy_path", "DSM-5-TR"),
                "chapter": result.get("chapter"),
                "section": result.get("section")
            })
        return citations
    
    def _build_context(self, results: List[Dict]) -> str:
        """Build context from Pinecone results."""
        context_parts = []
        for idx, result in enumerate(results, 1):
            header = f"[Source {idx}]"
            if result.get("disorder_name"):
                header += f" {result['disorder_name']}"
            if result.get("icd_code"):
                header += f" ({result['icd_code']})"
            context_parts.append(f"{header}\n{result.get('content', '')}\n")
        return "\n".join(context_parts)
    
    def _generate_response(self, query: str, context: str, conversation_history: List[Dict] = None) -> str:
        """Generate response using Groq."""
        messages = [
            {
                "role": "system",
                "content": """You are a psychiatric clinical decision support assistant with expertise in DSM-5-TR diagnostic criteria.

CRITICAL INSTRUCTIONS:
1. Base your response ONLY on the provided DSM-5-TR sources
2. Cite sources using ^1, ^2, ^3 format inline (e.g., "Major Depressive Disorder requires five symptoms^1")
3. Use multiple citations when combining information from different sources
4. Structure responses clearly with diagnostic criteria, features, and considerations
5. Include ICD codes when discussing specific disorders
6. If sources don't contain enough information, acknowledge limitations

RESPONSE FORMAT:
- Start with a clear answer to the clinical question
- Present diagnostic criteria as numbered lists when applicable
- Cite each major point with ^N notation
- End with clinical considerations or differential diagnosis if relevant"""
            }
        ]
        
        if conversation_history:
            for msg in conversation_history[-4:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({
            "role": "user",
            "content": f"""Based on these DSM-5-TR sources:

{context}

Question: {query}

Provide a detailed clinical response with inline citations (^1, ^2, etc.)."""
        })
        
        return groq_service.generate_response(messages)


# Global instance
cloud_rag_service = CloudRAGService()
