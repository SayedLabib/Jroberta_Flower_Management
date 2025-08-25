import base64
from typing import List
import openai
from app.core.config import settings
from app.services.Flower_merge.flower_merge_schema import FlowerMergeRequest, FlowerMergeResponse


class FlowerMergeAPIManager:
    """Simple API manager for creating flower bouquets using OpenAI"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.open_ai_api_key)
    
    def _validate_images(self, images: List[bytes]) -> None:
        """Validate uploaded images"""
        if len(images) < settings.min_images_per_request:
            raise ValueError(f"Need at least {settings.min_images_per_request} images")
        
        if len(images) > settings.max_images_per_request:
            raise ValueError(f"Too many images. Maximum is {settings.max_images_per_request}")
        
        for image_bytes in images:
            if len(image_bytes) > settings.max_file_size:
                raise ValueError(f"Image too large. Maximum size is {settings.max_file_size} bytes")
    
    def _analyze_flowers(self, images: List[bytes]) -> str:
        """Analyze flower images and return description"""
        # Convert images to base64
        encoded_images = [base64.b64encode(img).decode('utf-8') for img in images]
        
        # Create simple prompt for flower analysis
        content = [{"type": "text", "text": "Identify the flowers in these images and describe their colors. Format: 'flower1 - color1, flower2 - color2, etc.'"}]
        
        for encoded_image in encoded_images:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
            })
        
        # Get flower analysis
        response = self.client.chat.completions.create(
            model=settings.vision_model,
            messages=[{"role": "user", "content": content}],
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_bouquet_image(self, flower_description: str) -> str:
        """Generate bouquet image using DALL-E"""
        prompt = f"""A highly detailed, photorealistic photograph of a professionally arranged flower bouquet. 
The bouquet features the following flowers: {flower_description}. 
All flowers are tightly grouped into a classic bouquet shape with stems neatly bundled together and wrapped with a soft satin ribbon or floral paper in neutral tones (e.g., cream, white, or ivory). 

Style: Professional florist arrangement, wedding-style elegance, natural daylight lighting, shallow depth of field with a softly blurred background. 
Focus on texture and realism: visible petal veins, subtle shadows, natural color gradients, and lifelike greenery. 
No scattered petals, no loose stems, no artificial or surreal elements. 
Composition should be balanced and centered, suitable for bridal or formal event decor. 
High-resolution, 8K quality, studio photography style."""

        try:
            # Try DALL-E 3 first
            response = self.client.images.generate(
                model=settings.image_model_primary,
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                style="natural"
            )
            return response.data[0].url
            
        except Exception:
            # Fallback to DALL-E 2
            response = self.client.images.generate(
                model=settings.image_model_fallback,
                prompt=prompt,
                size="1024x1024"
            )
            return response.data[0].url
    
    def _generate_title(self, flower_description: str) -> str:
        """Generate a simple title for the bouquet"""
        response = self.client.chat.completions.create(
            model=settings.chat_model,
            messages=[{
                "role": "user",
                "content": f"Create a short bouquet title (max 5 words) for: {flower_description}"
            }],
            max_tokens=20
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
