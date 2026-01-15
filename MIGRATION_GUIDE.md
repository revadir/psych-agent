# Migration Guide: LLM-Only → RAG Architecture

## What Changed

### Before (LLM-Only)
```
User Query → Groq LLM → Response (no citations)
```

### After (RAG)
```
User Query → ChromaDB Search → Context + Groq LLM → Response + Citations
```

## Step-by-Step Migration

### 1. Verify Vector Database Exists

```bash
# Check if vector DB is present
ls -lh vector_db_hierarchical/

# Should see:
# - chroma.sqlite3
# - Collection folders with embeddings
```

If missing, regenerate:
```bash
cd backend
python ../scripts/ingest_hierarchical.py
```

### 2. Update Environment Variables

Add to `backend/.env`:
```bash
USE_RAG=true
VECTOR_DB_PATH=../vector_db_hierarchical
```

### 3. Install Dependencies (if needed)

```bash
cd backend
pip install langchain-chroma langchain-huggingface
```

### 4. Test RAG System

```bash
# Test vector search
python scripts/test_rag.py

# Should output:
# - Retrieved documents
# - Generated citations
# - Response with inline citations (^1, ^2, etc.)
```

### 5. Start Application

```bash
# Terminal 1: Backend
cd backend
python -m app.main

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 6. Verify in UI

Ask: **"What are the DSM-5-TR criteria for Major Depressive Disorder?"**

Expected:
- ✅ Response with inline citations (^1, ^2)
- ✅ Expandable citation cards below response
- ✅ Detailed metadata (ICD codes, hierarchy paths)

## Rollback to LLM-Only

If issues occur, temporarily disable RAG:

```bash
# In backend/.env
USE_RAG=false
```

Restart backend. System will use LLM-only fallback (no citations).

## Troubleshooting

### Issue: "Vector database not found"

**Solution:**
```bash
# Regenerate vector DB
cd backend
python ../scripts/ingest_hierarchical.py
```

### Issue: No citations in response

**Check:**
1. `USE_RAG=true` in `.env`
2. Vector DB path is correct
3. ChromaDB collection has documents:
```python
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
db = Chroma(persist_directory='vector_db_hierarchical', embedding_function=embeddings)
print(f'Documents: {db._collection.count()}')
```

### Issue: Slow responses

**Optimize:**
1. Reduce `k` parameter in `rag_service.py` (line 23): `k=3` instead of `k=5`
2. Use faster embedding model (if needed)
3. Add caching for frequent queries

### Issue: Poor quality responses

**Tune:**
1. Increase `k` parameter for more context
2. Adjust system prompt in `rag_service.py`
3. Improve chunking strategy in `ingest_hierarchical.py`

## Performance Comparison

| Metric | LLM-Only | RAG |
|--------|----------|-----|
| Response Time | 1-2s | 2-5s |
| Accuracy | Medium | High |
| Citations | None | 3-5 per response |
| Hallucinations | Possible | Minimal |
| Verifiability | Low | High |

## Next Steps

### Phase 2: Optimize RAG
- [ ] Add query expansion
- [ ] Implement re-ranking
- [ ] Cache frequent queries
- [ ] Add relevance scoring

### Phase 3: GraphRAG
- [ ] Build disorder relationship graph
- [ ] Add differential diagnosis paths
- [ ] Implement symptom clustering

### Phase 4: Multi-Source
- [ ] Add ICD-11 guidelines
- [ ] Integrate clinical practice guidelines
- [ ] Connect to PubMed for research

## Support

For issues or questions:
1. Check `RAG_ARCHITECTURE.md` for detailed documentation
2. Run `scripts/test_rag.py` for diagnostics
3. Review backend logs for errors

## Summary

✅ **RAG is now the primary method** for generating responses
✅ **Citations are automatically included** from DSM-5-TR
✅ **LLM-only fallback** available if RAG fails
✅ **No breaking changes** to frontend or API
✅ **Improved accuracy** and verifiability
