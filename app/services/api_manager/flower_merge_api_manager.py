import openai
import base64
import io
from typing import Any, Dict, List, Optional
from PIL import Image
import requests
from app.core.config import settings
from app.services.Flower_merge.flower_merge_schema import FlowerMergeRequest, FlowerMergeResponse


class FlowerMergeAPIManager:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.open_ai_api_key)

    def _encode_image_to_base64(self, image_bytes: bytes) -> str:
        """Convert image bytes to base64 string for OpenAI API"""
        return base64.b64encode(image_bytes).decode('utf-8')

    def _validate_images(self, images: List[bytes]) -> bool:
        """Validate image inputs - require exactly 4 images"""
        if len(images) != 4:
            raise ValueError(f"Exactly 4 images required. Received: {len(images)}")
        
        for image_bytes in images:
            if len(image_bytes) > settings.max_file_size:
                raise ValueError(f"Image size too large. Maximum allowed: {settings.max_file_size} bytes")
        
        return True

    def merge_flowers(self, request: FlowerMergeRequest) -> FlowerMergeResponse:
        """Main method to merge flower images using DALL-E model"""
        try:
            # Validate inputs
            self._validate_images(request.images)
            
            if len(request.images) != 4:
                raise ValueError("Exactly 4 images are required")
            
            if settings.debug:
                print(f"Creating flower bouquet from 4 flower images...")

            # Create a robust prompt for DALL-E to generate a flower bouquet using only the provided flowers
            generation_prompt = """Create a realistic flower bouquet using ONLY the exact 4 flower types, colors, and varieties shown in the uploaded images. 

STRICT REQUIREMENTS:
- Use EXCLUSIVELY the 4 specific flower types from the provided images
- DO NOT add any other flowers, greenery, or decorative elements
- DO NOT use your imagination to create additional flower varieties
- Maintain the exact colors, shapes, and characteristics of the uploaded flowers
- Create a simple, natural bouquet arrangement
- Use realistic proportions and natural flower positioning
- Clean white or neutral background
- No artistic effects, filters, or stylized elements
- Photorealistic quality that matches the input flower images

FORBIDDEN:
- Adding extra flowers not shown in the images
- Changing flower colors from the originals
- Adding leaves, stems, or greenery not present in originals
- Using fantasy or stylized flower designs
- Adding decorative elements like ribbons, vases, or backgrounds

Generate a straightforward, realistic flower bouquet that combines ONLY these exact 4 flower types as they appear in the uploaded images."""

            if settings.debug:
                print("Generating flower bouquet with DALL-E...")

            # Generate image using DALL-E model
            image_response = self.client.images.generate(
                model="dall-e-3",
                prompt=generation_prompt,
                size="1024x1024",
                quality="standard",
                response_format="url",
                n=1
            )
            
            image_url = image_response.data[0].url

            # Generate a simple title for the bouquet
            title_messages = [
                {
                    "role": "system",
                    "content": "You create simple, descriptive titles for flower bouquets."
                },
                {
                    "role": "user",
                    "content": "Create a simple descriptive title (maximum 6 words) for a beautiful flower bouquet made from 4 different flower types."
                }
            ]

            title_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=title_messages,
                max_tokens=30,
                temperature=0.5
            )
            
            title = title_response.choices[0].message.content.strip().strip('"').strip("'")

            if settings.debug:
                print(f"Generated title: {title}")
                print(f"Image URL: {image_url}")

            return FlowerMergeResponse(
                title=title,
                imageURL=image_url
            )
            
        except Exception as e:
            if settings.debug:
                print(f"Error in flower merge: {str(e)}")
            raise Exception(f"Failed to merge flowers: {str(e)}")

# Create singleton instance
flower_merge_api_manager = FlowerMergeAPIManager()
