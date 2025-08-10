from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.services.Flower_merge.flower_merge_routes import router as flower_merge_router
from app.core.config import settings

# Create FastAPI app with proper configuration
app = FastAPI(
    title=settings.app_name,
    description="Flower Management API - Merge multiple flower images into beautiful arrangements",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json"
)

# Include routers
app.include_router(flower_merge_router)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - redirects to docs"""
    return {
        "message": "Welcome to Flower Management API",
        "app_name": settings.app_name,
        "docs": "/docs",
        "health": "/flower-merge/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """General health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "debug": settings.debug
    }