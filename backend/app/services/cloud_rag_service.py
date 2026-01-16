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
        print(f"🔍 Pinecone returned {len(results)} results")
        if results:
            print(f"🔍 First result keys: {list(results[0].keys())}")
        import sys
        sys.stdout.flush()
        
        # 2. Format citations
        citations = self._format_citations(results)
        print(f"🔍 Formatted {len(citations)} citations")
        sys.stdout.flush()
        
        # 3. Build context
        context = self._build_context(results)
        
        # 4. Generate response
        response = self._generate_response(query, context, conversation_history)
        
        result = {
            "response": response,
            "citations": citations
        }
        
        print(f"🔍 CloudRAG returning: response_len={len(response)}, citations_count={len(citations)}")
        if citations:
            print(f"🔍 First citation: {citations[0]}")
        import sys
        sys.stdout.flush()
        
        return result
    
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

RESPONSE STRUCTURE (use this format for all clinical queries):

**Clinical Understanding:**
[Brief 2-3 sentence summary of the clinical presentation]

**Principal Diagnosis:**
[Primary diagnosis with ICD code^citation]

**Differential Diagnoses:**
1. [Alternative diagnosis with ICD code^citation]
2. [Alternative diagnosis with ICD code^citation]

**Medication Recommendations:**
- First-line: [medication class/specific agents^citation]
- Alternatives: [if applicable^citation]

**Long-term Course Management:**
- [Key monitoring points^citation]
- [Therapy recommendations^citation]
- [Follow-up considerations^citation]

CRITICAL INSTRUCTIONS:
1. Be CONCISE - avoid repetition, use bullet points
2. Cite sources using ^1, ^2, ^3 format inline
3. Base ONLY on provided DSM-5-TR sources
4. Include ICD codes for all diagnoses
5. If query is NOT psychiatric (e.g., general medical, non-clinical), respond: "This question appears to be outside the scope of psychiatric clinical decision support. I'm designed to help with psychiatric diagnoses, treatment planning, and DSM-5-TR criteria. Could you rephrase your question to focus on a psychiatric concern?"

NON-PSYCHIATRIC TOPICS TO DECLINE:
- General medical conditions (unless psychiatric comorbidity)
- Non-clinical questions (personal advice, general knowledge)
- Topics unrelated to mental health"""
            }
        ]
        
        if conversation_history:
            for msg in conversation_history[-4:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({
            "role": "user",
            "content": f"""Based on these DSM-5-TR sources:

{context}

Clinical Query: {query}

IMPORTANT: You have exactly {len(context.split('[Source'))-1} sources available (numbered 1-{len(context.split('[Source'))-1}). 
Only cite sources that exist. Do not cite ^{len(context.split('[Source'))} or higher.

Provide a structured response following the format above with inline citations."""
        })
        
        return groq_service.generate_response(messages)


# Global instance
cloud_rag_service = CloudRAGService()
