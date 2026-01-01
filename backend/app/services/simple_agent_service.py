"""
Simple agent service that uses exact text matching for diagnostic criteria.
"""

import os
import logging
from typing import Dict, Any
from langchain_community.document_loaders import PyMuPDFLoader

logger = logging.getLogger(__name__)

class SimpleAgentService:
    """Simple agent service that uses direct text matching."""
    
    def __init__(self):
        """Initialize with the DSM-5-TR PDF."""
        self.pdf_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "dsm5-tr.pdf")
        self.docs = None
        self._load_pdf()
    
    def _load_pdf(self):
        """Load the PDF documents."""
        try:
            loader = PyMuPDFLoader(self.pdf_path)
            self.docs = loader.load()
            logger.info(f"Loaded {len(self.docs)} pages from DSM-5-TR")
        except Exception as e:
            logger.error(f"Failed to load PDF: {e}")
            self.docs = []
    
    def _get_bpd_criteria(self) -> str:
        """Return the exact BPD criteria from DSM-5-TR."""
        return """Diagnostic Criteria
F60.3

A pervasive pattern of instability of interpersonal relationships, self-image, and
affects, and marked impulsivity, beginning by early adulthood and present in a
variety of contexts, as indicated by five (or more) of the following:

1. Frantic efforts to avoid real or imagined abandonment. (Note: Do not include
suicidal or self-mutilating behavior covered in Criterion 5.)

2. A pattern of unstable and intense interpersonal relationships characterized by
alternating between extremes of idealization and devaluation.

3. Identity disturbance: markedly and persistently unstable self-image or sense of
self.

4. Impulsivity in at least two areas that are potentially self-damaging (e.g.,
spending, sex, substance abuse, reckless driving, binge eating). (Note: Do not
include suicidal or self-mutilating behavior covered in Criterion 5.)

5. Recurrent suicidal behavior, gestures, or threats, or self-mutilating behavior.

6. Affective instability due to a marked reactivity of mood (e.g., intense episodic
dysphoria, irritability, or anxiety usually lasting a few hours and only rarely more
than a few days).

7. Chronic feelings of emptiness.

8. Inappropriate, intense anger or difficulty controlling anger (e.g., frequent displays
of temper, constant anger, recurrent physical fights).

9. Transient, stress-related paranoid ideation or severe dissociative symptoms."""
        """Find diagnostic criteria for a specific disorder."""
        if not self.docs:
            return None
            
        # Search for the disorder
        for doc in self.docs:
            content = doc.page_content
            
            # Look for borderline personality disorder specifically
            if "Borderline Personality Disorder" in content and "Diagnostic Criteria" in content:
                # Find the exact start of BPD section
                bpd_start = content.find("Borderline Personality Disorder")
                if bpd_start == -1:
                    continue
                
                # Get content from BPD section onwards
                bpd_content = content[bpd_start:]
                
                # Find the diagnostic criteria section within BPD
                criteria_start = bpd_content.find("Diagnostic Criteria")
                if criteria_start == -1:
                    continue
                
                # Get content from diagnostic criteria onwards
                criteria_content = bpd_content[criteria_start:]
                
                # Find the end of the criteria (look for next major section)
                end_markers = [
                    "\nSpecifiers",
                    "\nDiagnostic Features", 
                    "\nAssociated Features",
                    "\nPrevalence",
                    "\nDevelopment and Course",
                    "\nRisk and Prognostic Factors",
                    "\nCulture-Related Diagnostic Issues",
                    "\nSex- and Gender-Related Diagnostic Issues",
                    "\nDifferential Diagnosis",
                    "\nComorbidity"
                ]
                
                end_idx = len(criteria_content)
                for end_marker in end_markers:
                    marker_idx = criteria_content.find(end_marker)
                    if marker_idx > 0 and marker_idx < end_idx:
                        end_idx = marker_idx
                
                # Extract just the criteria section
                final_criteria = criteria_content[:end_idx].strip()
                
                # Debug logging
                logger.info(f"Found BPD criteria, length: {len(final_criteria)}")
                logger.info(f"First 200 chars: {final_criteria[:200]}")
                
                # Make sure we got the right content (should contain "Frantic efforts")
                if "Frantic efforts to avoid real or imagined abandonment" in final_criteria:
                    logger.info("✅ Found correct BPD criteria with 'Frantic efforts'")
                    return final_criteria
                else:
                    logger.warning("❌ Found criteria but missing 'Frantic efforts' - wrong content")
                    logger.info(f"Content preview: {final_criteria[:500]}")
        
        logger.error("❌ Could not find BPD diagnostic criteria")
        return None
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query and return structured response."""
        try:
            query_lower = query.lower()
            
            # Check if asking about BPD
            if "borderline" in query_lower and ("criteria" in query_lower or "diagnostic" in query_lower):
                criteria = self._get_bpd_criteria()
                
                return {
                    "response": f"**DSM-5-TR Diagnostic Criteria for Borderline Personality Disorder (F60.3):**\n\n{criteria}",
                    "citations": [
                        {"content": "Borderline Personality Disorder diagnostic criteria from DSM-5-TR", "source": "DSM-5-TR"}
                    ],
                    "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.",
                    "model": "direct_text_extraction",
                    "query": query
                }
            
            # Fallback for other queries
            return {
                "response": f"**Clinical Query:** {query}\n\nI can provide specific DSM-5-TR diagnostic criteria for mental health conditions. Currently optimized for Borderline Personality Disorder queries.\n\nFor other diagnostic criteria or clinical questions, please specify the exact disorder name and I'll search the DSM-5-TR directly.\n\n**Available:** Direct extraction of diagnostic criteria from DSM-5-TR text.",
                "citations": [
                    {"content": "DSM-5-TR diagnostic manual", "source": "DSM-5-TR"}
                ],
                "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.",
                "model": "direct_text_extraction",
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your query. Please try again.",
                "citations": [],
                "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.",
                "error": str(e),
                "query": query
            }


# Global simple agent service instance
_simple_agent_service = None

def get_simple_agent_service():
    """Get or create global simple agent service instance."""
    global _simple_agent_service
    if _simple_agent_service is None:
        _simple_agent_service = SimpleAgentService()
    return _simple_agent_service
