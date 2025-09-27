from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List
from .gemini_flower_merge_schema import GeminiFlowerMergeResponse
from .gemini_flower_merge_service import gemini_flower_merge_service

router = APIRouter(prefix="/flower-merge", tags=["Gemini Flower Merge"])


@router.post("/generate", response_model=GeminiFlowerMergeResponse)
async def generate_flower_composition(images: List[UploadFile] = File(...)):
    if not images or len(images) < 1 or len(images) > 6:
        raise HTTPException(status_code=400, detail="Provide 1-6 images")

    image_urls = await gemini_flower_merge_service.generate_flower_merge_image(images)

    return GeminiFlowerMergeResponse(
        title=f"Generated flower bouquet",
        imageURL=image_urls[0] if image_urls else None
    )