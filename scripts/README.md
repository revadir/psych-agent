# Scripts

Utility scripts for the psychiatric agent application.

## Available Scripts

### ingest.py
Ingests the DSM-5-TR PDF and builds the vector database.

**Usage:**
```bash
python scripts/ingest.py
```

**Requirements:**
- DSM-5-TR PDF must be located at `data/DSM5-TR.pdf`
- Creates vector database in `vector_db/` directory

## Future Scripts

Additional scripts will be added for:
- Database initialization (`init_db.py`)
- Allow-list management (`init_allowlist.py`)
- Deployment validation (`validate_deployment.py`)
