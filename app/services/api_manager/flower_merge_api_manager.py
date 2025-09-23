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
        
        for image_bytes in images:
            if len(image_bytes) > settings.max_file_size:
                raise ValueError(f"Image too large. Maximum size is {settings.max_file_size} bytes")

    """Used GPT 4 vision model for better extraction of flower details"""

    def _analyze_flowers(self, images: List[bytes]) -> str:
        
        """Analyze flower images and return detailed description"""
     
        content = [{"type": "text", "text": """Analyze these flowers in extreme detail for a flower arrangement:
        1. Identify each flower species precisely (e.g., 'garden rose' instead of just 'rose')
        2. Describe the exact color shade (e.g., 'pale dusty pink' instead of just 'pink')
        3. Note any notable textures or petal formations
        4. Estimate the approximate size/scale
        
        Format your response as: 'flower1 - detailed color description, flower2 - detailed color description, etc.'
        Be extremely specific about colors as this will be used to generate a realistic image."""}]
        
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
            max_tokens=600
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_bouquet_image(self, flower_description: str) -> str:


        """ The prompt has been enhanced using the flower description which is holding the extracted flower details"""

        # Create optimized farbished prompt within OpenAI's 1000-character hard limit
        
        base_prompt = f"""Award-winning studio photograph: {flower_description}

Canon EOS R5, 85mm macro, f/2.8, professional lighting, 8K ultra-sharp, shallow depth of field, beautiful bokeh. Elegant 3/4 angle, natural depth, dimensional layers, organic asymmetry.

Master florist artisanal arrangement, organic flow, premium technique, natural movement. Pearl-white silk ribbon, subtle texture. Pearl-gray gradient background, rim lighting, gentle shadows, edge highlights.

Morning dew droplets, natural saturation, botanical accuracy, visible petal veins, authentic textures, natural stem placement, perfect light positioning.

Luxury editorial style, high-end botanical magazine quality, museum-grade floral art, commercial perfection with artistic soul, hyper-realistic with natural imperfections."""
        
        # Ensure we stay under OpenAI's 1000-character hard limit
        if len(base_prompt) > 1000:
            base_prompt = base_prompt[:997] + "..."
        
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

        """Generate a simple title for the generated bouquet using gpt-4o model"""


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
        # Use ALL uploaded images for comprehensive composition analysis


        content = [{"type": "text", "text": f"""Given these flower images and the description: '{flower_description}',
        suggest a natural bouquet arrangement style that would look realistic with these flowers.
        Consider:
        1. Overall shape (round, cascading, asymmetrical, etc.)
        2. Color distribution - maintain the approximate color ratio/balance from the original images
        3. Density and spacing of flowers
        4. Suitable complementary greenery or filler flowers
        5. Specify which flowers should be prominent/focal and which should be supporting
        
        Provide detailed composition guidance (max 150 words) as it will be used in an image generation prompt."""}]
        
        # Process ALL images with correct MIME type detection
        for image_bytes in images:
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            mime_type = self._detect_image_format(image_bytes)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"}
            })
        
        # Get composition analysis with increased token limit for more images
        response = self.client.chat.completions.create(
            model=settings.vision_model,
            messages=[{"role": "user", "content": content}],
            max_tokens=400
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
