from pydantic import BaseModel, Field
from typing import List, Optional


class GeminiFlowerMergeResponse(BaseModel):
    title: str = Field(..., description="Title of the merged flower image according to the flower theme with a beautiful theme")
    imageURL: Optional[str] = Field(None, description="URL of the merged flower image")