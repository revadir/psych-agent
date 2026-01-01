"""
Hybrid agent service combining hierarchical vector search with direct text extraction.
"""

import os
import logging
from typing import Dict, Any, List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.core.config import settings
from app.services.simple_agent_service import SimpleAgentService

logger = logging.getLogger(__name__)


class HybridAgentService:
    """Hybrid agent combining vector search with direct extraction."""

    def __init__(self):
        """Initialize the hybrid agent service."""
        self.db_path = self._get_vector_db_path()
        self.simple_agent = SimpleAgentService()
        
        try:
            self._initialize_vector_components()
            logger.info("Hybrid agent service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize hybrid agent service: {e}")
            raise

    def _get_vector_db_path(self) -> str:
        """Get absolute path to vector database."""
        if settings.vector_db_path.startswith("./"):
            return os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "..", "..", 
                settings.vector_db_path.replace("./", "")
            ))
        return settings.vector_db_path

    def _initialize_vector_components(self):
        """Initialize vector database components."""
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        
        if not os.path.exists(self.db_path):
            logger.warning(f"Hierarchical vector database not found at {self.db_path}")
            self.vector_db = None
            return
        
        self.vector_db = Chroma(
            persist_directory=self.db_path, 
            embedding_function=self.embeddings
        )
        
        # Create retriever that prioritizes diagnostic criteria
        self.retriever = self.vector_db.as_retriever(
            search_kwargs={
                "k": 5,
                "filter": {"section_type": "Diagnostic Criteria"}  # Prioritize diagnostic criteria
            }
        )

    def _search_hierarchical(self, query: str) -> List[Dict[str, Any]]:
        """Search the hierarchical vector database."""
        if not self.vector_db:
            return []
        
        try:
            # First search for diagnostic criteria specifically
            criteria_results = self.vector_db.similarity_search(
                query, 
                k=3,
                filter={"section_type": "Diagnostic Criteria"}
            )
            
            # Then search for parent chunks (full disorder context)
            parent_results = self.vector_db.similarity_search(
                query,
                k=2, 
                filter={"chunk_type": "parent"}
            )
            
            # Combine and format results
            all_results = []
            
            for doc in criteria_results + parent_results:
                all_results.append({
                    "content": doc.page_content,
                    "disorder": doc.metadata.get("disorder_name", "Unknown"),
                    "section": doc.metadata.get("section_type", "Unknown"),
                    "icd_code": doc.metadata.get("icd_code", ""),
                    "source": "DSM-5-TR"
                })
            
            return all_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query using hybrid approach."""
        try:
            logger.info(f"🟡 HYBRID: Processing query: {query[:100]}...")
            
            # Try hierarchical vector search first
            vector_results = self._search_hierarchical(query)
            logger.info(f"🟡 HYBRID: Vector search returned {len(vector_results)} results")
            
            if vector_results:
                # Use vector search results
                context_text = "\n\n".join([
                    f"**{result['disorder']} ({result['icd_code']}) - {result['section']}:**\n{result['content']}"
                    for result in vector_results
                ])
                
                # Create a simple response using the context
                response = f"**Clinical Query:** {query}\n\n**DSM-5-TR Information Found:**\n\n{context_text}"
                
                citations = [
                    {
                        "content": f"{result['disorder']} - {result['section']}: {result['content'][:200]}...",
                        "source": f"DSM-5-TR ({result['icd_code']})" if result['icd_code'] else "DSM-5-TR"
                    }
                    for result in vector_results[:3]
                ]
                
                return {
                    "response": response,
                    "citations": citations,
                    "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.",
                    "model": "hierarchical_vector_search",
                    "query": query
                }
            
            else:
                # Fallback to simple agent
                logger.info("🟡 HYBRID: Vector search failed, using simple agent fallback")
                return self.simple_agent.process_query(query)
            
        except Exception as e:
            logger.error(f"🔴 HYBRID: Error processing query: {e}")
            # Final fallback
            return self.simple_agent.process_query(query)


# Global hybrid agent service instance
_hybrid_agent_service = None

def get_hybrid_agent_service():
    """Get or create global hybrid agent service instance."""
    global _hybrid_agent_service
    if _hybrid_agent_service is None:
        _hybrid_agent_service = HybridAgentService()
    return _hybrid_agent_service
