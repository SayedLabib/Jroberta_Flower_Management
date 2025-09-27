import base64
from typing import List
import openai
from app.core.config import settings
from app.services.Flower_merge.flower_merge_schema import FlowerMergeRequest, FlowerMergeResponse


class FlowerMergeAPIManager:
    """Simple API manager for creating flower bouquets using OpenAI"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.open_ai_api_key)
    
    def _detect_image_format(self, image_bytes: bytes) -> str:
        """Detect image format from bytes and return appropriate MIME type"""
        # Check magic bytes to determine image format
        if image_bytes.startswith(b'\xff\xd8\xff'):
            return "image/jpeg"
        elif image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return "image/png"
        elif image_bytes.startswith(b'GIF87a') or image_bytes.startswith(b'GIF89a'):
            return "image/gif"
        elif image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:12]:
            return "image/webp"
        else:
            # Default to JPEG if format cannot be determined
            return "image/jpeg"
    
    def _validate_images(self, images: List[bytes]) -> None:
        """Validate uploaded images"""
        if len(images) < settings.min_images_per_request:
            raise ValueError(f"Need at least {settings.min_images_per_request} images")
        
        if len(images) > settings.max_images_per_request:
            raise ValueError(f"Too many images. Maximum is {settings.max_images_per_request}")
        
        # Check total request size
        total_size = sum(len(image_bytes) for image_bytes in images)
        if total_size > settings.max_request_size:
            max_size_mb = settings.max_request_size / (1024 * 1024)
            raise ValueError(f"Total request size too large. Maximum is {max_size_mb}MB")
        
        for image_bytes in images:
            if len(image_bytes) > settings.max_file_size:
                raise ValueError(f"Image too large. Maximum size is {settings.max_file_size} bytes")

    """Used GPT 4 vision model for better extraction of flower details"""

    def _analyze_flowers(self, images: List[bytes]) -> str:
        """Analyze flower images and return detailed but concise description"""
        
        content = [{"type": "text", "text": "Identify each flower type with exact colors and key characteristics. Format: 'deep red roses with velvety petals, soft pink peonies, white baby's breath, purple lavender stems'. Be specific about flower types and accurate color descriptions."}]
        
        for image_bytes in images:
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            mime_type = self._detect_image_format(image_bytes)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"}
            })
        
       

        response = self.client.chat.completions.create(
            model=settings.vision_model,
            messages=[{"role": "user", "content": content}],
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_bouquet_image(self, flower_description: str) -> str:
        """Generate bouquet image with simple, realistic prompt"""
        
        # Simple 1-2 line prompt focusing on the essentials
        base_prompt = f"Generate flower bouquet with {flower_description}, tied with white ribbon, professional photography with realistic flowers, soft natural lighting, clean background."
        
        if settings.debug:
            print(f"DEBUG: Final prompt length: {len(base_prompt)} characters")
        
        try:
            # Try DALL-E 3 first
            response = self.client.images.generate(
                model=settings.image_model_primary,
                prompt=base_prompt,
                size="1024x1024",
                quality="hd",
                style="natural"
            )
            return response.data[0].url
            
        except Exception:
            
            # Used a Fallback mechanism in case DALL-E 3 fails iut will swich back to DALL-E 2 for security purposes

            response = self.client.images.generate(
                model=settings.image_model_fallback,
                prompt=base_prompt,
                size="1024x1024"
            )
            return response.data[0].url
    
    def _generate_title(self, flower_description: str) -> str:
        """Generate a simple title for the bouquet"""
        
        response = self.client.chat.completions.create(
            model=settings.chat_model,
            messages=[{
                "role": "user",
                "content": f"Create a short bouquet title (max 4 words) for: {flower_description}"
            }],
            max_tokens=15
        )
        
        return response.choices[0].message.content.strip().strip('"\'')
    

    
    def merge_flowers(self, request: FlowerMergeRequest) -> FlowerMergeResponse:
        """Create a flower bouquet from uploaded images"""
        try:
            # Validate images
            self._validate_images(request.images)
            
            if settings.debug:
                print(f"Processing {len(request.images)} flower images...")
            
            # Analyze flowers
            flower_description = self._analyze_flowers(request.images)
            if settings.debug:
                print(f"Flowers identified: {flower_description}")
            
            # Generate bouquet image
            image_url = self._generate_bouquet_image(flower_description)
            if settings.debug:
                print(f"Generated bouquet image: {image_url}")
            
            # Generate title
            title = self._generate_title(flower_description)
            if settings.debug:
                print(f"Generated title: {title}")
            
            return FlowerMergeResponse(title=title, imageURL=image_url)
            
        except Exception as e:
            if settings.debug:
                print(f"Error: {str(e)}")
            raise Exception(f"Failed to create bouquet: {str(e)}")


# Create singleton instance
flower_merge_api_manager = FlowerMergeAPIManager()
