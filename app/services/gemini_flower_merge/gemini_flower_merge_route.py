from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List
from .gemini_flower_merge_schema import GeminiFlowerMergeResponse
from .gemini_flower_merge_service import gemini_flower_merge_service

router = APIRouter(prefix="/flower-merge", tags=["Gemini Flower Merge"])


@router.post("/generate", response_model=GeminiFlowerMergeResponse)
async def generate_flower_composition(image_files: List[UploadFile] = File(...)):
    if not image_files or len(image_files) < 1 or len(image_files) > 6:
        raise HTTPException(status_code=400, detail="Provide 1-6 images")
    
    image_urls = await gemini_flower_merge_service.generate_flower_merge_image(image_files)
    
    return GeminiFlowerMergeResponse(
        success_message=f"Generated flower composition from {len(image_files)} images",
        image_urls=image_urls
    )