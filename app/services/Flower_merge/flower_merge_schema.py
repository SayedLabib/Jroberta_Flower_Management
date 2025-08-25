from pydantic import BaseModel, Field, validator
from typing import Optional, List


class FlowerMergeRequest(BaseModel):
    images: List[bytes] = Field(..., description="List of 1-6 flower images to merge")
    
    @validator('images')
    def validate_images(cls, v):
        if not v:
            raise ValueError('At least one image is required')
        if len(v) > 6:
            raise ValueError('Maximum 6 images allowed')
        return v


class FlowerMergeResponse(BaseModel):
    title: str = Field(..., description="Title of the merged flower image according to the flower theme with a beautiful theme")
    imageURL: str = Field(..., description="URL of the merged flower image")

