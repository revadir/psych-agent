"""
Advanced DSM-5-TR ingestion with hierarchical parent-child chunking.
"""

import os
import re
from typing import List, Dict, Any
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Configuration
DATA_PATH = "data/dsm5-tr.pdf"
DB_PATH = "vector_db_hierarchical"


class DSMHierarchicalChunker:
    """Advanced chunker for DSM-5-TR with parent-child structure."""
    
    def __init__(self):
        self.disorder_patterns = [
            r'([A-Z][a-z\s]+(?:Disorder|Syndrome|Condition))\s*\n.*?Diagnostic Criteria',
            r'F\d+\.\d+\s*\n([A-Z][a-z\s]+(?:Disorder|Syndrome|Condition))',
        ]
        
    def extract_disorder_info(self, content: str) -> Dict[str, str]:
        """Extract disorder name and ICD code from content."""
        # Look for ICD-10 codes
        icd_match = re.search(r'F(\d+)\.(\d+)', content)
        icd_code = icd_match.group(0) if icd_match else None
        
        # Look for disorder names
        disorder_name = None
        for pattern in self.disorder_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                disorder_name = match.group(1).strip()
                break
        
        # Common disorder names to look for
        common_disorders = [
            "Major Depressive Disorder", "Generalized Anxiety Disorder", 
            "Borderline Personality Disorder", "Bipolar I Disorder", "Bipolar II Disorder",
            "Schizophrenia", "Autism Spectrum Disorder", "ADHD", "PTSD", "OCD"
        ]
        
        if not disorder_name:
            for disorder in common_disorders:
                if disorder in content:
                    disorder_name = disorder
                    break
        
        return {
            "disorder_name": disorder_name,
            "icd_code": icd_code
        }
    
    def identify_section_type(self, text: str) -> str:
        """Identify the type of section based on content."""
        text_lower = text.lower()
        
        if "diagnostic criteria" in text_lower:
            return "Diagnostic Criteria"
        elif "differential diagnosis" in text_lower:
            return "Differential Diagnosis"
        elif "prevalence" in text_lower:
            return "Prevalence"
        elif "development and course" in text_lower:
            return "Development and Course"
        elif "risk and prognostic factors" in text_lower:
            return "Risk and Prognostic Factors"
        elif "culture-related" in text_lower:
            return "Culture-Related Diagnostic Issues"
        elif "associated features" in text_lower:
            return "Associated Features"
        elif "comorbidity" in text_lower:
            return "Comorbidity"
        else:
            return "General"
    
    def create_parent_child_chunks(self, docs: List[Document]) -> List[Document]:
        """Create hierarchical parent-child chunks."""
        chunks = []
        
        for doc in docs:
            content = doc.page_content
            
            # Skip pages without substantial content
            if len(content.strip()) < 200:
                continue
            
            # Extract disorder information
            disorder_info = self.extract_disorder_info(content)
            
            # Look for diagnostic criteria sections
            if "Diagnostic Criteria" in content and disorder_info["disorder_name"]:
                # This is a key diagnostic page
                disorder_name = disorder_info["disorder_name"]
                icd_code = disorder_info["icd_code"]
                
                # Create PARENT chunk (full disorder context)
                parent_metadata = {
                    **doc.metadata,
                    "chunk_type": "parent",
                    "disorder_name": disorder_name,
                    "icd_code": icd_code,
                    "section_type": "Complete Disorder",
                    "hierarchy_path": f"DSM-5-TR > {disorder_name}"
                }
                
                # Add contextual prepending to parent
                parent_content = f"DOCUMENT: DSM-5-TR; DISORDER: {disorder_name}; ICD-10: {icd_code}; COMPLETE_ENTRY: {content}"
                
                chunks.append(Document(
                    page_content=parent_content,
                    metadata=parent_metadata
                ))
                
                # Create CHILD chunks for specific sections
                sections = self._split_into_sections(content, disorder_name, icd_code, doc.metadata)
                chunks.extend(sections)
            
            elif disorder_info["disorder_name"]:
                # This has disorder content but no diagnostic criteria
                disorder_name = disorder_info["disorder_name"]
                section_type = self.identify_section_type(content)
                
                child_metadata = {
                    **doc.metadata,
                    "chunk_type": "child",
                    "disorder_name": disorder_name,
                    "icd_code": disorder_info["icd_code"],
                    "section_type": section_type,
                    "hierarchy_path": f"DSM-5-TR > {disorder_name} > {section_type}"
                }
                
                # Add contextual prepending
                child_content = f"DOCUMENT: DSM-5-TR; DISORDER: {disorder_name}; SECTION: {section_type}; TEXT: {content}"
                
                chunks.append(Document(
                    page_content=child_content,
                    metadata=child_metadata
                ))
        
        return chunks
    
    def _split_into_sections(self, content: str, disorder_name: str, icd_code: str, base_metadata: Dict) -> List[Document]:
        """Split disorder content into logical sections."""
        sections = []
        
        # Find diagnostic criteria section
        criteria_match = re.search(r'(Diagnostic Criteria.*?)(?=\n[A-Z][a-z]|\n\d+\.|\Z)', content, re.DOTALL)
        if criteria_match:
            criteria_text = criteria_match.group(1).strip()
            
            # NEVER split diagnostic criteria - keep as one chunk
            criteria_metadata = {
                **base_metadata,
                "chunk_type": "child",
                "disorder_name": disorder_name,
                "icd_code": icd_code,
                "section_type": "Diagnostic Criteria",
                "hierarchy_path": f"DSM-5-TR > {disorder_name} > Diagnostic Criteria"
            }
            
            # Add contextual prepending with emphasis on diagnostic criteria
            criteria_content = f"DOCUMENT: DSM-5-TR; DISORDER: {disorder_name}; ICD-10: {icd_code}; SECTION: Diagnostic Criteria; CRITERIA: {criteria_text}"
            
            sections.append(Document(
                page_content=criteria_content,
                metadata=criteria_metadata
            ))
        
        # Find other sections
        section_patterns = [
            (r'(Differential Diagnosis.*?)(?=\n[A-Z][a-z]|\Z)', "Differential Diagnosis"),
            (r'(Associated Features.*?)(?=\n[A-Z][a-z]|\Z)', "Associated Features"),
            (r'(Prevalence.*?)(?=\n[A-Z][a-z]|\Z)', "Prevalence"),
            (r'(Development and Course.*?)(?=\n[A-Z][a-z]|\Z)', "Development and Course"),
        ]
        
        for pattern, section_name in section_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                section_text = match.group(1).strip()
                
                section_metadata = {
                    **base_metadata,
                    "chunk_type": "child",
                    "disorder_name": disorder_name,
                    "icd_code": icd_code,
                    "section_type": section_name,
                    "hierarchy_path": f"DSM-5-TR > {disorder_name} > {section_name}"
                }
                
                # Add contextual prepending
                section_content = f"DOCUMENT: DSM-5-TR; DISORDER: {disorder_name}; SECTION: {section_name}; TEXT: {section_text}"
                
                sections.append(Document(
                    page_content=section_content,
                    metadata=section_metadata
                ))
        
        return sections


