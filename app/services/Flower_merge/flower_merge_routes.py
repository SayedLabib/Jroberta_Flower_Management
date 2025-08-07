from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from typing import List, Optional
from app.services.Flower_merge.flower_merge import flower_merge_service
from app.services.Flower_merge.flower_merge_schema import FlowerMergeResponse
from app.core.config import settings

router = APIRouter(prefix="/flower-merge", tags=["Flower flourishment"])

@router.post("/upload", response_model=FlowerMergeResponse)
async def upload_flower_image(
        files: List[UploadFile] = File(..., description="Exactly 4 flower images required")
):
    
    """
    Merge exactly 4 flower images into a beautiful floral bouquet.
    
    This endpoint uses DALL-E to create a flower bouquet from the provided images.

    """

    try:

        if len(files) != 4:
            raise HTTPException(status_code=400, detail="Exactly 4 images are required.")
        
        # Read validate files
        image_bytes_list = []

        for file in files:
            # valid content type
            if not file.content_type or not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}. Only image files are allowed.")
            
            # Read file content
            content = await file.read()

            # validate file size
            if len(content) > settings.max_file_size:
                raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds the maximum size of {settings.max_file_size / (1024 * 1024)} MB.")
            
            image_bytes_list.append(content)

        # Process the flower merge after collecting all images
        result = await flower_merge_service.process_flower_merge(
            images=image_bytes_list
        )

        return result
        
    except HTTPException:
        raise
    except Exception as e:
        if settings.debug:
            print(f"Error in merge_flowers endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error during flower merge: {str(e)}"
        )
    
@router.get("/health")
async def health_check():
    """Health check endpoint for the flower merge service"""
    return {
        "status": "healthy",
        "service": "flower-merge",
        "required_images": 4,
        "max_file_size": settings.max_file_size,
        "generation_model": "dall-e-3",
        "features": ["4 flower images", "automatic bouquet creation"],
        "output_format": "PNG (fixed)",
        "debug": f"Fixed to {settings.debug}"
    }