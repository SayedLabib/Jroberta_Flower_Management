from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.services.Flower_merge.flower_merge_routes import router as flower_merge_router
from app.services.gemini_flower_merge.gemini_flower_merge_route import router as gemini_flower_merge_router
from app.core.config import settings
import os

# Create FastAPI app with proper configuration
app = FastAPI(
    title=settings.app_name,
    description="Flower Management API - Merge multiple flower images into beautiful arrangements",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json"
)

# Create temporary generated images directory if it doesn't exist
temp_generated_images_dir = "temp_generated_images"
os.makedirs(temp_generated_images_dir, exist_ok=True)

# Mount static files for serving temporary generated images
app.mount("/temp-generated-images", StaticFiles(directory=temp_generated_images_dir), name="temp-generated-images")

# Include routers
app.include_router(flower_merge_router)
app.include_router(gemini_flower_merge_router)

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