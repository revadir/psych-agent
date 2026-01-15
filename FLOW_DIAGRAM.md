# RAG System Flow Diagram

## Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE (React)                          │
│  "What are the DSM-5-TR criteria for Major Depressive Disorder?"       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      CHAT API (FastAPI)                                 │
│  - Receives query                                                       │
│  - Loads conversation history (last 4 messages)                         │
│  - Calls cloud_agent_service.process_query()                            │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   CLOUD AGENT SERVICE                                   │
│  Decision: USE_RAG=true?                                                │
│    ├─ Yes → _process_with_rag()                                         │
│    └─ No  → _process_llm_only()                                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        RAG SERVICE                                      │
│                                                                         │
│  STEP 1: Vector Search                                                  │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ VectorService.similarity_search(query, k=5)                   │     │
│  │   ↓                                                            │     │
│  │ ChromaDB (vector_db_hierarchical/)                            │     │
│  │   - Semantic search using embeddings                          │     │
│  │   - Returns top 5 relevant chunks                             │     │
│  │   - Each with metadata (ICD code, disorder, section, etc.)    │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                 │                                       │
│                                 ▼                                       │
│  STEP 2: Format Citations                                              │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ _format_citations(docs)                                       │     │
│  │   - Extract metadata from each document                       │     │
│  │   - Create citation objects with:                             │     │
│  │     * id, disorder_name, icd_code                             │     │
│  │     * section_type, hierarchy_path                            │     │
│  │     * content (preview), full_content                         │     │
│  │     * page number, source                                     │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                 │                                       │
│                                 ▼                                       │
│  STEP 3: Build Context                                                 │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ _build_context(docs)                                          │     │
│  │   - Combine retrieved documents                               │     │
│  │   - Format as: [Source 1] Disorder (ICD) \n Content          │     │
│  │   - Add conversation history (last 4 messages)                │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                 │                                       │
│                                 ▼                                       │
│  STEP 4: Generate Response                                             │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ _generate_response(query, context, history)                   │     │
│  │   ↓                                                            │     │
│  │ Groq LLM (llama-3.3-70b-versatile)                            │     │
│  │   - System prompt: "Use inline citations ^1, ^2, ^3"          │     │
│  │   - Context: Retrieved DSM-5-TR content                       │     │
│  │   - History: Last 4 conversation messages                     │     │
│  │   - Query: User's question                                    │     │
│  │   ↓                                                            │     │
│  │ Response with inline citations                                │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         RESPONSE OBJECT                                 │
│  {                                                                      │
│    "response": "MDD requires five symptoms^1, including depressed       │
│                 mood^2 or anhedonia^3...",                              │
│    "citations": [                                                       │
│      {                                                                  │
│        "id": 1,                                                         │
│        "disorder_name": "Major Depressive Disorder",                    │
│        "icd_code": "F32.0",                                             │
│        "section_type": "Diagnostic Criteria",                           │
│        "hierarchy_path": "DSM-5-TR > Depressive Disorders > MDD",      │
│        "page": 155,                                                     │
│        "content": "Preview text...",                                    │
│        "full_content": "Complete diagnostic criteria..."                │
│      },                                                                 │
│      ...                                                                │
│    ]                                                                    │
│  }                                                                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CHAT API (Save to DB)                                │
│  - Save user message                                                    │
│  - Save assistant message with citations                                │
│  - Stream response to frontend                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND RENDERING                                   │
│                                                                         │
│  MessageList.tsx:                                                       │
│  1. Parse inline citations (^1, ^2, ^3)                                 │
│  2. Render as clickable superscript buttons                             │
│  3. Display citation cards below response                               │
│  4. Show expandable details:                                            │
│     - Source document (DSM-5-TR)                                        │
│     - Hierarchy path with icons                                         │
│     - ICD code badge                                                    │
│     - Section type                                                      │
│     - Page number                                                       │
│     - Preview + expandable full content                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Example

### Input
```
Query: "What are the DSM-5-TR criteria for Major Depressive Disorder?"
```

### Vector Search Results (ChromaDB)
```
[1] Persistent Depressive Disorder (F34.1)
    Section: Diagnostic Criteria
    Content: "DOCUMENT: DSM-5-TR; DISORDER: Persistent Depressive Disorder..."
    
[2] Induced Depressive Disorder
    Section: Diagnostic Criteria
    Content: "DOCUMENT: DSM-5-TR; DISORDER: Induced Depressive Disorder..."
    
[3] Major Depressive Disorder (F32.0)
    Section: Diagnostic Criteria
    Content: "A. Five (or more) of the following symptoms..."
```

