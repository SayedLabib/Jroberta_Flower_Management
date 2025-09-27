from pydantic import BaseModel
from typing import List


class GeminiFlowerMergeResponse(BaseModel):
    success_message: str
    image_urls: List[str]