"""
RAG service for knowledge base retrieval and response generation.
"""

from typing import Dict, Any, List
from app.services.vector_service import VectorService
from app.services.groq_service import groq_service


class RAGService:
    """RAG service combining vector search with LLM generation."""
    
    def __init__(self):
        self.vector_service = VectorService()
    
    def process_query(self, query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process query using RAG pipeline."""
        # 1. Retrieve relevant DSM-5-TR content
        relevant_docs = self.vector_service.similarity_search(query, k=5)
        
        # 2. Format citations from retrieved documents
        citations = self._format_citations(relevant_docs)
        
        # 3. Build context for LLM
        context = self._build_context(relevant_docs)
        
        # 4. Generate response with Groq
        response = self._generate_response(query, context, conversation_history)
        
        return {
            "response": response,
            "citations": citations
        }
    
    def _format_citations(self, docs: List) -> List[Dict[str, Any]]:
        """Format retrieved documents as citations."""
        citations = []
        for idx, doc in enumerate(docs, 1):
            metadata = doc.metadata
            citations.append({
                "id": idx,
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "full_content": doc.page_content,
                "source": metadata.get("source", "DSM-5-TR"),
                "page": metadata.get("page"),
                "disorder_name": metadata.get("disorder_name"),
                "icd_code": metadata.get("icd_code"),
                "section_type": metadata.get("section_type"),
                "hierarchy_path": metadata.get("hierarchy_path", "DSM-5-TR")
            })
        return citations
    
    def _build_context(self, docs: List) -> str:
        """Build context string from retrieved documents."""
        context_parts = []
        for idx, doc in enumerate(docs, 1):
            metadata = doc.metadata
            header = f"[Source {idx}]"
            if metadata.get("disorder_name"):
                header += f" {metadata['disorder_name']}"
            if metadata.get("icd_code"):
                header += f" ({metadata['icd_code']})"
            context_parts.append(f"{header}\n{doc.page_content}\n")
        return "\n".join(context_parts)
    
    def _generate_response(self, query: str, context: str, conversation_history: List[Dict] = None) -> str:
        """Generate response using Groq with retrieved context."""
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
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-4:]:  # Last 4 messages for context
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current query with context
        messages.append({
            "role": "user",
            "content": f"""Based on these DSM-5-TR sources:

{context}

Question: {query}

Provide a detailed clinical response with inline citations (^1, ^2, etc.)."""
        })
        
        return groq_service.generate_response(messages)


# Global instance
rag_service = RAGService()
