# Psychiatric Clinical Decision Support System

A production-grade cloud-based psychiatric clinical decision support system that provides a modern web interface for Subject Matter Experts (SMEs) to interact with a DSM-5-TR knowledge base through an AI-powered chatbot.

## Overview

This application transforms the console-based psych_agent into a full-stack web application with:
- **Frontend**: React SPA with modern UI/UX for chat interactions
- **Backend**: FastAPI server exposing RESTful endpoints for agent operations
- **Data Layer**: ChromaDB vector database with DSM-5-TR embeddings

## Project Structure

```
psych-agent/
├── frontend/                    # React application (to be initialized)
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── api/                # API routes
│   │   ├── core/               # Core configuration
│   │   ├── models/             # Data models
│   │   ├── services/           # Business logic
│   │   └── db/                 # Database utilities
│   └── requirements.txt
├── data/                        # Data files (DSM-5-TR PDF)
├── vector_db/                   # ChromaDB persistence
├── scripts/                     # Utility scripts
│   └── ingest.py               # Vector DB ingestion
├── .env.example                # Environment template
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Ollama with deepseek-r1 model (or alternative LLM provider)

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Build the vector database (if not already done):
```bash
python scripts/ingest.py
```

### Frontend Setup

Frontend will be initialized in a later task using Vite and React.

## Development

### Running the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### Running the Original Console Agent

The original console-based agent code has been preserved and refactored into services:
- Original: `agent.py` → Now: `backend/app/services/agent_service.py`
- Original: `ingest.py` → Now: `scripts/ingest.py`

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options.

Key configuration areas:
- **Application**: Environment, secret keys, CORS origins
- **Database**: SQLite and vector DB paths
- **LLM**: Provider, model, API keys
- **Authentication**: JWT settings
- **Server**: Host, port, logging

## Architecture

The system uses a three-tier architecture:
1. **Frontend**: React SPA with modern UI/UX
2. **Backend**: FastAPI server with RESTful API
3. **Data Layer**: ChromaDB vector database + SQLite for sessions/users

For detailed architecture and design decisions, see `.kiro/specs/cloud-psychiatry-app/design.md`.

## Requirements

For detailed requirements, see `.kiro/specs/cloud-psychiatry-app/requirements.md`.

## Implementation Tasks

For the implementation plan and task list, see `.kiro/specs/cloud-psychiatry-app/tasks.md`.

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
