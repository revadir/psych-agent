# Cloud Migration Summary

## What You Need to Do

### 1. Sign Up for Pinecone (5 minutes)
- Go to https://www.pinecone.io/
- Sign up (free tier, no credit card)
- Create index: `psych-agent`, 384 dimensions, cosine metric
- Copy your API key

### 2. Upload Vector Data (5 minutes)
```bash
cd /Users/vijayrevadigar/dev/psych_agent
export PINECONE_API_KEY="your-key"
export PINECONE_ENVIRONMENT="us-east-1"
cd backend
python ../scripts/upload_to_pinecone.py
```

### 3. Configure Railway (2 minutes)
Add to Railway environment variables:
```
PINECONE_API_KEY=your-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=psych-agent
USE_RAG=true
```

### 4. Deploy (automatic)
```bash
git add .
git commit -m "Add Pinecone cloud RAG"
git push origin main
```

Railway will auto-deploy.

## What Changed

### New Files
- `backend/app/services/cloud_rag_service.py` - Pinecone RAG service
- `CLOUD_DEPLOYMENT.md` - Detailed deployment guide
- `QUICK_CLOUD_DEPLOY.md` - Quick reference

### Updated Files
- `backend/app/services/cloud_agent_service.py` - Auto-detects environment

### How It Works
```python
# Automatic environment detection
is_cloud = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("VERCEL")

if is_cloud:
    # Use Pinecone (cloud)
    from app.services.cloud_rag_service import cloud_rag_service
else:
    # Use ChromaDB (local)
    from app.services.rag_service import rag_service
```

## Architecture

### Local Development
```
Query → ChromaDB (local files) → Groq → Response + Citations
```

### Cloud Production
```
Query → Pinecone (cloud API) → Groq → Response + Citations
```

**Same code, same citations, different vector DB.**

## Why Pinecone?

Railway/Vercel have **ephemeral filesystems**:
- ❌ ChromaDB files deleted on restart
- ❌ Can't persist 13MB+ vector database
- ❌ No local storage

Pinecone solves this:
- ✅ Persistent cloud storage
- ✅ Free tier (100K vectors)
- ✅ Fast API access
- ✅ Same citation quality

## Cost

| Service | Cost |
|---------|------|
| Pinecone | Free (100K vectors) |
| Groq | Free (14K requests/day) |
| Railway | $5/month |
| Vercel | Free |
| **Total** | **$5/month** |

## Testing

### After Deployment

1. Go to https://psych-agent-mj5t.vercel.app
2. Login
3. Ask: "What are the DSM-5-TR criteria for Major Depressive Disorder?"
4. Verify:
   - ✅ Response with inline citations (^1, ^2, ^3)
   - ✅ Citation cards below response
   - ✅ Detailed metadata (ICD codes, hierarchy)

### Check Railway Logs

Should see:
```
✅ Detected cloud environment, using Pinecone
✅ Found 5 results from Pinecone
✅ Generated 5 citations
```

## Rollback

If issues occur:
```bash
# In Railway, set:
USE_RAG=false

# Falls back to LLM-only (no citations)
```

## Next Steps

1. ✅ Setup Pinecone
2. ✅ Upload vectors
3. ✅ Configure Railway
4. ✅ Deploy
5. ✅ Test in production
6. ✅ Monitor logs

## Documentation

- **`QUICK_CLOUD_DEPLOY.md`** - Quick reference (start here)
- **`CLOUD_DEPLOYMENT.md`** - Detailed guide
- **`RAG_ARCHITECTURE.md`** - Architecture details
- **`READY_TO_USE.md`** - Local testing guide

## Summary

✅ **Pinecone** replaces ChromaDB for cloud  
✅ **Automatic** environment detection  
✅ **One-time** vector upload  
✅ **Same** citations as local  
✅ **Free tier** sufficient  
✅ **$5/month** total cost  

Your production app will have the same RAG + citations as local development.
