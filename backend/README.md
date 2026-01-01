# Backend Application

FastAPI-based backend for the psychiatric clinical decision support system.

## Structure

```
backend/
├── app/
│   ├── api/                # API route handlers
│   ├── core/               # Core configuration and utilities
│   │   └── config.py       # Settings management
│   ├── models/             # Data models (SQLAlchemy, Pydantic)
│   ├── services/           # Business logic services
│   │   ├── agent_service.py    # Psychiatric agent logic
│   │   └── vector_service.py   # Vector DB interactions
│   ├── db/                 # Database utilities
│   └── main.py             # FastAPI app entry point
├── tests/                  # Backend tests
└── requirements.txt        # Python dependencies
```

## Services

### AgentService
Handles psychiatric clinical decision support queries using:
- ChromaDB for DSM-5-TR retrieval
- LLM (Ollama/OpenRouter) for reasoning
- Chain-of-thought prompting for clinical analysis

### VectorService
Manages interactions with the ChromaDB vector database:
- Similarity search
- Retriever creation
- Embedding consistency

## Configuration

Configuration is managed through `app/core/config.py` using Pydantic Settings.
All settings can be overridden via environment variables.

## Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests
```bash
pytest
```

## API Endpoints

API endpoints will be implemented in subsequent tasks:
- `/api/auth/*` - Authentication endpoints
- `/api/chat/*` - Chat session and message endpoints
- `/api/admin/*` - Admin endpoints for allow-list management
- `/api/health` - Health check endpoint

## Next Steps

1. Implement FastAPI application foundation (Task 2)
2. Create database models (Task 3)
3. Implement authentication (Task 4)
4. Build chat endpoints (Task 8)