### Context Built for LLM
```
[Source 1] Persistent Depressive Disorder (F34.1)
DOCUMENT: DSM-5-TR; DISORDER: Persistent Depressive Disorder...

[Source 2] Induced Depressive Disorder
DOCUMENT: DSM-5-TR; DISORDER: Induced Depressive Disorder...

[Source 3] Major Depressive Disorder (F32.0)
A. Five (or more) of the following symptoms...

Question: What are the DSM-5-TR criteria for Major Depressive Disorder?
```

### LLM Response (Groq)
```
Major Depressive Disorder (MDD) is characterized by a prominent and 
persistent disturbance in mood^3. The diagnostic criteria include:

A. Five (or more) of the following symptoms^3:
   1. Depressed mood most of the day^3
   2. Markedly diminished interest or pleasure^3
   3. Significant weight loss or gain^3
   ...

The symptoms must cause clinically significant distress^3 and not be 
attributable to substance use^1 or another medical condition^2.
```

### Citations Returned
```json
[
  {
    "id": 1,
    "disorder_name": "Persistent Depressive Disorder",
    "icd_code": "F34.1",
    "section_type": "Diagnostic Criteria",
    "hierarchy_path": "DSM-5-TR > Persistent Depressive Disorder > Diagnostic Criteria",
    "page": 319,
    "content": "DOCUMENT: DSM-5-TR; DISORDER: Persistent Depressive Disorder...",
    "full_content": "..."
  },
  {
    "id": 2,
    "disorder_name": "Induced Depressive Disorder",
    "section_type": "Diagnostic Criteria",
    "hierarchy_path": "DSM-5-TR > Induced Depressive Disorder > Diagnostic Criteria",
    "page": 329,
    "content": "DOCUMENT: DSM-5-TR; DISORDER: Induced Depressive Disorder...",
    "full_content": "..."
  },
  {
    "id": 3,
    "disorder_name": "Major Depressive Disorder",
    "icd_code": "F32.0",
    "section_type": "Diagnostic Criteria",
    "hierarchy_path": "DSM-5-TR > Depressive Disorders > Major Depressive Disorder",
    "page": 155,
    "content": "A. Five (or more) of the following symptoms...",
    "full_content": "..."
  }
]
```

### Frontend Display
```
┌─────────────────────────────────────────────────────────────┐
│ Major Depressive Disorder (MDD) is characterized by a      │
│ prominent and persistent disturbance in mood [3].           │
│                                                             │
│ The diagnostic criteria include:                            │
│ A. Five (or more) of the following symptoms [3]:            │
│    1. Depressed mood most of the day [3]                    │
│    2. Markedly diminished interest or pleasure [3]          │
│    ...                                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 📚 Sources                                                  │
├─────────────────────────────────────────────────────────────┤
│ [1] Persistent Depressive Disorder (F34.1)                  │
│     📄 DSM-5-TR                                             │
│     🏥 Mental Health Condition: Persistent Depressive...    │
│     📋 Section: Diagnostic Criteria                         │
│     🏷️ ICD-10: F34.1                                        │
│     📖 Page: 319                                            │
│     [Expand ▼]                                              │
├─────────────────────────────────────────────────────────────┤
│ [2] Induced Depressive Disorder                             │
│     ...                                                     │
├─────────────────────────────────────────────────────────────┤
│ [3] Major Depressive Disorder (F32.0)                       │
│     ...                                                     │
└─────────────────────────────────────────────────────────────┘
```

## Fallback Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Attempt                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─ Success → Return response + citations
                     │
                     ├─ Vector DB Error → Fall back to LLM-only
                     │                     (no citations)
                     │
                     └─ LLM Error → Return error message
```

## Performance Metrics

```
┌──────────────────────┬──────────┬──────────┐
│ Component            │ Latency  │ Notes    │
├──────────────────────┼──────────┼──────────┤
│ Vector Search        │ 100-200ms│ Local DB │
│ Citation Formatting  │ <10ms    │ Fast     │
│ Context Building     │ <10ms    │ Fast     │
│ LLM Generation       │ 2-5s     │ Streaming│
├──────────────────────┼──────────┼──────────┤
│ Total                │ 2-5s     │ Good     │
└──────────────────────┴──────────┴──────────┘
```

## Key Advantages

✅ **Accuracy**: Grounded in DSM-5-TR content  
✅ **Verifiability**: Every claim has a citation  
✅ **Privacy**: Local vector database  
✅ **Cost**: No Pinecone subscription  
✅ **Performance**: Fast local search  
✅ **Extensibility**: Easy to add more sources  

## Future Enhancements

### Phase 2: Query Optimization
- Query expansion (synonyms)
- Re-ranking results
- Relevance scoring

### Phase 3: GraphRAG
- Disorder relationships
- Differential diagnosis paths
- Symptom clustering

### Phase 4: Multi-Source
- ICD-11 guidelines
- Clinical practice guidelines
- PubMed research
- Drug databases
