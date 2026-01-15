# RAG Architecture - Psych Agent

## Overview

The Psych Agent now uses a **RAG (Retrieval-Augmented Generation)** architecture that combines:
- **ChromaDB** vector database with hierarchical DSM-5-TR content
- **Groq** LLM for response generation
- **Detailed citation system** with expandable references

## Architecture Flow

```
User Query
    ↓
RAG Service
    ↓
1. Vector Search (ChromaDB)
   - Semantic search in DSM-5-TR
   - Retrieve top 5 relevant chunks
   - Extract metadata (ICD codes, disorder names, sections)
    ↓
2. Citation Formatting
   - Format retrieved docs as structured citations
   - Include hierarchy paths, ICD codes, page numbers
    ↓
3. Context Building
   - Combine retrieved content into context
   - Add conversation history (last 4 messages)
    ↓
4. LLM Generation (Groq)
   - Generate response with inline citations (^1, ^2, etc.)
   - Base answer strictly on retrieved sources
    ↓
Response + Citations
```

## Key Components

### 1. RAG Service (`backend/app/services/rag_service.py`)

**Primary service** that orchestrates the RAG pipeline:

- `process_query()`: Main entry point
- `_format_citations()`: Converts vector DB results to citation objects
- `_build_context()`: Creates context string for LLM
- `_generate_response()`: Calls Groq with context and instructions

**Citation Format:**
```python
{
    "id": 1,
    "content": "Preview text (200 chars)...",
    "full_content": "Complete chunk text",
    "source": "DSM-5-TR",
    "page": 123,
    "disorder_name": "Major Depressive Disorder",
    "icd_code": "F32.0",
    "section_type": "Diagnostic Criteria",
    "hierarchy_path": "DSM-5-TR > Depressive Disorders > Major Depressive Disorder"
}
```

### 2. Vector Service (`backend/app/services/vector_service.py`)

Manages ChromaDB interactions:
- Loads embeddings (HuggingFace all-MiniLM-L6-v2)
- Performs similarity search
- Returns documents with metadata

### 3. Cloud Agent Service (`backend/app/services/cloud_agent_service.py`)

**Updated** to use RAG as primary method:
- `_process_with_rag()`: Uses RAG service (primary)
- `_process_llm_only()`: Fallback without vector search
- Passes conversation history for context

### 4. Groq Service (`backend/app/services/groq_service.py`)

LLM interface for response generation:
- Uses `llama-3.3-70b-versatile` model
- Streaming support
- Temperature: 0.1 (deterministic)

## Citation System

### Inline Citations

The LLM is instructed to use `^N` notation:
```
Major Depressive Disorder requires five symptoms^1, including depressed mood^2.
```

### Frontend Rendering

`MessageList.tsx` component:
- Parses `^N` patterns in markdown
- Renders as clickable superscript buttons
- Expands full citation details on click
- Shows hierarchy path, ICD codes, metadata

### Citation Details Display

Each citation shows:
- **Source document**: DSM-5-TR
- **Hierarchy path**: Mental Health Condition > Section
- **ICD code**: With visual badge
- **Page number**: If available
- **Content**: Preview + expandable full text

## Configuration

### Environment Variables

```bash
# Enable/disable RAG
USE_RAG=true

# Vector database path
VECTOR_DB_PATH=../vector_db_hierarchical

# Groq API
GROQ_API_KEY=your_key_here

# Embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Toggle RAG On/Off

Set `USE_RAG=false` to fall back to LLM-only mode (no citations).

## Advantages of This Architecture

### 1. **Accuracy**
- Responses grounded in actual DSM-5-TR content
- Reduces hallucinations
- Verifiable sources

### 2. **Citations**
- Every claim is traceable
- Detailed metadata for clinical use
- Expandable references

### 3. **Privacy**
- ChromaDB runs locally
- No patient data sent to external vector DB
- Only LLM calls go to Groq

### 4. **Cost-Effective**
- No Pinecone subscription needed
- Only pay for Groq LLM tokens
- Local embeddings

### 5. **Extensible**
- Easy to add more knowledge sources
- Can integrate GraphRAG later
- Tool calling for external APIs

## Future Enhancements

### Phase 2: GraphRAG
```python
# Add relationship-based retrieval
graph_service.find_related_disorders(disorder_name)
graph_service.get_differential_diagnosis(symptoms)
```

### Phase 3: External Tools
```python
# Tool calling for:
- PubMed literature search
- Drug interaction databases
- Clinical calculators
```

### Phase 4: Multi-Source RAG
```python
# Combine multiple knowledge bases:
- DSM-5-TR (primary)
- ICD-11 guidelines
- Clinical practice guidelines
- Research papers
```

## Testing the RAG System

### 1. Test Vector Search
```python
from app.services.vector_service import VectorService

vs = VectorService()
results = vs.similarity_search("Major Depressive Disorder criteria", k=3)
for doc in results:
    print(doc.metadata)
    print(doc.page_content[:200])
```

### 2. Test RAG Pipeline
```python
from app.services.rag_service import rag_service

response = rag_service.process_query("What are the criteria for MDD?")
print(response["response"])
print(f"Citations: {len(response['citations'])}")
```

### 3. Test End-to-End
```bash
# Start backend
cd backend
python -m app.main

# Start frontend
cd frontend
npm run dev

# Ask: "What are the DSM-5-TR criteria for Borderline Personality Disorder?"
```

## Monitoring & Debugging

### Enable Debug Logging
```python
# In rag_service.py
print(f"Retrieved {len(relevant_docs)} documents")
print(f"Generated {len(citations)} citations")
```

### Check Vector DB
```bash
# Verify vector DB exists
ls -lh vector_db_hierarchical/

# Check collection
python -c "
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
db = Chroma(persist_directory='vector_db_hierarchical', embedding_function=embeddings)
print(f'Collection count: {db._collection.count()}')
"
```

## Troubleshooting

### No Citations Returned
- Check `USE_RAG=true` in `.env`
- Verify `vector_db_hierarchical/` exists
- Test vector search directly

### Poor Quality Responses
- Increase `k` parameter (retrieve more docs)
- Adjust LLM temperature
- Refine system prompt

### Slow Performance
- Reduce `k` parameter
- Use smaller embedding model
- Cache frequent queries

## Performance Metrics

**Current Setup:**
- Vector search: ~100-200ms
- LLM generation: ~2-5s (streaming)
- Total latency: ~2-5s
- Citations per response: 3-5

**Optimization Targets:**
- Vector search: <100ms
- LLM generation: <2s
- Total latency: <2s

## Comparison: RAG vs LLM-Only

| Aspect | RAG (Current) | LLM-Only (Fallback) |
|--------|---------------|---------------------|
| Accuracy | High (grounded) | Medium (may hallucinate) |
| Citations | Yes (detailed) | No |
| Latency | ~2-5s | ~1-2s |
| Cost | Low (local DB) | Very low |
| Privacy | High | High |
| Verifiability | High | Low |

## Conclusion

The RAG architecture provides:
✅ **Accurate** responses based on DSM-5-TR
✅ **Detailed citations** for clinical verification
✅ **Privacy-preserving** local vector database
✅ **Cost-effective** compared to cloud vector DBs
✅ **Extensible** for future enhancements

This is the **recommended approach** for clinical decision support where accuracy and verifiability are critical.