def build_hierarchical_vector_store():
    """Build hierarchical vector store with parent-child chunks."""
    print("🔄 Loading DSM-5-TR PDF...")
    loader = PyMuPDFLoader(DATA_PATH)
    docs = loader.load()
    print(f"📄 Loaded {len(docs)} pages")

    print("🔄 Creating hierarchical chunks...")
    chunker = DSMHierarchicalChunker()
    hierarchical_chunks = chunker.create_parent_child_chunks(docs)
    print(f"📦 Created {len(hierarchical_chunks)} hierarchical chunks")
    
    # Count chunk types
    parent_count = sum(1 for chunk in hierarchical_chunks if chunk.metadata.get("chunk_type") == "parent")
    child_count = sum(1 for chunk in hierarchical_chunks if chunk.metadata.get("chunk_type") == "child")
    print(f"   - {parent_count} parent chunks (full disorders)")
    print(f"   - {child_count} child chunks (specific sections)")

    print("🔄 Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("🔄 Building hierarchical vector database...")
    # Remove old database
    if os.path.exists(DB_PATH):
        import shutil
        shutil.rmtree(DB_PATH)
    
    vector_db = Chroma.from_documents(
        documents=hierarchical_chunks, 
        embedding=embeddings, 
        persist_directory=DB_PATH
    )
    
    print(f"✅ Hierarchical vector database created!")
    
    # Test searches
    test_queries = [
        "Borderline Personality Disorder diagnostic criteria",
        "BPD F60.3 criteria",
        "frantic efforts to avoid abandonment",
        "Major Depressive Disorder symptoms"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        results = vector_db.similarity_search(query, k=2)
        
        for i, result in enumerate(results):
            print(f"  📋 Result {i+1}:")
            print(f"    Disorder: {result.metadata.get('disorder_name', 'Unknown')}")
            print(f"    Section: {result.metadata.get('section_type', 'Unknown')}")
            print(f"    Type: {result.metadata.get('chunk_type', 'Unknown')}")
            print(f"    Content: {result.page_content[:150]}...")


if __name__ == "__main__":
    build_hierarchical_vector_store()
