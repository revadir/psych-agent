# Cloud Deployment Guide - RAG with Pinecone

## Overview

For cloud deployment (Railway + Vercel), we use **Pinecone** instead of ChromaDB because:
- Railway/Vercel have ephemeral filesystems
- ChromaDB files would be deleted on restart
- Pinecone provides persistent cloud vector storage

## Architecture

```
Local Development:
User → Backend (Railway) → ChromaDB (local) → Groq → Response

Cloud Production:
User → Backend (Railway) → Pinecone (cloud) → Groq → Response
```

The code **automatically detects** the environment and uses the appropriate vector DB.

## Step-by-Step Deployment

### 1. Setup Pinecone (One-Time)

```bash
# 1. Sign up at https://www.pinecone.io/ (free tier)
# 2. Create a new index:
#    - Name: psych-agent
#    - Dimensions: 384
#    - Metric: cosine
#    - Region: us-east-1 (or closest to you)
# 3. Copy your API key from the dashboard
```

### 2. Upload Vector Data to Pinecone (One-Time)

Run this **locally** to populate Pinecone:

```bash
cd /Users/vijayrevadigar/dev/psych_agent

# Set Pinecone credentials
export PINECONE_API_KEY="your-pinecone-api-key"
export PINECONE_ENVIRONMENT="us-east-1"  # or your region

# Upload data
cd backend
python ../scripts/upload_to_pinecone.py
```

Expected output:
```
🔄 Loading documents...
📄 Found 100 documents
🔄 Connecting to Pinecone...
✅ Connected to Pinecone
🔄 Uploading documents...
✅ Documents uploaded successfully!
🔄 Testing search...
✅ Search test returned 5 results
```

### 3. Configure Railway Environment Variables

In Railway dashboard (https://railway.app):

```bash
# Required
GROQ_API_KEY=gsk_your_groq_key
PINECONE_API_KEY=pc_your_pinecone_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=psych-agent

# RAG Configuration
USE_RAG=true

# Database
DATABASE_URL=postgresql://... (Railway provides this)

# Environment
ENVIRONMENT=production
```

### 4. Update Railway Deployment

```bash
# Commit changes
git add .
git commit -m "Add Pinecone cloud RAG support"
git push origin main

# Railway will auto-deploy
```

### 5. Verify Deployment

Test your production API:

```bash
# Test health endpoint
curl https://your-railway-app.railway.app/health

# Test chat (requires auth token)
curl -X POST https://your-railway-app.railway.app/api/chat/sessions/1/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "What are the criteria for Major Depressive Disorder?"}'
```

### 6. Update Vercel Frontend (if needed)

Your frontend should already point to the Railway backend. Verify in `frontend/.env.production`:

```bash
VITE_API_URL=https://your-railway-app.railway.app
```

## How It Works

### Automatic Environment Detection

The code automatically detects cloud vs local:

```python
# In cloud_agent_service.py
is_cloud = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("VERCEL")

if is_cloud:
    # Use Pinecone
    from app.services.cloud_rag_service import cloud_rag_service
    return cloud_rag_service.process_query(query)
else:
    # Use ChromaDB
    from app.services.rag_service import rag_service
    return rag_service.process_query(query)
```

### Local Development

```bash
# Uses ChromaDB (vector_db_hierarchical/)
cd backend
python -m app.main
```

### Cloud Production

```bash
# Uses Pinecone (automatic)
# Railway detects RAILWAY_ENVIRONMENT
# Switches to cloud_rag_service
```

## Cost Breakdown

### Pinecone Free Tier
- ✅ 1 index
- ✅ 100K vectors (enough for DSM-5-TR)
- ✅ 1 pod
- ✅ No credit card required

### Groq
- ✅ Free tier: 14,400 requests/day
- ✅ Fast inference
- ✅ No credit card required

### Railway
- ✅ $5/month starter plan
- ✅ Includes PostgreSQL

### Vercel
- ✅ Free tier for frontend
- ✅ Unlimited bandwidth

**Total: ~$5/month** (just Railway)

## Testing Cloud Deployment

### 1. Test Pinecone Connection

```bash
# SSH into Railway container
railway run bash

# Test Pinecone
python -c "
from app.services.pinecone_service import get_pinecone_service
ps = get_pinecone_service()
results = ps.search_similar_documents('depression', top_k=3)
print(f'Found {len(results)} results')
"
```

### 2. Test RAG Pipeline

```bash
# In Railway logs, look for:
✅ "Using Pinecone for cloud"
✅ "Found X results from Pinecone"
✅ "Generated Y citations"
```

### 3. Test in Browser

1. Go to https://psych-agent-mj5t.vercel.app
2. Login
3. Ask: "What are the criteria for Borderline Personality Disorder?"
4. Verify citations appear

## Troubleshooting

### "Pinecone API key not found"

```bash
# In Railway dashboard, verify:
PINECONE_API_KEY=pc_...
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=psych-agent
```

### "No results from Pinecone"

```bash
# Re-upload data
export PINECONE_API_KEY="your-key"
python scripts/upload_to_pinecone.py
```

### "ChromaDB error in cloud"

```bash
# Verify environment detection
# In Railway logs, should see:
"Detected cloud environment, using Pinecone"

# If not, add to Railway:
RAILWAY_ENVIRONMENT=production
```

### Slow responses

```python
# In cloud_rag_service.py, reduce top_k:
results = self.pinecone_service.search_similar_documents(query, top_k=3)
```

## Migration Checklist

- [ ] Sign up for Pinecone
- [ ] Create index (psych-agent, 384 dims, cosine)
- [ ] Upload data: `python scripts/upload_to_pinecone.py`
- [ ] Add Railway env vars (PINECONE_API_KEY, etc.)
- [ ] Commit and push code
- [ ] Verify Railway deployment
- [ ] Test in production browser
- [ ] Check citations appear

## Rollback Plan

If issues occur:

```bash
# In Railway, set:
USE_RAG=false

# System will fall back to LLM-only (no citations)
# Still functional, just without knowledge base
```

## Performance Comparison

| Metric | Local (ChromaDB) | Cloud (Pinecone) |
|--------|------------------|------------------|
| Vector Search | 100-200ms | 150-300ms |
| Total Latency | 2-5s | 2.5-5.5s |
| Citations | 3-5 | 3-5 |
| Accuracy | High | High |
| Cost | $0 | $0 (free tier) |

## Next Steps

After successful deployment:

1. ✅ Monitor Railway logs for errors
2. ✅ Check Pinecone usage dashboard
3. ✅ Test with real clinical queries
4. ✅ Verify citations are accurate
5. ✅ Monitor Groq API usage

## Summary

✅ **Pinecone** replaces ChromaDB for cloud  
✅ **Automatic detection** of environment  
✅ **One-time upload** of vector data  
✅ **No code changes** needed after setup  
✅ **Same citations** as local development  
✅ **Free tier** sufficient for your use case  

Your app will work identically in cloud and local, with the same detailed citations and RAG capabilities.
