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
        
        # Define clinical prompt template with natural conversation flow
        self.template = """You are a DSM-5-TR Clinical Reference Assistant providing psychiatric consultation.

INSTRUCTIONS:
- Respond naturally and professionally, varying your language based on context
- For new topics: Start directly with the clinical information requested
- For follow-up questions: Reference previous discussion naturally ("Regarding the PTSD we discussed...", "For that same condition...", etc.)
- For treatment questions: Focus on the disorder from recent conversation context
- Provide accurate DSM-5-TR information with diagnostic codes when relevant
- Be concise but thorough

{conversation_context}

DSM-5-TR CONTEXT:
{context}

CLINICIAN QUERY: {question}

RESPONSE:"""

        self.prompt = ChatPromptTemplate.from_template(self.template)
        
        # Build retrieval chain with better filtering
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 10})
        # We'll build the chain dynamically in process_query to access the query for filtering

    def _format_docs(self, docs):
        """Format retrieved documents for the prompt."""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def _build_conversation_context(self, query: str, conversation_history: list) -> str:
        """Build conversation context that helps generate natural, varied responses."""
        if not conversation_history or len(conversation_history) < 2:
            return "CONTEXT: This is a new conversation topic."
        
        # Build context with focus on topic continuity
        context_lines = []
        
        # Get last few exchanges for context
        recent_messages = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
        
        # Identify the main disorder being discussed
        all_content = " ".join([msg['content'].lower() for msg in recent_messages])
        main_disorder = None
        
        if "ptsd" in all_content or "posttraumatic stress" in all_content:
            main_disorder = "PTSD"
        elif "borderline personality" in all_content or "f60.3" in all_content:
            main_disorder = "Borderline Personality Disorder"
        elif "major depressive" in all_content or "depression" in all_content:
            main_disorder = "Major Depressive Disorder"
        
        if main_disorder:
            context_lines.append(f"CONTEXT: Ongoing discussion about {main_disorder}.")
            
            # Check if this is a follow-up question
            follow_up_indicators = ["treatment", "therapy", "medication", "prognosis", "how", "what about", "also", "additionally"]
            if any(indicator in query.lower() for indicator in follow_up_indicators):
                context_lines.append(f"This appears to be a follow-up question about {main_disorder}.")
        else:
            context_lines.append("CONTEXT: This appears to be a new topic.")
        
        # Add recent exchange for reference
        if len(recent_messages) >= 2:
            last_user = next((msg['content'] for msg in reversed(recent_messages) if msg['role'] == 'user'), "")
            if last_user and last_user != query:
                context_lines.append(f"Previous question: {last_user[:100]}...")
        
        return "\n".join(context_lines) + "\n"

    def _filter_relevant_docs(self, docs, query: str, conversation_history: list = None):
        """Filter documents to only include those relevant to the specific disorder queried."""
        query_lower = query.lower()
        
        # Check conversation history for context about what disorder we're discussing
        target_disorder = None
        
        # First check if there's context from conversation
        if conversation_history:
            recent_content = " ".join([msg['content'].lower() for msg in conversation_history[-3:]])
            if "ptsd" in recent_content or "posttraumatic stress" in recent_content:
                target_disorder = "ptsd"
            elif "borderline personality" in recent_content or "f60.3" in recent_content:
                target_disorder = "borderline"
            elif "major depressive" in recent_content or "depression" in recent_content:
                target_disorder = "major depressive"
            elif "intermittent explosive" in recent_content or "f63.81" in recent_content:
                target_disorder = "intermittent explosive"
        
        # Then check current query
        if "ptsd" in query_lower or "posttraumatic stress" in query_lower:
            target_disorder = "ptsd"
        elif "borderline personality disorder" in query_lower or "f60.3" in query_lower:
            target_disorder = "borderline"
        elif "major depressive disorder" in query_lower or "depression" in query_lower:
            target_disorder = "major depressive"
        elif "intermittent explosive" in query_lower or "f63.81" in query_lower:
            target_disorder = "intermittent explosive"
        elif "treatment" in query_lower or "therapy" in query_lower or "medication" in query_lower:
            # For treatment questions, keep the same disorder from context
            pass
        
        logger.info(f"🟡 FILTER: Target disorder: {target_disorder}")
        
        if not target_disorder:
            logger.info(f"🟡 FILTER: No specific disorder detected, returning top 3 docs")
            return docs[:3]
        
        # Filter documents
        filtered_docs = []
        for doc in docs:
            doc_content_lower = doc.page_content.lower()
            if target_disorder in doc_content_lower:
                filtered_docs.append(doc)
        
        logger.info(f"🟡 FILTER: Filtered from {len(docs)} to {len(filtered_docs)} documents")
        return filtered_docs[:5] if filtered_docs else docs[:3]

    def _create_contextual_preview(self, content: str, disorder_name: str, section_type: str) -> str:
        """Create a contextual preview that provides better understanding of the citation content."""
        # Parse structured content to get clean text
        clean_content = content
        if content.startswith('DOCUMENT:'):
            parts = content.split(';')
            text_part = next((p for p in parts if p.strip().startswith('TEXT:')), None)
            criteria_part = next((p for p in parts if p.strip().startswith('CRITERIA:')), None)
            if text_part:
                clean_content = text_part.replace('TEXT:', '').strip()
            elif criteria_part:
                clean_content = criteria_part.replace('CRITERIA:', '').strip()
        
        # Find a good starting point for the preview
        sentences = clean_content.split('. ')
        
        # Look for sentences that start with context-providing words
        good_starts = []
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower().strip()
            # Look for sentences that provide good context
            if any(starter in sentence_lower for starter in [
                'diagnostic criteria', 'the essential', 'characterized by', 
                'symptoms include', 'must be present', 'requires', 
                'differential diagnosis', 'prevalence', 'development'
            ]):
                good_starts.append(i)
        
        # Use the first good starting point, or start from beginning
        start_idx = good_starts[0] if good_starts else 0
        
        # Create preview with context
        preview_sentences = sentences[start_idx:start_idx + 3]  # Take 3 sentences for context
        preview = '. '.join(preview_sentences)
        
        # Add section context if available
        if section_type and section_type != 'General':
            preview = f"[{section_type}] {preview}"
        
        # Ensure reasonable length (400-500 chars for better context)
        if len(preview) > 500:
            preview = preview[:497] + "..."
        elif len(preview) < 100 and len(clean_content) > len(preview):
            # If preview is too short, extend it
            preview = clean_content[:400] + "..." if len(clean_content) > 400 else clean_content
        
        return preview

    def process_query(self, query: str, conversation_history: list = None) -> Dict[str, Any]:
        """
        Process a patient query and return structured response.
        
        Args:
            query: The current user query
            conversation_history: List of previous messages [{'role': 'user/assistant', 'content': '...'}]
        """
        try:
            logger.info(f"🟡 AGENT: Starting query processing: {query[:100]}...")
            
            # Build intelligent context from conversation history
            context_prefix = self._build_conversation_context(query, conversation_history)
            
            # Check if this is a BPD F60.3 query - use direct approach
            if "borderline personality disorder" in query.lower() or "f60.3" in query.lower():
                logger.info("🟡 AGENT: Detected BPD query, using direct criteria")
                
                # Return the exact DSM-5-TR criteria with natural language
                response = """**Borderline Personality Disorder (F60.3) - DSM-5-TR Diagnostic Criteria**^1

A pervasive pattern of instability of interpersonal relationships, self-image, and affects, and marked impulsivity, beginning by early adulthood and present in a variety of contexts, as indicated by five (or more) of the following:

1. Frantic efforts to avoid real or imagined abandonment. (Note: Do not include suicidal or self-mutilating behavior covered in Criterion 5.)

2. A pattern of unstable and intense interpersonal relationships characterized by alternating between extremes of idealization and devaluation.

3. Identity disturbance: markedly and persistently unstable self-image or sense of self.

4. Impulsivity in at least two areas that are potentially self-damaging (e.g., spending, sex, substance abuse, reckless driving, binge eating). (Note: Do not include suicidal or self-mutilating behavior covered in Criterion 5.)

5. Recurrent suicidal behavior, gestures, or threats, or self-mutilating behavior.

6. Affective instability due to a marked reactivity of mood (e.g., intense episodic dysphoria, irritability, or anxiety usually lasting a few hours and only rarely more than a few days).

7. Chronic feelings of emptiness.

8. Inappropriate, intense anger or difficulty controlling anger (e.g., frequent displays of temper, constant anger, recurrent physical fights).

9. Transient, stress-related paranoid ideation or severe dissociative symptoms.^1"""

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
            filtered_docs = self._filter_relevant_docs(docs, query, conversation_history)
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
                    "conversation_context": lambda _: context_prefix,
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
            
            # Format citations from filtered documents with hierarchical metadata
            citations = []
            for i, doc in enumerate(filtered_docs, 1):
                # Extract hierarchical metadata from document
                metadata = doc.metadata
                content = doc.page_content
                preview = content[:200] + "..." if len(content) > 200 else content
                
                # Extract disorder info from metadata or content
                disorder_name = metadata.get('disorder_name', 'Unknown Disorder')
                icd_code = metadata.get('icd_code', '')
                section_type = metadata.get('section_type', 'General')
                chunk_type = metadata.get('chunk_type', 'unknown')
                hierarchy_path = metadata.get('hierarchy_path', f'DSM-5-TR > {disorder_name}')
                page_number = metadata.get('page', None)
                
                # Parse structured content to extract disorder info
                if content.startswith('DOCUMENT:'):
                    parts = content.split(';')
                    for part in parts:
                        part = part.strip()
                        if part.startswith('DISORDER:'):
                            disorder_name = part.replace('DISORDER:', '').strip()
                        elif part.startswith('SECTION:'):
                            section_type = part.replace('SECTION:', '').strip()
                
                # Fallback extraction if still missing
                if disorder_name == 'Unknown Disorder':
                    if "borderline personality disorder" in content.lower():
                        disorder_name = "Borderline Personality Disorder"
                        icd_code = "F60.3"
                    elif "major depressive disorder" in content.lower():
                        disorder_name = "Major Depressive Disorder"
                        icd_code = "F32.9"
                    elif "intermittent explosive disorder" in content.lower():
                        disorder_name = "Intermittent Explosive Disorder" 
                        icd_code = "F63.81"
                    elif "ptsd" in content.lower() or "posttraumatic stress" in content.lower():
                        disorder_name = "Posttraumatic Stress Disorder"
                        icd_code = "F43.10"
                
                # Build proper hierarchy path
                if disorder_name != 'Unknown Disorder':
                    if section_type and section_type != 'General':
                        hierarchy_path = f"DSM-5-TR > {disorder_name} > {section_type}"
                    else:
                        hierarchy_path = f"DSM-5-TR > {disorder_name}"
                
                # Create hierarchical citation structure
                citations.append({
                    "id": i,
                    "document": "DSM-5-TR",
                    "disorder_name": disorder_name,
                    "icd_code": icd_code,
                    "section_type": section_type,
                    "chunk_type": chunk_type,
                    "hierarchy_path": hierarchy_path,
                    "page": page_number,
                    "content": f"Diagnostic criteria for {disorder_name}",
                    "full_content": content,
                    "source": "DSM-5-TR",
                    "preview": self._create_contextual_preview(content, disorder_name, section_type),
                    # Add parent-child context
                    "parent_context": hierarchy_path.split(' > ')[:-1] if ' > ' in hierarchy_path else [],
                    "child_context": section_type if chunk_type == 'child' else None
                })
            
            # Add inline citation markers to response (industry standard)
            if citations:
                # Add citation markers at the end of key statements
                response_with_citations = response
                # Simple approach: add citation markers after periods for key diagnostic information
                import re
                sentences = re.split(r'(?<=\.)\s+', response)
                if len(sentences) > 1:
                    # Add citation to first major sentence about criteria
                    for i, sentence in enumerate(sentences):
                        if any(word in sentence.lower() for word in ['criteria', 'disorder', 'diagnosis', 'symptoms']):
                            sentences[i] = sentence.rstrip() + f"^{citations[0]['id']}"
                            break
                    response_with_citations = ' '.join(sentences)
                else:
                    # Single sentence or paragraph - add citation at end
                    response_with_citations = response.rstrip() + f"^{citations[0]['id']}"
                
                response = response_with_citations
            
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
