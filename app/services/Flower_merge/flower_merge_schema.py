from pydantic import BaseModel, Field
from typing import Optional, List


class FlowerMergeRequest(BaseModel):
    images: List[bytes] = Field(..., description="List of exactly 4 flower images to merge")


class FlowerMergeResponse(BaseModel):
    title: str = Field(..., description="Title of the merged flower image according to the flower theme with a beautiful theme")
    imageURL: str = Field(..., description="URL of the merged flower image")

