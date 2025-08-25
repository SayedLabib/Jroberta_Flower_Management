from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.services.Flower_merge.flower_merge import flower_merge_service
from app.services.Flower_merge.flower_merge_schema import FlowerMergeResponse
from app.core.config import settings

router = APIRouter(prefix="/flower-merge", tags=["Flower Bouquet Creation"])

@router.post("/upload", response_model=FlowerMergeResponse)
async def upload_flower_images(
    images: List[UploadFile] = File(..., description="Upload 4-6 flower images to create a bouquet")
):
    """
    Create a beautiful flower bouquet from 4-6 flower images.
    
    Requirements:
    - Minimum: 4 images
    - Maximum: 6 images
    - Supported formats: JPG, PNG, GIF, BMP, WEBP
    - Max file size: 10MB per image
    
    The AI will generate a beautiful bouquet arrangement from your flower images.
    """
    
    try:
        # Validate number of images
        if len(images) < settings.min_images_per_request:
            raise HTTPException(
                status_code=400, 
                detail=f"Minimum {settings.min_images_per_request} images required. You uploaded {len(images)} images."
            )
        
        if len(images) > settings.max_images_per_request:
            raise HTTPException(
                status_code=400, 
                detail=f"Maximum {settings.max_images_per_request} images allowed. You uploaded {len(images)} images."
            )
        
        # Validate and process each image
        image_bytes_list = []
        
        for i, image in enumerate(images, 1):
            # Validate file type
            if not image.content_type or not image.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Image {i} ({image.filename}) is not a valid image file. Only image files are allowed."
                )
            
            # Read image content
            content = await image.read()
            
            # Validate file size
            if len(content) > settings.max_file_size:
                max_size_mb = settings.max_file_size / (1024 * 1024)
                raise HTTPException(
                    status_code=400, 
                    detail=f"Image {i} ({image.filename}) exceeds maximum size of {max_size_mb}MB."
                )
            
            image_bytes_list.append(content)
        
        # Generate bouquet
        result = await flower_merge_service.process_flower_merge(images=image_bytes_list)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        if settings.debug:
            print(f"Error in upload_flower_images: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for the flower merge service"""
    return {
        "status": "healthy",
        "service": "flower-merge",
        "min_images": settings.min_images_per_request,
        "max_images": settings.max_images_per_request,
        "max_file_size_mb": settings.max_file_size / (1024 * 1024),
        "supported_formats": ["JPG", "PNG", "GIF", "BMP", "WEBP"],
        "ai_model": "DALL-E 3"
    }