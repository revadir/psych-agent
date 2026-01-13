"""
FastAPI application entry point.
"""

print("🟡 DEBUG: Starting imports...")
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
print("🟡 DEBUG: Basic imports done, importing config...")
from app.core.config import settings
print("🟡 DEBUG: Config imported, importing routers...")
from app.api.auth import router as auth_router
print("🟡 DEBUG: Auth router imported...")
from app.api.admin import router as admin_router
print("🟡 DEBUG: Admin router imported...")
from app.api.chat import router as chat_router
print("🟡 DEBUG: Chat router imported...")
from app.api.feedback import router as feedback_router
print("🟡 DEBUG: Feedback router imported...")
from app.api.admin import router as admin_router_new
print("🟡 DEBUG: New admin router imported...")

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Psychiatric Clinical Decision Support API",
    description="API for psychiatric clinical decision support using DSM-5-TR",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(admin_router_new, prefix="/api")

# Serve static files (frontend)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend application."""
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend not built yet"}
else:
    @app.get("/")
    async def root():
        """Root endpoint when static files not available."""
        return {
            "message": "Psychiatric Clinical Decision Support API",
            "status": "ready",
            "version": "0.1.0",
            "frontend": "not built"
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.environment}


if __name__ == "__main__":
    try:
        print("🟡 DEBUG: Starting main...")
        print(f"🟡 DEBUG: Environment variables:")
        print(f"  - PORT: {os.getenv('PORT', 'not set')}")
        print(f"  - HOST: {os.getenv('HOST', 'not set')}")
        print(f"  - DATABASE_URL: {os.getenv('DATABASE_URL', 'not set')}")
        print(f"  - GROQ_API_KEY: {'set' if os.getenv('GROQ_API_KEY') else 'not set'}")
        
        import uvicorn
        print("🟡 DEBUG: Uvicorn imported, starting server...")
        port = int(os.getenv("PORT", settings.port))
        print(f"🟡 DEBUG: Starting on {settings.host}:{port}")
        uvicorn.run(app, host=settings.host, port=port)
    except Exception as e:
        print(f"🔴 ERROR: Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        raise
