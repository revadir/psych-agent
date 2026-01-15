# Quick Cloud Deployment Steps

## TL;DR

1. **Setup Pinecone** (5 min)
2. **Upload vectors** (5 min)
3. **Configure Railway** (2 min)
4. **Deploy** (automatic)

## 1. Setup Pinecone

```bash
# Go to: https://www.pinecone.io/
# Sign up (free)
# Create index:
#   Name: psych-agent
#   Dimensions: 384
#   Metric: cosine
# Copy API key
```

## 2. Upload Your DSM-5-TR Data

```bash
cd /Users/vijayrevadigar/dev/psych_agent

# Set credentials
export PINECONE_API_KEY="pc_your_key_here"
export PINECONE_ENVIRONMENT="us-east-1"

# Upload (one-time)
cd backend
python ../scripts/upload_to_pinecone.py

# Should see: ✅ Documents uploaded successfully!
```

## 3. Configure Railway

Add these environment variables in Railway dashboard:

```bash
PINECONE_API_KEY=pc_your_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=psych-agent
USE_RAG=true
```

## 4. Deploy

```bash
git add .
git commit -m "Add Pinecone cloud RAG"
git push origin main

# Railway auto-deploys
```

## 5. Test

Go to: https://psych-agent-mj5t.vercel.app

Ask: "What are the criteria for Major Depressive Disorder?"

Should see: Response with citations (^1, ^2, ^3)

## How It Works

```
Local:  ChromaDB (vector_db_hierarchical/) → Groq
Cloud:  Pinecone (cloud vector DB) → Groq
```

Code automatically detects environment and uses the right one.

## Cost

- Pinecone: **Free** (100K vectors)
- Groq: **Free** (14K requests/day)
- Railway: **$5/month**
- Vercel: **Free**

**Total: $5/month**

## Troubleshooting

**No citations?**
```bash
# Check Railway logs for:
"Using Pinecone for cloud"
"Found X results from Pinecone"
```

**Upload failed?**
```bash
# Verify credentials
echo $PINECONE_API_KEY
echo $PINECONE_ENVIRONMENT

# Try again
python scripts/upload_to_pinecone.py
```

## Files Changed

- ✅ `backend/app/services/cloud_rag_service.py` (new)
- ✅ `backend/app/services/cloud_agent_service.py` (updated)
- ✅ `scripts/upload_to_pinecone.py` (already exists)

## That's It!

Your cloud deployment will have the same RAG + citations as local development.

See `CLOUD_DEPLOYMENT.md` for detailed guide.
