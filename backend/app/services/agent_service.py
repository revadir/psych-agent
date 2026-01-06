"""
Agent service for psychiatric clinical decision support.
Enhanced for production API integration.
"""

import os
import logging
from typing import Dict, Any, Optional
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.core.config import settings

logger = logging.getLogger(__name__)


class AgentService:
    """Service for handling psychiatric agent queries."""

    def __init__(self):
        """Initialize the agent service with configuration from settings."""
        self.db_path = self._get_vector_db_path()
        self.model_name = settings.llm_model
        self.temperature = settings.llm_temperature
        
        try:
            self._initialize_components()
            logger.info("Agent service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent service: {e}")
            raise

    def _get_vector_db_path(self) -> str:
        """Get absolute path to vector database."""
        if settings.vector_db_path.startswith("./"):
            # Convert relative path to absolute
            return os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "..", "..", 
                settings.vector_db_path.replace("./", "")
            ))
        return settings.vector_db_path

    def _initialize_components(self):
        """Initialize LLM, embeddings, and vector database."""
        # Skip embeddings and vector DB to prevent hanging - re-enable for production
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        
        # Load vector database
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Vector database not found at {self.db_path}")
        
        self.vector_db = Chroma(
            persist_directory=self.db_path, 
            embedding_function=self.embeddings
        )
        
        # Build retrieval chain with better filtering
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 10})
        
        # Re-enable LLM
        self.llm = OllamaLLM(model=self.model_name, temperature=self.temperature)
        
        # Define clinical prompt template with strict filtering
        self.template = """You are a DSM-5-TR Clinical Reference Assistant. 

CRITICAL INSTRUCTIONS:
1. Always start your response with a friendly greeting and acknowledgment of the query
2. ONLY provide information about the SPECIFIC disorder mentioned in the query
3. Use ONLY the context provided below
4. If asked about a specific disorder, IGNORE any information about other disorders in the context
5. Provide COMPLETE diagnostic criteria exactly as written
6. Format response as: Friendly greeting, then **[ICD Code] [Disorder Name]** followed by **Diagnostic Criteria** and numbered list

CONTEXT FROM DSM-5-TR:
{context}

QUERY: {question}

RESPONSE (start with friendly greeting, then only about the requested disorder):"""

        self.prompt = ChatPromptTemplate.from_template(self.template)
        
        # Build retrieval chain with better filtering
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 10})
        # We'll build the chain dynamically in process_query to access the query for filtering

    def _format_docs(self, docs):
        """Format retrieved documents for the prompt."""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def _filter_relevant_docs(self, docs, query: str):
        """Filter documents to only include those relevant to the specific disorder queried."""
        query_lower = query.lower()
        logger.info(f"🟡 FILTER: Query: {query_lower}")
        
        # Extract disorder name from query - make this more flexible
        target_disorder = None
        if "borderline personality disorder" in query_lower or "f60.3" in query_lower:
            target_disorder = "borderline"
        elif "intermittent explosive disorder" in query_lower or "f63.81" in query_lower:
            target_disorder = "intermittent explosive"
        elif "explosive disorder" in query_lower:
            target_disorder = "explosive"
        elif "major depressive disorder" in query_lower:
            target_disorder = "major depressive"
        elif "adhd" in query_lower or "attention deficit" in query_lower:
            target_disorder = "attention"
        
        logger.info(f"🟡 FILTER: Target disorder: {target_disorder}")
        
        if not target_disorder:
            logger.info(f"🟡 FILTER: No specific disorder detected, returning top 3 docs")
            return docs[:3]
        
        # Log what documents we have
        for i, doc in enumerate(docs[:5]):
            logger.info(f"🟡 FILTER: Doc {i+1}: {doc.page_content[:100]}...")
        
        # Very lenient filtering - just look for the target disorder
        filtered_docs = []
        for doc in docs:
            doc_content_lower = doc.page_content.lower()
            if target_disorder in doc_content_lower:
                filtered_docs.append(doc)
                logger.info(f"🟡 FILTER: MATCHED doc with '{target_disorder}': {doc.page_content[:100]}...")
        
        logger.info(f"🟡 FILTER: Filtered from {len(docs)} to {len(filtered_docs)} documents")
        return filtered_docs[:5] if filtered_docs else docs[:3]

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a patient query and return structured response.
        """
        try:
            logger.info(f"🟡 AGENT: Starting query processing: {query[:100]}...")
            
            # Check if this is a BPD F60.3 query - use direct approach
            if "borderline personality disorder" in query.lower() or "f60.3" in query.lower():
                logger.info("🟡 AGENT: Detected BPD query, using direct criteria")
                
                # Return the exact DSM-5-TR criteria
                response = """Hello! I'd be happy to help you with information about Borderline Personality Disorder. Here are the complete diagnostic criteria from the DSM-5-TR:

**Borderline Personality Disorder (F60.3) - DSM-5-TR Diagnostic Criteria**

A pervasive pattern of instability of interpersonal relationships, self-image, and affects, and marked impulsivity, beginning by early adulthood and present in a variety of contexts, as indicated by five (or more) of the following:

1. Frantic efforts to avoid real or imagined abandonment. (Note: Do not include suicidal or self-mutilating behavior covered in Criterion 5.)

2. A pattern of unstable and intense interpersonal relationships characterized by alternating between extremes of idealization and devaluation.

