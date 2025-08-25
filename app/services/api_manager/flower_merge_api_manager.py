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
        """Analyze flower images and return detailed description"""
        # Convert images to base64
        encoded_images = [base64.b64encode(img).decode('utf-8') for img in images]
        
        # Create detailed prompt for flower analysis
        content = [{"type": "text", "text": """Analyze these flowers in extreme detail for a flower arrangement:
        1. Identify each flower species precisely (e.g., 'garden rose' instead of just 'rose')
        2. Describe the exact color shade (e.g., 'pale dusty pink' instead of just 'pink')
        3. Note any notable textures or petal formations
        4. Estimate the approximate size/scale
        
        Format your response as: 'flower1 - detailed color description, flower2 - detailed color description, etc.'
        Be extremely specific about colors as this will be used to generate a realistic image."""}]
        
        for encoded_image in encoded_images:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
            })
        
        # Get flower analysis with increased token limit for more details
        response = self.client.chat.completions.create(
            model=settings.vision_model,
            messages=[{"role": "user", "content": content}],
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_bouquet_image(self, flower_description: str) -> str:
        """Generate bouquet image using DALL-E"""
        prompt = f"""Photorealistic photograph of a fresh flower bouquet taken by a professional botanical photographer.
                    8K ultra high-definition, shot with a Canon EOS R5, natural soft window lighting, shallow depth of field.
                    
                    The bouquet features exactly: {flower_description}
                    
                    Key photographic elements:
                    - Extremely natural arrangement that looks hand-assembled by a skilled florist
                    - Hyper-detailed textures showing individual petal veins and natural imperfections
                    - Subtle color transitions with accurate botanical coloration (no artificial saturation)
                    - Water droplets visible on some petals for freshness
                    - Stems wrapped in simple cream floral paper with minimal styling
                    - Shot against a neutral cream background with natural shadows
                    
                    This must be an ultra-realistic photograph of real flowers with botanical accuracy. Show the bouquet from a 3/4 angle to capture both the front arrangement and some side detail."""

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
    
    def _analyze_composition(self, images: List[bytes], flower_description: str) -> str:
        """Analyze the composition and arrangement style from the uploaded images"""
        # Convert images to base64 (use only first 3 images to stay within token limits)
        encoded_images = [base64.b64encode(img).decode('utf-8') for img in images[:3]]
        
        # Create prompt for composition analysis
        content = [{"type": "text", "text": f"""Given these flower images and the description: '{flower_description}',
        suggest a natural bouquet arrangement style that would look realistic with these flowers.
        Consider:
        1. Overall shape (round, cascading, asymmetrical, etc.)
        2. Color distribution - maintain the approximate color ratio/balance from the original images
        3. Density and spacing of flowers
        4. Suitable complementary greenery or filler flowers
        5. Specify which flowers should be prominent/focal and which should be supporting
        
        Keep your response concise (max 100 words) as it will be used in an image generation prompt."""}]
        
        for encoded_image in encoded_images:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
            })
        
        # Get composition analysis
        response = self.client.chat.completions.create(
            model=settings.vision_model,
            messages=[{"role": "user", "content": content}],
            max_tokens=250
        )
        
        return response.choices[0].message.content.strip()
    
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
            
            # Analyze composition style
            composition_style = self._analyze_composition(request.images, flower_description)
            if settings.debug:
                print(f"Composition style: {composition_style}")
            
            # Generate bouquet image with enhanced prompt including composition
            enhanced_description = f"{flower_description}. {composition_style}"
            image_url = self._generate_bouquet_image(enhanced_description)
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
