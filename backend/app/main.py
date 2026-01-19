"""
FastAPI application entry point.
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Minimal health check first - no dependencies
app = FastAPI(title="Psych Agent API", version="0.1.0")

@app.get("/health")
async def health_check():
    """Minimal health check endpoint."""
    return {"status": "healthy"}

# Now load everything else
try:
    from app.core.config import settings
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup - load routers after health check is working
        try:
            include_routers()
        except Exception as e:
            logger.error(f"Failed to load routers: {e}")
        yield
        # Shutdown (if needed)

    # Update app with full config
    app.title = "Psychiatric Clinical Decision Support API"
    app.description = "API for psychiatric clinical decision support using DSM-5-TR"
    app.router.lifespan_context = lifespan

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Lazy import routers to speed up startup
    def include_routers():
        """Import and include routers only when needed"""
        from app.api.auth import router as auth_router
        from app.api.admin import router as admin_router
        from app.api.chat import router as chat_router
        from app.api.feedback import router as feedback_router
        from app.api.endpoints.asr import router as asr_router
        
        app.include_router(auth_router, prefix="/api")
        app.include_router(admin_router, prefix="/api")
        app.include_router(chat_router, prefix="/api")
        app.include_router(feedback_router, prefix="/api")
        app.include_router(asr_router, prefix="/api/asr")

except Exception as e:
    # If anything fails, at least health check works
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to load full app config: {e}")
    
    def include_routers():
        pass

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
    """Minimal health check endpoint."""
    return {"status": "healthy"}


@app.post("/setup-admin")
async def setup_admin(email: str = "revadigar@gmail.com"):
    """One-time setup endpoint to create admin user and all tables."""
    try:
        from app.db.session import get_db, SessionLocal
        from app.models import Allowlist, User
        from app.models.database import Base
        from app.db.session import engine
        
        db = SessionLocal()
        try:
            # Create all tables (including feedback, chat_sessions, etc.)
            Base.metadata.create_all(bind=engine)
            
            # Check if already in allowlist
            existing_allowlist = db.query(Allowlist).filter(Allowlist.email == email).first()
            if existing_allowlist:
                return {"message": "Admin user already exists, tables verified", "email": email}
            
            # Add to allowlist
            allowlist_entry = Allowlist(email=email, is_admin=True)
            db.add(allowlist_entry)
            db.commit()
            
            # Create user
            user = User(email=email, is_admin=True)
            db.add(user)
            db.commit()
            
            return {
                "message": "Admin user created successfully and all tables initialized",
                "email": email,
                "default_password": "admin123",
                "note": "Please change password after first login"
            }
        finally:
            db.close()
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    try:
        import uvicorn
        port = int(os.getenv("PORT", settings.port))
        uvicorn.run(app, host=settings.host, port=port)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
