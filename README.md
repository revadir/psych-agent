# Psych Agent - Psychiatric Clinical Decision Support System

A production-grade web application that provides psychiatric clinical decision support using DSM-5-TR diagnostic criteria through an AI-powered interface.

## 🚀 Quick Start

### Prerequisites

Make sure you have these installed on your machine:

- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Ollama** - [Download here](https://ollama.ai/) (for local AI model)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/psych-agent.git
cd psych-agent

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Install Node.js dependencies
cd frontend
npm install
cd ..
```

### 2. Setup Ollama AI Model

```bash
# Install and start Ollama (if not already running)
ollama serve

# In a new terminal, pull the required model
ollama pull llama3.2:1b
```

### 3. Initialize Database

```bash
# From the project root directory
cd backend
python -c "
from app.db.session import engine
from app.models.database import Base
Base.metadata.create_all(bind=engine)
print('Database initialized!')
"

# Create admin user
python -c "
from app.db.session import SessionLocal
from app.services.auth_service import AuthService
db = SessionLocal()
try:
    AuthService.add_user_to_allowlist(db, 'admin@example.com', is_admin=True)
    print('Admin user created: admin@example.com / admin123')
finally:
    db.close()
"
```

### 4. Setup Vector Database

The application requires a vector database with DSM-5-TR content. You'll need to obtain and process the DSM-5-TR document:

#### Obtain DSM-5-TR
1. **Purchase/Access DSM-5-TR**: You need a legitimate copy of the DSM-5-TR PDF
   - Available from [American Psychiatric Association](https://www.psychiatry.org/psychiatrists/practice/dsm)
   - Many universities and medical institutions provide access
   - Check your local medical library

2. **Place the PDF**: Save the DSM-5-TR PDF as `DSM-5-TR.pdf` in the `data/` directory:
   ```bash
   # Create data directory if it doesn't exist
   mkdir -p data
   # Place your DSM-5-TR PDF here
   cp /path/to/your/DSM-5-TR.pdf data/DSM-5-TR.pdf
   ```

#### Create Vector Database
```bash
# From the project root directory
cd backend
python ../scripts/ingest_hierarchical.py
```

#### Create Vector Database
```bash
# From the project root directory
cd backend
python ../scripts/ingest_hierarchical.py
```

This will create the `vector_db_hierarchical/` directory with processed embeddings.

**Note:** The vector database creation may take several minutes depending on your system.

### 5. Setup ASR Integration (Optional)

For speech-to-text functionality:

```bash
# Run the ASR setup script
python scripts/setup_asr.py

# Or manually add to backend/.env:
# ASSEMBLYAI_API_KEY=your_api_key_here
```

**Get AssemblyAI API Key:**
1. Sign up at [AssemblyAI](https://www.assemblyai.com/)
2. Get $50 free credits (~3,700 minutes)
3. Copy API key from dashboard

### 6. Run the Application

**Terminal 1 - Start Backend:**
```bash
cd backend
LLM_MODEL=llama3.2:1b python -m app.main
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Access the Application

1. Open your browser to: **http://localhost:5173**
2. Login with: **admin@example.com** / **admin123**
3. Start asking clinical questions!

## 🏗️ Architecture

```
psych-agent/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── core/           # Configuration & auth
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   └── requirements.txt
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts
│   │   └── services/       # API client
│   └── package.json
├── data/                   # DSM-5-TR PDF and documents
├── vector_db/             # ChromaDB vector database
└── scripts/               # Utility scripts
```

## 🎯 Features

- **DSM-5-TR Integration**: Complete diagnostic criteria database
- **AI-Powered Responses**: Uses local Ollama models for privacy
- **Real-time Chat**: Streaming responses with citations
- **Clinical Accuracy**: Structured diagnostic criteria with ICD codes
- **Modern UI**: Walnut sci-fi theme with responsive design
- **Secure**: JWT authentication with user management
- **Expandable Citations**: Full DSM-5-TR references with metadata
- **🎤 ASR Integration**: Real-time speech-to-text with AssemblyAI
- **📋 Clinical Reports**: AI-generated structured clinical reports
- **🔊 Audio Recording**: Record sessions or upload audio files

## 🛠️ Development

### Backend Development

```bash
cd backend

# Run with auto-reload
LLM_MODEL=llama3.2:1b uvicorn app.main:app --reload --port 8001

# Run tests
python -m pytest

# Add new dependencies
pip install package_name
pip freeze > requirements.txt
```

### Frontend Development

```bash
cd frontend

# Start development server
npm run dev

# Build for production
npm run build

# Add new dependencies
npm install package_name
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Environment
DATABASE_URL=sqlite:///./data/app.db
VECTOR_DB_PATH=../vector_db_hierarchical

# LLM Configuration
LLM_MODEL=llama3.2:1b
LLM_TEMPERATURE=0.1
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Server
HOST=127.0.0.1
PORT=8001
ENVIRONMENT=development
```

## 🔧 Troubleshooting

### Common Issues

**Backend won't start:**
- Ensure Python virtual environment is activated
- Check that Ollama is running: `ollama serve`
- Verify the model is installed: `ollama list`

**Frontend connection errors:**
- Ensure backend is running on port 8001
- Check browser console for specific errors
- Try hard refresh (Cmd+Shift+R / Ctrl+Shift+R)

**Database errors:**
- Run the database initialization commands again
- Check that SQLite file has write permissions

**AI responses not working:**
- Verify Ollama is running and model is pulled
- Check backend logs for LLM connection errors
- Ensure `LLM_MODEL` environment variable is set

**Vector database errors:**
- Ensure DSM-5-TR.pdf is in the `data/` directory
- Run the ingestion script: `python scripts/ingest_hierarchical.py`
- Check that `vector_db_hierarchical/` directory was created

### Getting Help

1. Check the backend logs in Terminal 1
2. Check browser console (F12) for frontend errors
3. Ensure all prerequisites are properly installed
4. Verify environment variables are set correctly

## 📝 Usage Examples

**Ask about diagnostic criteria:**
- "What are the DSM-5-TR diagnostic criteria for Major Depressive Disorder?"
- "Show me the criteria for Borderline Personality Disorder F60.3"
- "What are the symptoms of ADHD?"

**Clinical scenarios:**
- "Patient presents with mood swings and fear of abandonment"
- "Describe the diagnostic features of Intermittent Explosive Disorder"

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add feature description"`
5. Push to your fork: `git push origin feature-name`
6. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This is a clinical decision support tool and not a replacement for professional psychiatric evaluation. Always consult with qualified mental health professionals for diagnosis and treatment decisions.