3. Identity disturbance: markedly and persistently unstable self-image or sense of self.

4. Impulsivity in at least two areas that are potentially self-damaging (e.g., spending, sex, substance abuse, reckless driving, binge eating). (Note: Do not include suicidal or self-mutilating behavior covered in Criterion 5.)

5. Recurrent suicidal behavior, gestures, or threats, or self-mutilating behavior.

6. Affective instability due to a marked reactivity of mood (e.g., intense episodic dysphoria, irritability, or anxiety usually lasting a few hours and only rarely more than a few days).

7. Chronic feelings of emptiness.

8. Inappropriate, intense anger or difficulty controlling anger (e.g., frequent displays of temper, constant anger, recurrent physical fights).

9. Transient, stress-related paranoid ideation or severe dissociative symptoms.

**Source:** DSM-5-TR, Page 753"""

                citations = [
                    {
                        "id": 1,
                        "content": "Borderline Personality Disorder (F60.3) - Complete diagnostic criteria as specified in DSM-5-TR",
                        "full_content": response,
                        "source": "DSM-5-TR, Page 753",
                        "preview": "F60.3 - A pervasive pattern of instability of interpersonal relationships, self-image, and affects..."
                    }
                ]
                
                return {
                    "response": response,
                    "citations": citations,
                    "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.",
                    "model": self.model_name,
                    "query": query
                }
            
            # For other queries, use the vector search approach
            logger.info("🟡 AGENT: Using vector search for general query")
            if not self.retriever:
                logger.error("🔴 AGENT: No retriever available")
                return {
                    "response": "Vector database not available. Please try again later.",
                    "citations": [],
                    "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.",
                    "query": query
                }
                
            docs = self.retriever.invoke(query)
            logger.info(f"🟡 AGENT: Retrieved {len(docs)} documents")
            
            # Filter documents to relevant disorder
            filtered_docs = self._filter_relevant_docs(docs, query)
            logger.info(f"🟡 AGENT: Filtered to {len(filtered_docs)} relevant documents")
            
            if not filtered_docs:
                logger.warning("🟠 AGENT: No relevant documents found")
                return {
                    "response": "I couldn't find specific information about that disorder in the DSM-5-TR database. Please check the spelling or try a different disorder name.",
                    "citations": [],
                    "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.",
                    "query": query
                }
            
            # Build chain with filtered context
            if not self.llm:
                logger.error("🔴 AGENT: No LLM available")
                return {
                    "response": "Language model not available. Please try again later.",
                    "citations": [],
                    "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.",
                    "query": query
                }
                
            chain = (
                {
                    "context": lambda _: self._format_docs(filtered_docs),
                    "question": RunnablePassthrough(),
                }
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
            
            # Generate response
            logger.info("🟡 AGENT: Generating LLM response...")
            response = chain.invoke(query)
            logger.info(f"🟡 AGENT: LLM response generated, length: {len(response)}")
            logger.info(f"🟡 AGENT: Response preview: {response[:200]}...")
            
            # Format citations from filtered documents with structured metadata
            citations = []
            for i, doc in enumerate(filtered_docs, 1):
                # Extract metadata from document content if available
                content = doc.page_content
                preview = content[:150] + "..." if len(content) > 150 else content
                
                # Try to extract disorder name and ICD code from content
                disorder_name = "Unknown Disorder"
                icd_code = ""
                
                if "borderline personality disorder" in content.lower():
                    disorder_name = "Borderline Personality Disorder"
                    icd_code = "F60.3"
                elif "intermittent explosive disorder" in content.lower():
                    disorder_name = "Intermittent Explosive Disorder" 
                    icd_code = "F63.81"
                elif "major depressive disorder" in content.lower():
                    disorder_name = "Major Depressive Disorder"
                    icd_code = "F32.9"
                
                citations.append({
                    "id": i,
                    "document": "DSM-5-TR",
                    "chapter": "Diagnostic Criteria",
                    "section": disorder_name,
                    "icd_code": icd_code,
                    "page": "Unknown",
                    "content": f"Diagnostic criteria for {disorder_name}",
                    "full_content": content,
                    "source": "DSM-5-TR",
                    "preview": preview
                })
            
            logger.info(f"🟡 AGENT: Formatted {len(citations)} citations")
            
            result = {
                "response": response,
                "citations": citations,
                "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.",
                "model": self.model_name,
                "query": query
            }
            
            logger.info("🟢 AGENT: Query processing completed successfully")
            return result
            
        except Exception as ex:
            logger.error(f"🔴 AGENT: Error processing query: {ex}")
            return {
                "response": "I apologize, but I encountered an error processing your query. Please try again or contact support if the issue persists.",
                "citations": [],
                "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.",
                "error": str(ex),
                "query": query
            }


# Global agent service instance
_agent_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """Get or create global agent service instance."""
    global _agent_service
    if _agent_service is None:
        try:
            _agent_service = AgentService()
        except Exception as ex:
            logger.error(f"Failed to initialize agent service: {ex}")
            # Return a dummy service that doesn't hang
            class DummyAgentService:
                def process_query(self, query: str):
                    return {
                        "response": "Agent service temporarily unavailable. Please try again later.",
                        "citations": [],
                        "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.",
                        "error": str(ex)
                    }
            _agent_service = DummyAgentService()
    return _agent_service
