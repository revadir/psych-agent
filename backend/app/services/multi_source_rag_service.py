"""
Multi-source RAG service that synthesizes information from multiple sources.
Implements "Verify-then-Respond" workflow.
"""

from typing import Dict, Any, List
from app.services.cloud_rag_service import cloud_rag_service
from app.services.icd11_service import icd11_service
from app.services.groq_service import groq_service


class MultiSourceRAGService:
    """RAG service that retrieves from multiple sources and synthesizes."""
    
    def process_query(self, query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Verify-then-Respond workflow:
        1. Retrieve from DSM-5-TR (Pinecone)
        2. Cross-reference with ICD-11
        3. Synthesize with LLM
        """
        
        print(f"🔍 Multi-Source RAG: Processing query")
        
        # Step 1: Get DSM-5-TR information
        dsm_result = cloud_rag_service.process_query(query, conversation_history)
        print(f"🔍 DSM-5-TR returned {len(dsm_result.get('citations', []))} citations")
        
        # Step 2: Cross-reference with ICD-11
        print(f"🔍 Searching ICD-11 for: {query}")
        icd11_results = icd11_service.search_mental_disorders(query, max_results=3)
        print(f"🔍 ICD-11 returned {len(icd11_results)} results")
        if icd11_results:
            print(f"🔍 First ICD-11 result: {icd11_results[0]}")
        
        # Step 3: Synthesize
        if icd11_results:
            print(f"🔍 Synthesizing DSM-5-TR + ICD-11")
            synthesized_response = self._synthesize_sources(
                query, 
                dsm_result, 
                icd11_results,
                conversation_history
            )
            return synthesized_response
        else:
            print(f"🔍 No ICD-11 results, returning DSM-only")
            # No ICD-11 results, return DSM-only
            return dsm_result
    
    def _synthesize_sources(
        self, 
        query: str, 
        dsm_result: Dict[str, Any],
        icd11_results: List[Dict[str, Any]],
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """Synthesize information from DSM-5-TR and ICD-11."""
        
        # Build ICD-11 context
        icd11_context = "\n\n".join([
            f"ICD-11 Code: {r['icd_code']}\nTitle: {r['title']}"
            for r in icd11_results
        ])
        
        # Create synthesis prompt
        messages = [
            {
                "role": "system",
                "content": """You are synthesizing information from multiple authoritative sources:
1. DSM-5-TR (American Psychiatric Association)
2. ICD-11 (World Health Organization)

Your task: Integrate both sources to provide the most accurate clinical guidance.

RESPONSE STRUCTURE:

**Clinical Understanding:**
[Brief 2-3 sentence summary]

**Principal Diagnosis:**
[Primary diagnosis with BOTH DSM-5-TR and ICD-11 codes^citation]

**Differential Diagnoses:**
1. [Alternative with codes^citation]
2. [Alternative with codes^citation]

**Medication Recommendations:**
- First-line: [medication class^citation]
- Alternatives: [if applicable^citation]

**Long-term Course Management:**
- [Key points^citation]

CRITICAL RULES:
1. Cite DSM-5-TR sources as ^1, ^2, etc.
2. Reference ICD-11 codes when available
3. If sources conflict, note the difference
4. Only use provided information - no hallucination
5. Be concise"""
            }
        ]
        
        if conversation_history:
            for msg in conversation_history[-4:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({
            "role": "user",
            "content": f"""Query: {query}

DSM-5-TR Response:
{dsm_result['response']}

ICD-11 Cross-Reference:
{icd11_context}

Synthesize these sources into a unified clinical response. Include both DSM-5-TR and ICD-11 codes where applicable."""
        })
        
        synthesized_text = groq_service.generate_response(messages)
        
        # Add ICD-11 citations
        all_citations = dsm_result.get('citations', []).copy()
        for idx, icd_result in enumerate(icd11_results, start=len(all_citations) + 1):
            all_citations.append({
                'id': idx,
                'content': f"ICD-11: {icd_result['title']} ({icd_result['icd_code']})",
                'full_content': f"ICD-11 Code: {icd_result['icd_code']}\nTitle: {icd_result['title']}\nSource: World Health Organization ICD-11",
                'source': 'ICD-11',
                'icd_code': icd_result['icd_code'],
                'disorder_name': icd_result['title'],
                'hierarchy_path': 'ICD-11 > Mental, Behavioural or Neurodevelopmental Disorders'
            })
        
        return {
            'response': synthesized_text,
            'citations': all_citations
        }


# Global instance
multi_source_rag_service = MultiSourceRAGService()
