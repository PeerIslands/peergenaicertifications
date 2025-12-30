"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.config.database import init_db
from src.config.initializer import initialize_data
from src.api.routes import users

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Modern REST API for user management - Migrated from Java Spring Boot",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS (matching legacy behavior)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)

# Health check endpoint at root level
@app.get("/health", tags=["health"])
def root_health_check():
    """Root level health check endpoint."""
    return {"status": "healthy", "message": "API is running!"}


@app.on_event("startup")
async def startup_event():
    """Initialize database and seed data on application startup."""
    print("Initializing database...")
    initialize_data()
    print("Application startup complete!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

