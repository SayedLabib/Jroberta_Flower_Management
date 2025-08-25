from typing import List
from app.services.Flower_merge.flower_merge_schema import FlowerMergeRequest, FlowerMergeResponse
from app.services.api_manager.flower_merge_api_manager import flower_merge_api_manager

class FlowerMergeService:

    def __init__(self):
        self.api_manager = flower_merge_api_manager

    async def process_flower_merge(
        self,
        images: List[bytes]
    ) -> FlowerMergeResponse:
        
        """
        Process 1-6 flower images and merge them into a bouquet
        
        Args:
            images: List of 1-6 flower image bytes
            
        Returns:
            FlowerMergeResponse with title and image URL
        """
        
        # Creating a request object
        request = FlowerMergeRequest(
            images=images
        )

        response = self.api_manager.merge_flowers(request)
        return response


flower_merge_service = FlowerMergeService()