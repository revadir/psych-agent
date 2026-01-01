# Project Structure

This document describes the production-grade organization of the psychiatric clinical decision support system.

## Directory Layout

```
psych-agent/
├── .kiro/                       # Kiro specifications
│   └── specs/
│       └── cloud-psychiatry-app/
│           ├── requirements.md  # System requirements
│           ├── design.md        # Design document
│           └── tasks.md         # Implementation tasks
│
├── frontend/                    # React application (to be initialized)
│   └── README.md
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI entry point
│   │   ├── api/                # API route handlers
│   │   │   └── __init__.py
│   │   ├── core/               # Core configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py       # Settings management
│   │   ├── models/             # Data models
│   │   │   └── __init__.py
│   │   ├── services/           # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── agent_service.py    # Psychiatric agent
│   │   │   └── vector_service.py   # Vector DB service
│   │   └── db/                 # Database utilities
│   │       └── __init__.py
│   ├── tests/                  # Backend tests
│   │   ├── __init__.py
│   │   └── conftest.py
│   ├── requirements.txt        # Python dependencies
│   └── README.md
│
├── data/                        # Data files
│   └── dsm5-tr.pdf             # DSM-5-TR source document
│
├── vector_db/                   # ChromaDB persistence directory
│
├── scripts/                     # Utility scripts
│   ├── ingest.py               # Vector DB ingestion
│   └── README.md
│
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
├── .python-version             # Python version specification
├── pyproject.toml              # Project metadata
├── README.md                   # Main project documentation
└── PROJECT_STRUCTURE.md        # This file
```

## Legacy Files

The following files from the original console application are preserved in the root directory but are no longer used:

- `agent.py` → Refactored into `backend/app/services/agent_service.py`
- `ingest.py` → Moved to `scripts/ingest.py`
- `strands_agent.py` → Alternative implementation (preserved for reference)
- `main.py` → Simple placeholder (replaced by `backend/app/main.py`)

These files can be removed once the migration is complete and verified.

## Key Design Principles

### Separation of Concerns
- **Frontend**: User interface and client-side logic
- **Backend**: API, business logic, and data access
- **Scripts**: One-time operations and utilities
- **Data**: Static data files and databases

### Configuration Management
- All configuration via environment variables
- `.env.example` provides template
- `backend/app/core/config.py` manages settings
- No hardcoded secrets or paths

### Extensibility
- Modular service architecture
- Clear interfaces between components
- Easy to add new features without refactoring
- Supports multiple LLM providers

### Production-Ready
- Proper error handling structure
- Logging configuration
- Testing infrastructure
- Deployment configuration support

## Next Steps

1. **Task 2**: Implement FastAPI application foundation
2. **Task 3**: Create database models and initialization
3. **Task 4**: Implement authentication service
4. **Task 10**: Initialize React frontend with Vite

## Migration Notes

### From Console to Web Application

**Original Structure:**
```
psych-agent/
├── agent.py          # Console agent
├── ingest.py         # Vector DB builder
├── strands_agent.py  # Alternative implementation
└── main.py           # Simple entry point
```

**New Structure:**
- Console agent logic → `backend/app/services/agent_service.py`
- Ingestion script → `scripts/ingest.py`
- New FastAPI app → `backend/app/main.py`
- Configuration → `backend/app/core/config.py`
- Frontend → `frontend/` (to be created)

### Benefits of New Structure

1. **Maintainability**: Clear separation makes code easier to understand and modify
2. **Testability**: Each component can be tested independently
3. **Scalability**: Easy to add new features and services
4. **Deployment**: Ready for containerization and cloud deployment
5. **Collaboration**: Multiple developers can work on different parts
6. **Best Practices**: Follows industry standards for Python and React projects
